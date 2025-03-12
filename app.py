from flask import Flask, request, jsonify
import random
from g4f.client import Client
from queue import Queue
import threading

app = Flask(__name__)

# Cola para manejar las solicitudes
request_queue = Queue()

# Lista de modelos disponibles
MODELS = [
    "sdxl-turbo",
    "sd-3.5",
    "flux",
    "flux-pro",
    "flux-dev",
    "flux-schnell",
    "dall-e-3",
    "midjourney"
]

# Función para procesar las solicitudes en la cola
def process_queue():
    while True:
        # Obtener la solicitud de la cola
        request_data = request_queue.get()
        callback = request_data["callback"]
        try:
            # Seleccionar un modelo aleatorio
            model = random.choice(MODELS)
            client = Client()
            response = client.images.generate(
                model=model,
                prompt=request_data["prompt"],
                response_format="url"
            )
            # Llamar al callback con la respuesta
            callback({"image_url": response.data[0].url})
        except Exception as e:
            callback({"error": str(e)})
        finally:
            request_queue.task_done()

# Iniciar el hilo para procesar la cola
threading.Thread(target=process_queue, daemon=True).start()

# Endpoint para generar imágenes
@app.route("/generate/image", methods=["POST"])
def generate_image():
    # Validar que el JSON contenga el campo 'prompt'
    data = request.get_json()
    if not data or "prompt" not in data or not data["prompt"].strip():
        return jsonify({"error": "El campo 'prompt' es obligatorio y no puede estar vacío."}), 400

    # Variable para almacenar la respuesta
    response_data = {}

    # Callback para manejar la respuesta
    def callback(data):
        nonlocal response_data
        response_data.update(data)

    # Agregar la solicitud a la cola
    request_queue.put({"prompt": data["prompt"], "callback": callback})

    # Esperar a que se procese la solicitud
    request_queue.join()

    # Verificar si hubo un error
    if "error" in response_data:
        return jsonify({"error": response_data["error"]}), 500

    # Retornar la URL de la imagen generada
    return jsonify({"image_url": response_data["image_url"]})

if __name__ == "__main__":
    app.run(debug=True)