#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble the experiment-log index: records, status history, charts, web_assets."""
from __future__ import annotations

import ast
import csv
import hashlib
import html
import json
import re
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import visuals
from visuals import (
    DISCLAIMER,
    color_grid,
    esc,
    fmt_num,
    page_shell,
    record_card,
    render_index,
    stat_pill,
    svg_bars_cmp,
    svg_flow,
    svg_funnel,
    svg_gantt_stages,
    svg_threshold_bars,
)

TZ = ZoneInfo("Asia/Taipei")
ROOT = Path(__file__).resolve().parent
SRC = Path("/workspace/ml_meta")
WEB_ASSETS = SRC / "web_assets"
STATUS_DIR = ROOT / "status"
STATUS_HIST = ROOT / "status_history.json"
ASSETS_DIR = ROOT / "assets" / "imported"
ASSETS_MANIFEST = ROOT / "assets_manifest.json"
PLACEHOLDER_DIR = ROOT / "assets" / "placeholder"
ASSET_CHECK = ROOT / "ASSET_CHECK.txt"

VERIFIED_URLS = [
    "https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf",
    "https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf",
    "https://www.econometricsociety.org/publications/econometrica/1989/03/01/new-approach-economic-analysis-nonstationary-time-series-and",
    "https://export.arxiv.org/abs/1707.06347",
]


def sha1_file(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def normalized_sha1(data: bytes) -> str:
    """Ignore matplotlib / ISO timestamps so redraws of the same figure are treated as unchanged."""
    text = data.decode("utf-8", "replace")
    text = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d.+-]*", "", text)
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?: \+0800)?", "", text)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def load_json(path: Path, default):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def src_sha(path: Path) -> str | None:
    return sha1_file(path) if path.is_file() else None


def footnote_sources(*paths: Path) -> list[dict]:
    out = []
    for p in paths:
        if p.is_file():
            out.append({"path": str(p), "sha1": sha1_file(p)})
    return out


def linkify(text: str) -> str:
    escaped = esc(text)
    for u in VERIFIED_URLS:
        escaped = escaped.replace(esc(u), f'<a href="{esc(u)}" rel="nofollow noopener noreferrer">{esc(u)}</a>')
    return escaped


# ---------- parse sources ----------

def read_progress() -> tuple[dict | None, str | None]:
    p = SRC / "v14" / "progress.json"
    if not p.is_file():
        return None, None
    try:
        return json.loads(p.read_text(encoding="utf-8")), sha1_file(p)
    except json.JSONDecodeError:
        return None, sha1_file(p)


def official_counts() -> dict:
    p = SRC / "official_v1" / "SUMMARY.csv"
    out = {"path": p, "rows": None, "conclusions": {}, "tiers": {}, "tenyear_ge_300": None, "second_ge_5": None, "cells": []}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out["rows"] = len(rows)
    out["conclusions"] = dict(Counter(r.get("official_conclusion") or "" for r in rows))
    out["tiers"] = dict(Counter(r.get("research_tier") or "" for r in rows))
    out["tenyear_ge_300"] = sum(1 for r in rows if r.get("tenyear_ge_300") == "True")
    out["second_ge_5"] = sum(1 for r in rows if r.get("second_ge_5") == "True")
    out["cells"] = rows
    return out


def r2_cell_counts() -> dict:
    p = SRC / "round2_run" / "screen" / "cell_summary.csv"
    out = {"path": p, "n_cells": None, "n_trials": None, "n_eligible": None, "n_frozen": None, "n_rank1": None, "n_zero": None}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out["n_cells"] = len(rows)
    out["n_trials"] = sum(int(r["n_trials"]) for r in rows)
    out["n_eligible"] = sum(int(r["n_eligible"]) for r in rows)
    out["n_frozen"] = sum(int(r["n_frozen"]) for r in rows)
    out["n_rank1"] = sum(1 for r in rows if r.get("rank1_trial_id"))
    out["n_zero"] = sum(1 for r in rows if int(r["n_eligible"]) == 0)
    return out


def r2_stageA_v2_counts() -> dict:
    p = SRC / "round2_run" / "stageA_v2" / "summary.csv"
    out = {"path": p, "tiers": {}, "stopped": None, "ge300": None, "ge5": None, "both": None, "evaled": None, "skip": None}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tiers = []
    skip = 0
    stopped = 0
    ge300 = ge5 = both = 0
    for r in rows:
        if r.get("skip") in ("True", "true", "1"):
            skip += 1
            continue
        g = r.get("research_grade") or ""
        try:
            d = ast.literal_eval(g)
        except Exception:
            d = {}
        if isinstance(d, dict):
            tiers.append(d.get("research_tier"))
            if d.get("judgment_stopped"):
                stopped += 1
        try:
            t = float(r.get("tenyear_n") or 0)
            s = float(r.get("second_n") or 0)
        except ValueError:
            continue
        if t >= 300:
            ge300 += 1
        if s >= 5:
            ge5 += 1
        if t >= 300 and s >= 5:
            both += 1
    out.update(tiers=dict(Counter(tiers)), stopped=stopped, ge300=ge300, ge5=ge5, both=both, evaled=len(tiers), skip=skip)
    return out


def r1_stageA_counts() -> dict:
    p = SRC / "round1_run" / "stageA" / "summary.csv"
    out = {"path": p, "n": None, "skip": None, "tiers": {}}
    if not p.is_file():
        return out
    with p.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out["n"] = len(rows)
    skip = 0
    tiers = []
    for r in rows:
        if r.get("skip") in ("True", "true", "1"):
            skip += 1
            continue
        g = r.get("research_grade") or ""
        try:
            d = ast.literal_eval(g)
            tiers.append(d.get("research_tier") if isinstance(d, dict) else None)
        except Exception:
            tiers.append(None)
    out["skip"] = skip
    out["tiers"] = dict(Counter(tiers))
    return out


# ---------- experiment log ----------

FIELD_MAP = [
    ("時間", "time"),
    ("目的", "purpose"),
    ("白話說明", "one_liner"),
    ("方案規模", "scale"),
    ("使用的方法與文獻出處", "method"),
    ("方法與出處", "method"),
    ("預估耗時", "timing"),
    ("預估與實際耗時", "timing"),
    ("過程中遇到的問題與替代嘗試", "issues"),
    ("過程", "issues"),
    ("問題與替代嘗試", "issues"),
    ("成功或失敗", "outcome"),
    ("成敗", "outcome"),
    ("改善思路", "next"),
    ("摘要", "summary"),
    ("結果標記", "label"),
]


