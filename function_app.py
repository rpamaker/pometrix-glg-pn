import azure.functions as func
import logging
import json
import PyPDF2
import io
import base64
import hashlib
import time

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Authentication helper functions
def create_session_token(username: str) -> str:
    """Create a simple session token for the user"""
    timestamp = str(int(time.time()))
    data = f"{username}:{timestamp}"
    token = base64.b64encode(data.encode()).decode()
    return token

def validate_session_token(token: str) -> str:
    """Validate session token and return username if valid"""
    try:
        data = base64.b64decode(token.encode()).decode()
        username, timestamp = data.split(':')

        # Check if token is not older than 1 hour (3600 seconds)
        if int(time.time()) - int(timestamp) > 3600:
            return None

        return username
    except:
        return None

def validate_password(username: str, password: str) -> bool:
    """Validate password against the pattern {username}2025!"""
    expected_password = f"{username}2025!"
    return password == expected_password

def get_login_html() -> str:
    """Return the login form HTML"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF Splitter - Login</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 100px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input[type="text"], input[type="password"] {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            input[type="text"]:focus, input[type="password"]:focus {
                border-color: #4CAF50;
                outline: none;
            }
            button {
                width: 100%;
                padding: 12px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            button:hover:not(:disabled) {
                background-color: #45a049;
            }
            .error-message {
                color: #d32f2f;
                font-size: 14px;
                margin-top: 10px;
                text-align: center;
                display: none;
            }
            .info-message {
                color: #666;
                font-size: 14px;
                text-align: center;
                margin-top: 20px;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 Acceso PDF Splitter</h1>
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">Usuario:</label>
                    <input type="text" id="username" name="username" required>
                </div>

                <div class="form-group">
                    <label for="password">Contraseña:</label>
                    <input type="password" id="password" name="password" required>
                </div>

                <button type="submit" id="loginButton">INGRESAR</button>
                <div class="error-message" id="errorMessage"></div>

            </form>
        </div>

        <script>
            $(document).ready(function() {
                $('#loginForm').submit(function(e) {
                    e.preventDefault();

                    const username = $('#username').val().trim();
                    const password = $('#password').val();

                    if (!username || !password) {
                        $('#errorMessage').text('Por favor complete todos los campos.').show();
                        return;
                    }

                    $('#loginButton').prop('disabled', true).text('Verificando...');
                    $('#errorMessage').hide();

                    const formData = new FormData();
                    formData.append('action', 'login');
                    formData.append('username', username);
                    formData.append('password', password);

                    $.ajax({
                        url: window.location.href,
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function(data, status, xhr) {
                            // Successful login should redirect or reload the page
                            window.location.reload();
                        },
                        error: function(xhr, status, error) {
                            const errorText = xhr.responseText || 'Error de autenticación';
                            $('#errorMessage').text(errorText).show();
                            $('#loginButton').prop('disabled', false).text('INGRESAR');
                        }
                    });
                });
            });
        </script>
    </body>
    </html>
    """

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

