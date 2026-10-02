# Research ledger

Primary source: Jianzhu Yao et al., [MegaFlux: Skew-Resilient MoE Megakernels via Pipelined Expert Replication](https://arxiv.org/html/2610.00671v1), arXiv:2610.00671v1, September 30, 2026. Read October 2, 2026. The paper is CC BY 4.0. All reported results below are the authors' measurements; none were rerun for this article.

## Mechanism audit

- §2: MegaMoE already overlaps token communication and FC1/FC2 using a persistent kernel. Metadata routing and the final top-k sum remain separate launches. “Megakernel” does not mean the entire model or every MoE operation is one kernel.
- §3.1: Partition each expert's rows into blocks before assignment. This leaves at most one partial block per expert across all copies. Positive q[e,r] on a non-owner consumes one replica slot, regardless of assigned block count.
- Appendix A.1: Four candidates combine two donor priorities and two fan-out rules. Move v = min(owner's remaining blocks, receiver's capacity to τ). Do NOT additionally cap v by the donor's excess. Stop after s+2 rounds or no movement; this is not an optimality/convergence proof.
- Refinement: Select minimum maximum load, tie-break by fewer replicas. Prune whole replicas onto existing copies and move individual blocks only between existing copies. Do not create replicas during refinement.
- Appendix A.2: n[r] counts remote replicas of experts OWNED by GPU r, not replicas HOSTED by r. λ = 12 is a fixed heuristic in block units, not a measured transfer-time conversion. Prune small replicas from the maximum augmented-load owner, then fall back to fixed placement unless the proxy strictly improves. Inference omits this pass.
- Training chooses the reduction-aware plan before forward and reuses it in backward. Charge planning once to forward.
- §3.2: Forward W1 and W2 readiness are separate. FC1 additionally needs an input block; FC2 needs a completed activation block. Input-transfer warps eventually join replica transfer work; a small subset starts servicing weights immediately.
- Backward DGrad consumes W2 then W1. DGrad and WGrad have different reduction axes, requiring token-axis requantization for the MXFP8 WGrad path. Workers transition independently; no device-wide DGrad/WGrad phase barrier.
- Owner gradient reduction waits for matching partial tiles from all participating GPUs. Prioritize replicated-expert gradient production across participants; owner pulls and accumulates in FP32 in a fixed order.

## Result audit

| Claim | Location | Qualification |
| --- | --- | --- |
| Real route skew adds 7.3–41.0% latency | §2.2, Figure 1 | P95-skew profiles, native OLMoE/Qwen3 shapes and checkpoint weights, BF16, EP8 B200. Balanced comparison changes expert IDs. |
| 1.45× forward, 1.28× backward geometric means; 2.14×/2.64× peaks | §4.1–4.2, Figure 3 | 147 configurations per direction, same fixed-placement megakernel baseline, 8 B200 in one NVLink domain. |
| Main grid | §4.1, Appendix B.1 | E = 64/128/256, M = 1/2/4/8/16/32/64K per rank, seven route families; 3 × 7 × 7 = 147. Dimensions 7168/2048, top-8, β = 128, 25% extra expert capacity. |
| Precisions | §4.1 | Forward MXFP4 weights + MXFP8 activations; backward MXFP8 operands; FP32 accumulation and BF16 outputs. |
| Measurement scope | §4.1 | Includes transport, expert compute, output combination, replica operations. Excludes router and shared expert. Forward includes separately measured planner latency; backward reuses plan. |
| Trace-derived grid is not full-model replay | §4.1, Appendix B.1 | Synthetic weights/activations. Histograms rebinned/rescaled, counts permuted across owners, top-k distinctness enforced. Labels source-relative. |
| Additional pipelining reductions up to 13.2%/26.7% | §4.3, Figure 4 | Same replica/block plans, relative to separate-stage replication. Not additive percentage points on the fixed-placement speedup. |
| Hidden communication 56–76% forward; ~91–100% backward | §4.3, Figure 5 | Estimated from latency differences on selected real-high cases (1/2/4/6K, E=256), not direct link utilization and not all grid cases. |
| Balanced 0.985×/0.999×; small backward as low as 0.91× | §4.2 | Honest counterexamples to “replication always helps.” |
| Planner 42.6–65.9 μs E128; 49.8–72.0 μs E256 | §4.5 | Real-high, 1K–128K per rank; main performance grid stops at 64K. |
| BF16 prior-art means | §4.4 | Forward/backward vs Megatron-Core 2.31×/1.53×; UltraEP 1.74×/2.35×; raw MoK 1.84×/1.37×. MoK does additional work; serial comparable-work estimate gives 1.70×/1.26×. Keep distinct from main low-precision grid. |
| End-to-end exact table | §4.6, Table 1 | Batch 8: 1.128×/1.133×; batch 16: 1.227×/1.238×; batch 32: 1.165×/1.260× for 16K/32K chunks. |
| End-to-end setup | §4.6 | vLLM 0.27.1, DeepSeek-V4-Pro-0813, EP8 B200, 160 LongBench-Pro prompts, 2 replica slots/rank. Batch latency until all requests have their first output token. Not steady-state decode throughput. |
| Limitations | §4.6 | One NVLink domain. Runtime profitability gate and topology-aware cross-node placement are future work. |

## Interpretation boundaries

The article's break-even inequality and Amdahl illustration are explanatory inferences, not formulas evaluated by the authors. The interactive implementation models block assignment and reduction-aware pruning from Appendix A; it omits token metadata construction, GPU kernels, measured communication costs, and the full experimental shapes. It is not a speed predictor.

No MegaFlux source-release link was identified in the paper HTML. The paper links to the [pinned CuTeDSL MegaMoE baseline](https://github.com/NVIDIA/TensorRT-LLM/tree/b5011b14415d45c2f0cfeb31cf50e2ab68377867/tensorrt_llm/_torch/cute_dsl_kernels/cutedsl_megamoe). Do not label that baseline as MegaFlux's implementation.
