# chalice-api

[![Python package](https://github.com/TestBoxLab/chalice-api/actions/workflows/test.yml/badge.svg)](https://github.com/TestBoxLab/chalice-api/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Chalice x APISpec x Pydantic plug-ins**

Combines the power of Chalice, APISpec, and Pydantic to make AWS Chalice apps easily documented

## Installation

First, add chalice-api:

```shell
poetry add chalice_api
```

We consider Chalice, APISpec, and Pydantic "peer dependencies." We only include them as dev
dependencies in our codebase, and you may need to install them in yours if you haven't
already.

```shell
poetry add chalice apispec pydantic
```

## Setup

First, instantiate your APISpec object with *both* the Pydantic and Chalice plug-ins, assuming
you need the functionality of each. While the Pydantic plugin can be used alone, you currently must use
the Pydantic plugin with the Chalice plugin.

```python
app = Chalice(app_name="hello_world")
spec = APISpec(chalice_app=app,
               ...,
               plugins=[PydanticPlugin(), ChalicePlugin()])
```

## Usage

### Requests

To document your API, use your existing Pydantic models and add kwargs to Chalice decorators.

**Before:**
```python
@app.route('/', methods=["POST"])
def example():
    body = MySchema.parse_obj(app.current_request.json_body)
```

**After:**
```python
@app.route('/', methods=["POST"], post_body_model=MySchema)
def example():
    body = MySchema.parse_obj(app.current_request.json_body)
```

If you have multiple methods supported, you may have something like:

```python
@app.route('/', methods=["POST", "PUT"], post_body_model=MyCreateSchema, put_body_model=MyEditSchema)
def example():
    # code goes here
    pass
```

### Responses

```python
@app.route("/", methods=["POST", "PUT"],
           post_response_model=MyCreateResponseSchema,
           put_response_body=MyEditResponseSchema)
def example():
    # code goes here
    pass
```

You may edit the response codes and schema description by passing kwargs like `post_response_code` or
`post_response_description`, respectively. Without passing these values, there are sensible defaults.