@app.route(route="pdfsplitter", methods=["GET", "POST"])
def pdf_splitter(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PDF Splitter function processed a request.')

    if req.method == "GET":
        # Check authentication via cookie
        session_token = None
        cookies = req.headers.get('cookie', '')
        for cookie in cookies.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('session_token='):
                session_token = cookie.split('=', 1)[1]
                break

        # Validate session token
        authenticated_user = None
        if session_token:
            authenticated_user = validate_session_token(session_token)

        # If not authenticated, return login form
        if not authenticated_user:
            return func.HttpResponse(
                get_login_html(),
                status_code=200,
                mimetype="text/html"
            )
        # Return authenticated PDF form
        html_content = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PDF Splitter</title>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #555;
                }
                input[type="file"], input[type="number"] {
                    width: 100%;
                    padding: 10px;
                    border: 2px solid #ddd;
                    border-radius: 5px;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                input[type="file"]:focus, input[type="number"]:focus {
                    border-color: #4CAF50;
                    outline: none;
                }
                .page-inputs {
                    display: flex;
                    gap: 15px;
                }
                .page-inputs .form-group {
                    flex: 1;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 18px;
                    cursor: pointer;
                    margin-top: 10px;
                }
                button:disabled {
                    background-color: #cccccc;
                    cursor: not-allowed;
                }
                button:hover:not(:disabled) {
                    background-color: #45a049;
                }
                .error-message {
                    color: #d32f2f;
                    font-size: 14px;
                    margin-top: 5px;
                    display: none;
                }
                .loading {
                    display: none;
                    text-align: center;
                    color: #666;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
                    <h1 style="margin: 0; color: #333;">PDF Splitter</h1>
                    <div>
                        <span style="color: #666; margin-right: 10px;">Bienvenido, """ + authenticated_user + """!</span>
                        <button type="button" onclick="logout()" style="background-color: #f44336; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-size: 12px;">Cerrar Sesión</button>
                    </div>
                </div>
                <form id="pdfForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="pdfFile">Seleccionar archivo PDF:</label>
                        <input type="file" id="pdfFile" name="pdfFile" accept=".pdf" required>
                        <div class="error-message" id="fileError">Por favor, seleccione un archivo PDF válido.</div>
                    </div>

                    <div class="page-inputs">
                        <div class="form-group">
                            <label for="desdePagina">Desde página:</label>
                            <input type="number" id="desdePagina" name="desdePagina" min="1" required>
                            <div class="error-message" id="fromPageError">Ingrese una página válida.</div>
                        </div>

                        <div class="form-group">
                            <label for="hastaPagina">Hasta página:</label>
                            <input type="number" id="hastaPagina" name="hastaPagina" min="1" required>
                            <div class="error-message" id="toPageError">Ingrese una página válida.</div>
                        </div>
                    </div>

                    <button type="submit" id="splitButton" disabled>SPLIT</button>
                    <div class="loading" id="loading">Procesando PDF...</div>
                </form>
            </div>

            <script>
                $(document).ready(function() {
                    let isValidFile = false;
                    let isValidPages = false;

                    // File validation
                    $('#pdfFile').change(function() {
                        const file = this.files[0];
                        if (file && file.type === 'application/pdf') {
                            isValidFile = true;
                            $('#fileError').hide();
                        } else {
                            isValidFile = false;
                            $('#fileError').show();
                        }
                        updateButtonState();
                    });

                    // Page validation
                    function validatePages() {
                        const fromPage = parseInt($('#desdePagina').val());
                        const toPage = parseInt($('#hastaPagina').val());

                        let isValid = true;

                        // Reset errors
                        $('#fromPageError').hide();
                        $('#toPageError').hide();

                        if (isNaN(fromPage) || fromPage < 1) {
                            $('#fromPageError').show();
                            isValid = false;
                        }

                        if (isNaN(toPage) || toPage < 1) {
                            $('#toPageError').show();
                            isValid = false;
                        }

                        if (!isNaN(fromPage) && !isNaN(toPage) && fromPage > toPage) {
                            $('#fromPageError').text('La página inicial debe ser menor o igual a la final.').show();
                            isValid = false;
                        }

                        isValidPages = isValid;
                        updateButtonState();
                    }

                    $('#desdePagina, #hastaPagina').on('input', validatePages);

                    function updateButtonState() {
                        $('#splitButton').prop('disabled', !(isValidFile && isValidPages));
                    }

                    // Form submission
                    $('#pdfForm').submit(function(e) {
                        e.preventDefault();

                        if (!isValidFile || !isValidPages) {
                            return;
                        }

                        const formData = new FormData(this);

                        $('#splitButton').prop('disabled', true);
                        $('#loading').show();

                        $.ajax({
                            url: window.location.href,
                            type: 'POST',
                            data: formData,
                            processData: false,
                            contentType: false,
                            xhrFields: {
                                responseType: 'blob'
                            },
                            success: function(data, status, xhr) {
                                // Create download link
                                const blob = new Blob([data], {type: 'application/pdf'});
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = 'split_pdf.pdf';
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                window.URL.revokeObjectURL(url);

                                $('#loading').hide();
                                $('#splitButton').prop('disabled', false);
                            },
                            error: function(xhr, status, error) {
                                alert('Error: ' + (xhr.responseText || error));
                                $('#loading').hide();
                                $('#splitButton').prop('disabled', false);
                            }
                        });
                    });
                });

                // Logout function
                function logout() {
                    const formData = new FormData();
                    formData.append('action', 'logout');

                    $.ajax({
                        url: window.location.href,
                        type: 'POST',
                        data: formData,
                        processData: false,
                        contentType: false,
                        success: function(data, status, xhr) {
                            // Reload page to show login form
                            window.location.reload();
                        },
                        error: function(xhr, status, error) {
                            // Even if there's an error, try to reload the page
                            window.location.reload();
                        }
                    });
                }
            </script>
        </body>
        </html>
        """

        return func.HttpResponse(
            html_content,
            status_code=200,
            mimetype="text/html"
        )

    elif req.method == "POST":
        try:
            # Get form data
            files = req.files
            form = req.form

            # Check if this is a login request
            if form.get('action') == 'login':
                username = form.get('username', '').strip()
                password = form.get('password', '')

                if not username or not password:
                    return func.HttpResponse("Usuario y contraseña requeridos", status_code=400)

                # Validate password
                if not validate_password(username, password):
                    return func.HttpResponse("Credenciales inválidas", status_code=401)

                # Create session token
                session_token = create_session_token(username)

                # Return success response with cookie
                response = func.HttpResponse("Login exitoso", status_code=200)
                response.headers['Set-Cookie'] = f'session_token={session_token}; Path=/; Max-Age=3600; HttpOnly'
                return response

            # Check if this is a logout request
            if form.get('action') == 'logout':
                # Return response that clears the session cookie
                response = func.HttpResponse("Logout exitoso", status_code=200)
                response.headers['Set-Cookie'] = 'session_token=; Path=/; Max-Age=0; HttpOnly'
                return response

            # For PDF processing, check authentication first
            session_token = None
            cookies = req.headers.get('cookie', '')
            for cookie in cookies.split(';'):
                cookie = cookie.strip()
                if cookie.startswith('session_token='):
                    session_token = cookie.split('=', 1)[1]
                    break

            authenticated_user = None
            if session_token:
                authenticated_user = validate_session_token(session_token)

            if not authenticated_user:
                return func.HttpResponse("No autenticado", status_code=401)

            # PDF processing logic (existing code)
            if 'pdfFile' not in files:
                return func.HttpResponse("No file uploaded", status_code=400)

            pdf_file = files['pdfFile']
            desde_pagina = int(form.get('desdePagina', 1))
            hasta_pagina = int(form.get('hastaPagina', 1))

            # Validate page numbers
            if desde_pagina < 1 or hasta_pagina < 1 or desde_pagina > hasta_pagina:
                return func.HttpResponse("Invalid page range", status_code=400)

            # Read the PDF
            pdf_data = pdf_file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))

            # Validate page range against PDF
            total_pages = len(pdf_reader.pages)
            if hasta_pagina > total_pages:
                return func.HttpResponse(f"PDF only has {total_pages} pages", status_code=400)

            # Create new PDF with selected pages
            pdf_writer = PyPDF2.PdfWriter()

            # Add pages (PyPDF2 uses 0-based indexing)
            for page_num in range(desde_pagina - 1, hasta_pagina):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            # Write to bytes
            output_pdf = io.BytesIO()
            pdf_writer.write(output_pdf)
            output_pdf.seek(0)

            # Return the split PDF
            return func.HttpResponse(
                output_pdf.read(),
                status_code=200,
                mimetype="application/pdf",
                headers={
                    "Content-Disposition": "attachment; filename=split_pdf.pdf"
                }
            )

        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            return func.HttpResponse(f"Error processing PDF: {str(e)}", status_code=500)