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

    # Espera un payload con una lista bajo la clave 'items'
    if not isinstance(req_body, dict) or 'items' not in req_body or not isinstance(req_body['items'], list):
        return func.HttpResponse(
            "Invalid payload: expected a JSON object with an 'items' list",
            status_code=400
        )

    # Sumar todos los valores VALOR_TOTAL_ITEM
    total_suma = 0.0
    for item in req_body['items']:
        valor_total_item = item.get('VALOR_TOTAL_ITEM', 0)
        if isinstance(valor_total_item, (int, float)):
            total_suma += float(valor_total_item)
    
    # Agregar el total_suma al payload
    req_body['total_suma'] = total_suma

    return func.HttpResponse(
        json.dumps(req_body),
        status_code=200,
        mimetype="application/json"
    )