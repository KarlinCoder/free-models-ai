from flask import Flask, request, jsonify
import random
import queue
import threading
import time
from g4f import Model, Provider, generate_async

app = Flask(__name__)

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

# Cola para manejar las solicitudes
request_queue = queue.Queue()

# Función para procesar las solicitudes en la cola
def process_queue():
    while True:
        if not request_queue.empty():
            # Obtener la solicitud de la cola
            task = request_queue.get()
            prompt = task["prompt"]
            callback = task["callback"]

            try:
                # Seleccionar un modelo aleatorio
                selected_model = random.choice(MODELS)
                print(f"Modelo seleccionado: {selected_model}")

                # Generar la imagen usando g4f
                response = generate_async(
                    model=selected_model,
                    prompt=prompt
                )

                # Llamar al callback con la respuesta
                callback(response)
            except Exception as e:
                callback({"error": str(e)})
            
            # Marcar la tarea como completada
            request_queue.task_done()
        else:
            # Esperar un momento si la cola está vacía
            time.sleep(1)

# Iniciar el hilo para procesar la cola
threading.Thread(target=process_queue, daemon=True).start()

# Endpoint para generar imágenes
@app.route('/generate/image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "El campo 'prompt' es obligatorio"}), 400

    # Respuesta que se enviará al cliente
    response_data = {}

    # Callback para manejar la respuesta
    def callback(response):
        if "error" in response:
            response_data["error"] = response["error"]
        else:
            response_data["image_url"] = response

    # Agregar la tarea a la cola
    request_queue.put({"prompt": prompt, "callback": callback})

    # Esperar hasta que la tarea se complete
    request_queue.join()

    # Devolver la respuesta al cliente
    if "error" in response_data:
        return jsonify(response_data), 500
    else:
        return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)