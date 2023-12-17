from chalice_spec import ChaliceWithSpec, PydanticPlugin
from apispec import APISpec
from chalice_spec.docs import Docs, Operation
from chalice_spec.runtime import APIRuntimeBedrockAgent
from chalice import BadRequestError
from chalicelib.data_type import (
    TalkResponse,
    TalkInput,
    SellOrderResponse,
    SellOrderInput,
    PurchaseOrderResponse,
    PurchaseOrderInput,
)
from random import randint
import json

spec = APISpec(
    title="Purchase Sample Schema",
    openapi_version="3.0.1",
    version="0.1.0",
    plugins=[PydanticPlugin()],
)
app = ChaliceWithSpec(
    app_name="app_sample_purchase_api", spec=spec, runtime=APIRuntimeBedrockAgent
)


@app.route(
    "/talk",
    methods=["POST"],
    docs=Docs(
        post=Operation(
            request=TalkInput,
            response=TalkResponse,
        )
    ),
)
def talk_to_shop():
    """
    Talk with Shopkeeper.

    Shopkeeper response welcome message.
    """
    # 200: OK
    return TalkResponse(
        message="Welcome. If you're after weapons or armour, you've come to the right place. What can I do for you?"
    ).json()


@app.route(
    "/purchase",
    methods=["POST"],
    docs=Docs(
        post=Operation(
            request=PurchaseOrderInput,
            response=PurchaseOrderResponse,
        )
    ),
)
def purchase():
    """
    Purchase from Shopkeeper.

    Pass the name and price of the item you want to purchase.
    """
    try:
        input = PurchaseOrderInput.parse_obj(app.current_request.json_body)
    except Exception as e:
        # 400: Bad Request, Response
        raise BadRequestError(e)
    # 200: But, money is not enough to purchase.
    if input.price < 100:
        return PurchaseOrderResponse(
            message=f"{input.price} gold? Sorry, I'm not interested in things like that."
        ).json()
    # 200: OK
    return PurchaseOrderResponse(
        message=f"Who's going to carry {input.name}? Do you want to equip your purchase now?"
    ).json()


@app.route(
    "/sell",
    methods=["POST"],
    docs=Docs(
        post=Operation(
            request=SellOrderInput,
            response=SellOrderResponse,
        )
    ),
)
def sell():
    """
    Sell to Shopkeeper.

    Pass the name of the item you want to sell.
    """
    try:
        input = SellOrderInput.parse_obj(app.current_request.json_body)
    except Exception as e:
        # 400: Bad Request, Response
        raise BadRequestError(e)
    price = randint(100, 9999)
    # 200: OK
    return SellOrderResponse(
        price=price,
        message=f"Who wants to sell something? {input.name}? I'll give you {price} gold coins. Does that sound fair?",
    ).json()


if __name__ == "__main__":
    print(json.dumps(spec.to_dict(), indent=2))
