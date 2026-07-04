from __future__ import annotations

import json
import math
from typing import Any

import pytest
from pydantic import ValidationError

from data.schemas import Entity, Episode, EvalItem, Event, Relation, Sample, Scene


def test_all_schema_models_round_trip_through_json() -> None:
    artifacts = [
        Entity(category="jan", color="loje", size="suli", pos=(0.25, 0.5), pose_seed=11),
        Relation(kind="poka", a=0, b=1),
        _scene(),
        Event(kind="move", agent=0, params={"to": [0.6, 0.5]}),
        _episode(),
        _sample(),
        _eval_item(),
    ]

    for artifact in artifacts:
        reloaded = type(artifact).model_validate_json(artifact.model_dump_json())
        assert reloaded == artifact


def test_scene_round_trip_preserves_contract_fields() -> None:
    scene = _scene()

    dumped = scene.model_dump(mode="json")
    reloaded = Scene.model_validate(dumped)

    assert set(dumped) == {"entities", "relations", "seed"}
    assert set(_first_entity(dumped)) == {"category", "color", "size", "pos", "pose_seed"}
    assert reloaded == scene


def test_episode_sample_and_eval_item_construct() -> None:
    episode = _episode()
    sample = _sample()
    eval_item = _eval_item()

    assert episode.events[0].kind == "move"
    assert sample.text == "jan loje li lon."
    assert eval_item.scene == _scene()


def test_eval_item_nested_json_dump_uses_contract_field_names() -> None:
    dumped = json.loads(_eval_item().model_dump_json())

    assert set(dumped) == {
        "uid",
        "eval_id",
        "prompt",
        "choices",
        "answer",
        "frames",
        "scene",
        "episode",
        "split_tags",
        "metadata",
    }
    assert dumped["scene"]["entities"][0]["pos"] == [0.25, 0.5]
    assert dumped["episode"]["events"][0]["params"] == {"to": [0.6, 0.5]}
    assert dumped["metadata"]["score_key"] == {"answer": 0}


def test_scene_rejects_relation_indices_outside_entities() -> None:
    with pytest.raises(ValidationError, match="Relation entity index out of range"):
        Scene(
            entities=[
                Entity(category="jan", color="loje", size="suli", pos=(0.5, 0.5), pose_seed=1)
            ],
            relations=[Relation(kind="poka", a=0, b=1)],
            seed=3,
        )


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        (
            {"category": "", "color": "loje", "size": "suli", "pos": (0.5, 0.5), "pose_seed": 1},
            "category",
        ),
        (
            {
                "category": "jan",
                "color": "loje",
                "size": "suli",
                "pos": (-0.1, 0.5),
                "pose_seed": 1,
            },
            "greater than or equal",
        ),
        (
            {"category": "jan", "color": "loje", "size": "suli", "pos": (0.5, 1.1), "pose_seed": 1},
            "less than or equal",
        ),
        (
            {"category": "jan", "color": "loje", "size": "suli", "pos": (0.5,), "pose_seed": 1},
            "Field required",
        ),
        (
            {
                "category": "jan",
                "color": "loje",
                "size": "suli",
                "pos": (0.5, 0.5),
                "pose_seed": -1,
            },
            "greater than or equal",
        ),
        (
            {"category": "jan", "color": "loje", "size": "suwi", "pos": (0.5, 0.5), "pose_seed": 1},
            "Input should be",
        ),
        (
            {
                "category": "jan",
                "color": "loje",
                "size": "suli",
                "pos": (0.5, 0.5),
                "pose_seed": 1,
                "extra": True,
            },
            "Extra inputs",
        ),
    ],
)
def test_entity_rejects_invalid_inputs(payload: dict[str, Any], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        Entity(**payload)


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ({"kind": "poka", "a": 0, "b": 0}, "distinct entities"),
        ({"kind": "poka", "a": -1, "b": 0}, "greater than or equal"),
        ({"kind": "weka", "a": 0, "b": 1}, "Input should be"),
        ({"kind": "poka", "a": 0, "b": 1, "extra": True}, "Extra inputs"),
    ],
)
def test_relation_rejects_invalid_inputs(payload: dict[str, Any], match: str) -> None:
    with pytest.raises(ValidationError, match=match):
        Relation(**payload)


def test_scene_rejects_entity_count_bounds() -> None:
    with pytest.raises(ValidationError, match="at least 1 item"):
        Scene(entities=[], seed=1)

    with pytest.raises(ValidationError, match="at most 6 items"):
        Scene(entities=[_entity(index) for index in range(7)], seed=1)


def test_episode_rejects_scene_count_bounds() -> None:
    with pytest.raises(ValidationError, match="at least 1 item"):
        Episode(scenes=[])

    with pytest.raises(ValidationError, match="at most 8 items"):
        Episode(scenes=[_scene(seed=index) for index in range(9)])


