"""Chart helpers (HTML/CSS bars, stacks, donuts) shared by the case study builder."""
import html

SHADES = ["#0b0b0b", "#8a8a8a", "#cfcfcf", "#5c5c5c", "#e6e6e6"]


def hbars(rows, maxv=None, unit="%", hi=None, label_w="minmax(120px,200px)"):
    """rows: [(label, value)]; hi: set of labels drawn in ink, others grey (all ink when None)."""
    maxv = maxv or max(v for _, v in rows)
    out = []
    for lab, v in rows:
        cls = "" if (hi is None or lab in hi) else "g"
        out.append(f'<div class="hb-row" style="grid-template-columns:{label_w} minmax(0,1fr) 64px" title="{e(lab)}: {v}{unit}">'
                   f'<span>{e(lab)}</span><span class="tr"><i class="{cls}" style="width:{v / maxv * 100:.1f}%"></i></span><b>{v}{unit}</b></div>')
    return '<div class="hb">' + "".join(out) + "</div>"


def stacked(segs, unit="%"):
    """segs: [(label, value)] summing to ~100."""
    total = sum(v for _, v in segs)
    bar = "".join(f'<i title="{e(l)}: {v}{unit}" style="width:{v / total * 100:.1f}%;background:{SHADES[i % 5]}"></i>' for i, (l, v) in enumerate(segs))
    leg = "".join(f'<span><i style="background:{SHADES[i % 5]}"></i>{e(l)} <b>{v}{unit}</b></span>' for i, (l, v) in enumerate(segs))
    return f'<div class="stk">{bar}</div><div class="stk-l">{leg}</div>'


def donut(segs, centre, sub):
    r, c = 70, 2 * 3.14159 * 70
    off, arcs = 0, []
    for i, (l, v) in enumerate(segs):
        ln = v / 100 * c
        arcs.append(f'<circle cx="90" cy="90" r="{r}" fill="none" stroke="{SHADES[i % 5]}" stroke-width="26" '
                    f'stroke-dasharray="{ln:.1f} {c - ln:.1f}" stroke-dashoffset="{-off:.1f}"><title>{e(l)}: {v}%</title></circle>')
        off += ln
    leg = "".join(f'<span><i style="background:{SHADES[i % 5]}"></i>{e(l)} <b>{v}%</b></span>' for i, (l, v) in enumerate(segs))
    return (f'<div class="dn"><svg viewBox="0 0 180 180" style="transform:rotate(-90deg)">{"".join(arcs)}</svg>'
            f'<div class="dn-c"><b>{centre}</b><span>{sub}</span></div></div><div class="stk-l" style="flex-direction:column;gap:8px">{leg}</div>')


def grouped(rows, series):
    """rows: [(label, [v1, v2, v3])] as percentages."""
    out = []
    for lab, vals in rows:
        bars = "".join(f'<div class="gl" title="{e(series[j])}: {v}%"><span><i style="width:{v}%;background:{SHADES[j]}"></i></span><b>{v}</b></div>' for j, v in enumerate(vals))
        out.append(f'<div class="gb-row"><span>{e(lab)}</span><div class="gb">{bars}</div></div>')
    leg = "".join(f'<span><i style="background:{SHADES[j]}"></i>{e(s)}</span>' for j, s in enumerate(series))
    return '<div class="gbs">' + "".join(out) + f'</div><div class="stk-l">{leg}</div>'


def panel(title, body, note=""):
    n = f'<p class="chart-s">{e(note)}</p>' if note else ""
    return f'<div class="panel"><p class="chart-t">{e(title)}</p>{body}{n}</div>'


def stat(k, n, p, dark=False):
    return f'<div class="t{" dk" if dark else ""}"><span class="k">{e(k)}</span><div class="n">{n}</div><p>{e(p)}</p></div>'


def quote(who, role, text, dark=False):
    return (f'<div class="t q{" dk" if dark else ""}"><p class="qt">"{e(text)}"</p>'
            f'<span class="k">{e(who)} / {e(role)}</span></div>')



e = html.escape
