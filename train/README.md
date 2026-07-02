# Train

Training code lives here.

Planned modules:

- `loop.py`: resume-safe training loop.
- `curriculum.py`: tier scheduling with rehearsal.
- `data.py`: shard readers and batch collation.
- `rl/`: stage-2 instruction-following environment and PPO.

All randomness should flow through explicit seeded generators.