def parse_experiment_log(text: str) -> list[dict]:
    recs = []
    parts = re.split(r"(?m)^## ", text)
    for part in parts[1:]:
        lines = part.strip().splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        m = re.match(r"^(E\d+)\s*(.*)$", header)
        rid = m.group(1) if m else header.split()[0]
        title = (m.group(2) if m else header).strip()
        rec = {"id": rid, "title": title, "raw": "\n".join(lines)}
        # parse "關鍵字：" lines; multiline until next key or end
        body = "\n".join(lines[1:])
        keys = [k for k, _ in FIELD_MAP]
        # Allow a short parenthetical between the key and the colon.
        pattern = r"(?m)^(" + "|".join(re.escape(k) for k in keys) + r")(?:[（(][^\n]{0,80}[）)])?[：:]"
        spans = list(re.finditer(pattern, body))
        for i, sp in enumerate(spans):
            key = sp.group(1)
            start = sp.end()
            end = spans[i + 1].start() if i + 1 < len(spans) else len(body)
            val = body[start:end].strip()
            dest = dict(FIELD_MAP)[key]
            if dest not in rec or not rec[dest]:
                rec[dest] = val
        recs.append(rec)
    seen = {}
    for rec in recs:
        base = rec["id"]
        n = seen.get(base, 0) + 1
        seen[base] = n
        rec["id_source"] = base
        if n > 1:
            rec["id"] = f"{base}-{n}"
    return recs


def parse_log_file() -> tuple[list[dict], bool, str | None]:
    p = SRC / "v14" / "EXPERIMENT_LOG.md"
    if not p.is_file():
        return [], False, None
    return parse_experiment_log(p.read_text(encoding="utf-8")), True, sha1_file(p)


# ---------- charts / facts ----------

def facts_bundle() -> dict:
    off = official_counts()
    r2c = r2_cell_counts()
    r2a = r2_stageA_v2_counts()
    r1a = r1_stageA_counts()
    prog, prog_sha = read_progress()
    return {
        "official": off,
        "r2c": r2c,
        "r2a": r2a,
        "r1a": r1a,
        "progress": prog,
        "progress_sha": prog_sha,
    }


def placeholder_charts(facts: dict) -> dict[str, str]:
    """Simple in-repo charts, keyed by kind. Used when web_assets has no matching file."""
    off = facts["official"]
    r2c = facts["r2c"]
    r2a = facts["r2a"]
    r1a = facts["r1a"]
    prog = facts["progress"] or {}

    s_plan13 = SRC / "PLAN_v13.md"
    s_r2sum = SRC / "round2_run" / "SUMMARY_v1.md"
    s_off = SRC / "official_v1" / "SUMMARY.csv"
    s_offmd = SRC / "official_v1" / "SUMMARY.md"
    s_diag = SRC / "reports" / "DIAG_TRADECOUNT_v1.md"
    s_r2cell = SRC / "round2_run" / "screen" / "cell_summary.csv"
    s_r2a = SRC / "round2_run" / "stageA_v2" / "summary.csv"
    s_r1a = SRC / "round1_run" / "stageA" / "summary.csv"
    s_prog = SRC / "v14" / "progress.json"
    s_r2prog = SRC / "round2_run" / "progress.json"
    s_r1prog = SRC / "round1_run" / "progress.json"

    conc = off.get("conclusions") or {}
    charts = {}

    charts["funnel_r1"] = svg_funnel(
        "第一輪漏斗（候選 → 前七年篩選 → 凍結 → 後三年評估）",
        [
            {"label": "候選試驗", "value": 4410},
            {"label": "前七年篩選", "value": 4410},
            {"label": "凍結", "value": None},  # 摘要未寫總凍結筆數
            {"label": "後三年評估（rank-1）", "value": 60},
        ],
        footnote_sources(s_plan13, s_r1a, s_offmd),
    )
    charts["funnel_r2"] = svg_funnel(
        "第二輪漏斗（候選 → 前七年篩選 → 凍結 → 後三年指標）",
        [
            {"label": "候選試驗", "value": r2c.get("n_trials")},
            {"label": "前七年已跑完", "value": r2c.get("n_trials")},
            {"label": "凍結", "value": r2c.get("n_frozen")},
            {"label": "後三年指標", "value": None},  # SUMMARY：未計算、未輸出
        ],
        footnote_sources(s_r2sum, s_r2cell),
    )
    charts["flow"] = svg_flow(
        "研究流程（規則，不是新結論）",
        [
            {"label": "前七年選參", "sub": "三折擴張窗口"},
            {"label": "每格凍結前 100", "sub": "只看前七年"},
            {"label": "每格 rank-1", "sub": "只評一次"},
            {"label": "後三年／官方", "sub": "探索性"},
        ],
        footnote_sources(s_plan13, s_r2sum),
    )

    # official 60 + A3/A3B 30 missing for a 90-cell picture
    modes = ["A1", "A1B", "A2", "A2B", "A3", "A3B"]
    feats = ["F1", "F2", "F3", "F4", "F5"]
    fams_r1 = ["gbdt", "logistic", "rule_table"]
    by = {r["cell"]: r for r in off.get("cells") or []}
    grid_cells = []
    for mo in modes:
        for ft in feats:
            for fa in fams_r1:
                name = f"{mo}|{ft}|{fa}"
                short = f"{mo}-{ft[1:]}-{fa[:2]}"
                row = by.get(name)
                if row:
                    grid_cells.append({
                        "name": name,
                        "short": short,
                        "official": row.get("official_conclusion"),
                        "research": row.get("research_tier"),
                    })
                else:
                    grid_cells.append({"name": name, "short": short, "missing": True})
    charts["official_grid"] = color_grid(
        "官方路徑結論色塊（60 格有 rank-1；A3／A3B 30 格無合格 rank-1）",
        grid_cells,
        "official",
        {"PASS": "#2f6f4e", "FAIL": "#b42318", "紅線 4 停止判定／ValueError": "#b54708"},
        footnote_sources(s_off, s_offmd),
    )
    charts["research_grid"] = color_grid(
        "第一輪研究分級色塊（研究 A／B／Fail，不是官方處分）",
        grid_cells,
        "research",
        {"A": "#1d4e89", "B": "#155e75", "Fail": "#9f1239"},
        footnote_sources(s_off, s_r1a),
    )
    charts["time_r2"] = svg_bars_cmp(
        "第二輪快篩耗時：預估 vs 實際",
        [
            {
                "label": "第二輪快篩",
                "estimate": 0.17 * 3600,
                "actual": 83.6,
                "estimate_label": "0.17 小時",
                "actual_label": "83.6 秒",
            }
        ],
        footnote_sources(s_r2sum),
    )
    charts["diag_trades"] = svg_threshold_bars(
        "底層 PCR 模式十年完成交易 vs 門檻 300",
        [
            {"label": "A1／A1B", "value": 175},
            {"label": "A2／A2B", "value": 189},
            {"label": "A3／A3B", "value": 16},
            {"label": "PCR_ONLY 對照", "value": 191},
        ],
        300,
        "門檻 300",
        footnote_sources(s_diag),
    )
    stages = (prog or {}).get("stages") or []
    charts["gantt"] = svg_gantt_stages(
        "v14 進度（讀 progress.json 的 stages；缺時間不編）",
        stages,
        footnote_sources(s_prog),
    )
    return charts


