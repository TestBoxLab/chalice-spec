from pydantic import BaseModel, Field


class PurchaseOrderInput(BaseModel):
    """
    Purchase information, purchase from Shopkeeper.
    """

    name: str = Field(min_length=1, max_length=10, description="Name of purchase item")
    price: int = Field(ge=1, description="Price of purchase item, unit is gold")


class PurchaseOrderResponse(BaseModel):
    """
    Purchase response from Shopkeeper.
    """

    message: str = Field(description="Message from Shopkeeper")


class SellOrderInput(BaseModel):
    """
    Sell information, sell to Shopkeeper.
    """

    name: str = Field(min_length=1, max_length=10, description="Name of sell item")


class SellOrderResponse(BaseModel):
    """
    Sell response from Shopkeeper.
    """

    message: str = Field(description="Message from Shopkeeper")
    price: int = Field(description="Price of sell item, unit is gold")


class TalkInput(BaseModel):
    """
    Talk information, talk to Shopkeeper.
    """

    pass


class TalkResponse(BaseModel):
    """
    Talk response from Shopkeeper.
    """

    message: str = Field(description="Message from Shopkeeper")
