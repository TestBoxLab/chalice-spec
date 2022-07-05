from pydantic import BaseModel


class TestSchema(BaseModel):
    hello: str
    world: int

    __test__ = False
