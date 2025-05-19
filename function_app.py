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

    # Ejemplo: responder con parte del payload
    rut = req_body.get("rut", "undefined")
    total = req_body.get("total_amount", 0)

    result = {
        "status": "ok",
        "message": f"Procesado RUT: {rut}, Total: {total}",
        "received": req_body
    }
    logging.info(f"Processed data: {result}")

    return func.HttpResponse(
        json.dumps(req_body),
        status_code=200,
        mimetype="application/json"
    )