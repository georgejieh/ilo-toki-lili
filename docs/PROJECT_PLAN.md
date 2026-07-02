# Project Plan

ilo toki lili is a controlled comparison of three small Toki Pona language models:

1. `toki-taso`: a text-only transformer baseline.
2. `toki-lukin`: the same transformer family with visual grounding.
3. `toki-sona`: a grounded architecture with object slots and persistent state.

The project tests whether grounding and persistent state improve systematic behavior under a small, auditable language and dataset.

## Non-Negotiable Research Rules

- Model-visible text stays within the frozen Toki Pona vocabulary, punctuation, and special tokens.
- All model weights initialize from scratch.
- Holdouts are locked before training and enforced by linters.
- The three model families stay within the same parameter budget.
- The text stream is identical across models, with images added only for grounded variants.
- Result tables are generated from evaluation artifacts, not edited by hand.
- Model-specific tuning budgets are capped equally and tracked through committed configs.
- Public demo feedback is follow-up material only; it does not enter v1 training or frozen evaluation evidence.

## Phases

0. Foundations: dependencies, vocabulary, tokenizer, schemas, CI, contamination checks.
1. World engine: scene sampling, sprites, rendering, physics, review.
2. Language engine: grammar, parser, generated descriptions, holdouts.
3. Dataset v1: tiered corpus, shard writer, statistics, review.
4. Model A: text baseline, training loop, tuning-budget decision, core evals.
5. Model B: multimodal transformer, grounded evals.
6. Model C: slots, recurrent state, latent prediction, full eval matrix.
7. Final science runs: frozen evals, seeds, ablations, confidence intervals, domain-shift robustness.
8. Stage-2 reinforcement learning: grounded instruction following.
9. Writeup and release: paper, dataset card, model cards, reproducible reports.
10. Public demo: side-by-side model testing, scene explorer, anomaly playback, blind arena feedback.

## Deliverables

- Grounded dataset with registered holdouts.
- Three trained model families plus ablations.
- Evaluation suite and generated reports.
- Public paper or technical report.
- Web app for interactive comparison and post-publication arena feedback.
