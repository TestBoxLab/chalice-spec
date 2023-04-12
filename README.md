# chalice-spec

[![Python package](https://github.com/TestBoxLab/chalice-spec/actions/workflows/test.yml/badge.svg)](https://github.com/TestBoxLab/chalice-spec/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Chalice × APISpec × Pydantic plug-ins**

Combines the power of Chalice, APISpec, and Pydantic to make AWS Chalice apps easily documented

## Installation

First, add chalice-spec:

```shell
poetry add chalice_spec
```

We consider Chalice, APISpec, and Pydantic "peer dependencies." We only include them as dev
dependencies in our codebase, and you may need to install them in yours if you haven't
already.

```shell
poetry add chalice apispec pydantic
```

## Setup

chalice-spec provides a subclass of the main `Chalice` class, called `ChaliceWithSpec`.
Here is an example of how to get started:

Before:

```python
from chalice import Chalice

app = Chalice(app_name="hello_world")
```

After:

```python
from chalice_spec import ChaliceWithSpec, PydanticPlugin
from apispec import APISpec

spec = APISpec(chalice_app=app,
               ...,
               plugins=[PydanticPlugin()])

app = ChaliceWithSpec(app_name="hello_world", spec=spec)
```

If you use

```python
ChaliceWithSpec(..., generate_default_docs=True)
```

the plugin will generate empty docs (with empty request and response schemas) for every endpoint that you've defined in your app. This can be useful as a starting point / overview while developing.

## Usage

To document your API, use your existing Pydantic models and add kwargs to Chalice decorators.

**Before:**
```python
@app.route('/', methods=["POST"])
def example():
    body = MySchema.parse_obj(app.current_request.json_body)
```

**After:**
```python
@app.route('/', methods=["POST"], docs=Docs(
    post=Operation(request=MySchema)
))
def example():
    body = MySchema.parse_obj(app.current_request.json_body)
```

If you have multiple methods supported, you may have something like:

```python
@app.route('/', methods=["POST", "PUT"],
           docs=Docs(
               post=Operation(request=MyCreateSchema, response=MyReadSchema),
               put=Operation(request=MyEditSchema, response=MyReadSchema)
           )
def example():
    # code goes here
    pass
```

### API

- [ ] TODO: this section coming soon!
