"""SVG diagrams and charts for the presentation guide (no external dependencies).

Charts follow the dataviz method: thin bars with rounded data ends, direct value labels,
a legend whenever there are two series, recessive grid, text in ink colours (never the
series colour). Palette validated with the dataviz validator (blue/orange pass CVD checks).
"""

from html import escape

# Brand (diagrams) — matches the dashboard's teal accent on slate
TEAL, TEAL_SOFT, TEAL_INK = "#0f766e", "#e6f4f2", "#134e4a"
SLATE, SLATE_SOFT, LINE = "#334155", "#f1f5f9", "#cbd5e1"
INK, INK_2, INK_3 = "#0f172a", "#475569", "#94a3b8"
# Charts — validated categorical slots + neutral baseline
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#a8a29e"
WARN, BAD = "#b45309", "#b91c1c"
FONT = "Segoe UI, Inter, Arial, sans-serif"


def _t(x, y, s, size=13, fill=INK, weight=400, anchor="start", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" font-family="{FONT}"{st}>{escape(s)}</text>')


def _box(x, y, w, h, fill=SLATE_SOFT, stroke=LINE, r=10, sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def _arrow(x1, y1, x2, y2, color=INK_2, sw=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"'
            f' marker-end="url(#arr)"{d}/>')


def _svg(w, h, body, label):
    defs = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK_2}"/>'
            '</marker></defs>')
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{escape(label)}" '
            f'xmlns="http://www.w3.org/2000/svg">{defs}{body}</svg>')


def _card(x, y, w, h, title, lines, accent=TEAL, fill="#ffffff", title_size=14):
    out = [_box(x, y, w, h, fill=fill, stroke=LINE),
           f'<rect x="{x}" y="{y}" width="5" height="{h}" rx="2" fill="{accent}"/>',
           _t(x + 16, y + 24, title, title_size, INK, 600)]
    for i, ln in enumerate(lines):
        out.append(_t(x + 16, y + 44 + i * 17, ln, 11.5, INK_2))
    return "".join(out)


# ============================================================================ diagrams
def concept():
    """The idea in one picture: three signals -> reliability -> fusion -> trustworthy output."""
    b = []
    rows = [("Voice", "How it sounds", "WavLM speech model"),
            ("Words", "What is said", "Whisper + DeBERTa"),
            ("Face", "How it looks", "Face detector + ViT")]
    for i, (name, what, model) in enumerate(rows):
        y = 30 + i * 105
        b.append(_card(20, y, 190, 80, name, [what, model]))
        b.append(_arrow(212, y + 40, 262, y + 40))
        b.append(_box(266, y + 8, 150, 64, fill=TEAL_SOFT, stroke="#99d5cc"))
        b.append(_t(341, y + 32, "Reliability check", 12.5, TEAL_INK, 600, "middle"))
        b.append(_t(341, y + 50, "noise · blur · light ·", 10.5, INK_2, 400, "middle"))
        b.append(_t(341, y + 64, "ASR confidence", 10.5, INK_2, 400, "middle"))
        b.append(_arrow(418, y + 40, 490, 175))
    b.append(_box(494, 120, 170, 110, fill=TEAL, stroke=TEAL))
    b.append(_t(579, 160, "Fusion model", 15, "#ffffff", 700, "middle"))
    b.append(_t(579, 182, "combines all signals,", 11.5, "#e6f4f2", 400, "middle"))
    b.append(_t(579, 198, "trained to cope with", 11.5, "#e6f4f2", 400, "middle"))
    b.append(_t(579, 214, "damaged or missing ones", 11.5, "#e6f4f2", 400, "middle"))
    b.append(_arrow(666, 175, 712, 175))
    out = ["Emotion  (7 classes)", "Calibrated confidence", "or “uncertain”", "Plain-language reasons",
           "Alerts + session summary"]
    b.append(_box(716, 60, 214, 230, fill="#ffffff", stroke=TEAL, sw=1.6))
    b.append(_t(823, 88, "Output per segment", 14, INK, 700, "middle"))
    for i, o in enumerate(out):
        y = 122 + i * 34
        b.append(f'<circle cx="738" cy="{y - 4}" r="4" fill="{TEAL}"/>')
        b.append(_t(752, y, o, 12.5, INK_2))
    return _svg(950, 345, "".join(b), "Concept: voice, words and face are checked for reliability "
                "and fused into an emotion with confidence and reasons")