def write_placeholders(charts: dict[str, str]) -> None:
    PLACEHOLDER_DIR.mkdir(parents=True, exist_ok=True)
    # Only write if content changed, and never overwrite a different existing file in place
    # under a new name — these are "current placeholder" working copies, but we also
    # archive a timestamped copy when content sha1 changes.
    archive = ROOT / "assets" / "placeholder_history"
    archive.mkdir(parents=True, exist_ok=True)
    for kind, html_frag in charts.items():
        cur = PLACEHOLDER_DIR / f"{kind}.html"
        data = html_frag.encode("utf-8")
        digest = hashlib.sha1(data).hexdigest()
        if cur.is_file() and sha1_file(cur) == digest:
            continue
        if cur.is_file():
            old_sha = sha1_file(cur)
            # move aside, do not delete
            aside = archive / f"{cur.stem}_{old_sha[:8]}.html"
            if not aside.exists():
                shutil.copy2(cur, aside)
            # replace current working copy only after archiving
        cur.write_bytes(data)


# ---------- web_assets ----------

def import_web_assets(stamp: str) -> dict:
    report = {
        "dir_exists": WEB_ASSETS.is_dir(),
        "copied": [],
        "reused": [],
        "skipped_nonvisual": [],
        "latest_by_kind": {},
        "all_imported": [],
        "mismatches": [],
    }
    manifest = load_json(ASSETS_MANIFEST, [])
    sha_to_rec = {m["sha1"]: m for m in manifest}
    if not WEB_ASSETS.is_dir():
        save_json(ASSETS_MANIFEST, manifest)
        return report
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for p in sorted(WEB_ASSETS.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".svg", ".html", ".css"}:
            report["skipped_nonvisual"].append(str(p))
            continue
        data = p.read_bytes()
        sha = hashlib.sha1(data).hexdigest()
        nsha = normalized_sha1(data)
        if sha in sha_to_rec:
            report["reused"].append({"src": str(p), "sha1": sha, "dest": sha_to_rec[sha].get("dest")})
            continue
        same_norm = next((m for m in manifest if m.get("name")==p.name and m.get("norm_sha1")==nsha), None)
        if same_norm:
            report["reused"].append({"src": str(p), "sha1": sha, "dest": same_norm.get("dest"), "note": "normalized-same"})
            continue
        dest_name = f"{stamp}_{p.name}"
        dest = ASSETS_DIR / dest_name
        if dest.exists():
            dest_name = f"{stamp}_{sha[:8]}_{p.name}"
            dest = ASSETS_DIR / dest_name
        dest.write_bytes(data)
        rec = {
            "time": stamp,
            "src": str(p),
            "dest": f"assets/imported/{dest_name}",
            "sha1": sha,
            "norm_sha1": nsha,
            "name": p.name,
        }
        manifest.append(rec)
        sha_to_rec[sha] = rec
        report["copied"].append(rec)
    save_json(ASSETS_MANIFEST, manifest)
    # latest per original filename
    latest = {}
    for m in manifest:
        key = m.get("name") or m["dest"]
        if key not in latest:
            latest[key] = m  # keep first dest; later redraws with only a timestamp do not retarget the page
    report["all_imported"] = list(latest.values())
    report["latest_by_kind"] = classify_assets(latest.values())
    return report


KIND_KEYS = {
    "funnel_r1": ["funnel_r1", "funnel-r1", "funnel1"],
    "funnel_r2": ["funnel_r2", "funnel-r2", "funnel2"],
    "funnel": ["funnel"],
    "gantt": ["gantt", "progress", "stages"],
    "flow": ["flow", "pipeline"],
    "time_r2": ["timing_bars", "timing", "time", "elapsed", "duration", "耗時"],
    "official_grid": ["official", "pass_fail", "color_official", "outcome_blocks"],
    "research_grid": ["research_grid", "tier", "research"],
    "diag_trades": ["diag", "trade_count", "threshold", "漏斗交易"],
}


def classify_assets(recs) -> dict[str, dict]:
    by = {}
    used = set()
    for kind, keys in KIND_KEYS.items():
        for rec in recs:
            name = (rec.get("name") or rec.get("dest") or "").lower()
            if rec.get("dest") in used:
                continue
            if any(k.lower() in name for k in keys):
                by[kind] = rec
                used.add(rec.get("dest"))
                break
    return by


