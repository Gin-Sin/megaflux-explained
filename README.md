# MegaFlux, explained

A visual teaching article about **MegaFlux: Skew-Resilient MoE Megakernels via Pipelined Expert Replication**, Jianzhu Yao et al., [arXiv:2610.00671v1](https://arxiv.org/html/2610.00671v1), September 30, 2026.

The site combines a technical article, an interactive block-assignment model, three original Manim animations, a benchmark reading guide, and a public editorial storyboard. It targets ML engineers who know matrix multiplication and transformer inference. It is an independent explanation, not an author implementation or a benchmark reproduction.

## Read and run

- Published site: https://gin-sin.github.io/megaflux-explained/
- Storyboard: https://gin-sin.github.io/megaflux-explained/storyboard.html
- Serve locally: `python3 -m http.server 8080 --directory site`
- Open http://localhost:8080

All runtime resources are local. The site requires no build step, API key, or external CDN. JavaScript adds the planner and navigation; the article, figures, tables, and transcripts remain readable without it.

## Reproduce the illustrations

Python 3.12, FFmpeg, Cairo, Pango, development headers, LaTeX, `dvisvgm`, and the CMU font family are required. On Debian/Ubuntu, the additional typography packages include `fonts-cmu`, `texlive-latex-extra`, and `dvisvgm`. See [Manim installation instructions](https://docs.manim.community/en/stable/installation/uv.html).

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/render.py
.venv/bin/python scripts/build_storyboard.py
```

`animations/scenes.py` contains three Manim Community scenes. `scripts/render.py` renders 1280 × 720, 30 fps MP4 files and extracts PNG posters into `site/assets/`. Timelines and block counts are explicitly schematic, not GPU measurements. Every video has a nearby HTML transcript.

## Validate

```sh
npm test
python3 -m http.server 8080 --directory site
# In another terminal, with Chromium installed for Playwright:
.venv/bin/python tests/browser.py http://localhost:8080
```

Planner tests check conservation, integer block assignments, replica limits, refinement, and the owner-side reduction proxy. Browser checks cover desktop/mobile overflow, local links/assets, keyboard controls, interactive values, video decoding, and browser errors. `test-results/` is local only.

## Editorial sources

[docs/ARTICLE_PLAN.md](docs/ARTICLE_PLAN.md) records the audience, learning objectives, article skeleton, and shot-by-shot storyboard. [docs/RESEARCH.md](docs/RESEARCH.md) maps claims to the paper and records experimental limits. Google's Technical Writing lessons inform the structure and captions; direct lesson links and their application appear on the storyboard page.

## Deployment

GitHub Pages serves the `site/` directory through `.github/workflows/pages.yml`. Each push to `main` uploads only the static site, then deploys it to Pages. Enable **GitHub Actions** as the Pages source in repository settings.

## Attribution

Paper: Jianzhu Yao, Siva Kumar Sastry Hari, Vignesh Balaji, Sana Damani, Insu Jang, Pramod Viswanath, and Christos Kozyrakis. The paper is licensed CC BY 4.0. This article paraphrases it and creates new schematic illustrations; all paper-derived numerical results are attributed and are not independently reproduced here. Google Technical Writing materials are linked and paraphrased. See [LICENSE](LICENSE) for the original code and article licenses.

3Blue1Brown's matrix-multiplication and backpropagation lessons are visual/pedagogical references, linked in the article and storyboard. No reference footage is included. Prose, code, and mathematics have distinct font roles. Bundled Computer Modern Unicode font files retain their SIL Open Font License; see `site/assets/fonts/LICENSE.txt`.
