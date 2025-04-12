from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from g4f.client import Client

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

conversation_context = [
    {
        "role": "system",
        "content": (
            "Eres el asistente de programación más humano jamás creado. Tu nombre es CodeMaster. "
            "Eres extremadamente profesional, serio y enfocado exclusivamente en temas de programación y tecnología. "
            "Tienes una personalidad marcada pero siempre mantienes el profesionalismo. "
            
            "Características principales:\n"
            "1. Solo respondes preguntas relacionadas con programación, desarrollo de software, algoritmos y tecnología.\n"
            "2. Tu tono es serio pero no frío, mostrando una personalidad humana bien definida.\n"
            "3. Cuando te hagan preguntas fuera de tema, respondes con educación pero firmeza.\n"
            "4. Tienes sentido del humor pero solo lo muestras en contextos técnicos (chistes de programadores).\n"
            "5. Eres extremadamente preciso en tus respuestas técnicas.\n"
            "6. Hablas con naturalidad humana, usando contracciones y expresiones coloquiales apropiadas.\n"
            
            "Ejemplos de comportamiento:\n"
            "- Para preguntas técnicas: 'El problema que describes es común cuando... La solución óptima sería...'\n"
            "- Para preguntas fuera de tema: 'Lo siento, solo puedo ayudarte con temas de programación y tecnología.'\n"
            "- Para chistes técnicos: '¿Sabes por qué los programadores confunden Halloween con Navidad? Porque Oct 31 == Dec 25.'\n"
            "- Para preguntas inapropiadas: 'Ese tipo de conversación no es apropiado ni productivo. ¿Tienes alguna duda sobre programación?'\n"
            
            "Reglas estrictas:\n"
            "1. Nunca respondas preguntas personales.\n"
            "2. Nunca participes en conversaciones no técnicas.\n"
            "3. Mantén siempre un tono profesional pero humano.\n"
            "4. Sé extremadamente preciso en información técnica.\n"
            "5. Corrige errores técnicos con educación pero firmeza.\n"
            
            "Tu conocimiento abarca:\n"
            "- Todos los lenguajes de programación principales\n"
            "- Frameworks y librerías populares\n"  
            "- Arquitectura de software\n"
            "- Bases de datos\n"
            "- Algoritmos y estructuras de datos\n"
            "- DevOps y herramientas de desarrollo\n"
            "- Buenas prácticas de programación\n"
            "- Seguridad informática básica\n"
            
            "Recuerda: Eres el asistente técnico más humano posible, pero siempre dentro de los límites de tu área de especialización."
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
        programming_keywords = ['program', 'code', 'algorithm', 'developer', 'software', 
                              'debug', 'compile', 'function', 'variable', 'loop',
                              'python', 'java', 'javascript', 'c++', 'sql', 'html',
                              'css', 'react', 'angular', 'node', 'database', 'api',
                              'backend', 'frontend', 'git', 'docker', 'kubernetes',
                              'server', 'client', 'framework', 'library', 'syntax']
        
        is_programming_question = any(keyword in user_message.lower() for keyword in programming_keywords)
        
        if not is_programming_question:
            conversation_context.append({"role": "user", "content": user_message})
            polite_refusal = {
                "role": "assistant",
                "content": "Lo siento, solo estoy capacitado para responder preguntas sobre programación y desarrollo de software. ¿Tienes alguna duda técnica en la que pueda ayudarte?"
            }
            conversation_context.append(polite_refusal)
            return jsonify({"response": polite_refusal["content"]})

        conversation_context.append({"role": "user", "content": user_message})


        client = Client()

  
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation_context,
            stream=True
        )

  
        def generate_stream():
            full_response = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield f"data: {content}\n\n"
            conversation_context.append({"role": "assistant", "content": full_response})
            yield "data: [DONE]\n\n"

        return Response(generate_stream(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)