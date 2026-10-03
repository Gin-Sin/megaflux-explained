# Typography and animation audit — October 3, 2026

## Explicit font roles

| Content | Videos | Website |
| --- | --- | --- |
| Explanatory prose | Lato `Text` | Self-hosted Lato, with real bold and italic faces |
| Code and pseudocode | DejaVu Sans Mono `Text` | Self-hosted DejaVu Sans Mono |
| Mathematical expressions | Manim `MathTex`, compiled by LaTeX | Pre-rendered KaTeX HTML and accessible MathML |
| Editorial titles | Computer Modern Serif | Editorial serif heading stack |

Routing and backward contain no code snippets, so they do not introduce a code face unnecessarily. Mathematical expert IDs, loads, weight symbols, gradient partials, and matrices are TeX objects. The forward readiness statements are executable-style pseudocode and use monospace. The renderer rejects missing required fonts instead of silently falling back.

The website typesets the planner objective and constraints, skew statistic, projection equations, backward products, reduction proxy, and inline symbols. Semantic math is available without JavaScript. Long expressions scroll within their own keyboard-focusable container instead of overflowing the page.

## Reference-to-motion mapping

References: 3Blue1Brown's [matrix multiplication lesson](https://www.3blue1brown.com/lessons/matrix-multiplication/) and [backpropagation lesson](https://www.3blue1brown.com/lessons/backpropagation/). The associativity and weight-nudging clips were inspected as sequences of frames. No reference footage is republished.

- **Identity survives motion.** The same amber blocks travel to new GPUs; weight badges copy, while work blocks move.
- **Symbols carry meaning into a new representation.** Weight symbols and projection labels become timeline stages; copies of those stages move into their pipeline lanes.
- **Motion explains concurrency.** The second weight transfer and first projection fill together, with a shared cursor and temporary outline.
- **Focus follows the dependency.** The overloaded queue, first readiness gate, and last missing gradient partial receive temporary emphasis.
- **A visible cause changes a visible result.** Counts update as blocks arrive; the gradient accumulator changes as each contribution arrives.
- **Reading holds separate ideas.** Pauses follow the initial model, readiness events, and final results.

All timeline widths, block counts, and 2×2 gradient values are schematic. The original paper is the source of the dependency rules; it is not the source of these toy measurements or illustrations.

## Verification

The final review follows the `create-manim-animations` skill's film/design and validation/publishing guides: preserve object identity and invariants, inspect intermediate frames, keep literal code indentation, derive checkpoints from renderer time, and validate the encoded and deployed artifacts. The skill review prompted two corrections: the maximum-load equation now updates on every transfer, and pseudocode retains its four-column indentation after Manim aligns the text objects. These are silent illustrations with nearby HTML transcripts; no speech or audio pipeline is used.

- `scripts/review_frames.py` extracts reading holds and transition interiors for all three scenes. Contact sheets and full-size source frames are kept under ignored `test-results/`.
- `tests/animation_audit.py` probes the actual MP4 streams and checks font roles, scene checkpoints, and frame boundaries against `site/assets/animation-audit.json`.
- `tests/typography.py` uses Chromium's `CSS.getPlatformFontsForNode` to identify the fonts that actually drew prose, code, and math. It checks expanded disclosures, 320/390/768/1440 px viewports, 200% zoom, and no-JavaScript MathML.
- `tests/browser.py` checks keyboard interaction, video decoding, internal links, browser errors, and responsive layout.

The browser font report identifies **Lato-Regular**, **DejaVuSansMono**, and **KaTeX_Math-Italic** as loaded custom fonts. Visual inspection covers both resting layouts and moving states; a font-family declaration or a final poster alone is insufficient evidence.