def extract_text_numbers(text: str) -> list[str]:
    # visible-ish numbers, including 10,440 and 83.6
    return re.findall(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+", text)


def expected_numbers(facts: dict) -> dict[str, set[str]]:
    """Numbers we may legitimately see, keyed loosely. Used to flag unexpected ones is hard;
    instead we check that required numbers appear, and list extras that contradict known facts."""
    off = facts["official"]
    r2c = facts["r2c"]
    prog = facts["progress"] or {}
    req = {
        "official_fail": str((off.get("conclusions") or {}).get("FAIL", "")),
        "official_stop": str((off.get("conclusions") or {}).get("紅線 4 停止判定／ValueError", "")),
        "r2_trials": str(r2c.get("n_trials") or ""),
        "r2_frozen": str(r2c.get("n_frozen") or ""),
        "v14_done": str(prog.get("v14_trials_done", "")),
        "prior": str(prog.get("cumulative_trials_prior", "")),
    }
    return req


def check_asset_numbers(rec: dict, facts: dict) -> list[str]:
    """Compare a few well-known totals if the asset appears to state them."""
    path = ROOT / rec["dest"]
    if not path.is_file():
        return [f"{rec['dest']} 複製後找不到檔"]
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    # Known contradictions: if both a required total and a different nearby total appear
    # we only flag when the chart labels a known metric with a wrong value.
    # Heuristic: look for "PASS" count, "10,440" vs wrong prior, 676,068, 1,620, 4,410, 51, 0.
    checks = [
        (r"(累計[^0-9]{0,8}|prior[^0-9]{0,8}|10[, ]?440)", "10440", "10,440", "累計起點 10,440"),
        (r"(FAIL|失敗)[^\d]{0,12}51\b", "51", "51", "官方 FAIL 51"),
        (r"(1[, ]?620|1620)", "1620", "1,620", "第二輪試驗 1,620"),
        (r"(4[, ]?410|4410)", "4410", "4,410", "第一輪試驗 4,410"),
        (r"(536)", "536", "536", "第二輪凍結 536"),
        (r"(676[, ]?068|676068)", "676068", "676,068", "v14 試驗 676,068"),
    ]
    # Only flag if a label is present but the expected number is absent and another number is in its place.
    # Conservative: if the exact expected number string (with or without comma) is in the file, OK.
    # If a label like 'FAIL' appears with a nearby integer that isn't 51 when official FAIL is 51, flag.
    off_fail = (facts["official"].get("conclusions") or {}).get("FAIL")
    if off_fail is not None:
        for m in re.finditer(r"FAIL[^\d]{0,8}(\d+)", text, re.I):
            if int(m.group(1)) != int(off_fail) and int(m.group(1)) not in (0, 43, 23):
                issues.append(f"{rec['dest']}: 圖中 FAIL 附近寫 {m.group(1)}，來源 official SUMMARY 為 {off_fail}")
        for m in re.finditer(r"PASS[^\d]{0,8}(\d+)", text, re.I):
            if int(m.group(1)) != 0:
                issues.append(f"{rec['dest']}: 圖中 PASS 附近寫 {m.group(1)}，來源 official SUMMARY 為 0")
    name = (rec.get("name") or rec.get("dest") or "").lower()
    if any(k in name for k in ("timing", "time_bar", "elapsed", "gantt")):
        r2_trials = None  # duration charts are not trial-count charts
    else:
        r2_trials = facts["r2c"].get("n_trials")
    if r2_trials:
        for m in re.finditer(r"(第二輪試驗|第二輪候選|round\s*2 trials)[^\d]{0,16}(\d[\d,]*)", text, re.I):
            got = int(m.group(2).replace(",", ""))
            if got not in (int(r2_trials), 540, 1080, 536, 40, 60, 20, 66, 2, 15, 23, 10440, 8820) and got > 20:
                issues.append(f"{rec['dest']}: 圖中「{m.group(1)}」附近寫 {m.group(2)}，來源 cell_summary 試驗合計為 {r2_trials}")
    return issues


def pick_chart(kind: str, placeholders: dict[str, str], imported: dict[str, dict], facts: dict, mismatches: list[str]) -> tuple[str, str]:
    """Return (html, origin) where origin is 'web_assets' or 'placeholder'."""
    rec = imported.get(kind)
    # also allow generic 'funnel' for both if specific missing
    if rec is None and kind.startswith("funnel"):
        rec = imported.get("funnel")
    if rec:
        path = ROOT / rec["dest"]
        if path.is_file():
            mismatches.extend(check_asset_numbers(rec, facts))
            # Prefer the sibling .svg and reference it by path (do not inline huge matplotlib docs).
            svg = path.with_suffix(".svg") if path.suffix.lower() != ".svg" else path
            if not svg.is_file() and path.suffix.lower() == ".svg":
                svg = path
            # If dest is html, a same-stem svg may live next to it.
            if path.suffix.lower() != ".svg":
                cand = path.with_suffix(".svg")
                if cand.is_file():
                    svg = cand
            if svg.is_file():
                rel = svg.relative_to(ROOT).as_posix()
                sha = sha1_file(svg)
                inner = (
                    f'<img class="asset-img" src="{esc(rel)}" '
                    f'alt="{esc(kind)}" />'
                )
                cap = (
                    f'<p class="fn">美編圖 · {esc(Path(rec.get("src") or "").name or "未取得")}'
                    f' · {esc(Path(rel).name)} · {esc(sha[:8])}</p>'
                )
                return f'<figure class="fig imported">{inner}{cap}</figure>', "web_assets"
            content = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"<html", content, re.I):
                # last resort: iframe the imported html, do not paste the whole document
                rel = path.relative_to(ROOT).as_posix()
                inner = f'<iframe class="asset-frame" src="{esc(rel)}" title="{esc(kind)}"></iframe>'
            else:
                inner = content
            cap = (
                f'<p class="fn">美編圖 · {esc(Path(rec.get("src") or "").name or "未取得")}'
                f' · {esc((rec.get("sha1") or "")[:8] or "未取得")}</p>'
            )
            return f'<figure class="fig imported">{inner}{cap}</figure>', "web_assets"
    return placeholders[kind], "placeholder"


# ---------- status history ----------

def status_payload(prog: dict | None, sha: str | None) -> dict:
    if not prog:
        return {"sha1": sha, "missing": True, "label": "未取得 v14/progress.json"}
    keys = [
        "updated_at_taipei", "stage", "stage_detail", "done", "total",
        "elapsed_sec", "eta_sec", "eta_days", "v14_trials_done",
        "cumulative_trials_prior", "cumulative_trials_now", "results_label",
        "note", "n_workers", "failures", "alternatives", "best_exploratory",
        "experiment_log_latest_id", "experiment_log_sha1",
    ]
    body = {k: prog[k] for k in keys if k in prog}
    body["stages"] = prog.get("stages")
    body["sha1"] = sha
    return body


