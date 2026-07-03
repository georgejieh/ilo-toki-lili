from __future__ import annotations

import math
from typing import Any

import pytest
from pydantic import ValidationError

from data.schemas import Entity, Episode, EvalItem, Event, Relation, Sample, Scene


def test_scene_round_trip_preserves_contract_fields() -> None:
    scene = _scene()

    dumped = scene.model_dump(mode="json")
    reloaded = Scene.model_validate(dumped)

    assert set(dumped) == {"entities", "relations", "seed"}
    assert set(_first_entity(dumped)) == {"category", "color", "size", "pos", "pose_seed"}
    assert reloaded == scene


def test_episode_sample_and_eval_item_construct() -> None:
    start = _scene()
    end = Scene(
        entities=[
            Entity(category="jan", color="loje", size="suli", pos=(0.6, 0.5), pose_seed=11),
            Entity(category="soweli", color="laso", size="lili", pos=(0.8, 0.5), pose_seed=12),
        ],
        relations=[Relation(kind="poka", a=0, b=1)],
        seed=8,
    )
    episode = Episode(
        scenes=[start, end],
        events=[Event(kind="move", agent=0, params={"to": [0.6, 0.5]})],
    )
    sample = Sample(
        uid="sample-0001",
        text="jan loje li lon.",
        frames=["frames/000000.png"],
        split_tags=["train", "t0"],
    )
    eval_item = EvalItem(
        uid="eval-0001",
        eval_id="E2",
        prompt="jan li lon anu seme?",
        choices=["lon", "lon ala"],
        answer=0,
        frames=["frames/000000.png"],
        scene=start,
        episode=episode,
        split_tags=["eval", "e2"],
        metadata={"score_key": {"answer": 0}},
    )

    assert episode.events[0].kind == "move"
    assert sample.text == "jan loje li lon."
    assert eval_item.scene == start


def test_scene_rejects_relation_indices_outside_entities() -> None:
    with pytest.raises(ValidationError, match="Relation entity index out of range"):
        Scene(
            entities=[
                Entity(category="jan", color="loje", size="suli", pos=(0.5, 0.5), pose_seed=1)
            ],
            relations=[Relation(kind="poka", a=0, b=1)],
            seed=3,
        )


def test_event_params_reject_non_json_values() -> None:
    bad_params: dict[str, Any] = {"bad": object()}

    with pytest.raises(ValidationError):
        Event(kind="move", params=bad_params)

    with pytest.raises(ValidationError, match="finite JSON"):
        Event(kind="move", params={"bad": math.nan})


def _scene() -> Scene:
    return Scene(
        entities=[
            Entity(category="jan", color="loje", size="suli", pos=(0.25, 0.5), pose_seed=11),
            Entity(category="soweli", color="laso", size="lili", pos=(0.75, 0.5), pose_seed=12),
        ],
        relations=[Relation(kind="poka", a=0, b=1)],
        seed=7,
    )


def _first_entity(value: dict[str, Any]) -> dict[str, Any]:
    entities = value["entities"]
    if not isinstance(entities, list):
        raise TypeError("Expected entities to dump as a list")
    first = entities[0]
    if not isinstance(first, dict):
        raise TypeError("Expected entity to dump as a dict")
    return first
