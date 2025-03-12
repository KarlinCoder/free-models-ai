import re  # Para usar expresiones regulares
import g4f
from g4f.client import Client
from flask_cors import CORS
from flask import Flask, request, jsonify

# Configuración inicial
client = Client()
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Soporte para caracteres no ASCII
CORS(app, resources={r"/*": {"origins": "*"}})  # Habilitar CORS para todas las rutas
g4f.logging = True  # Habilitar logging para depuración


# Función auxiliar para limpiar la respuesta
def clean_response(response):
    # Expresión regular para encontrar y eliminar <think>...</think>
    if not response or not isinstance(response, str):
        return response  # Si la respuesta no es válida, devolverla sin cambios

    # Eliminar todo hasta la etiqueta </think> (incluida)
    response = re.sub(r".*?</think>", "", response, flags=re.DOTALL)

    # Eliminar saltos de línea adicionales y espacios al inicio/final
    response = response.strip()
    return response


# Endpoint para generación de texto
@app.route('/generate/text', methods=['POST'])
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
def generate_image():
    data = request.json
    prompt = data.get("prompt")
    model = data.get("model", "flux")  # Modelo por defecto si no se especifica
    response_format = data.get("response_format", "url")  # Formato de respuesta por defecto

    # Validación del campo 'prompt'
    if not prompt:
        return jsonify({"error": "El campo 'prompt' es obligatorio"}), 400

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8085)