"""Pydantic JSON contracts shared across data, training, eval, and serving."""

from __future__ import annotations

import math
from typing import Annotated, Any, Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

type Color = Literal["loje", "laso", "jelo", "walo", "pimeja"]
type Size = Literal["suli", "lili"]
type RelationKind = Literal["lon", "insa", "poka", "sewi", "anpa", "monsi", "sinpin"]
type EventKind = Literal["move", "transfer", "ingest", "fall", "contain", "destroy"]

COLORS: Final[tuple[str, ...]] = ("loje", "laso", "jelo", "walo", "pimeja")
SIZES: Final[tuple[str, ...]] = ("suli", "lili")
RELATION_KINDS: Final[tuple[str, ...]] = (
    "lon",
    "insa",
    "poka",
    "sewi",
    "anpa",
    "monsi",
    "sinpin",
)
EVENT_KINDS: Final[tuple[str, ...]] = (
    "move",
    "transfer",
    "ingest",
    "fall",
    "contain",
    "destroy",
)

type JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
NonEmptyStr = Annotated[str, Field(min_length=1)]
NonNegativeInt = Annotated[int, Field(ge=0)]
UnitFloat = Annotated[float, Field(ge=0.0, le=1.0)]
type Position = tuple[UnitFloat, UnitFloat]


class SchemaModel(BaseModel):
    """Base model for project artifact contracts."""

    model_config = ConfigDict(extra="forbid")


class Entity(SchemaModel):
    category: NonEmptyStr
    color: Color
    size: Size
    pos: Position
    pose_seed: NonNegativeInt


class Relation(SchemaModel):
    kind: RelationKind
    a: NonNegativeInt
    b: NonNegativeInt

    @model_validator(mode="after")
    def _validate_distinct_endpoints(self) -> Self:
        if self.a == self.b:
            raise ValueError("Relation endpoints must refer to distinct entities")
        return self


class Scene(SchemaModel):
    entities: list[Entity] = Field(min_length=1, max_length=6)
    relations: list[Relation] = Field(default_factory=list)
    seed: NonNegativeInt

    @model_validator(mode="after")
    def _validate_relation_indices(self) -> Self:
        entity_count = len(self.entities)
        for relation in self.relations:
            if relation.a >= entity_count or relation.b >= entity_count:
                raise ValueError("Relation entity index out of range")
        return self


class Event(SchemaModel):
    kind: EventKind
    agent: NonNegativeInt | None = None
    patient: NonNegativeInt | None = None
    params: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("params")
    @classmethod
    def _validate_params(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        _validate_json_value(value, "params")
        return value


class Episode(SchemaModel):
    scenes: list[Scene] = Field(min_length=1, max_length=8)
    events: list[Event] = Field(default_factory=list)


class Sample(SchemaModel):
    uid: NonEmptyStr
    text: NonEmptyStr
    frames: list[NonEmptyStr] = Field(default_factory=list)
    split_tags: list[NonEmptyStr] = Field(default_factory=list)


class EvalItem(SchemaModel):
    uid: NonEmptyStr
    eval_id: NonEmptyStr
    prompt: NonEmptyStr
    choices: list[NonEmptyStr] = Field(default_factory=list)
    answer: JsonValue = None
    frames: list[NonEmptyStr] = Field(default_factory=list)
    scene: Scene | None = None
    episode: Episode | None = None
    split_tags: list[NonEmptyStr] = Field(default_factory=list)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)

    @field_validator("answer")
    @classmethod
    def _validate_answer(cls, value: JsonValue) -> JsonValue:
        _validate_json_value(value, "answer")
        return value

    @field_validator("metadata")
    @classmethod
    def _validate_metadata(cls, value: dict[str, JsonValue]) -> dict[str, JsonValue]:
        _validate_json_value(value, "metadata")
        return value


def _validate_json_value(value: JsonValue, field_path: str) -> None:
    if value is None or isinstance(value, bool | int | str):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field_path} must contain only finite JSON numbers")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{field_path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{field_path} must contain only string object keys")
            _validate_json_value(item, f"{field_path}.{key}")
        return
    raise ValueError(f"{field_path} contains a non-JSON value")


__all__ = (
    "COLORS",
    "EVENT_KINDS",
    "RELATION_KINDS",
    "SIZES",
    "Color",
    "Entity",
    "Episode",
    "EvalItem",
    "Event",
    "EventKind",
    "JsonValue",
    "Position",
    "Relation",
    "RelationKind",
    "Sample",
    "Scene",
    "Size",
)
