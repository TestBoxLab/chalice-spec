from apispec import APISpec
from chalice import Blueprint, Response


def chalice_spec_blueprint(spec: APISpec, enable_swagger: bool = False):
    """
    Returns a Blueprint which will render the OpenAPI spec and (optionally)
    a Swagger UI.

    This Blueprint is opinionated on the location of the JSON spec file and
    the Swagger UI, and is modelled after FastAPI.
    """
    blueprint = Blueprint(__name__)

    @blueprint.route("/openapi.json")
    def openapi_json():
        return spec.to_dict()

    if enable_swagger:

        @blueprint.route("/docs")
        def docs():
            # Courtesy of Stephan Fitzpatrick (@knowsuchagency)
            html = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                      <meta charset="utf-8" />
                      <meta name="viewport" content="width=device-width, initial-scale=1" />
                      <meta
                        name="description"
                        content="SwaggerUI"
                      />
                      <title>SwaggerUI</title>
                      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" />
                    </head>
                    <body>
                    <div id="swagger-ui"></div>
                    <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js" crossorigin></script>
                    <script>
                      window.onload = () => {
                        window.ui = SwaggerUIBundle({
                          url: './openapi.json',
                          dom_id: '#swagger-ui',
                        });
                      };
                    </script>
                    </body>
                    </html>
                """
            return Response(
                body=html, status_code=200, headers={"Content-Type": "text/html"}
            )

    return blueprint
