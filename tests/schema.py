from pydantic import BaseModel


class TestSchema(BaseModel):
    hello: str
    world: int

    __test__ = False


class AnotherSchema(BaseModel):
    nintendo: str
    atari: str

    __test__ = False
