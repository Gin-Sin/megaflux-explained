"""Publish the editorial source as a browsable static companion page."""
from pathlib import Path
import re
from markdown_it import MarkdownIt

root = Path(__file__).resolve().parents[1]
source = (root / "docs/ARTICLE_PLAN.md").read_text()
source = source.split("\n", 1)[1]
body = MarkdownIt("commonmark").enable("table").render(source)
body = body.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
for index, slug in enumerate(["routing-skew", "forward-pipeline", "backward-reduction"], 1):
    pattern = rf'(<h3>Scene {index}.*?</h3>)'
    body = re.sub(pattern, rf'\1<figure><img src="assets/{slug}.png" alt="Final frame of Manim scene {index}; described in the storyboard below" style="width:100%;border-radius:8px;margin:20px 0" loading="lazy"></figure>', body)
page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="The audience, learning objectives, complete skeleton, and Manim storyboard behind MegaFlux, explained, informed by Google Technical Writing.">
<title>The editorial storyboard — MegaFlux, explained</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#storyboard">Skip to storyboard</a>
<header class="site-header"><a class="wordmark" href="./"><span class="brand-symbol" aria-hidden="true">m<span>f</span></span> SYSTEMS / EXPLAINED</a><nav aria-label="Site"><a href="./">Article</a><a href="https://arxiv.org/html/2610.00671v1">Paper ↗</a><a href="https://github.com/Gin-Sin/megaflux-explained">Source ↗</a></nav></header>
<main class="story-main" id="storyboard"><p class="eyebrow">BEHIND THE ARTICLE / EDITORIAL DESIGN</p><h1>How this article<br><em>teaches the paper.</em></h1>
<p class="lead">The complete skeleton and visual storyboard, from the reader’s prerequisites to the last gradient partial.</p>
<p>Google’s Technical Writing guidance shapes the order, wording, and illustrations. This page makes those choices inspectable. <a href="./">Read the finished article →</a></p>
'''+body+'''</main><footer class="site-footer"><a class="wordmark" href="./">SYSTEMS / EXPLAINED</a><p>Independent explanation of arXiv:2610.00671v1.<br>Original scenes rendered with Manim Community.</p><nav aria-label="Footer"><a href="./">Read the article</a><a href="https://github.com/Gin-Sin/megaflux-explained/blob/main/docs/ARTICLE_PLAN.md">Editable source ↗</a></nav></footer></body></html>'''
(root / "site/storyboard.html").write_text(page)
print("Built site/storyboard.html")