def render_status_block(payload: dict, heading: str) -> str:
    if payload.get("missing"):
        return f"<p>{esc(heading)}：未取得。</p>"
    pills = [
        stat_pill("階段", payload.get("stage"), ""),
        stat_pill("已完成", payload.get("done"), ""),
        stat_pill("總數", payload.get("total") if payload.get("total") is not None else "未取得", ""),
        stat_pill("v14 已做試驗", payload.get("v14_trials_done"), ""),
        stat_pill("累計目前", payload.get("cumulative_trials_now"), ""),
    ]
    rows = []
    for k, lab in [
        ("updated_at_taipei", "更新時間（來源欄位）"),
        ("stage_detail", "階段說明"),
        ("elapsed_sec", "已用時（秒）"),
        ("eta_sec", "預估剩餘（秒）"),
        ("eta_days", "預估剩餘（天）"),
        ("note", "備註"),
        ("results_label", "結果標記"),
        ("experiment_log_latest_id", "最新實驗編號"),
    ]:
        if k in payload:
            val = payload[k]
            rows.append(f"<tr><th>{esc(lab)}</th><td><code>{esc(json.dumps(val, ensure_ascii=False))}</code></td></tr>")
        else:
            rows.append(f"<tr><th>{esc(lab)}</th><td>未取得</td></tr>")
    return f"<p class='meta'>{esc(heading)}</p><div class='stats'>{''.join(pills)}</div><div class='scroll'><table class='kv'>{''.join(rows)}</table></div>"


