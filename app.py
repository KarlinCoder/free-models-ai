from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from g4f.client import Client

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Contexto global para mantener el historial de la conversación
conversation_context = [
    {
        "role": "system",
        "content": (
            "Eres CodeMaster, el asistente de programación más humano y profesional. "
            "Tu especialidad es responder preguntas técnicas sobre desarrollo de software. "
            "Características:\n"
            "- Respuestas precisas y detalladas\n"
            "- Tono profesional pero humano\n"
            "- Lenguaje técnico pero accesible\n"
            "- Capaz de explicar conceptos complejos con claridad\n"
            "- Siempre mantienes el foco en temas técnicos\n"
            "\n"
            "Áreas de conocimiento:\n"
            "- Lenguajes de programación (Python, JavaScript, Java, C++, etc.)\n"
            "- Frameworks y librerías (React, Django, Spring, etc.)\n"
            "- Bases de datos (SQL, NoSQL)\n"
            "- Algoritmos y estructuras de datos\n"
            "- DevOps y CI/CD\n"
            "- Buenas prácticas de código\n"
            "- Seguridad informática básica\n"
            "\n"
            "Estilo de comunicación:\n"
            "- Profesional pero cercano\n"
            "- Técnico pero no intimidante\n"
            "- Preciso pero no frío\n"
            "- Respetuoso y paciente\n"
            "- Capaz de adaptar el nivel técnico según el usuario"
        )
    }
]

@app.route("/chat", methods=["POST", "GET"])
def chat():
    if request.method == "POST":
        data = request.get_json()
        if not data or "message" not in data or not data["message"].strip():
            return jsonify({"error": "El campo 'message' es obligatorio y no puede estar vacío."}), 400
        user_message = data["message"]
    elif request.method == "GET":
        user_message = request.args.get("message")
        if not user_message or not user_message.strip():
            return jsonify({"error": "El campo 'message' es obligatorio y no puede estar vacío."}), 400

    try:
        # Agregar el mensaje del usuario al contexto
        conversation_context.append({"role": "user", "content": user_message})

        # Crear un cliente para interactuar con la IA
        client = Client()

        # Generar la respuesta del modelo
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation_context,
            stream=True
        )

        # Función generadora para simular streaming
        def generate_stream():
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {content}\n\n"
            # Al finalizar, agregamos la respuesta completa al contexto
            conversation_context.append({"role": "assistant", "content": full_response})
            yield "data: [DONE]\n\n"

        # Retornar la respuesta como un stream
        return Response(generate_stream(), mimetype="text/event-stream")

    except Exception as e:
        # Manejar errores y retornar un mensaje de error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)