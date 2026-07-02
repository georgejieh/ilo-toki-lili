# Configs

One experiment equals one YAML config. Run IDs are derived from the config hash plus seed, so completed-run config keys are append-only.

Model-specific tuning attempts are part of the experimental record. Before the first baseline training run, a dated decision must fix the per-model tuning cap. Every counted attempt should be a committed YAML config with a matching tracked run, while shared defaults inherited by all models count against no one.

Planned base configs:

- `a_base.yaml`: `toki-taso`, text-only transformer.
- `b_base.yaml`: `toki-lukin`, transformer with visual prefix.
- `c_base.yaml`: `toki-sona`, grounded model with persistent state.

Ablations live in `ablations/`.
