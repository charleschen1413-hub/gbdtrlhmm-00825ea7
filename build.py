#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only ingest of /workspace/ml_meta summaries → append-only entries + index.html.

Idempotent: never overwrites an existing entries/* file. history.json is append-only.
Does not modify any file under /workspace/ml_meta.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown

TZ = ZoneInfo("Asia/Taipei")
ROOT = Path(__file__).resolve().parent
ENTRIES = ROOT / "entries"
HISTORY_PATH = ROOT / "history.json"
SRC_ROOT = Path("/workspace/ml_meta")

DISCLAIMER = "探索性、非獨立盲測；非官方驗收"
TRIALS_BASE = 10440
TRIALS_BASE_NOTE = "10,440（第一輪 8,820＋第二輪 1,620）"

# Named sources that must appear as 找到 or 未找到, even if missing.
FIXED_SOURCES = [
    SRC_ROOT / "PLAN_v13.md",
    SRC_ROOT / "reports" / "DIAG_TRADECOUNT_v1.md",
    SRC_ROOT / "reports" / "INVENTORY_priorphases_v1.md",
    SRC_ROOT / "v14" / "progress.json",
    SRC_ROOT / "v14" / "SUMMARY_v14.md",
    SRC_ROOT / "v14" / "EXPERIMENT_LOG.md",
]
# If these exact paths are absent, still list them as 未找到.
EXPECTED_MAYBE_MISSING = [
    SRC_ROOT / "round1_run" / "SUMMARY.md",
    SRC_ROOT / "v14" / "SUMMARY_v14.md",
    SRC_ROOT / "v14" / "EXPERIMENT_LOG.md",
]
DISCOVER_DIRS = [
    SRC_ROOT / "round1_run",
    SRC_ROOT / "official_v1",
    SRC_ROOT / "round2_run",
]

# Trial-level CSVs above this row count are recorded by sha1/header only
# (no full dump; those files list per-trial ledger sha1s).
CSV_FULL_SNAPSHOT_MAX_ROWS = 120

SENSITIVE_RE = re.compile(
    r"token|password|passwd|secret|ghp_|gho_|github_pat|AKIA|"
    r"BEGIN PRIVATE|api[_-]?key|credential|npm_token|xox[bps]-",
    re.IGNORECASE,
)


def now_taipei() -> datetime:
    return datetime.now(TZ)


def stamp(dt: datetime) -> str:
    return dt.strftime("%Y%m%d_%H%M")


def stamp_human(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") + "（台北時間）"


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def sha1_file(path: Path) -> str:
    return sha1_bytes(path.read_bytes())


def slug_for(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(SRC_ROOT.resolve())
    except ValueError:
        rel = path.name
    text = str(rel).replace("\\", "/")
    text = text.replace("/", "_")
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text)
    return text


def discover_summary_files() -> list[Path]:
    found: list[Path] = []
    for d in DISCOVER_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_file() and "summary" in p.name.lower():
                found.append(p)
    return found


def collect_sources() -> tuple[list[Path], list[Path]]:
    """Return (existing files to snapshot, missing expected paths)."""
    wanted: dict[str, Path] = {}
    for p in FIXED_SOURCES:
        wanted[str(p)] = p
    for p in discover_summary_files():
        wanted[str(p)] = p
    existing: list[Path] = []
    missing: list[Path] = []
    for p in wanted.values():
        if p.is_file():
            existing.append(p)
        else:
            missing.append(p)
    for p in EXPECTED_MAYBE_MISSING:
        if not p.is_file() and p not in missing:
            missing.append(p)
    existing.sort(key=lambda x: str(x))
    missing.sort(key=lambda x: str(x))
    return existing, missing


def load_history() -> list[dict]:
    if not HISTORY_PATH.is_file():
        return []
    data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("history.json 不是陣列，拒絕覆寫；請人工檢查")
    return data


def save_history(rows: list[dict]) -> None:
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    HISTORY_PATH.write_text(text, encoding="utf-8")


def csv_to_markdown(path: Path, max_rows: int) -> tuple[str, bool]:
    """Return (markdown, truncated?)."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    if not rows:
        return "_（空檔）_\n", False

    def esc(cell: str) -> str:
        return cell.replace("|", "\\|").replace("\n", " ").strip()

    header = rows[0]
    body = rows[1:]
    truncated = len(body) > max_rows
    if truncated:
        body = body[:max_rows]
    lines = [
        "| " + " | ".join(esc(c) for c in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for r in body:
        # pad / trim to header width
        cells = list(r) + [""] * max(0, len(header) - len(r))
        cells = cells[: len(header)]
        lines.append("| " + " | ".join(esc(c) for c in cells) + " |")
    if truncated:
        lines.append("")
        lines.append(
            f"以下列數超過 {max_rows}，完整列未收入本快照（避免刊登試驗級帳本欄位）；"
            f"來源共 {len(rows)-1} 列資料。只保留檔名與 sha1 供核對。"
        )
        # For truncated files, do not include the partial table either —
        # only metadata + columns + count, to avoid an incomplete official record.
        col_list = "、".join(f"`{c}`" for c in header)
        return (
            f"此 CSV 為試驗級摘要（{len(rows)-1} 列），未全文刊登。\n\n"
            f"- 欄位：{col_list}\n"
            f"- 資料列數：{len(rows)-1}\n"
        ), True
    return "\n".join(lines) + "\n", False


def snapshot_markdown(path: Path, sha: str, when: datetime) -> str:
    header = (
        f"# 來源快照：`{path}`\n\n"
        f"- **{DISCLAIMER}**\n"
        f"- 來源路徑：`{path}`\n"
        f"- sha1：`{sha}`\n"
        f"- 快照時間：{stamp_human(when)}\n"
        f"- 本頁只轉述來源文件已有的內容，不自行推論或加數字。\n\n"
        f"---\n\n"
    )
    suffix = path.suffix.lower()
    if suffix == ".md":
        body = path.read_text(encoding="utf-8", errors="replace")
        return header + body + ("\n" if not body.endswith("\n") else "")
    if suffix == ".json":
        raw = path.read_text(encoding="utf-8", errors="replace")
        try:
            pretty = json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pretty = raw
        return header + "```json\n" + pretty + "\n```\n"
    if suffix == ".csv":
        table, _ = csv_to_markdown(path, CSV_FULL_SNAPSHOT_MAX_ROWS)
        return header + table
    # Fallback: treat as text, but only first 200 lines to stay summary-sized
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if len(lines) > 200:
        text = "\n".join(lines[:200]) + f"\n\n…（來源共 {len(lines)} 行，其餘未刊登，只保留 sha1。）\n"
    return header + "```\n" + text + "\n```\n"


def page_shell(title: str, body: str, rel_prefix: str = "") -> str:
    css = f"{rel_prefix}style.css"
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{css}">
</head>
<body>
  <div class="wrap">
    <div class="banner">{html.escape(DISCLAIMER)}</div>
    {body}
    <footer>
      <p>{html.escape(DISCLAIMER)}　本站只刊登彙總結果與檔名／sha1，不刊登原始資料、tick、帳本 CSV 或憑證。</p>
    </footer>
  </div>
</body>
</html>
"""


def render_md_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"],
        output_format="html5",
    )


def write_entry_html(md_path: Path, html_path: Path, title: str) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    body = (
        f'<p class="back"><a href="../index.html">← 回到索引</a></p>\n'
        f'<header class="site"><h1>{html.escape(title)}</h1>'
        f'<p class="sub">{html.escape(DISCLAIMER)}</p></header>\n'
        f'<div class="entry-body scroll">{render_md_html(md_text)}</div>\n'
    )
    html_path.write_text(page_shell(f"{title}｜{DISCLAIMER}", body, "../"), encoding="utf-8")


def read_v14_trials(existing: list[Path]) -> dict:
    """Quote v14 trial fields as written; never invent."""
    out = {
        "progress_path": str(SRC_ROOT / "v14" / "progress.json"),
        "progress_found": False,
        "progress_sha1": None,
        "fields": {},
        "summary_v14_path": str(SRC_ROOT / "v14" / "SUMMARY_v14.md"),
        "summary_v14_found": False,
        "summary_v14_sha1": None,
        "summary_v14_note": "未取得",
    }
    prog = SRC_ROOT / "v14" / "progress.json"
    if prog.is_file():
        out["progress_found"] = True
        out["progress_sha1"] = sha1_file(prog)
        try:
            data = json.loads(prog.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            out["fields"] = {"_error": "progress.json 不是合法 JSON，未解析試驗數"}
        else:
            keys = [
                "v14_trials_done",
                "cumulative_trials_prior",
                "cumulative_trials_now",
                "done",
                "total",
                "stage",
                "stage_detail",
                "results_label",
                "updated_at_taipei",
                "note",
            ]
            fields = {}
            for k in keys:
                if k in data:
                    fields[k] = data[k]
            out["fields"] = fields
    summ = SRC_ROOT / "v14" / "SUMMARY_v14.md"
    if summ.is_file():
        out["summary_v14_found"] = True
        out["summary_v14_sha1"] = sha1_file(summ)
        out["summary_v14_note"] = "已找到，見該來源快照；本索引不自行加總數字。"
    return out


def excerpt_section(md_text: str, heading_substrings: list[str], max_chars: int = 4000) -> str | None:
    lines = md_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("#") and any(s in line for s in heading_substrings):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    level = len(lines[start]) - len(lines[start].lstrip("#"))
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("#"):
            this = len(lines[j]) - len(lines[j].lstrip("#"))
            if this <= level:
                end = j
                break
    text = "\n".join(lines[start:end]).strip()
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n…（摘錄截斷，完整內容見快照頁。）"
    return text


def build_index(
    when: datetime,
    existing: list[tuple[Path, str]],
    missing: list[Path],
    history: list[dict],
    added: list[dict],
    skipped_existed: list[str],
    v14: dict,
) -> str:
    # Latest entry per source_path
    latest_by_src: dict[str, dict] = {}
    for row in history:
        src = row.get("source_path")
        if src:
            latest_by_src[src] = row  # history is append-only, last wins

    def src_rows() -> str:
        parts = []
        for path, sha in existing:
            rec = latest_by_src.get(str(path))
            link = ""
            if rec and rec.get("html"):
                href = html.escape(rec["html"])
                link = f'<a href="{href}">最新快照</a>'
            parts.append(
                "<tr class='found'>"
                f"<td><code>{html.escape(str(path))}</code></td>"
                f"<td class='sha'>{html.escape(sha)}</td>"
                f"<td>{link}</td>"
                "</tr>"
            )
        return "\n".join(parts)

    miss_rows = "\n".join(
        f"<tr class='missing'><td><code>{html.escape(str(p))}</code></td><td>未找到</td><td></td></tr>"
        for p in missing
    )

    # history newest first for display; do not mutate history
    hist_rev = list(reversed(history))
    hist_rows = []
    for row in hist_rev:
        href = html.escape(row.get("html") or row.get("filename") or "")
        hist_rows.append(
            "<tr>"
            f"<td>{html.escape(row.get('time_taipei', ''))}</td>"
            f"<td><code>{html.escape(row.get('source_path', ''))}</code></td>"
            f"<td class='sha'>{html.escape(row.get('sha1', ''))}</td>"
            f"<td><a href='{href}'>{html.escape(Path(row.get('filename') or href).name)}</a></td>"
            "</tr>"
        )
    hist_table = "\n".join(hist_rows) if hist_rows else "<tr><td colspan='4'>尚無快照</td></tr>"

    # excerpts from latest known markdown summaries (verbatim sections)
    excerpts = []
    excerpt_specs = [
        (SRC_ROOT / "PLAN_v13.md", ["結論先講"], "PLAN_v13.md 結論先講"),
        (SRC_ROOT / "official_v1" / "SUMMARY.md", ["結論"], "official_v1/SUMMARY.md 結論"),
        (SRC_ROOT / "round2_run" / "SUMMARY_v1.md", ["官方路徑", "第二輪 tick", "結論"], None),
        (SRC_ROOT / "reports" / "DIAG_TRADECOUNT_v1.md", ["結論先講"], "DIAG_TRADECOUNT_v1.md 結論先講"),
    ]
    # For round2, include the whole short file rather than multiple sections
    r2 = SRC_ROOT / "round2_run" / "SUMMARY_v1.md"
    for path, heads, title in excerpt_specs:
        if path == r2:
            if path.is_file():
                excerpts.append(
                    f"<h3>{html.escape('round2_run/SUMMARY_v1.md（全文轉載於快照，此處為原文）')}</h3>\n"
                    f"<div class='scroll'>{render_md_html(path.read_text(encoding='utf-8'))}</div>"
                )
            continue
        if not path.is_file():
            continue
        text = excerpt_section(path.read_text(encoding="utf-8"), heads)
        if not text:
            continue
        excerpts.append(
            f"<h3>{html.escape(title)}</h3>\n"
            f"<div class='scroll'>{render_md_html(text)}</div>"
        )

    # v14 trials block — only quote fields present
    if v14["progress_found"]:
        field_lis = "".join(
            f"<li><code>{html.escape(k)}</code>：<code>{html.escape(json.dumps(v, ensure_ascii=False))}</code></li>"
            for k, v in v14["fields"].items()
        )
        v14_prog = (
            f"<p>已找到 <code>{html.escape(v14['progress_path'])}</code>，"
            f"sha1 <code>{html.escape(v14['progress_sha1'])}</code>。來源欄位原文：</p>"
            f"<ul class='plain'>{field_lis}</ul>"
        )
    else:
        v14_prog = f"<p>未取得 <code>{html.escape(v14['progress_path'])}</code>，不猜測試驗數。</p>"

    if v14["summary_v14_found"]:
        v14_sum = (
            f"<p>已找到 <code>{html.escape(v14['summary_v14_path'])}</code>，"
            f"sha1 <code>{html.escape(v14['summary_v14_sha1'])}</code>。{html.escape(v14['summary_v14_note'])}</p>"
        )
    else:
        v14_sum = f"<p><code>{html.escape(v14['summary_v14_path'])}</code>：未取得。</p>"

    added_note = "、".join(html.escape(r["filename"]) for r in added) or "無（本分鐘已有同名快照，未覆寫）"
    skipped_note = "、".join(html.escape(s) for s in skipped_existed)
    added_line = f"本次新寫入：{added_note}"
    if skipped_note:
        added_line += f"；同名已存在故跳過：{skipped_note}"

    body = f"""
    <header class="site">
      <h1>GBDTRLHMM 新制度變形｜結果彙總</h1>
      <p class="sub">專屬累積頁。歷史只附加、不覆蓋舊紀錄。{html.escape(DISCLAIMER)}</p>
    </header>

    <section class="card">
      <h2>試驗累計</h2>
      <p>起點：{html.escape(TRIALS_BASE_NOTE)}。此起點依本頁建置任務設定，不是本腳本自行加總。</p>
      <p>v14 試驗數只轉述來源檔已寫下的欄位；讀不到就寫「未取得」，不猜測。</p>
      {v14_prog}
      {v14_sum}
    </section>

    <section class="card">
      <h2>來源檔（本次掃描）</h2>
      <p class="meta">最新快照：{html.escape(history[-1]["time_taipei"] if history else "尚無")}。只讀 <code>/workspace/ml_meta</code>，未改動來源。</p>
      <div class="scroll">
      <table>
        <thead><tr><th>來源路徑</th><th>sha1</th><th>快照</th></tr></thead>
        <tbody>
          {src_rows()}
          {miss_rows}
        </tbody>
      </table>
      </div>
      <p class="meta">歷史只附加：來源內容若與上一筆快照 sha1 相同則不新寫；同名檔既已存在則不覆蓋。</p>
    </section>

    <section class="card">
      <h2>來源要點（原文摘錄）</h2>
      <p class="meta">以下只轉載來源文件既有段落，不另加數字或結論。完整內容以快照頁為準。</p>
      {"".join(excerpts) if excerpts else "<p>尚未取得可摘錄的摘要檔。</p>"}
    </section>

    <section class="card">
      <h2>累積紀錄（最新在上）</h2>
      <div class="scroll">
      <table>
        <thead><tr><th>時間（台北時間）</th><th>來源檔路徑</th><th>sha1</th><th>摘要連結</th></tr></thead>
        <tbody>
          {hist_table}
        </tbody>
      </table>
      </div>
    </section>
    """
    return page_shell("GBDTRLHMM 新制度變形｜結果彙總（探索性、非獨立盲測；非官方驗收）", body, "")


def scan_published() -> list[tuple[Path, int, str]]:
    """Return hits of sensitive patterns in files that will be published."""
    hits: list[tuple[Path, int, str]] = []
    skip_dirs = {".git", "__pycache__"}
    # Only scan published site artifacts, not the build scripts (they contain the pattern list).
    allowed_suffix = {".html", ".md", ".json", ".css"}
    allowed_names = {"robots.txt", "README.md"}
    skip_names = {"build.py", "publish.sh", "SCAN_REPORT.txt", ".gitignore"}
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.name in skip_names:
            continue
        if p.suffix.lower() not in allowed_suffix and p.name not in allowed_names:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if SENSITIVE_RE.search(line):
                hits.append((p, i, line.strip()[:200]))
    return hits


def main() -> None:
    ENTRIES.mkdir(parents=True, exist_ok=True)
    when = now_taipei()
    existing_paths, missing = collect_sources()
    existing: list[tuple[Path, str]] = [(p, sha1_file(p)) for p in existing_paths]
    history = load_history()
    known_files = {row.get("filename") for row in history}

    added: list[dict] = []
    skipped_existed: list[str] = []
    ts = stamp(when)
    human = stamp_human(when)

    for path, sha in existing:
        slug = slug_for(path)
        # entries/<YYYYMMDD_HHMM>_<名稱>.md — keep original suffix inside 名稱, add .md only if needed
        if slug.endswith(".md"):
            name = f"{ts}_{slug}"
        else:
            name = f"{ts}_{slug}.md"
        rel = f"entries/{name}"
        dest = ENTRIES / name
        html_name = name[:-3] + ".html" if name.endswith(".md") else name + ".html"
        html_rel = f"entries/{html_name}"
        dest_html = ENTRIES / html_name
        if dest.exists() or rel in known_files:
            skipped_existed.append(rel)
            continue
        prior = [r for r in history if r.get("source_path") == str(path)]
        if prior and prior[-1].get("sha1") == sha:
            # content unchanged since last snapshot — do not add a duplicate
            skipped_existed.append(f"{rel}（內容 sha1 與上一筆相同，未附加）")
            continue
        md = snapshot_markdown(path, sha, when)
        dest.write_text(md, encoding="utf-8")
        title = path.name
        write_entry_html(dest, dest_html, title)
        rec = {
            "time_taipei": human,
            "source_path": str(path),
            "sha1": sha,
            "filename": rel,
            "html": html_rel,
            "bytes": dest.stat().st_size,
        }
        history.append(rec)
        added.append(rec)

    if added:
        save_history(history)
    from assemble import assemble_site
    info = assemble_site(when, existing, missing, history, added, skipped_existed, ts, human)
    print("INDEX_CHANGED", info.get("index_changed"))
    print("LOG_FOUND", info.get("log_found"), "sha1", info.get("log_sha"))
    print("PROGRESS_SHA", info.get("progress_sha"))
    print("CHART_ORIGINS", info.get("origins"))
    print("ASSET_MISMATCHES", len(info.get("mismatches") or []))
    for m in info.get("mismatches") or []:
        print("ASSET_MISMATCH", m)

    hits = scan_published()
    report = ROOT / "SCAN_REPORT.txt"
    if hits:
        # Remove offending files' content lines? Task: 發現就移除並回報.
        # We must not publish secrets. For generated site files, strip matching lines
        # and rewrite, except we should not silently corrupt research facts if the
        # match is a false positive — write the report and fail closed by
        # replacing the matching line with a redaction marker.
        lines_out = [f"掃描時間：{human}", f"命中 {len(hits)} 處，已在發布檔以 [REDACTED] 取代該行。", ""]
        touched: dict[Path, set[int]] = {}
        for p, ln, preview in hits:
            touched.setdefault(p, set()).add(ln)
            lines_out.append(f"{p}:{ln}: {preview}")
        for p, line_nos in touched.items():
            raw = p.read_text(encoding="utf-8", errors="replace").splitlines()
            new = []
            for i, line in enumerate(raw, 1):
                if i in line_nos:
                    new.append("[REDACTED]")
                else:
                    new.append(line)
            p.write_text("\n".join(new) + "\n", encoding="utf-8")
        report.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
        print("SENSITIVE_HITS", len(hits))
        print("\n".join(lines_out))
    else:
        report.write_text(f"掃描時間：{human}\n無命中敏感字樣（憑證、私鑰、通行碼等）。\n", encoding="utf-8")
        print("SCAN_CLEAN")

    print(f"ADDED {len(added)}")
    print(f"SKIPPED {len(skipped_existed)}")
    print(f"EXISTING_SOURCES {len(existing)}")
    print(f"MISSING {len(missing)}")
    for p in missing:
        print(f"MISSING_PATH {p}")
    for path, sha in existing:
        print(f"SOURCE {path} {sha}")


if __name__ == "__main__":
    main()