def update_status_history(prog: dict | None, sha: str | None, stamp: str, human: str) -> list[dict]:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    hist = load_json(STATUS_HIST, [])
    # Seed the superseded 22:41 snapshot once, from the already-archived entry (do not invent).
    if not hist:
        seed = ROOT / "entries" / "20261111_2248_v14_progress.json.md"
        if seed.is_file():
            raw = seed.read_text(encoding="utf-8")
            m = re.search(r"```json\n(.*?)\n```", raw, re.S)
            if m:
                try:
                    old = json.loads(m.group(1))
                    old_sha = "70b7da31122a06f8c7423030bc2c88ac948fecfc"
                    old_name = "20261111_2241_progress.json"
                    dest = STATUS_DIR / old_name
                    if not dest.exists():
                        dest.write_text(json.dumps(old, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    hist.append({
                        "time_taipei": "2026-11-11 22:41:12 +0800（來源 updated_at_taipei）",
                        "sha1": old_sha,
                        "file": f"status/{old_name}",
                        "stage": old.get("stage"),
                    })
                except json.JSONDecodeError:
                    pass
    if sha and hist and hist[-1].get("sha1") == sha:
        save_json(STATUS_HIST, hist)
        return hist
    if not sha:
        save_json(STATUS_HIST, hist)
        return hist
    fname = f"{stamp}_progress.json"
    dest = STATUS_DIR / fname
    if dest.exists():
        fname = f"{stamp}_{sha[:8]}_progress.json"
        dest = STATUS_DIR / fname
    dest.write_text(json.dumps(prog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hist.append({
        "time_taipei": (prog or {}).get("updated_at_taipei") or human,
        "sha1": sha,
        "file": f"status/{fname}",
        "stage": (prog or {}).get("stage"),
    })
    save_json(STATUS_HIST, hist)
    return hist



def render_status_section(hist: list[dict], prog: dict | None, sha: str | None) -> str:
    if not prog:
        body = "<p>目前狀態：未取得 progress.json。</p>"
    else:
        stage = prog.get("stage") or "未取得"
        detail = (prog.get("stage_detail") or "").strip()
        st = next((s for s in (prog.get("stages") or []) if s.get("name") == stage), None)
        raw_status = (st or {}).get("status") or ""
        status_zh = {
            "not_started": "未開始",
            "running": "進行中",
            "done": "完成",
            "failed": "失敗",
        }.get(raw_status, raw_status)
        when = prog.get("updated_at_taipei") or "未取得"
        v14d = prog.get("v14_trials_done")
        nowc = prog.get("cumulative_trials_now")
        line1 = f"目前階段「{esc(stage)}」"
        if status_zh:
            line1 += f"（{esc(status_zh)}）"
        line1 += "。"
        if detail:
            line1 += esc(detail if detail.endswith("。") else detail + "。")
        line2 = (
            f"v14 已做試驗 {esc(fmt_num(v14d) if v14d is not None else '未取得')}，"
            f"累計目前 {esc(fmt_num(nowc) if nowc is not None else '未取得')}。"
            f"來源更新於 {esc(when)}。"
        )
        body = f"<p class='status-lead'>{line1}{line2}</p>"
    old = hist[:-1] if hist else []
    details = []
    for rec in reversed(old):
        short = (rec.get("sha1") or "")[:8] or "未取得"
        details.append(
            f"<li>{esc(rec.get('time_taipei',''))}　{esc(rec.get('stage') or '未取得')}　{esc(short)}</li>"
        )
    old_wrap = ""
    if details:
        old_wrap = (
            "<details class='old-status-pack'><summary>先前狀態（保留，不刪）</summary>"
            f"<ul class='old-status-list'>{''.join(details)}</ul></details>"
        )
    fn = visuals.footnote(footnote_sources(SRC / "v14" / "progress.json"))
    return f"<section class='card' id='status'><h2>目前狀態</h2>{body}{fn}{old_wrap}</section>"


def hist_records(facts: dict) -> list[dict]:
    off = facts["official"]
    r2c = facts["r2c"]
    r2a = facts["r2a"]
    r1a = facts["r1a"]
    conc = off.get("conclusions") or {}
    tiers = off.get("tiers") or {}
    r1t = r1a.get("tiers") or {}
    r1prog = SRC / "round1_run" / "progress.json"
    r2prog = SRC / "round2_run" / "progress.json"
    r1p = json.loads(r1prog.read_text()) if r1prog.is_file() else {}
    r2p = json.loads(r2prog.read_text()) if r2prog.is_file() else {}

    rec_r1 = {
        "id": "HIST-R1",
        "title": "第一輪（規則表／邏輯迴歸／GBDT）與官方路徑",
        "one_liner": "90 格裡 60 格有 rank-1；官方路徑合格數 0。探索性、非獨立盲測；非官方驗收。",
        "time": (
            f"tick 帳本階段 {r1p.get('started_at_taipei','未取得')}～{r1p.get('finished_at_taipei','未取得')}。"
            "快篩起訖未取得。"
        ),
        "purpose": "在前七年為規則表／邏輯迴歸／GBDT 選參並凍結，每格只把第一名拿去評後三年。",
        "scale": "90 格、試驗 4,410（另有被取代的 v1 4,410）。30 個模式×特徵組合，每組規則表 9、邏輯迴歸 30、GBDT 108。",
        "method": "前七年三折擴張窗口排序，每格取前 100 名凍結。文獻出處待補。",
        "timing": (
            f"快篩預估與實際：未取得。"
            f"tick 帳本階段 elapsed_sec＝{r1p.get('elapsed_sec','未取得')}（來源 round1_run/progress.json）。"
        ),
        "issues": (
            "A3／A3B 共 30 格無合格 rank-1。"
            "官方路徑另存 official_v1，不覆蓋 e2e_tick_v3；後三年數字沿用同一份 rank-1 帳本，不重跑 MC95。"
            "PLAN_v13 載明 ledger_reproduced 為腳本自填，與「兩個獨立程序產出位元組級相同 CSV」不符。"
        ),
        "outcome": (
            f"研究分級（官方 SUMMARY／stageA）：A {tiers.get('A', r1t.get('A','未取得'))}／"
            f"B {tiers.get('B', r1t.get('B','未取得'))}／"
            f"Fail {tiers.get('Fail', r1t.get('Fail','未取得'))}／"
            f"停止判定（研究分級空或無）{tiers.get('', r1t.get(None, '未取得'))}。"
            f"官方路徑：PASS {conc.get('PASS', 0)}／FAIL {conc.get('FAIL','未取得')}／"
            f"紅線 4 停止判定／ValueError {conc.get('紅線 4 停止判定／ValueError','未取得')}。"
            f"十年≥300：{off.get('tenyear_ge_300')} 格；二考≥5：{off.get('second_ge_5')} 格。官方合格數 0。"
        ),
        "next": "PLAN_v13 載明後繼官方 evidence 必須另存新檔，ledger_reproduced 須符合雙程序重現。診斷見 HIST-DIAG。",
    }
    rec_r2 = {
        "id": "HIST-R2",
        "title": "第二輪（HMM／RL）",
        "one_liner": "1,620 筆試驗跑完；有 rank-1 的 40 格裡研究 A 2、合格數 0。探索性、非獨立盲測；非官方驗收。",
        "time": (
            f"tick v2：{r2p.get('tick_started_at_taipei','未取得')}～{r2p.get('finished_at_taipei','未取得')}。"
            "快篩耗時見 SUMMARY（83.6 秒），快篩起訖鐘點未取得。"
        ),
        "purpose": "在同一 30 個組合上試 HMM／RL。",
        "scale": f"試驗合計 {r2c.get('n_trials')}（SUMMARY 寫 HMM 540＋RL 1,080），格數 {r2c.get('n_cells')}。",
        "method": "規則凍結於 freeze/screen_rules_v3.json（SUMMARY：寫於看結果前）。hmmlearn 0.3.3。文獻出處待補。",
        "timing": (
            "快篩預估：外推單程序約 0.17 小時；實際 83.6 秒（round2_run/SUMMARY_v1.md）。"
            f"tick 預估：未取得。progress.json elapsed_sec＝{r2p.get('elapsed_sec','未取得')}。"
        ),
        "issues": (
            "tick v1 因 0 筆帳本 CSV 無欄名在階段 B 失敗，改 v2 新目錄重跑，v1 產物保留。"
            "重跑 test_lookahead_v3.py 時就地覆蓋 reports/test_lookahead_v3_normal.json。"
            "階段 B 未計算、未輸出後三年指標。"
        ),
        "outcome": (
            f"有 rank-1 的格 {r2c.get('n_rank1')}；凍結 {r2c.get('n_frozen')}。"
            f"stageA_v2 研究分級：A { (r2a.get('tiers') or {}).get('A','未取得') }／"
            f"B {(r2a.get('tiers') or {}).get('B', 0)}／"
            f"Fail {(r2a.get('tiers') or {}).get('Fail','未取得')}／"
            f"紅線 4 停止判定／ValueError {r2a.get('stopped','未取得')}。"
            f"十年≥300 且二考≥5：{r2a.get('both')} 格（SUMMARY 寫這 2 格皆研究 Fail）。合格數 0。"
        ),
        "next": "所列來源檔未載明下一輪方案本文（見後續 E001 若存在）。",
    }
    rec_d = {
        "id": "HIST-DIAG",
        "title": "交易筆數流失診斷",
        "one_liner": "六種底層 PCR 模式十年完成交易皆不足 300，二考皆為 0；這是第一限制，不是特徵集。",
        "time": "2026-11-11 22:31（台北時間）撰寫。只讀既有輸出，未重跑試驗。",
        "purpose": "查「十年≥300、二考≥5」為何幾乎沒有格子達到。",
        "scale": "六種 PCR 模式底層 1 分 K 全接受帳本，加上第一輪 60 格與第二輪有 rank-1 的格子。",
        "method": "對既有帳本按 freeze/windows_v2.json 切窗計數；對照模型十年交易與接受率。文獻出處待補。",
        "timing": "預估與實際耗時：未取得（本檔未重跑試驗）。",
        "issues": (
            "各模式×延遲的 tick 全接受十年帳本未找到，其餘五模式只能引用 1 分 K 帳本。"
            "F4／F5 延遲全接受的獨立交易帳本亦缺。"
        ),
        "outcome": (
            "六種底層模式十年完成交易皆不足 300：A1／A1B＝175、A2／A2B＝189、A3／A3B＝16；PCR_ONLY 對照＝191；二考皆為 0。"
            "第一輪 60 格十年交易最多 275，0 格 ≥300。只有第二輪兩格達到十年≥300 且二考≥5，研究分級皆 Fail。"
        ),
        "next": (
            "診斷本身的改善緣由：底層模式單獨無法滿足十年≥300 與二考≥5，後續若要達標須面對這個上限。"
            "方案本文以 EXPERIMENT_LOG.md 已寫下的條目為準；本診斷檔未載明新格點設計。"
        ),
    }
    return [rec_r1, rec_r2, rec_d]


def records_to_cards(log_recs: list[dict], hist: list[dict], charts_for: dict) -> list[dict]:
    cards = []
    # collect log + historical; display order is set by sort_cards_newest_first
    for rec in log_recs:
        method = rec.get("method") or "出處待補"
        rec = dict(rec)
        rec["method"] = {"html": linkify(method)}
        if not rec.get("one_liner"):
            rec["one_liner"] = rec.get("purpose") or ""
        if not rec.get("next"):
            rec["next"] = "未取得"
        if not rec.get("timing"):
            rec["timing"] = "未取得"
        if rec.get("summary") and rec.get("id"):
            rec["outcome"] = rec.get("outcome") or rec.get("summary")
        rec["footnote_html"] = visuals.footnote(
            footnote_sources(SRC / "v14" / "EXPERIMENT_LOG.md")
        )
        cards.append(rec)
    hist_fn = {
        "HIST-R1": [
            SRC / "official_v1" / "SUMMARY.md",
            SRC / "official_v1" / "SUMMARY.csv",
            SRC / "PLAN_v13.md",
            SRC / "round1_run" / "stageA" / "summary.csv",
            SRC / "round1_run" / "progress.json",
        ],
        "HIST-R2": [
            SRC / "round2_run" / "SUMMARY_v1.md",
            SRC / "round2_run" / "screen" / "cell_summary.csv",
            SRC / "round2_run" / "stageA_v2" / "summary.csv",
            SRC / "round2_run" / "progress.json",
        ],
        "HIST-DIAG": [SRC / "reports" / "DIAG_TRADECOUNT_v1.md"],
    }
    for rec in hist:
        rec = dict(rec)
        rec["footnote_html"] = visuals.footnote(footnote_sources(*hist_fn.get(rec.get("id"), [])))
        cards.append(rec)
    return sort_cards_newest_first(cards)


_TIME_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?")


def card_time(rec: dict) -> datetime | None:
    """Latest timestamp written in the record's 時間 field (Taipei wall clock); None if absent."""
    found = []
    for m in _TIME_RE.finditer(str(rec.get("time") or "")):
        y, mo, d, h, mi, sec = m.groups()
        try:
            found.append(datetime(int(y), int(mo), int(d), int(h), int(mi), int(sec or 0)))
        except ValueError:
            continue
    return max(found) if found else None


def sort_cards_newest_first(cards: list[dict]) -> list[dict]:
    """Display order only: newest on top (Charles 2026-11-12 17:10). Records are not changed.
    An undated record inherits the time of the record listed before it; ties keep later-listed first."""
    keyed = []
    last = datetime.min
    for i, rec in enumerate(cards):
        t = card_time(rec)
        if t is None:
            t = last
        else:
            last = t
        keyed.append((t, i, rec))
    keyed.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [rec for _, _, rec in keyed]


# ---------- index tables ----------


def src_table(existing: list[tuple[Path, str]], missing: list[Path], history: list[dict]) -> str:
    latest = {}
    for row in history:
        src = row.get("source_path")
        if src:
            latest[src] = row
    parts = []
    for path, sha in existing:
        rec = latest.get(str(path))
        link = ""
        if rec and rec.get("html"):
            link = f"<a href='{esc(rec['html'])}'>最新快照</a>"
        parts.append(
            "<tr class='found'>"
            f"<td>{esc(path.name)}</td>"
            f"<td class='path'><code>{esc(path)}</code></td>"
            f"<td class='sha'><code>{esc(sha)}</code></td>"
            f"<td>{link}</td></tr>"
        )
    for miss in missing:
        parts.append(
            "<tr class='missing'>"
            f"<td>{esc(miss.name)}</td>"
            f"<td class='path'><code>{esc(miss)}</code></td>"
            f"<td>未找到</td><td></td></tr>"
        )
    return "\n".join(parts)



def hist_table(history: list[dict]) -> str:
    rows = []
    for row in reversed(history):
        href = esc(row.get("html") or row.get("filename") or "")
        src = row.get("source_path") or ""
        rows.append(
            "<tr>"
            f"<td>{esc(row.get('time_taipei',''))}</td>"
            f"<td>{esc(Path(src).name if src else '未取得')}</td>"
            f"<td class='path'><code>{esc(src)}</code></td>"
            f"<td class='sha'><code>{esc(row.get('sha1',''))}</code></td>"
            f"<td><a href='{href}'>{esc(Path(row.get('filename') or href).name)}</a></td>"
            "</tr>"
        )
    return "\n".join(rows) if rows else "<tr><td colspan='5'>尚無快照</td></tr>"



ARCHIVE = ROOT / "archive"


def rewrite_archived_index(html_text: str) -> str:
    html_text = html_text.replace('href="style.css"', 'href="../style.css"')
    html_text = html_text.replace('src="assets/', 'src="../assets/')
    html_text = html_text.replace('href="assets/', 'href="../assets/')
    html_text = html_text.replace('href="entries/', 'href="../entries/')
    html_text = html_text.replace("href='entries/", "href='../entries/")
    html_text = html_text.replace('href="sources.html"', 'href="../sources.html"')
    return html_text


def archive_current_index(stamp: str, new_html: str) -> Path | None:
    """Copy the live homepage aside before replacing it. Never overwrite an archive file."""
    index_path = ROOT / "index.html"
    if not index_path.is_file():
        return None
    old = index_path.read_text(encoding="utf-8")
    if old == new_html:
        return None
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    dest = ARCHIVE / f"index_{stamp}.html"
    if dest.exists():
        short = hashlib.sha1(old.encode("utf-8")).hexdigest()[:8]
        dest = ARCHIVE / f"index_{stamp}_{short}.html"
        if dest.exists():
            return dest
    dest.write_text(rewrite_archived_index(old), encoding="utf-8")
    return dest


def list_archives() -> list[dict]:
    if not ARCHIVE.is_dir():
        return []
    items = sorted(ARCHIVE.glob("index_*.html"), key=lambda p: p.name, reverse=True)
    return [{"name": p.name, "href": f"archive/{p.name}"} for p in items]


def footer_links(archives: list[dict]) -> str:
    bits = ['<p class="footer-links"><a href="sources.html">完整來源清單</a>']
    if archives:
        bits.append("　舊版首頁：")
        bits.append("　".join(f'<a href="{esc(a["href"])}">{esc(a["name"])}</a>' for a in archives))
    bits.append("</p>")
    return "".join(bits)


# ---------- chart groups (display order v2, Charles 2026-11-12 17:10) ----------
# Order inside one version group, per display_order_v2 handoff: funnel first.
GROUP_KIND_ORDER = ["funnel", "outcome_blocks", "timing_bars", "method_flow", "gantt", "v14_progress_card"]
GROUP_KIND_TITLE = {
    "funnel": "漏斗：候選 → 前七年篩選 → 凍結 top100 → 後三年評估",
    "outcome_blocks": "成敗色塊表（A／B／Fail／ValueError）",
    "timing_bars": "耗時條圖（預估 vs 實際）",
    "method_flow": "方法流程圖",
    "gantt": "整體甘特圖",
    "v14_progress_card": "v14 即時進度卡",
}
_GROUP_NAME_RE = re.compile(
    r"^(latest_)?(" + "|".join(GROUP_KIND_ORDER) + r")(?:_(v1|\d{8}_\d{4}))?\.svg$"
)


def _group_stamp(rec: dict, latest: bool, stamp: str | None) -> tuple[str, str]:
    """(sort stamp, label). Named timestamp wins; latest_* follows its symlink target; else import time."""
    if stamp and stamp != "v1":
        return stamp, stamp
    if latest:
        src = Path(rec.get("src") or "")
        try:
            target = src.resolve().name if src.is_symlink() else ""
        except OSError:
            target = ""
        m = _GROUP_NAME_RE.match(target)
        if m and m.group(3) and m.group(3) != "v1":
            return m.group(3), m.group(3)
    t = rec.get("time") or ""
    return t, f"{t}（v1 匯入）" if stamp == "v1" else t


def chart_groups_newest_first(facts: dict, mismatches: list[str]) -> list[str]:
    """All imported chart version groups, newest group on top; same sha1 shown once (newest kept).
    Display order only: no file under assets/imported is changed or removed."""
    manifest = load_json(ASSETS_MANIFEST, [])
    groups: dict[str, dict] = {}
    for rec in manifest:
        m = _GROUP_NAME_RE.match(rec.get("name") or "")
        if not m:
            continue
        path = ROOT / rec["dest"]
        if not path.is_file():
            continue
        key, label = _group_stamp(rec, bool(m.group(1)), m.group(3))
        g = groups.setdefault(key, {"label": label, "items": []})
        g["items"].append((m.group(2), rec, path))
    out = []
    seen_sha = set()
    for key in sorted(groups, reverse=True):
        g = groups[key]
        g["items"].sort(key=lambda x: GROUP_KIND_ORDER.index(x[0]))
        figs = []
        for kind, rec, path in g["items"]:
            sha = sha1_file(path)
            if sha in seen_sha:
                continue
            seen_sha.add(sha)
            mismatches.extend(check_asset_numbers(rec, facts))
            rel = path.relative_to(ROOT).as_posix()
            title = GROUP_KIND_TITLE[kind]
            figs.append(
                f'<figure class="fig imported"><img class="asset-img" src="{esc(rel)}" alt="{esc(title)}" />'
                f'<p class="one-liner">{esc(title)}</p>'
                f'<p class="fn">美編圖 · {esc(Path(rec.get("src") or "").name or "未取得")}'
                f' · {esc(path.name)} · {esc(sha[:8])}</p></figure>'
            )
        if figs:
            out.append(f'<h3 class="stamp-h">版本 {esc(g["label"])}</h3>' + "".join(figs))
    return out


def assemble_site(when: datetime, existing, missing, history, added, skipped, stamp: str, human: str) -> dict:
    facts = facts_bundle()
    placeholders = placeholder_charts(facts)
    write_placeholders(placeholders)
    assets = import_web_assets(stamp)
    mismatches = list(assets.get("mismatches") or [])
    imported_kinds = assets.get("latest_by_kind") or {}

    origins = {}
    chosen = {}
    for kind in placeholders:
        html_frag, origin = pick_chart(kind, placeholders, imported_kinds, facts, mismatches)
        chosen[kind] = html_frag
        origins[kind] = origin
    assets["mismatches"] = mismatches
    assets["origins"] = origins

    # write asset check (stable if same issues)
    lines = [
        f"web_assets 目錄存在：{assets['dir_exists']}",
        f"新複製：{len(assets['copied'])}；已有相同 sha1 故未再拷：{len(assets['reused'])}",
        "各圖來源：",
    ]
    for k, o in origins.items():
        lines.append(f"  - {k}: {o}")
    if mismatches:
        lines.append("數字不一致（未改圖）：")
        lines.extend(f"  - {m}" for m in mismatches)
    else:
        lines.append("未發現可判定的數字不一致（或本輪僅用占位圖，數字由來源檔繪製）。")
    check_text = "\n".join(lines) + "\n"
    if not ASSET_CHECK.is_file() or ASSET_CHECK.read_text(encoding="utf-8") != check_text:
        ASSET_CHECK.write_text(check_text, encoding="utf-8")

    prog, prog_sha = facts["progress"], facts["progress_sha"]
    status_hist = update_status_history(prog, prog_sha, stamp, human)
    status_html = render_status_section(status_hist, prog, prog_sha)

    log_recs, log_found, log_sha = parse_log_file()
    hist = hist_records(facts)
    cards = records_to_cards(log_recs, hist, {})

    overview = chart_groups_newest_first(facts, mismatches)
    if not overview:
        # no imported chart groups: fall back to the single placeholder set, each image once
        seen_chart = set()
        for kind in ("funnel_r1", "funnel_r2", "official_grid", "time_r2", "gantt"):
            frag = chosen[kind]
            if frag in seen_chart:
                continue
            seen_chart.add(frag)
            overview.append(frag)

    latest_time = history[-1]["time_taipei"] if history else "尚無"
    src_html = src_table(existing, missing, history)
    hist_html = hist_table(history)
    ctx = {
        "v14": prog or {},
        "overview_charts": overview,
        "records": cards,
        "src_table_html": src_html,
        "hist_table_html": hist_html,
        "experiment_log_found": log_found,
        "latest_time": latest_time,
        "status_html": status_html,
    }

    # Write sources.html first (same-dir links). Archive old homepage, then write the new one.
    sources_page = visuals.render_sources_page(ctx)
    sources_path = ROOT / "sources.html"
    sources_changed = (not sources_path.is_file()) or sources_path.read_text(encoding="utf-8") != sources_page
    if sources_changed:
        sources_path.write_text(sources_page, encoding="utf-8")

    index_path = ROOT / "index.html"
    # footer lists archives including the one we are about to add
    ctx["footer_extra"] = footer_links(list_archives())
    index = render_index(ctx)
    archived_path = archive_current_index(stamp, index)
    ctx["footer_extra"] = footer_links(list_archives())
    index = render_index(ctx)
    if not index_path.is_file() or index_path.read_text(encoding="utf-8") != index:
        index_path.write_text(index, encoding="utf-8")
        index_changed = True
    else:
        index_changed = False

    return {
        "index_changed": index_changed,
        "sources_changed": sources_changed,
        "archived": str(archived_path) if archived_path else None,
        "assets": assets,
        "log_found": log_found,
        "log_sha": log_sha,
        "progress_sha": prog_sha,
        "n_log_recs": len(log_recs),
        "origins": origins,
        "mismatches": mismatches,
    }
