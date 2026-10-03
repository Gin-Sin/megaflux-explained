# MegaFlux, explained

A visual teaching article about **MegaFlux: Skew-Resilient MoE Megakernels via Pipelined Expert Replication**, Jianzhu Yao et al., [arXiv:2610.00671v1](https://arxiv.org/html/2610.00671v1), September 30, 2026.

The site combines a technical article, an interactive block-assignment model, three original Manim animations, a benchmark reading guide, and a public editorial storyboard. It targets ML engineers who know matrix multiplication and transformer inference. It is an independent explanation, not an author implementation or a benchmark reproduction.

## Read and run

- Published site: https://gin-sin.github.io/megaflux-explained/
- Storyboard: https://gin-sin.github.io/megaflux-explained/storyboard.html
- Serve locally: `python3 -m http.server 8080 --directory site`
- Open http://localhost:8080

All runtime resources are local. The committed `site/` directory runs without a build step, API key, or external CDN. JavaScript adds the planner and navigation; the article, typeset equations, figures, tables, and transcripts remain readable without it.

## Edit the article and typeset equations

Edit `content/article.html`, using `<math-inline>` or `<math-block>` for TeX expressions. KaTeX generates static HTML plus accessible MathML. Its CSS and fonts are copied into the site; no browser-side math renderer is required.

```sh
npm ci
npm run build
```

The storyboard source is `docs/ARTICLE_PLAN.md`. Regenerate `content/storyboard.html` with `.venv/bin/python scripts/build_storyboard.py`, then run `npm run build`. Do not edit the generated `site/index.html` or `site/storyboard.html` directly.

## Reproduce the illustrations

Python 3.12, FFmpeg, Cairo, Pango, development headers, LaTeX, `dvisvgm`, and the CMU, Lato, and DejaVu font families are required. On Debian/Ubuntu, the additional typography packages include `fonts-cmu`, `fonts-lato`, `fonts-dejavu-core`, `texlive-latex-extra`, and `dvisvgm`. Rendering fails if a required prose/code/title font is missing. See [Manim installation instructions](https://docs.manim.community/en/stable/installation/uv.html).

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/render.py
.venv/bin/python scripts/build_storyboard.py
npm run build
```

`animations/scenes.py` contains three Manim Community scenes. `scripts/render.py` renders 1920 × 1080, 30 fps MP4 files and extracts PNG posters into `site/assets/`. Use `--draft` for 480p review copies that do not replace site assets. `scripts/review_frames.py` extracts reading holds and transition samples; pass `--draft` to inspect draft videos. Timelines, block counts, and the 2×2 gradient values are explicitly schematic, not GPU measurements. Every video has a nearby HTML transcript.

## Validate

```sh
npm test
python3 -m http.server 8080 --directory site
# In another terminal, with Chromium installed for Playwright:
.venv/bin/python tests/browser.py http://localhost:8080
.venv/bin/python tests/typography.py http://localhost:8080
.venv/bin/python tests/animation_audit.py
```

Planner tests check conservation, integer block assignments, replica limits, refinement, and the owner-side reduction proxy. Browser checks cover desktop/mobile overflow, local links/assets, keyboard controls, interactive values, video decoding, and browser errors. Typography checks query Chromium for the fonts actually used to draw the glyphs, expand every math disclosure, check 320–1440 px widths and 200% zoom, and check no-JavaScript rendering. Video audit checks inspect the rendered streams and per-scene font/geometry records. `test-results/` is local only.

## Editorial sources

[docs/ARTICLE_PLAN.md](docs/ARTICLE_PLAN.md) records the audience, learning objectives, article skeleton, and shot-by-shot storyboard. [docs/RESEARCH.md](docs/RESEARCH.md) maps claims to the paper and records experimental limits. Google's Technical Writing lessons inform the structure and captions; direct lesson links and their application appear on the storyboard page.

## Deployment

GitHub Pages serves the `site/` directory through `.github/workflows/pages.yml`. Each push to `main` typesets the article, runs planner tests, uploads only the static site, then deploys it to Pages. Manim videos are rendered locally and committed. Enable **GitHub Actions** as the Pages source in repository settings.

## Attribution

Paper: Jianzhu Yao, Siva Kumar Sastry Hari, Vignesh Balaji, Sana Damani, Insu Jang, Pramod Viswanath, and Christos Kozyrakis. The paper is licensed CC BY 4.0. This article paraphrases it and creates new schematic illustrations; all paper-derived numerical results are attributed and are not independently reproduced here. Google Technical Writing materials are linked and paraphrased. See [LICENSE](LICENSE) for the original code and article licenses.

3Blue1Brown's matrix-multiplication and backpropagation lessons are visual/pedagogical references, linked in the article and storyboard. No reference footage is included. [docs/VISUAL_AUDIT.md](docs/VISUAL_AUDIT.md) records the typography and motion design. Font licenses accompany the self-hosted assets. KaTeX's license is in `site/assets/katex/LICENSE`.
