# Configs

One experiment equals one YAML config. Run IDs are derived from the config hash plus seed, so completed-run config keys are append-only.

Planned base configs:

- `a_base.yaml`: `toki-taso`, text-only transformer.
- `b_base.yaml`: `toki-lukin`, transformer with visual prefix.
- `c_base.yaml`: `toki-sona`, grounded model with persistent state.

Ablations live in `ablations/`.