def architecture():
    b = []
    # Browser
    b.append(_card(20, 40, 210, 120, "Browser — dashboard", ["React + TypeScript", "Upload · Live · Reports",
                                                          "Sessions · System page"]))
    b.append(_arrow(232, 100, 300, 100))
    b.append(_t(266, 90, "HTTPS", 10.5, INK_3, 400, "middle"))
    b.append(_t(266, 124, "WebSocket", 10.5, INK_3, 400, "middle"))
    # nginx
    b.append(_box(304, 60, 110, 80, fill=SLATE_SOFT))
    b.append(_t(359, 94, "nginx", 14, INK, 600, "middle"))
    b.append(_t(359, 113, "one origin,", 10.5, INK_2, 400, "middle"))
    b.append(_t(359, 127, "security headers", 10.5, INK_2, 400, "middle"))
    b.append(_arrow(416, 100, 470, 100))
    # API
    b.append(_box(474, 20, 300, 255, fill="#ffffff", stroke=TEAL, sw=1.6))
    b.append(_t(624, 44, "FastAPI service", 15, INK, 700, "middle"))
    mods = [("Auth & roles", "JWT · Argon2 · rate limit"), ("Sessions API", "upload · export · alerts"),
            ("Live stream", "WebSocket, 3-second windows"), ("Analysis worker", "segments a recording")]
    for i, (a, s) in enumerate(mods):
        y = 58 + i * 52
        b.append(_box(490, y, 268, 44, fill=SLATE_SOFT))
        b.append(_t(504, y + 19, a, 12.5, INK, 600))
        b.append(_t(504, y + 35, s, 10.5, INK_2))
    # Engine
    b.append(_arrow(776, 160, 826, 160))
    b.append(_box(830, 40, 250, 235, fill=TEAL_SOFT, stroke="#99d5cc"))
    b.append(_t(955, 64, "Inference engine", 15, TEAL_INK, 700, "middle"))
    eng = ["Speech recognition (Whisper)", "Voice encoder (WavLM)", "Text model (DeBERTa)",
           "Face detector + ViT", "Reliability + fusion", "Calibration · abstention",
           "Explanations · conflict"]
    for i, e in enumerate(eng):
        b.append(_t(850, 92 + i * 25, "•  " + e, 12, INK_2))
    # DB and bundle
    b.append(_box(474, 300, 300, 62, fill="#ffffff"))
    b.append(_t(624, 326, "Database", 13.5, INK, 600, "middle"))
    b.append(_t(624, 344, "SQLite (dev) · PostgreSQL (prod)", 11, INK_2, 400, "middle"))
    b.append(_arrow(624, 277, 624, 298))
    b.append(_box(830, 300, 250, 62, fill="#ffffff", dash="5 4"))
    b.append(_t(955, 326, "Versioned model bundle", 13.5, INK, 600, "middle"))
    b.append(_t(955, 344, "weights · calibration · CV results", 11, INK_2, 400, "middle"))
    b.append(_arrow(955, 298, 955, 277))
    # Offline ML
    b.append(_box(20, 300, 410, 62, fill="#ffffff", dash="5 4"))
    b.append(_t(225, 326, "Offline ML pipeline (training & evaluation)", 13.5, INK, 600, "middle"))
    b.append(_t(225, 344, "datasets → features → cross-validation → bundle export", 11, INK_2, 400, "middle"))
    b.append(_arrow(432, 331, 826, 331, dash="4 3"))
    return _svg(1100, 380, "".join(b), "System architecture: browser, nginx, FastAPI service, "
                "inference engine, database, model bundle")


