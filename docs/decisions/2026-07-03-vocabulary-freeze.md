# Vocabulary Freeze

Date: 2026-07-03

## Decision

Freeze `data/vocab.json` for the v1 experiment.

The artifact contains the 137 selected Toki Pona words from Linku `sona`, explicit token IDs for every special, punctuation, word, and reserved token, and partition tags used by the dataset builders.

Any later vocabulary, token ID, or partition change invalidates tokenizer compatibility and any checkpoints trained against this artifact.

## Review Notes

Sound and speech words are not claimed as visually grounded in v1. `kalama`, `mu`, and `toki` are deferred because the renderer has no audio channel and no committed visual convention for sound.

`kute` stays visually grounded as the ear/body-part sense, not as hearing.

`nanpa` is treated as a function/operator word for ordinal and number-marker constructions.

`ale` stays visually grounded as a set or universal quantifier over visible scene entities.

`tenpo` stays temporal because the dataset includes ordered episodes and before/after reasoning.

`kon` is deferred until the world engine defines an unambiguous air, gas, or wind convention.

`mi`, `sina`, and `ona` are intentionally deferred. They are deictic and perspective-dependent, and v1 third-person scenes do not define speaker/addressee roles.