@pytest.mark.parametrize(
    ("model_type", "payload", "match"),
    [
        (Sample, {"uid": "", "text": "jan li lon."}, "uid"),
        (Sample, {"uid": "sample-1", "text": ""}, "text"),
        (Sample, {"uid": "sample-1", "text": "jan li lon.", "frames": [""]}, "frames"),
        (EvalItem, {"uid": "", "eval_id": "E2", "prompt": "seme?"}, "uid"),
        (EvalItem, {"uid": "eval-1", "eval_id": "", "prompt": "seme?"}, "eval_id"),
        (EvalItem, {"uid": "eval-1", "eval_id": "E2", "prompt": ""}, "prompt"),
        (
            EvalItem,
            {"uid": "eval-1", "eval_id": "E2", "prompt": "seme?", "choices": [""]},
            "choices",
        ),
    ],
)
def test_text_artifacts_reject_empty_contract_strings(
    model_type: type[Sample] | type[EvalItem],
    payload: dict[str, Any],
    match: str,
) -> None:
    with pytest.raises(ValidationError, match=match):
        model_type(**payload)


def test_event_params_reject_non_json_values() -> None:
    bad_params: dict[str, Any] = {"bad": object()}

    with pytest.raises(ValidationError):
        Event(kind="move", params=bad_params)

    with pytest.raises(ValidationError, match="valid string"):
        Event.model_validate({"kind": "move", "params": {1: "bad"}})

    with pytest.raises(ValidationError, match="finite JSON"):
        Event(kind="move", params={"bad": math.nan})

    with pytest.raises(ValidationError, match="finite JSON"):
        Event(kind="move", params={"nested": [1, {"bad": math.inf}]})


def test_eval_item_answer_and_metadata_reject_non_json_values() -> None:
    with pytest.raises(ValidationError):
        EvalItem.model_validate(
            {"uid": "eval-1", "eval_id": "E2", "prompt": "seme?", "answer": object()}
        )

    with pytest.raises(ValidationError, match="finite JSON"):
        EvalItem(uid="eval-1", eval_id="E2", prompt="seme?", answer={"bad": -math.inf})

    with pytest.raises(ValidationError):
        EvalItem.model_validate(
            {"uid": "eval-1", "eval_id": "E2", "prompt": "seme?", "metadata": {"bad": object()}}
        )


def test_event_rejects_invalid_kind_and_negative_indices() -> None:
    with pytest.raises(ValidationError, match="Input should be"):
        Event.model_validate({"kind": "listen"})

    with pytest.raises(ValidationError, match="greater than or equal"):
        Event(kind="move", agent=-1)

    with pytest.raises(ValidationError, match="greater than or equal"):
        Event(kind="transfer", patient=-1)


def _entity(index: int = 0) -> Entity:
    return Entity(
        category=f"thing-{index}",
        color="loje",
        size="suli",
        pos=(0.1 * (index % 6), 0.5),
        pose_seed=index,
    )


def _scene(seed: int = 7) -> Scene:
    return Scene(
        entities=[
            Entity(category="jan", color="loje", size="suli", pos=(0.25, 0.5), pose_seed=11),
            Entity(category="soweli", color="laso", size="lili", pos=(0.75, 0.5), pose_seed=12),
        ],
        relations=[Relation(kind="poka", a=0, b=1)],
        seed=seed,
    )


def _episode() -> Episode:
    return Episode(
        scenes=[
            _scene(),
            Scene(
                entities=[
                    Entity(category="jan", color="loje", size="suli", pos=(0.6, 0.5), pose_seed=11),
                    Entity(
                        category="soweli",
                        color="laso",
                        size="lili",
                        pos=(0.8, 0.5),
                        pose_seed=12,
                    ),
                ],
                relations=[Relation(kind="poka", a=0, b=1)],
                seed=8,
            ),
        ],
        events=[Event(kind="move", agent=0, params={"to": [0.6, 0.5]})],
    )


def _sample() -> Sample:
    return Sample(
        uid="sample-0001",
        text="jan loje li lon.",
        frames=["frames/000000.png"],
        split_tags=["train", "t0"],
    )


def _eval_item() -> EvalItem:
    return EvalItem(
        uid="eval-0001",
        eval_id="E2",
        prompt="jan li lon anu seme?",
        choices=["lon", "lon ala"],
        answer=0,
        frames=["frames/000000.png"],
        scene=_scene(),
        episode=_episode(),
        split_tags=["eval", "e2"],
        metadata={"score_key": {"answer": 0}},
    )


def _first_entity(value: dict[str, Any]) -> dict[str, Any]:
    entities = value["entities"]
    if not isinstance(entities, list):
        raise TypeError("Expected entities to dump as a list")
    first = entities[0]
    if not isinstance(first, dict):
        raise TypeError("Expected entity to dump as a dict")
    return first