def upload_workflow():
    steps = [("1", "Upload + consent", "WAV · MP3 · MP4 · WEBM"), ("2", "Validate", "type, size ≤ 200 MB,\nlength ≤ 60 min"),
             ("3", "Split into speech", "segments of 1–6 s"), ("4", "Per segment", "transcript + 16 face\nframes + audio"),
             ("5", "Three models", "voice · words · face"), ("6", "Reliability + fusion", "weights each signal"),
             ("7", "Calibrate", "confidence, or\n“uncertain”"), ("8", "Explain + store", "reasons, conflict flag"),
             ("9", "Session insights", "timeline · alerts ·\nsummary · export")]
    b = []
    w, h, gap = 166, 92, 22
    for i, (n, title, sub) in enumerate(steps):
        row, col = divmod(i, 5)
        col = col if row == 0 else 4 - col  # snake layout
        x, y = 20 + col * (w + gap), 20 + row * (h + 56)
        fill = TEAL_SOFT if n in ("5", "6", "7") else "#ffffff"
        b.append(_box(x, y, w, h, fill=fill, stroke="#99d5cc" if fill == TEAL_SOFT else LINE))
        b.append(f'<circle cx="{x + 20}" cy="{y + 22}" r="11" fill="{TEAL}"/>')
        b.append(_t(x + 20, y + 26.5, n, 12, "#ffffff", 700, "middle"))
        b.append(_t(x + 38, y + 27, title, 12.5, INK, 600))
        for j, ln in enumerate(sub.split("\n")):
            b.append(_t(x + 14, y + 52 + j * 16, ln, 11, INK_2))
        if i < len(steps) - 1:
            if i == 4:
                b.append(_arrow(x + w / 2, y + h + 2, x + w / 2, y + h + 52))
            elif row == 0:
                b.append(_arrow(x + w + 2, y + h / 2, x + w + gap - 2, y + h / 2))
            else:
                b.append(_arrow(x - 2, y + h / 2, x - gap + 2, y + h / 2))
    b.append(_t(20, 300, "Raw recordings are deleted after analysis by default; only results are stored.",
                11.5, INK_3, 400, italic=True))
    return _svg(960, 312, "".join(b), "Upload workflow in nine steps")


def live_sequence():
    b = []
    lanes = [("Browser", 120), ("API (WebSocket)", 470), ("Inference engine", 820)]
    for name, x in lanes:
        b.append(_box(x - 95, 14, 190, 38, fill=TEAL if name == "Browser" else SLATE_SOFT,
                      stroke=TEAL if name == "Browser" else LINE))
        b.append(_t(x, 38, name, 13, "#ffffff" if name == "Browser" else INK, 600, "middle"))
        b.append(f'<line x1="{x}" y1="54" x2="{x}" y2="330" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    msgs = [(120, 470, 80, "connect with login token  →  “loading models” … “ready”"),
            (120, 470, 120, "microphone audio, every 250 ms (16 kHz)"),
            (120, 470, 152, "camera frames, 6 per second (JPEG)"),
            (470, 820, 196, "every 3 seconds: one window of audio + frames"),
            (820, 470, 236, "emotion · confidence · reliability · reasons"),
            (470, 120, 276, "segment result → timeline + live alerts update"),
            (120, 470, 314, "stop  →  session saved with summary")]
    for x1, x2, y, label in msgs:
        b.append(_arrow(x1 + (6 if x2 > x1 else -6), y, x2 - (6 if x2 > x1 else -6), y,
                        color=TEAL if x1 == 820 or (x1 == 470 and x2 == 120) else INK_2))
        b.append(_t((x1 + x2) / 2, y - 7, label, 11.5, INK_2, 400, "middle"))
    b.append(_t(470, 352, "If analysis falls behind, video frames are dropped first so audio stays real-time.",
                11.5, INK_3, 400, "middle", italic=True))
    return _svg(940, 362, "".join(b), "Live mode sequence between browser, API and inference engine")


