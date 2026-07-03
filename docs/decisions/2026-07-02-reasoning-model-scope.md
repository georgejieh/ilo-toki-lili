# Reasoning Model Scope

Date: 2026-07-02

## Decision

The v1 comparison does not train or evaluate the models as explicit chain-of-thought or scratchpad reasoning models.

`toki-sona` may use additional latent computation through object slots, recurrent world state, and latent prediction losses. That is part of the architecture being tested. It should not be described as a verbal scratchpad model, and v1 training should not add hidden or visible step-by-step reasoning text.

Phase 8 reinforcement learning remains in scope as grounded instruction following with verifiable task and action rewards. It is not a license to add free-form chain-of-thought supervision.

## Rationale

The main experiment needs parity across models. Adding scratchpad traces to only one model, or giving one model extra verbal inference tokens, would blur the comparison between text-only learning, visual grounding, and persistent latent state.

Scratchpad training would also create a new data source and tuning surface, which puts pressure on the equal tuning-budget rule.

## Follow-Up

A later product or research surface may test verbal scratchpads, wrapper-style extended reasoning, council sampling, or vetted-source retrieval around `toki-sona`. Those experiments must stay separate from frozen v1 training, evaluation artifacts, and headline claims.
