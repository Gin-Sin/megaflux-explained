# Editorial plan and storyboard

## Reader contract

Audience: an ML engineer familiar with transformer inference, matrix multiplication, and basic backpropagation. Explain expert parallelism, persistent kernels, tile readiness, and gradient reduction before relying on them. Keep the main path conceptual; put gradient algebra and planner details in expandable sections.

Reader outcome: explain why a well-pipelined MoE kernel can still have GPU stragglers; work through a valid token-block placement; identify the exact forward and backward dependencies that allow overlap; and distinguish layer speedups from end-to-end gains.

Scope: the design and evidence in arXiv:2610.00671v1, submitted September 30, 2026. The interactive model teaches the planner. It does not implement the CUDA executor, predict wall-clock latency, reproduce the experiments, or cover cross-node deployment.

Thesis: move some of a hot expert's blocks to spare GPUs, then bring the added weight and gradient communication inside the persistent execution schedule.

## Google Technical Writing applied

| Lesson | Concrete editorial decision |
| --- | --- |
| [Audience](https://developers.google.com/tech-writing/one/audience) | State prerequisites; define MoE-specific terms; separate optional math from the main story. |
| [Documents](https://developers.google.com/tech-writing/one/documents) | Lead with the central result, give scope and learning goals, organize around reader questions. |
| [Paragraphs](https://developers.google.com/tech-writing/one/paragraphs) | Start each paragraph with its technical point and develop one idea at a time. |
| [Clear sentences](https://developers.google.com/tech-writing/one/clear-sentences) | Use named actors and concrete verbs: the planner assigns, loaders wait, owners accumulate. Qualify every performance number. |
| [Illustrating](https://developers.google.com/tech-writing/two/illustrations) | Write each takeaway caption first, show one mechanism per scene, use consistent labels, add equivalent text, review readability. |

## Typography and visual reference

Use Lato for prose and explanatory labels, DejaVu Sans Mono for code, and actual TeX typesetting for every mathematical expression. Video titles use Computer Modern Serif. The website pre-renders KaTeX HTML plus MathML and self-hosts its fonts; fractions, operator limits, matrices, and superscripts therefore remain typeset even with JavaScript disabled. Distinct CSS font-family declarations alone do not count as a typography check: inspect the loaded fonts and rendered glyphs.

Visual references: 3Blue1Brown's [Matrix multiplication as composition](https://www.3blue1brown.com/lessons/matrix-multiplication/) (including its associativity clip) and [What is backpropagation really doing?](https://www.3blue1brown.com/lessons/backpropagation/) (including its weight-nudging clip). Reference footage is inspected locally, not republished. Apply these concrete patterns:

| Reference pattern | Original MegaFlux application |
| --- | --- |
| Carry a mathematical object through a change of representation | Forward weight symbols become schedule labels, then the same labeled stages move into separate lanes. |
| Keep color attached to meaning | Amber identifies the hot expert/weights; each gradient contributor keeps its color in the sum. Labels reinforce color. |
| Move an existing object instead of replacing a whole frame | Routing blocks follow visible paths to their new GPU; the total stays on screen. |
| Draw attention to the currently relevant dependency | An outline isolates the busy queue, the first readiness gate, or the last missing gradient partial. |
| Make change in one quantity visibly affect another | GPU counts update when blocks arrive; the accumulator updates when a contribution arrives. |
| Pause after a conceptual change | Reading holds follow setup, readiness, and the final equation. |

The scenes are independently authored, with no copied characters or footage. Actual `MathTex` objects render all mathematical video labels. Code appears only where useful (the forward readiness rule); the other scenes do not introduce artificial code panels.

## Article skeleton

| Beat | Reader question | Explanation and evidence | Transition |
| --- | --- | --- | --- |
| Opening | What is the central idea? | A busy expert creates a straggler; replicate work and pipeline the cost. Define the three learning goals. | First identify what is already optimized. |
| 1. The straggler | Why does a fused kernel still stall? | Expert ownership, dispatch/compute/return, layer latency as the slowest rank. Toy loads 12/4/4/4. Paper §2. | Moving tokens requires the destination to hold the expert weights. |
| 2. The plan | What may move, and what must remain fixed? | Keep expert IDs, weights, routing weights, and token identities. Partition once into blocks, assign under replica limits. Interactive model. §3.1, Appendix A. | A good assignment creates communication obligations. |
| 3. Forward | When may a replica start? | FC1 needs W1 and input; FC2 needs W2 and activation. Reuse communication warps. §3.2. | Training adds gradients that must return to owners. |
| 4. Backward | Why does one early partial not suffice? | DGrad before WGrad dependencies; all contributors must publish a matching tile. Coordinate replicated-expert priority. §3.2, Appendix A.2. | A plausible mechanism still needs a controlled evaluation. |
| 5. Evidence | What do the reported speedups measure? | Separate same-kernel low-precision grid, same-plan ablations, BF16 prior-art comparison, and vLLM prefill. §4, Table 1, Appendix B. | Identify where the benefits stop. |
| 6. Judgment | When would this be worth implementing? | Skew, spare capacity, work volume, topology, and exposed replication cost. No automatic gate in the evaluated design. §4.6. | Use retrieval questions to test understanding. |
| Closing | Can I reconstruct the design? | Five revealable questions, compact glossary, paper and writing references. | Return to the paper with a dependency-first reading map. |

## Storyboard: original Manim illustrations

All time widths are schematic. The dark background, amber work blocks, teal progress, and violet gradient tiles remain consistent. Color is reinforced by labels. Use native video controls, no autoplay, PNG posters, HTML transcripts, and text explanations.

### Scene 1 — `RoutingSkew` (~23 seconds)

Caption: **Redistributing the same expert's blocks shortens the busiest queue.**

1. Establish four GPU lanes and their expert identities with separate prose and TeX labels. Reveal 12/4/4/4 blocks, the maximum-load equation, and the conserved total of 24.
2. Outline the busy queue and emphasize the maximum. Pause before introducing the solution.
3. Copy the hot expert's weight badge into three spare slots, with the original work blocks held in place. A replica duplicates parameters.
4. Highlight and move the original amber blocks along continuous paths, two per receiver. Update donor and receiver counts and the maximum on each arrival: 12 → 10 → 8 → 6. A work assignment moves rather than duplicates.
5. Emphasize the final maximum of 6 and the unchanged sum of 24. Hold on the completed diagram.

Source: §§2–3.1. Four GPUs simplify the eight-GPU paper setup. Counts model equal-cost blocks; they do not establish a measured 2× speedup.

### Scene 2 — `ForwardPipeline` (~27 seconds)

Caption: **FC1 can begin after its weights arrive while the next projection's weights are still moving.**

1. Write the two projection equations and activation in TeX. Color the weight symbols consistently and identify FC1/FC2 in monospace.
2. Carry the weight symbols and operation labels into a separate-stage schedule, retaining identity across representations.
3. Copy the same stages into transfer and compute lanes. Dim the baseline to preserve context without competing for attention.
4. Move a time cursor with the first weight-transfer fill. Highlight the completed transfer and the available input. Show the readiness rule in a code font.
5. Grow the second weight transfer and FC1 computation concurrently, not as unrelated fade-ins. Mark their common interval.
6. Update the monospace condition only when the second weights and activation exist, then grow FC2. End on the dependency rule.

Source: §3.2. Input is assumed ready. Durations and widths are schematic. The prose, code, and TeX font roles are visually distinct.

### Scene 3 — `BackwardReduction` (~23 seconds)

Caption: **Reduce a gradient tile when every participating copy has produced its partial.**

1. Establish owner, replica A, and replica B with colored TeX partial-gradient symbols. Write their sum before evaluating it.
2. Reveal two illustrative 2×2 partial matrices and mark them ready. Keep replica B pending; outline it as the last prerequisite.
3. Reveal B's partial and emphasize its matching term in the sum. Only now expose the owner accumulator.
4. Move copies of the three partials into the accumulator in a fixed order. Its displayed values become [[1,2],[0,1]], [[1,3],[3,1]], then [[3,3],[4,2]].
5. Grow later-tile progress bars during these contribution transfers and additions. Hold on the completed sum and overlapping work.

Source: §3.2. The 2×2 values are invented teaching examples. They illustrate gradient addition, not GPU measurements or the paper's parameter dimensions. Fixed-order accumulation and overlap are the paper's mechanisms.

## Interactive and data storyboard

The planner uses four GPUs and four home experts, with adjustable E0 block count and replica budget. Show before/after per-GPU loads, expert identities inside the after bars, the average-load lower bound, total conservation, maximum load, and replica count. A training mode applies the paper's reduction-aware pruning with <math-inline>\lambda=12</math-inline>. Label outputs as a block-load model, never as predicted latency. Provide a reset control and live textual results.

The evidence panel shows geometric means and maxima as separate, labeled quantities. A semantic table contains the six exact end-to-end speedups from Table 1. An optional Amdahl calculation is explicitly an illustrative inference. Never generate a dense experimental curve from sparse headline values.

## Review gates

- Every result names its baseline, precision, workload, and measurement scope.
- No schematic is described as a benchmark or an exact GPU schedule.
- Each numeric paper claim links to a section or table.
- The toy planner conserves blocks, uses integer assignments, and respects replica capacity.
- The article distinguishes the exact mathematical objective, the bounded heuristic, and a latency predictor.
- Check reading holds and transition interiors in all three videos; reject text outside the frame.
- Check actual loaded prose/code/math fonts, all expanded equations, 320–1440 px widths, 200% zoom, and no-JavaScript math.
- Mobile and desktop layouts, video playback, keyboard controls, and all internal links work.
- Publication uploads only this repository's static site and original content.