def model_diagram():
    b = []
    ins = [("Voice features", "13 layers × 1536", "frozen WavLM-Base+"),
           ("Text features", "768 + 7 emotion scores", "DeBERTa trained on MELD"),
           ("Face features", "16 frames × 768", "frozen ViT face model")]
    for i, (a, s, m) in enumerate(ins):
        y = 24 + i * 112
        b.append(_card(16, y, 200, 86, a, [s, m]))
        b.append(_arrow(218, y + 43, 262, y + 43))
        b.append(_box(266, y + 10, 128, 66, fill="#ffffff"))
        b.append(_t(330, y + 38, "Branch head", 12.5, INK, 600, "middle"))
        b.append(_t(330, y + 56, "embedding + guess", 10.5, INK_2, 400, "middle"))
        b.append(_arrow(396, y + 43, 446, y + 43))
        b.append(_box(450, y + 10, 128, 66, fill=TEAL_SOFT, stroke="#99d5cc"))
        b.append(_t(514, y + 34, "Reliability r", 12.5, TEAL_INK, 600, "middle"))
        b.append(_t(514, y + 51, "quality signals +", 10.5, INK_2, 400, "middle"))
        b.append(_t(514, y + 65, "branch uncertainty", 10.5, INK_2, 400, "middle"))
        b.append(_arrow(580, y + 43, 636, 180))
        b.append(f'<path d="M330 {y + 76} C 330 {y + 96}, 600 {y + 96}, 636 182" fill="none" stroke="{INK_3}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    b.append(_box(640, 96, 200, 170, fill=TEAL, stroke=TEAL))
    for i, ln in enumerate(["Cross-modal", "transformer", "", "attention to signal k gets", "a bonus  β · log(r_k)",
                            "missing signals are masked"]):
        b.append(_t(740, 130 + i * 20, ln, 14 if i < 2 else 11.5, "#ffffff" if i < 2 else "#d8f0ec",
                    700 if i < 2 else 400, "middle"))
    b.append(_arrow(842, 181, 884, 181))
    b.append(_box(888, 120, 150, 122, fill="#ffffff", stroke=TEAL, sw=1.6))
    for i, ln in enumerate(["Temperature", "calibration", "", "confidence < 0.45", "→ “uncertain”"]):
        b.append(_t(963, 148 + i * 18, ln, 13 if i < 2 else 11.5, INK if i < 2 else INK_2,
                    600 if i < 2 else 400, "middle"))
    return _svg(1050, 355, "".join(b), "Fusion model: three branches, reliability scores, "
                "cross-modal transformer, calibration")


def cv_diagram():
    b = []
    b.append(_t(20, 24, "5-fold speaker-independent cross-validation on CREMA-D (91 actors)", 13.5, INK, 600))
    colors = {"train": "#cbd5e1", "val": "#fbbf24", "test": TEAL}
    for f in range(5):
        y = 44 + f * 34
        b.append(_t(20, y + 19, f"Round {f + 1}", 12, INK_2))
        for g in range(5):
            role = "test" if g == f else "val" if g == (f + 1) % 5 else "train"
            x = 100 + g * 118
            b.append(f'<rect x="{x}" y="{y}" width="112" height="26" rx="5" fill="{colors[role]}"/>')
            if f == 0:
                b.append(_t(x + 56, 222, f"speaker group {g + 1}", 10.5, INK_3, 400, "middle"))
    for i, (k, lbl) in enumerate([("train", "train (≈ 55 actors)"), ("val", "validation + calibration (≈ 18)"),
                                  ("test", "test — never seen (≈ 18)")]):
        x = 100 + i * 205
        b.append(f'<rect x="{x}" y="238" width="14" height="14" rx="3" fill="{colors[k]}"/>')
        b.append(_t(x + 20, 250, lbl, 11.5, INK_2))
    b.append(_t(20, 280, "Every actor is tested exactly once, on a model that never heard or saw them. "
                "Scores are the mean ± spread over the 5 rounds.", 11.5, INK_3, italic=True))
    return _svg(720, 290, "".join(b), "Cross-validation: each round tests on unseen speakers")


def corruption_diagram():
    items = [("Clean", "original input"), ("Noise 10 dB", "busy office"), ("Noise 0 dB", "noisy room,\nASR re-run"),
             ("Blur", "out-of-focus face"), ("Dark", "poor lighting"), ("Occluded", "half the face hidden"),
             ("Word drop", "50% of words lost"), ("Missing", "camera or mic off")]
    b = [_t(20, 22, "During training every example is randomly damaged, so the model learns to cope:", 13, INK, 600)]
    for i, (a, s) in enumerate(items):
        x = 20 + (i % 4) * 172
        y = 38 + (i // 4) * 78
        clean = i == 0
        b.append(_box(x, y, 160, 64, fill=TEAL_SOFT if clean else "#ffffff",
                      stroke="#99d5cc" if clean else LINE))
        b.append(_t(x + 14, y + 24, a, 12.5, INK, 600))
        for j, ln in enumerate(s.split("\n")):
            b.append(_t(x + 14, y + 42 + j * 14, ln, 11, INK_2))
    b.append(_t(20, 206, "Each signal is clean 40% of the time; each is dropped entirely 20% of the time "
                "(at least one always remains).", 11.5, INK_3, italic=True))
    return _svg(720, 216, "".join(b), "Corruption and modality-dropout training")


def milestones():
    ms = [("M0", "Foundations", "honest baseline,\nCI, data pipeline"), ("M1", "Unimodal models", "voice · words ·\nface branches"),
          ("M2", "Reliability + fusion", "robust fusion,\ncalibration"), ("M3", "Platform", "API · live stream ·\ndashboard"),
          ("M4", "Hardening", "security · Docker ·\nload test"), ("M5", "Report + demo", "evaluation,\npresentation")]
    b = [f'<line x1="80" y1="48" x2="920" y2="48" stroke="{LINE}" stroke-width="3"/>']
    for i, (m, t, s) in enumerate(ms):
        x = 80 + i * 168
        b.append(f'<circle cx="{x}" cy="48" r="17" fill="{TEAL}"/>')
        b.append(_t(x, 53, m, 13, "#ffffff", 700, "middle"))
        b.append(_t(x, 92, t, 14, INK, 600, "middle"))
        for j, ln in enumerate(s.split("\n")):
            b.append(_t(x, 112 + j * 17, ln, 12.5, INK_2, 400, "middle"))
        b.append(_t(x, 20, "✓ done", 12, TEAL, 600, "middle"))
    return _svg(1000, 150, "".join(b), "Project milestones M0 to M5, all complete")


# ============================================================================ charts
def _value_bar(x, y, w, h, color):
    """Bar anchored left with a 4px rounded data end on the right."""
    r = min(4, w / 2, h / 2)
    if w <= 0:
        return ""
    return (f'<path d="M{x},{y} H{x + w - r} Q{x + w},{y} {x + w},{y + r} V{y + h - r} '
            f'Q{x + w},{y + h} {x + w - r},{y + h} H{x} Z" fill="{color}"/>')


def hbars(rows, title, xmax=1.0, note=None, width=720, label_w=250, fmt="{:.3f}"):
    """rows: (label, value, color, err_or_None). One series: no legend; the title names it."""
    row_h, bar_h = 34, 16
    plot_w = width - label_w - 70
    top = 40
    b = [_t(0, 18, title, 13.5, INK, 600)]
    for k in range(0, 5):
        gx = label_w + plot_w * k / 4
        b.append(f'<line x1="{gx}" y1="{top - 6}" x2="{gx}" y2="{top + len(rows) * row_h}" stroke="#eef0f3" stroke-width="1"/>')
        b.append(_t(gx, top + len(rows) * row_h + 16, f"{xmax * k / 4:.2f}".rstrip("0").rstrip(".") if k else "0",
                    10.5, INK_3, 400, "middle"))
    for i, (lab, v, col, err) in enumerate(rows):
        y = top + i * row_h
        b.append(_t(label_w - 10, y + bar_h - 3, lab, 12, INK, 600 if col == BLUE else 400, "end"))
        bw = plot_w * v / xmax
        b.append(_value_bar(label_w, y, bw, bar_h, col))
        if err:
            ex0, ex1 = label_w + plot_w * (v - err) / xmax, label_w + plot_w * (v + err) / xmax
            b.append(f'<line x1="{ex0}" y1="{y + bar_h / 2}" x2="{ex1}" y2="{y + bar_h / 2}" stroke="{INK}" stroke-width="1.2" opacity="0.55"/>')
        b.append(_t(label_w + bw + 8 + (plot_w * err / xmax if err else 0), y + bar_h - 3,
                    fmt.format(v), 12, INK, 600 if col == BLUE else 400))
    hgt = top + len(rows) * row_h + 26
    if note:
        b.append(_t(0, hgt + 6, note, 11, INK_3, italic=True))
        hgt += 14
    return _svg(width, hgt, "".join(b), title)


def dumbbell(rows, title, names, colors=(BLUE, ORANGE), xmin=0.0, xmax=1.0, width=720, label_w=220,
             ref=None, note=None, fmt="{:.2f}"):
    """rows: (label, a, b). Two series per row joined by a line; legend + direct labels."""
    row_h = 30
    top = 74 if ref is not None else 56
    plot_w = width - label_w - 40

    def sx(v):
        return label_w + plot_w * (v - xmin) / (xmax - xmin)

    b = [_t(0, 18, title, 13.5, INK, 600)]
    for i, (n, c) in enumerate(zip(names, colors, strict=True)):
        lx = label_w + i * 230
        b.append(f'<circle cx="{lx + 6}" cy="35" r="6" fill="{c}"/>')
        b.append(_t(lx + 18, 39.5, n, 11.5, INK_2))
    for k in range(5):
        v = xmin + (xmax - xmin) * k / 4
        gx = sx(v)
        b.append(f'<line x1="{gx}" y1="{top - 8}" x2="{gx}" y2="{top + len(rows) * row_h - 8}" stroke="#eef0f3"/>')
        b.append(_t(gx, top + len(rows) * row_h + 8, f"{v:.2f}", 10.5, INK_3, 400, "middle"))
    if ref is not None:
        rv, rl = ref
        b.append(f'<line x1="{sx(rv)}" y1="{top - 8}" x2="{sx(rv)}" y2="{top + len(rows) * row_h - 8}" stroke="{INK_2}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        b.append(_t(sx(rv), top - 16, rl, 10.5, INK_2, 600, "middle"))
    for i, (lab, a, c) in enumerate(rows):
        y = top + i * row_h
        b.append(_t(label_w - 12, y + 4, lab, 12, INK, 400, "end"))
        b.append(f'<line x1="{sx(min(a, c))}" y1="{y}" x2="{sx(max(a, c))}" y2="{y}" stroke="{LINE}" stroke-width="3"/>')
        for v, col in ((c, colors[1]), (a, colors[0])):
            b.append(f'<circle cx="{sx(v)}" cy="{y}" r="6.5" fill="{col}" stroke="#ffffff" stroke-width="2"/>')
        right = max(a, c)
        b.append(_t(sx(right) + 12, y + 4, fmt.format(a), 11.5, INK, 600))
    hgt = top + len(rows) * row_h + 18
    if note:
        b.append(_t(0, hgt + 6, note, 11, INK_3, italic=True))
        hgt += 14
    return _svg(width, hgt, "".join(b), title)


def grouped(rows, title, names, colors=(BLUE, ORANGE), xmax=1.0, width=720, label_w=200, note=None,
            fmt="{:.0%}"):
    """Two-series horizontal grouped bars with legend and direct labels; 2px gap between bars."""
    bar_h, gap, row_h = 13, 2, 40
    top = 52
    plot_w = width - label_w - 60
    b = [_t(0, 18, title, 13.5, INK, 600)]
    for i, (n, c) in enumerate(zip(names, colors, strict=True)):
        lx = label_w + i * 230
        b.append(f'<rect x="{lx}" y="29" width="12" height="12" rx="3" fill="{c}"/>')
        b.append(_t(lx + 18, 39.5, n, 11.5, INK_2))
    for k in range(5):
        gx = label_w + plot_w * k / 4
        b.append(f'<line x1="{gx}" y1="{top - 6}" x2="{gx}" y2="{top + len(rows) * row_h - 8}" stroke="#eef0f3"/>')
        b.append(_t(gx, top + len(rows) * row_h + 8, fmt.format(xmax * k / 4), 10.5, INK_3, 400, "middle"))
    for i, (lab, a, c) in enumerate(rows):
        y = top + i * row_h
        b.append(_t(label_w - 10, y + bar_h + 1, lab, 12, INK, 400, "end"))
        for j, (v, col) in enumerate(((a, colors[0]), (c, colors[1]))):
            yy = y + j * (bar_h + gap)
            bw = plot_w * v / xmax
            b.append(_value_bar(label_w, yy, bw, bar_h, col))
            b.append(_t(label_w + bw + 6, yy + bar_h - 2.5, fmt.format(v), 11, INK, 400))
    hgt = top + len(rows) * row_h + 16
    if note:
        b.append(_t(0, hgt + 6, note, 11, INK_3, italic=True))
        hgt += 14
    return _svg(width, hgt, "".join(b), title)
