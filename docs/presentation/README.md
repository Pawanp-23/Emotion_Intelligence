# Presentation guide

[`RAMEI-Presentation-Guide.pdf`](RAMEI-Presentation-Guide.pdf) — 21-page guide for the faculty
review: project summary, architecture and workflow diagrams, results charts, app screenshots,
a 12-minute presentation script, a live-demo runbook, likely questions with answers, and a glossary.

Rebuild after changing results or text (needs Microsoft Edge or Chrome for printing):

```bash
python docs/presentation/build_guide.py
```

- `build_guide.py` — content and page layout; reads results from `docs/reports/data/*.json`
- `figures.py` — the SVG diagrams and charts
- `img/` — dashboard screenshots (light theme, 1440×900 at 2×)
