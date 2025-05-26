import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )

    # Espera un payload con una lista bajo la clave 'posting'
    if not isinstance(req_body, dict) or 'posting' not in req_body or not isinstance(req_body['posting'], list):
        return func.HttpResponse(
            "Invalid payload: expected a JSON object with a 'posting' list",
            status_code=400
        )

    for item in req_body['posting']:
        numero_factura = str(item.get('NUMERO DE FACTURA', ''))
        proveedor_nombre = str(item.get('PROVEEDOR NOMBRE O RAZON SOCIAL', ''))
        item['CONCEPTO'] = f"{numero_factura} - {proveedor_nombre}"

    return func.HttpResponse(
        json.dumps(req_body),
        status_code=200,
        mimetype="application/json"
    )