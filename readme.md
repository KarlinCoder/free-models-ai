# **Documentación de la API de Generación de Texto e Imágenes**

## **Descripción General**

Esta API permite a los usuarios generar texto y crear imágenes utilizando una variedad de modelos avanzados de inteligencia artificial. Los usuarios pueden especificar un modelo personalizado o utilizar uno predeterminado si no se proporciona.

La API está diseñada para ser flexible, fácil de usar y compatible con múltiples proveedores de modelos.

---

## **Base URL**

La base de la API es:  
`http://<host>:8085`

Por ejemplo, si la API está alojada localmente, la URL base sería:  
`http://localhost:8085`

---

## **Endpoints**

### **1. Generación de Texto**

**Endpoint**: `/generate/text`  
**Método**: `POST`  
**Descripción**: Genera texto basado en un prompt proporcionado. Opcionalmente, puedes especificar un modelo.

#### **Parámetros de la solicitud (JSON)**

| Campo    | Tipo   | Requerido | Descripción                                                                      |
| -------- | ------ | --------- | -------------------------------------------------------------------------------- |
| `prompt` | string | Sí        | El texto de entrada que describe lo que deseas generar.                          |
| `model`  | string | No        | El modelo de lenguaje a utilizar. Si no se especifica, se usa el predeterminado. |

#### **Modelos Disponibles para Generación de Texto**

Los siguientes modelos están disponibles para el endpoint `/generate/text`:

- **OpenAI**:

  - `gpt-4`
  - `gpt-4o`
  - `gpt-4o-mini`
  - `o1`
  - `o1-mini`
  - `o3-mini`

- **Meta (Llama Series)**:

  - `llama-2-7b`
  - `llama-3-8b`
  - `llama-3-70b`
  - `llama-3.1-8b`
  - `llama-3.1-70b`
  - `llama-3.1-405b`
  - `llama-3.2-1b`
  - `llama-3.2-3b`
  - `llama-3.2-11b`
  - `llama-3.2-90b`
  - `llama-3.3-70b`

- **Mistral**:

  - `mixtral-8x7b`
  - `mixtral-8x22b`
  - `mistral-nemo`
  - `mixtral-small-24b`
  - `mixtral-small-28b`

- **Microsoft**:

  - `phi-3.5-mini`
  - `phi-4`
  - `wizardlm-2-7b`
  - `wizardlm-2-8x22b`

- **Google DeepMind (Gemini Series)**:

  - `gemini-2.0`
  - `gemini-exp`
  - `gemini-1.5-flash`
  - `gemini-1.5-pro`
  - `gemini-2.0-flash`
  - `gemini-2.0-flash-thinking`
  - `gemini-2.0-pro`

- **Anthropic (Claude Series)**:

  - `claude-3-haiku`
  - `claude-3-sonnet`
  - `claude-3-opus`
  - `claude-3.5-sonnet`
  - `claude-3.7-sonnet`
  - `claude-3.7-sonnet-thinking`

- **Otros Modelos**:
  - `reka-core` (Reka AI)
  - `deepseek-chat` (DeepSeek)
  - `deepseek-v3` (DeepSeek)
  - `deepseek-r1` (DeepSeek)
  - `grok-3` (x.ai)
  - `grok-3-r1` (x.ai)
  - `sonar` (Perplexity AI)
  - `sonar-pro` (Perplexity AI)
  - `r1-1776` (Perplexity AI)
  - `nemotron-70b` (Nvidia)
  - `dbrx-instruct` (Databricks)
  - `glm-4` (THUDM)

#### **Ejemplo de Solicitud**

```json
{
  "prompt": "Explica qué es la inteligencia artificial.",
  "model": "gpt-4o-mini"
}
```

#### **Respuesta Exitosa**

```json
{
  "response": "La inteligencia artificial es la simulación de procesos humanos por sistemas informáticos..."
}
```

#### **Respuesta de Error**

```json
{
  "error": "El campo 'prompt' es obligatorio"
}
```

---

### **2. Generación de Imágenes**

**Endpoint**: `/generate/image`  
**Método**: `POST`  
**Descripción**: Genera una imagen basada en un prompt proporcionado. Opcionalmente, puedes especificar un modelo y el formato de respuesta.

#### **Parámetros de la solicitud (JSON)**

| Campo             | Tipo   | Requerido | Descripción                                                                                    |
| ----------------- | ------ | --------- | ---------------------------------------------------------------------------------------------- |
| `prompt`          | string | Sí        | El texto de entrada que describe la imagen que deseas generar.                                 |
| `model`           | string | No        | El modelo de generación de imágenes a utilizar. Si no se especifica, se usa el predeterminado. |
| `response_format` | string | No        | Formato de la respuesta (`url` o `base64`). Por defecto es `url`.                              |

#### **Modelos Disponibles para Generación de Imágenes**

Los siguientes modelos están disponibles para el endpoint `/generate/image`:

- **Stability AI**:

  - `sdxl-turbo`
  - `sd-3.5`

- **Black Forest Labs**:

  - `flux`
  - `flux-pro`
  - `flux-dev`
  - `flux-schnell`

- **OpenAI**:

  - `dall-e-3`

- **Midjourney**:
  - `midjourney`

#### **Ejemplo de Solicitud**

```json
{
  "prompt": "Un paisaje futurista con ciudades flotantes",
  "model": "flux",
  "response_format": "url"
}
```

#### **Respuesta Exitosa**

```json
{
  "image_url": "https://example.com/generated-image.jpg"
}
```

#### **Respuesta de Error**

```json
{
  "error": "El campo 'prompt' es obligatorio"
}
```

---

## **Errores Comunes**

1. **Campo 'prompt' faltante**:

   ```json
   {
     "error": "El campo 'prompt' es obligatorio"
   }
   ```

2. **Error interno del servidor**:

   ```json
   {
     "error": "Error al generar texto: <mensaje de error>"
   }
   ```

3. **Modelo no soportado**:
   Si se especifica un modelo no válido, se devolverá un error indicando que el modelo no está disponible.

---

## **Consideraciones Adicionales**

1. **Compatibilidad con CORS**:

   - La API está configurada para permitir solicitudes desde cualquier origen (`*`) mediante CORS.

2. **Depuración**:

   - El logging está habilitado para facilitar la depuración. Puedes revisar los logs en la consola del servidor.

3. **Formato de Respuesta**:

   - Todas las respuestas están en formato JSON y son compatibles con caracteres no ASCII.

4. **Modelos Predeterminados**:
   - Si no se especifica un modelo, se usará el predeterminado:
     - Para texto: `gpt-4o-mini`
     - Para imágenes: `flux`

---

Con esta documentación, los usuarios pueden entender fácilmente cómo interactuar con la API y aprovechar todas sus funcionalidades. 😊
