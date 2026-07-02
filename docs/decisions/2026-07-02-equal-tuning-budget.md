# Equal Tuning Budget

Date: 2026-07-02

Decision: adopt an equal tuning-budget rule for `toki-taso`, `toki-lukin`, and `toki-sona`.

The exact per-model cap is not fixed yet. It must be recorded in a later dated decision before the first real `toki-taso` training run. Until then, the planning default is 20 model-specific dev configs per model.

Shared defaults inherited by all three models do not count against any one model. Model-specific deviations do count, including loss-weight tuning and slot-collapse fallback attempts for `toki-sona`.

Consequence: a headline comparison is not reportable if one model receives materially more tuning than another.
