#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SVG/HTML visuals and experiment-log index. Numbers must be supplied by the caller from real files."""
from __future__ import annotations

import html
from typing import Any


DISCLAIMER = "探索性、非獨立盲測；非官方驗收"


def esc(s: Any) -> str:
    return html.escape("" if s is None else str(s))


def fmt_num(n: Any) -> str:
    if n is None:
        return "未取得"
    if isinstance(n, bool):
        return str(n)
    if isinstance(n, float):
        if n != n:  # NaN
            return "未取得"
        if n == int(n):
            return f"{int(n):,}"
        return f"{n:,.4g}"
    if isinstance(n, int):
        return f"{n:,}"
    return str(n)


def footnote(sources: list[dict]) -> str:
    if not sources:
        return f'<p class="fn">數字來源未取得。</p>'
    bits = []
    for s in sources:
        path = esc(s.get("path", ""))
        sha = s.get("sha1") or ""
        short = esc(sha[:8] if sha else "未取得")
        bits.append(f"<code>{path}</code> sha1 <code>{short}</code>…")
    return '<p class="fn">數字來源：' + "；".join(bits) + "。文獻出處見各筆紀錄。</p>"


def stat_pill(label: str, value: Any, kind: str = "") -> str:
    klass = f"stat {kind}".strip()
    return f'<div class="{klass}"><span class="stat-val">{esc(fmt_num(value))}</span><span class="stat-lbl">{esc(label)}</span></div>'


def svg_funnel(title: str, stages: list[dict], sources: list[dict], width: int = 880) -> str:
    """stages: {label, value, note?} value may be None → 未取得."""
    n = max(1, len(stages))
    h = 168
    pad = 16
    gap = 10
    box_w = (width - pad * 2 - gap * (n - 1)) / n
    known = [s["value"] for s in stages if isinstance(s.get("value"), (int, float)) and s["value"] is not None]
    vmax = max(known) if known else 1
    parts = [f'<svg class="chart" viewBox="0 0 {width} {h}" role="img" aria-label="{esc(title)}">']
    parts.append(f'<text x="{pad}" y="22" class="svg-title">{esc(title)}</text>')
    for i, st in enumerate(stages):
        x = pad + i * (box_w + gap)
        val = st.get("value")
        y0, bh = 36, 88
        if val is None:
            parts.append(
                f'<rect x="{x:.1f}" y="{y0}" width="{box_w:.1f}" height="{bh}" rx="10" fill="none" stroke="#b0a898" stroke-dasharray="5 4"/>'
            )
            parts.append(
                f'<text x="{x+box_w/2:.1f}" y="{y0+48}" text-anchor="middle" class="svg-missing">未取得</text>'
            )
        else:
            frac = 0.35 + 0.65 * (float(val) / vmax) if vmax else 0.5
            inner_h = bh * frac
            iy = y0 + (bh - inner_h)
            shade = 28 + int(140 * (1 - i / max(1, n - 1)))
            fill = f"rgb({180+shade//5},{70+shade//6},{40})"
            parts.append(
                f'<rect x="{x:.1f}" y="{iy:.1f}" width="{box_w:.1f}" height="{inner_h:.1f}" rx="10" fill="{fill}"/>'
            )
            parts.append(
                f'<text x="{x+box_w/2:.1f}" y="{iy+inner_h/2+6:.1f}" text-anchor="middle" class="svg-num">{esc(fmt_num(val))}</text>'
            )
        parts.append(
            f'<text x="{x+box_w/2:.1f}" y="{h-14}" text-anchor="middle" class="svg-lbl">{esc(st.get("label",""))}</text>'
        )
    parts.append("</svg>")
    return f'<figure class="fig">{"".join(parts)}{footnote(sources)}</figure>'


