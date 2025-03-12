from flask import Flask, request, jsonify
from flask_cors import CORS  # Importa CORS
import random
from g4f.client import Client

app = Flask(__name__)
CORS(app)  # Habilita CORS para toda la aplicación

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

# Endpoint para generar imágenes
@app.route("/generate/image", methods=["POST"])
def generate_image():
    # Validar que el JSON contenga el campo 'prompt'
    data = request.get_json()
    if not data or "prompt" not in data or not data["prompt"].strip():
        return jsonify({"error": "El campo 'prompt' es obligatorio y no puede estar vacío."}), 400

    # Obtener el número de imágenes a generar (por defecto 1)
    num_images = data.get("num_images", 1)
    if num_images not in [1, 2]:
        return jsonify({"error": "El número de imágenes debe ser 1 o 2."}), 400

    try:
        # Array para almacenar las URLs de las imágenes generadas
        image_urls = []

        # Generar las imágenes solicitadas
        for _ in range(num_images):
            model = random.choice(MODELS)
            client = Client()
            response = client.images.generate(
                model=model,
                prompt=data["prompt"],
                response_format="url"
            )
            # Agregar la URL de la imagen al array
            image_urls.append(response.data[0].url)

        # Retornar el array con las URLs de las imágenes generadas
        return jsonify({"image_urls": image_urls})
    except Exception as e:
        # Manejar errores y retornar un mensaje de error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)  # Habilita múltiples hilos