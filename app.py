import re
import g4f
from g4f.client import Client
from flask_cors import CORS
from flask import Flask, request, jsonify
from queue import Queue
from threading import Thread
from functools import wraps
from time import time, sleep

# Configuración inicial
client = Client()
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Soporte para caracteres no ASCII
g4f.logging = True  # Habilitar logging para depuración

# Configuración avanzada de CORS
CORS(
    app,
    resources={r"/*": {"origins": "*"}},  # Permitir todos los orígenes
    supports_credentials=True,            # Habilitar credenciales si es necesario
    methods=["GET", "POST", "OPTIONS"],   # Métodos HTTP permitidos
    allow_headers=["Content-Type", "Authorization"]  # Encabezados permitidos
)

# Cola para manejar las solicitudes concurrentes
request_queue = Queue()

# Rate Limiting: Diccionario para rastrear las solicitudes por IP
request_limits = {}

# Función auxiliar para limpiar la respuesta
def clean_response(response):
    if not response or not isinstance(response, str):
        return response  # Si la respuesta no es válida, devolverla sin cambios

    # Eliminar todo hasta la etiqueta </think> (incluida)
    response = re.sub(r".*?</think>", "", response, flags=re.DOTALL)

    # Eliminar saltos de línea adicionales y espacios al inicio/final
    response = response.strip()
    return response


# Middleware para Rate Limiting
def rate_limit(limit=5, per=60):  # Máximo 5 solicitudes por minuto
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            current_time = time()

            # Limpiar registros antiguos
            if ip in request_limits:
                request_limits[ip] = [t for t in request_limits[ip] if current_time - t < per]

            # Verificar límite
            if ip not in request_limits or len(request_limits[ip]) < limit:
                if ip not in request_limits:
                    request_limits[ip] = []
                request_limits[ip].append(current_time)
                return f(*args, **kwargs)
            else:
                return jsonify({"error": "Demasiadas solicitudes. Intente de nuevo más tarde."}), 429
        return wrapped
    return decorator


# Función para procesar solicitudes en la cola
def process_queue():
    while True:
        task = request_queue.get()
        if task is None:
            break
        try:
            task()  # Ejecutar la tarea
        except Exception as e:
            print(f"Error al procesar la solicitud: {str(e)}")
        finally:
            request_queue.task_done()


# Endpoint para generación de texto
@app.route('/generate/text', methods=['POST'])
@rate_limit(limit=5, per=60)  # Aplicar Rate Limiting
def generate_text():
    data = request.json
    prompt = data.get("prompt")
    model = data.get("model", "gpt-4o-mini")  # Modelo por defecto si no se especifica

    # Validación del campo 'prompt'
    if not prompt:
        return jsonify({"error": "El campo 'prompt' es obligatorio"}), 400

    try:
        # Generar respuesta usando el modelo especificado o el predeterminado
        response = g4f.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            web_search=False
        )
        # Limpiar la respuesta antes de enviarla
        cleaned_response = clean_response(response)
        return jsonify({"response": cleaned_response})
    except Exception as e:
        # Devolver un mensaje de error claro en caso de fallo
        return jsonify({"error": f"Error al generar texto: {str(e)}"}), 500


# Endpoint para generación de imágenes
@app.route('/generate/image', methods=['POST'])
@rate_limit(limit=3, per=60)  # Menor límite para imágenes debido a su intensidad
def generate_image():
    data = request.json
    prompt = data.get("prompt")
    model = data.get("model", "flux")  # Modelo por defecto si no se especifica
    response_format = data.get("response_format", "url")  # Formato de respuesta por defecto

    # Validación del campo 'prompt'
    if not prompt:
        return jsonify({"error": "El campo 'prompt' es obligatorio"}), 400

    def generate_task():
        try:
            # Generar imagen usando el modelo especificado o el predeterminado
            response = client.images.generate(
                model=model,
                prompt=prompt,
                response_format=response_format
            )
            # Extraer la URL de la imagen y devolverla en la respuesta
            image_url = response.data[0].url if response_format == "url" else response.data[0]
            return jsonify({"image_url": image_url})
        except Exception as e:
            # Devolver un mensaje de error claro en caso de fallo
            return jsonify({"error": f"Error al generar imagen: {str(e)}"}), 500

    # Agregar la tarea a la cola
    request_queue.put(generate_task)
    return jsonify({"message": "Solicitud en proceso. Espere unos momentos..."}), 202


@app.route('/check', methods=['GET'])
def check():
    return jsonify({"status": "OK", "message": "API is up and running!"}), 200


if __name__ == '__main__':
    # Iniciar el hilo para procesar la cola
    worker_thread = Thread(target=process_queue, daemon=True)
    worker_thread.start()

    # Iniciar la aplicación Flask
    app.run(debug=True, host='0.0.0.0', port=8085)