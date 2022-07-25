from pydantic import BaseModel


class TestSchema(BaseModel):
    hello: str
    world: int

    __test__ = False


class AnotherSchema(BaseModel):
    nintendo: str
    atari: str

    __test__ = False


class MoreDeeplyNestedSchema(BaseModel):
    base_type: str


class DeeplyNestedSchema(BaseModel):
    more_deeply: MoreDeeplyNestedSchema


class NestedSchema(BaseModel):
    hello: str
    deeply: DeeplyNestedSchema