def svg_bars_cmp(title: str, rows: list[dict], sources: list[dict], width: int = 880) -> str:
    """rows: {label, estimate, actual, estimate_label, actual_label}. values in seconds, or None."""
    row_h = 64
    top = 36
    h = top + row_h * max(1, len(rows)) + 16
    left, right = 200, 20
    inner = width - left - right
    secs = []
    for r in rows:
        for k in ("estimate", "actual"):
            if isinstance(r.get(k), (int, float)):
                secs.append(float(r[k]))
    vmax = max(secs) if secs else 1
    parts = [f'<svg class="chart" viewBox="0 0 {width} {h}" role="img" aria-label="{esc(title)}">']
    parts.append(f'<text x="16" y="22" class="svg-title">{esc(title)}</text>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        parts.append(f'<text x="16" y="{y+28}" class="svg-lbl">{esc(r.get("label",""))}</text>')
        # estimate
        ev, av = r.get("estimate"), r.get("actual")
        elab = r.get("estimate_label") or ("未取得" if ev is None else fmt_num(ev))
        alab = r.get("actual_label") or ("未取得" if av is None else fmt_num(av))
        if ev is None:
            parts.append(
                f'<rect x="{left}" y="{y+4}" width="{inner*0.4:.1f}" height="16" rx="4" fill="none" stroke="#b0a898" stroke-dasharray="4 3"/>'
            )
            parts.append(f'<text x="{left+6}" y="{y+16}" class="svg-missing">預估 未取得</text>')
        else:
            w = max(8, inner * (float(ev) / vmax))
            parts.append(f'<rect x="{left}" y="{y+4}" width="{w:.1f}" height="16" rx="4" fill="#d4a06a"/>')
            parts.append(f'<text x="{left+w+6:.1f}" y="{y+16}" class="svg-lbl">預估 {esc(elab)}</text>')
        if av is None:
            parts.append(
                f'<rect x="{left}" y="{y+28}" width="{inner*0.4:.1f}" height="16" rx="4" fill="none" stroke="#b0a898" stroke-dasharray="4 3"/>'
            )
            parts.append(f'<text x="{left+6}" y="{y+40}" class="svg-missing">實際 未取得</text>')
        else:
            w = max(8, inner * (float(av) / vmax))
            parts.append(f'<rect x="{left}" y="{y+28}" width="{w:.1f}" height="16" rx="4" fill="#8a2f1d"/>')
            parts.append(f'<text x="{left+w+6:.1f}" y="{y+40}" class="svg-lbl">實際 {esc(alab)}</text>')
    parts.append("</svg>")
    return f'<figure class="fig">{"".join(parts)}{footnote(sources)}</figure>'


def svg_gantt(title: str, rows: list[dict], sources: list[dict], width: int = 880) -> str:
    """rows: {label, status, done, total, elapsed_label, eta_label, when}. No invented dates."""
    row_h = 52
    top = 36
    h = top + row_h * max(1, len(rows)) + 20
    left = 200
    inner = width - left - 24
    parts = [f'<svg class="chart" viewBox="0 0 {width} {h}" role="img" aria-label="{esc(title)}">']
    parts.append(f'<text x="16" y="22" class="svg-title">{esc(title)}</text>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        parts.append(f'<text x="16" y="{y+22}" class="svg-lbl">{esc(r.get("label",""))}</text>')
        parts.append(f'<rect x="{left}" y="{y+6}" width="{inner}" height="22" rx="6" fill="#efe8da"/>')
        done, total = r.get("done"), r.get("total")
        status = r.get("status") or ""
        if total in (None, 0) or done is None:
            parts.append(
                f'<text x="{left+10}" y="{y+22}" class="svg-missing">{esc(status or "未開始")}（總數未取得，不畫期間）</text>'
            )
        else:
            frac = min(1.0, max(0.0, float(done) / float(total)))
            fill = "#2f6f4e" if frac >= 1 else "#c45c26"
            parts.append(
                f'<rect x="{left}" y="{y+6}" width="{inner*frac:.1f}" height="22" rx="6" fill="{fill}"/>'
            )
            parts.append(
                f'<text x="{left+10}" y="{y+22}" class="svg-num-sm">{esc(fmt_num(done))}／{esc(fmt_num(total))}　{esc(status)}</text>'
            )
        extra = []
        if r.get("elapsed_label"):
            extra.append(f"已用時 {r['elapsed_label']}")
        if r.get("eta_label"):
            extra.append(f"預估剩餘 {r['eta_label']}")
        if r.get("when"):
            extra.append(str(r["when"]))
        if extra:
            parts.append(f'<text x="{left}" y="{y+42}" class="svg-fn">{esc(" · ".join(extra))}</text>')
    parts.append("</svg>")
    return f'<figure class="fig">{"".join(parts)}{footnote(sources)}</figure>'


def svg_flow(title: str, nodes: list[dict], sources: list[dict], width: int = 880) -> str:
    """nodes: {label, sub}. Linear flow with arrows. Pure SVG, no CDN."""
    n = max(1, len(nodes))
    h = 150
    pad = 16
    gap = 36
    box_w = (width - pad * 2 - gap * (n - 1)) / n
    bh = 78
    y = 40
    parts = [f'<svg class="chart" viewBox="0 0 {width} {h}" role="img" aria-label="{esc(title)}">']
    parts.append(f'<text x="{pad}" y="22" class="svg-title">{esc(title)}</text>')
    for i, nd in enumerate(nodes):
        x = pad + i * (box_w + gap)
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{box_w:.1f}" height="{bh}" rx="12" fill="#fffdf8" stroke="#c45c26" stroke-width="1.6"/>')
        parts.append(f'<text x="{x+box_w/2:.1f}" y="{y+32}" text-anchor="middle" class="svg-lbl">{esc(nd.get("label",""))}</text>')
        parts.append(f'<text x="{x+box_w/2:.1f}" y="{y+54}" text-anchor="middle" class="svg-num-sm">{esc(nd.get("sub",""))}</text>')
        if i < n - 1:
            ax1 = x + box_w
            ax2 = x + box_w + gap
            mid = y + bh / 2
            parts.append(
                f'<path d="M{ax1+4:.1f} {mid:.1f} L{ax2-6:.1f} {mid:.1f}" stroke="#8a2f1d" stroke-width="2" fill="none" marker-end="url(#arr)"/>'
            )
    parts.append(
        '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8a2f1d"/></marker></defs>'
    )
    parts.append("</svg>")
    return f'<figure class="fig">{"".join(parts)}{footnote(sources)}</figure>'


def svg_threshold_bars(title: str, rows: list[dict], threshold: float | None, threshold_label: str, sources: list[dict], width: int = 880) -> str:
    """rows: {label, value}. Horizontal bars vs a threshold line. value may be None."""
    row_h = 36
    top = 40
    h = top + row_h * max(1, len(rows)) + 16
    left, right = 160, 80
    inner = width - left - right
    vals = [float(r["value"]) for r in rows if isinstance(r.get("value"), (int, float))]
    if threshold is not None:
        vals.append(float(threshold))
    vmax = max(vals) if vals else 1
    parts = [f'<svg class="chart" viewBox="0 0 {width} {h}" role="img" aria-label="{esc(title)}">']
    parts.append(f'<text x="16" y="22" class="svg-title">{esc(title)}</text>')
    if threshold is not None:
        tx = left + inner * (float(threshold) / vmax)
        parts.append(f'<line x1="{tx:.1f}" y1="{top-8}" x2="{tx:.1f}" y2="{h-10}" stroke="#8a2f1d" stroke-dasharray="4 3"/>')
        parts.append(f'<text x="{tx+4:.1f}" y="{top-10}" class="svg-fn">{esc(threshold_label)}</text>')
    for i, r in enumerate(rows):
        y = top + i * row_h
        parts.append(f'<text x="16" y="{y+18}" class="svg-lbl">{esc(r.get("label",""))}</text>')
        val = r.get("value")
        if val is None:
            parts.append(f'<text x="{left}" y="{y+18}" class="svg-missing">未取得</text>')
        else:
            w = max(4, inner * (float(val) / vmax))
            over = threshold is not None and float(val) >= float(threshold)
            fill = "#2f6f4e" if over else "#c45c26"
            parts.append(f'<rect x="{left}" y="{y+4}" width="{w:.1f}" height="20" rx="5" fill="{fill}"/>')
            parts.append(f'<text x="{left+w+6:.1f}" y="{y+18}" class="svg-num-sm">{esc(fmt_num(val))}</text>')
    parts.append("</svg>")
    return f'<figure class="fig">{"".join(parts)}{footnote(sources)}</figure>'


OFFICIAL_COLORS = {
    "PASS": "#2f6f4e",
    "FAIL": "#b42318",
    "紅線 4 停止判定／ValueError": "#b54708",
}
RESEARCH_COLORS = {
    "A": "#1d4e89",
    "B": "#155e75",
    "Fail": "#9f1239",
}


def color_legend(items: list[tuple[str, str]]) -> str:
    bits = []
    for name, color in items:
        bits.append(
            f'<span class="leg"><i style="background:{color}"></i>{esc(name)}</span>'
        )
    bits.append('<span class="leg"><i class="miss"></i>無合格 rank-1／未列入</span>')
    return '<div class="legend">' + "".join(bits) + "</div>"


def color_grid(title: str, cells: list[dict], key: str, palette: dict, sources: list[dict]) -> str:
    """cells: {name, official, research, missing?}."""
    tiles = []
    for c in cells:
        if c.get("missing"):
            tiles.append(
                f'<span class="tile miss" title="{esc(c.get("name",""))} 無合格 rank-1">{esc(c.get("short") or c.get("name",""))}</span>'
            )
            continue
        val = c.get(key) or ""
        color = palette.get(val, "#9a9488")
        label = val if val else "未取得"
        tiles.append(
            f'<span class="tile" style="background:{color}" title="{esc(c.get("name",""))}　{esc(label)}">{esc(c.get("short") or c.get("name",""))}</span>'
        )
    return (
        f'<figure class="fig"><div class="fig-title">{esc(title)}</div>'
        f'<div class="grid">{"".join(tiles)}</div>'
        f'{color_legend(list(palette.items()))}{footnote(sources)}</figure>'
    )


def record_card(rec: dict) -> str:
    fields = [
        ("時間", rec.get("time")),
        ("目的", rec.get("purpose")),
        ("規模", rec.get("scale")),
        ("方法與出處", rec.get("method")),
        ("預估與實際耗時", rec.get("timing")),
        ("問題與替代嘗試", rec.get("issues")),
        ("成敗", rec.get("outcome")),
        ("改善思路", rec.get("next")),
    ]
    def cell(v):
        if isinstance(v, dict) and "html" in v:
            return v["html"] or "未取得"
        return esc(v) if v else "未取得"
    rows = "".join(
        f"<tr><th>{esc(k)}</th><td>{cell(v)}</td></tr>" for k, v in fields
    )
    charts = rec.get("charts_html") or ""
    link = rec.get("href")
    heading = f"{esc(rec.get('id',''))}　{esc(rec.get('title',''))}"
    more = f'<p class="more"><a href="{esc(link)}">完整快照</a></p>' if link else ""
    return f"""
    <article class="card record" id="{esc(rec.get('id',''))}">
      <h2>{heading}</h2>
      <p class="one-liner">{esc(rec.get("one_liner") or rec.get("purpose") or "")}</p>
      {charts}
      <div class="scroll">
        <table class="kv">{rows}</table>
      </div>
      {more}
    </article>
    """


def page_shell(title: str, body: str, rel_prefix: str = "") -> str:
    css = f"{rel_prefix}style.css"
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{css}">
</head>
<body>
  <div class="wrap">
    <div class="banner">{esc(DISCLAIMER)}</div>
    {body}
    <footer>
      <p>{esc(DISCLAIMER)}　本站只刊登彙總結果與檔名／sha1，不刊登原始資料、tick、帳本 CSV 或憑證。圖由建置腳本從真實檔案重繪；缺資料標「未取得／未開始」，不編時間、不猜數字。</p>
    </footer>
  </div>
</body>
</html>
"""


def render_index(ctx: dict) -> str:
    v14 = ctx["v14"]
    overview_charts = "".join(ctx.get("overview_charts") or [])
    records_html = "".join(record_card(r) for r in ctx.get("records") or [])
    status_html = ctx.get("status_html") or ""
    src_rows = ctx.get("src_table_html") or ""
    hist_table = ctx.get("hist_table_html") or ""
    trials = ctx.get("trials_html") or ""
    missing_log = ""
    if not ctx.get("experiment_log_found"):
        missing_log = (
            "<p class=\"meta\"><code>/workspace/ml_meta/v14/EXPERIMENT_LOG.md</code>：未找到。"
            "以下最早幾條紀錄依既有摘要檔核對寫成，待該檔出現後以它為主，歷史只附加。</p>"
        )
    body = f"""
    <header class="site">
      <h1>GBDTRLHMM 新制度變形｜實驗紀錄</h1>
      <p class="sub">嘗試、規模、耗時、成敗與改善思路。文不如表、表不如圖。{esc(DISCLAIMER)}</p>
    </header>

    <section class="card">
      <h2>試驗與進度總覽</h2>
      {trials}
    </section>
    {status_html}
    {overview_charts}

    <section>
      <h2 class="section-h">實驗紀錄</h2>
      {missing_log}
      {records_html or "<p>尚未取得可刊登的實驗紀錄。</p>"}
    </section>

    <section class="card">
      <h2>來源檔（本次掃描）</h2>
      <p class="meta">最新快照：{esc(ctx.get("latest_time") or "尚無")}。只讀 <code>/workspace/ml_meta</code>，未改動來源。歷史只附加：來源內容若與上一筆快照 sha1 相同則不新寫；同名檔既已存在則不覆蓋。</p>
      <div class="scroll">
      <table>
        <thead><tr><th>來源路徑</th><th>sha1</th><th>快照</th></tr></thead>
        <tbody>
          {src_rows}
        </tbody>
      </table>
      </div>
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
    return page_shell("GBDTRLHMM 實驗紀錄（探索性、非獨立盲測；非官方驗收）", body, "")


def svg_gantt_stages(title: str, stages: list[dict], sources: list[dict], width: int = 880) -> str:
    """Gantt-like rows from progress.json stages. Never invent start/end times."""
    rows = []
    for st in stages or []:
        status = st.get("status") or ""
        status_zh = {"not_started": "未開始", "running": "進行中", "done": "完成", "failed": "失敗"}.get(status, status)
        start, end = st.get("start_time"), st.get("end_time")
        eta = st.get("end_time_estimated")
        eta_sec = st.get("eta_seconds")
        when_bits = []
        if start:
            when_bits.append(f"開始 {start}")
        else:
            when_bits.append("開始時間未取得" if status != "not_started" else "未開始")
        if end:
            when_bits.append(f"結束 {end}")
        elif status == "running":
            when_bits.append("結束時間未取得")
        if eta:
            when_bits.append(f"預估結束 {eta}")
        eta_label = None
        if eta_sec is not None:
            eta_label = f"{eta_sec} 秒"
        elif eta is None and status == "not_started":
            eta_label = "未取得"
        rows.append({
            "label": st.get("name") or "（未命名階段）",
            "status": status_zh,
            "done": st.get("done"),
            "total": st.get("total"),
            "elapsed_label": None,
            "eta_label": eta_label,
            "when": "；".join(when_bits),
        })
    if not rows:
        rows = [{"label": "stages", "status": "未取得", "done": None, "total": None, "elapsed_label": None, "eta_label": None, "when": "progress.json 無 stages 陣列"}]
    return svg_gantt(title, rows, sources, width)
