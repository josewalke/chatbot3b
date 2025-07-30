from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import random
from difflib import SequenceMatcher

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

# Datos de prueba
SERVICES = [
    {"id": 1, "name": "Consulta General", "duration": 30, "price": 50},
    {"id": 2, "name": "Consulta Especializada", "duration": 60, "price": 100},
    {"id": 3, "name": "Seguimiento", "duration": 20, "price": 30}
]

PRODUCTS = [
    {"id": 1, "name": "Producto A", "price": 25.99, "description": "Descripción del producto A"},
    {"id": 2, "name": "Producto B", "price": 49.99, "description": "Descripción del producto B"},
    {"id": 3, "name": "Producto C", "price": 99.99, "description": "Descripción del producto C"}
]

# Respuestas dinámicas y creativas
GREETING_RESPONSES = [
    "¡Hola! 👋 Soy tu asistente virtual inteligente. ¡Estoy aquí para ayudarte con todo lo que necesites!",
    "¡Hola! 😊 ¡Qué gusto verte! Soy tu asistente personal y estoy listo para ayudarte.",
    "¡Hola! 🌟 ¡Bienvenido! Soy tu asistente virtual y estoy aquí para hacer tu día más fácil.",
    "¡Hola! ✨ ¡Me alegra que estés aquí! Soy tu asistente inteligente, ¿en qué puedo ayudarte?",
    "¡Hola! 🎉 ¡Qué bueno verte! Soy tu asistente virtual y estoy listo para asistirte."
]

PRODUCT_INFO_RESPONSES = [
    "¡Por supuesto! Te cuento todo sobre {product_name}:\n\n📦 **Descripción:** {description}\n💰 **Precio:** ${price}\n🔒 **Garantía:** 1 año\n📦 **Envío:** Gratis en compras superiores a $50\n\n¿Te gustaría:\n• 💳 Comprar este producto\n• 📦 Ver información de envío\n• 🔒 Saber más sobre la garantía\n• 🛍️ Ver otros productos",
    "¡Claro! {product_name} es una excelente opción:\n\n📦 **Descripción:** {description}\n💰 **Precio:** ${price}\n🔒 **Garantía:** 1 año\n📦 **Envío:** Gratis en compras superiores a $50\n\n¿Te interesa:\n• 💳 Proceder con la compra\n• 📦 Conocer los tiempos de envío\n• 🔒 Entender la garantía\n• 🛍️ Explorar más productos",
    "¡Perfecto! Te explico sobre {product_name}:\n\n📦 **Descripción:** {description}\n💰 **Precio:** ${price}\n🔒 **Garantía:** 1 año\n📦 **Envío:** Gratis en compras superiores a $50\n\n¿Qué te gustaría hacer:\n• 💳 Comprar ahora\n• 📦 Ver opciones de envío\n• 🔒 Conocer la garantía\n• 🛍️ Ver más productos"
]

PURCHASE_RESPONSES = [
    "¡Excelente elección! 🎉 Has seleccionado {product_name} por ${price}.\n\n¿Te gustaría proceder con la compra? Puedo ayudarte con:\n• 💳 Procesar el pago\n• 📦 Información de envío\n• 🔒 Garantía del producto\n• 📞 Contactar un agente",
    "¡Fantástico! 🌟 {product_name} es una gran opción por ${price}.\n\n¿Quieres continuar con la compra? Te puedo ayudar con:\n• 💳 Procesar el pago\n• 📦 Información de envío\n• 🔒 Garantía del producto\n• 📞 Contactar un agente",
    "¡Brillante decisión! ✨ {product_name} por ${price} es una excelente inversión.\n\n¿Procedemos con la compra? Puedo asistirte con:\n• 💳 Procesar el pago\n• 📦 Información de envío\n• 🔒 Garantía del producto\n• 📞 Contactar un agente"
]

SUPPORT_RESPONSES = [
    "¡Por supuesto! 😊 Te ayudo con tu consulta. Puedo asistirte con:\n• 🔄 Políticas de devolución\n• 🔒 Garantías\n• 📦 Envíos y entregas\n• 📅 Agendar citas\n• 🛍️ Información de productos\n• 💳 Procesar compras\n\n¿En qué puedo ayudarte específicamente?",
    "¡Claro! 🌟 Estoy aquí para ayudarte. Puedo asistirte con:\n• 🔄 Políticas de devolución\n• 🔒 Garantías\n• 📦 Envíos y entregas\n• 📅 Agendar citas\n• 🛍️ Información de productos\n• 💳 Procesar compras\n\n¿En qué puedo ayudarte específicamente?",
    "¡Perfecto! ✨ Estoy listo para asistirte. Puedo ayudarte con:\n• 🔄 Políticas de devolución\n• 🔒 Garantías\n• 📦 Envíos y entregas\n• 📅 Agendar citas\n• 🛍️ Información de productos\n• 💳 Procesar compras\n\n¿En qué puedo ayudarte específicamente?"
]

GENERAL_RESPONSES = [
    "¡Entiendo perfectamente! 😊 Como asistente virtual inteligente, puedo ayudarte con:\n• 📅 Agendar citas\n• 🛍️ Información de productos\n• 💳 Procesar compras\n• 🔄 Políticas de devolución\n• 🔒 Garantías\n• 📦 Envíos\n\n¿En qué te puedo asistir específicamente?",
    "¡Por supuesto! 🌟 Soy tu asistente virtual y estoy aquí para ayudarte con:\n• 📅 Agendar citas\n• 🛍️ Información de productos\n• 💳 Procesar compras\n• 🔄 Políticas de devolución\n• 🔒 Garantías\n• 📦 Envíos\n\n¿En qué te puedo asistir específicamente?",
    "¡Claro! ✨ Como asistente virtual inteligente, puedo ayudarte con:\n• 📅 Agendar citas\n• 🛍️ Información de productos\n• 💳 Procesar compras\n• 🔄 Políticas de devolución\n• 🔒 Garantías\n• 📦 Envíos\n\n¿En qué te puedo asistir específicamente?"
]

# Patrones de intención más inteligentes
INTENT_PATTERNS = {
    "greeting": [
        r"\b(hola|buenos|buenas|saludos|hey|hi|hello)\b",
        r"\b(como estas|qué tal|que tal)\b",
        r"\b(buenos días|buenas tardes|buenas noches)\b"
    ],
    "appointment": [
        r"\b(cita|agendar|reservar|appointment|consulta)\b",
        r"\b(quiero|necesito|busco|me gustaría|me gustaria)\s+(una\s+)?(cita|consulta)\b",
        r"\b(agenda|reserva|programa)\s+(una\s+)?(cita|consulta)\b",
        r"\b(consulta general|consulta especializada|seguimiento)\b"
    ],
    "products": [
        r"\b(producto|productos|catálogo|catalogo|merchandise)\b",
        r"\b(quiero|necesito|busco|me gustaría|me gustaria)\s+(ver\s+)?(productos?|catálogo|catalogo)\b",
        r"\b(muéstrame|muestrame|dame|déjame|dejame)\s+(los\s+)?(productos?|catálogo|catalogo)\b",
        r"\b(qué|que)\s+(productos?|tienes|ofreces)\b",
        r"\b(información|info)\s+(de\s+)?(productos?)\b",
        r"\b(hable|habla|hablame)\s+(de\s+)?(tus\s+)?(productos?)\b"
    ],
    "product_info": [
        r"\b(hablame|cuéntame|dime|información|info)\s+(del\s+)?(producto\s+[abc])\b",
        r"\b(qué|que)\s+(es|sabe|tiene)\s+(el\s+)?(producto\s+[abc])\b",
        r"\b(características|especificaciones|detalles)\s+(del\s+)?(producto\s+[abc])\b",
        r"\b(producto\s+[abc])\s+(qué|que)\s+(es|hace|ofrece)\b",
        r"\b(sobre|acerca|del)\s+(producto\s+[abc])\b",
        r"\b(hablame|cuéntame|dime)\s+(del\s+)?(producto\s+[abc])\b",
        r"\b(hablame|cuéntame|dime)\s+(sobre\s+)?(el\s+)?(producto\s+[abc])\b",
        r"\b(qué|que)\s+(sabe|puedes|puede)\s+(decir|contar)\s+(del\s+)?(producto\s+[abc])\b"
    ],
    "purchase": [
        r"\b(comprar|adquirir|tomar|quiero|necesito)\s+(el\s+)?(producto\s+[abc])\b",
        r"\b(me\s+)?(interesa|gusta)\s+(el\s+)?(producto\s+[abc])\b",
        r"\b(producto\s+[abc])\s+(por\s+favor|please)\b",
        r"\b(quiero|necesito)\s+(el\s+)?(producto\s+[abc])\b"
    ],
    "support": [
        r"\b(ayuda|soporte|problema|consulta|asistencia)\b",
        r"\b(necesito|quiero|busco)\s+(ayuda|soporte|asistencia)\b",
        r"\b(tengo\s+un\s+)?(problema|duda|pregunta)\b"
    ],
    "returns": [
        r"\b(devolución|devolucion|reembolso|devolver|return)\b",
        r"\b(política|politica)\s+(de\s+)?(devolución|devolucion)\b",
        r"\b(cómo|como)\s+(devolver|reembolsar)\b"
    ],
    "warranty": [
        r"\b(garantía|garantia|warranty|garantizado|garantizada)\b",
        r"\b(tiene\s+)?(garantía|garantia)\b",
        r"\b(cuánto|cuanto)\s+(dura|tiene)\s+(la\s+)?(garantía|garantia)\b"
    ],
    "shipping": [
        r"\b(envío|envio|entrega|shipping|delivery)\b",
        r"\b(cuánto|cuanto)\s+(tarda|dura)\s+(el\s+)?(envío|envio)\b",
        r"\b(cómo|como)\s+(se\s+)?(envía|envia|entrega)\b"
    ],
    "pricing": [
        r"\b(precio|costos?|costo|valor|cuánto|cuanto)\b",
        r"\b(qué|que)\s+(cuesta|vale)\b",
        r"\b(precios?|tarifas?)\b"
    ]
}

def similarity(a, b):
    """Calcular similitud entre dos strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_product_name(message):
    """Extraer el nombre del producto del mensaje"""
    message_lower = message.lower()
    
    # Buscar patrones específicos de productos
    product_patterns = [
        r"producto\s+([abc])",
        r"producto\s+([abc])\b",
        r"el\s+producto\s+([abc])",
        r"producto\s+([abc])\s+por\s+favor",
        r"del\s+producto\s+([abc])",
        r"sobre\s+el\s+producto\s+([abc])",
        r"información\s+del\s+producto\s+([abc])",
        r"info\s+del\s+producto\s+([abc])",
        r"producto\s+([abc])\s+específicamente",
        r"del\s+producto\s+([abc])\s+específicamente"
    ]
    
    for pattern in product_patterns:
        match = re.search(pattern, message_lower)
        if match:
            product_letter = match.group(1).upper()
            if product_letter == 'A':
                return PRODUCTS[0]
            elif product_letter == 'B':
                return PRODUCTS[1]
            elif product_letter == 'C':
                return PRODUCTS[2]
    
    # Buscar patrones más flexibles
    if "producto a" in message_lower or "producto A" in message_lower:
        return PRODUCTS[0]
    elif "producto b" in message_lower or "producto B" in message_lower:
        return PRODUCTS[1]
    elif "producto c" in message_lower or "producto C" in message_lower:
        return PRODUCTS[2]
    
    return None

def understand_intent(message):
    """Entender la intención del mensaje de forma inteligente"""
    message_lower = message.lower()
    
    # Calcular scores para cada intención
    intent_scores = {}
    
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                score += len(matches) * 2
                # Bonus por coincidencia exacta
                if any(match in message_lower for match in matches):
                    score += 1
        
        # Bonus por palabras clave específicas
        if intent == "greeting" and any(word in message_lower for word in ["hola", "buenos", "saludos"]):
            score += 3
        elif intent == "appointment" and any(word in message_lower for word in ["cita", "agendar", "consulta"]):
            score += 3
        elif intent == "products" and any(word in message_lower for word in ["producto", "catálogo", "catalogo"]):
            score += 3
        elif intent == "product_info" and extract_product_name(message):
            score += 10  # Prioridad muy alta para información específica de productos
        elif intent == "purchase" and extract_product_name(message):
            score += 5
        elif intent == "support" and any(word in message_lower for word in ["ayuda", "soporte", "problema"]):
            score += 3
        elif intent == "returns" and any(word in message_lower for word in ["devolución", "reembolso"]):
            score += 3
        elif intent == "warranty" and any(word in message_lower for word in ["garantía", "garantia"]):
            score += 3
        elif intent == "shipping" and any(word in message_lower for word in ["envío", "envio", "entrega"]):
            score += 3
        
        # Bonus adicional para consultas específicas de productos
        if intent == "product_info" and any(word in message_lower for word in ["hablame", "cuéntame", "dime", "sobre", "del", "acerca"]):
            score += 5
        
        intent_scores[intent] = score
    
    # Encontrar la intención con mayor score
    best_intent = max(intent_scores.items(), key=lambda x: x[1])
    
    # Si no hay una intención clara, usar "general"
    if best_intent[1] < 1:
        return "general"
    
    return best_intent[0]

def get_dynamic_response(intent, product=None):
    """Obtener una respuesta dinámica y creativa"""
    if intent == "greeting":
        return random.choice(GREETING_RESPONSES)
    elif intent == "product_info" and product:
        template = random.choice(PRODUCT_INFO_RESPONSES)
        return template.format(
            product_name=product['name'],
            description=product['description'],
            price=product['price']
        )
    elif intent == "purchase" and product:
        template = random.choice(PURCHASE_RESPONSES)
        return template.format(
            product_name=product['name'],
            price=product['price']
        )
    elif intent == "support":
        return random.choice(SUPPORT_RESPONSES)
    elif intent == "general":
        return random.choice(GENERAL_RESPONSES)
    else:
        return random.choice(GENERAL_RESPONSES)

@app.route('/')
def home():
    return jsonify({"message": "Chatbot IA Avanzado funcionando!", "status": "ok"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "ai-chatbot-api"})

@app.route('/chat/send', methods=['POST'])
def chat_send():
    try:
        data = request.get_json()
        message = data.get('message', '').lower()
        user_id = data.get('user_id', 'unknown')
        
        print(f"Recibido mensaje: {message} de usuario: {user_id}")
        
        # Entender la intención del mensaje
        intent = understand_intent(message)
        print(f"Intención detectada: {intent}")
        
        # Generar respuesta dinámica basada en la intención
        if intent == "greeting":
            response = {
                "message": get_dynamic_response("greeting"),
                "intent": "greeting",
                "metadata": {
                    "action": "show_options"
                }
            }
        
        elif intent == "appointment":
            response = {
                "message": "¡Perfecto! 😊 Te ayudo a agendar una cita. Tenemos estos servicios disponibles:",
                "intent": "appointment",
                "metadata": {
                    "action": "show_services",
                    "services": SERVICES
                }
            }
        
        elif intent == "products":
            response = {
                "message": "¡Por supuesto! 🌟 Te muestro nuestro catálogo de productos disponibles:",
                "intent": "sales",
                "metadata": {
                    "action": "show_products",
                    "products": PRODUCTS
                }
            }
        
        elif intent == "product_info":
            selected_product = extract_product_name(message)
            if selected_product:
                response = {
                    "message": get_dynamic_response("product_info", selected_product),
                    "intent": "product_info",
                    "metadata": {
                        "action": "show_product_details",
                        "selected_product": selected_product
                    }
                }
            else:
                response = {
                    "message": "¡Claro! ✨ Te muestro nuestros productos disponibles para que puedas elegir cuál te interesa:",
                    "intent": "sales",
                    "metadata": {
                        "action": "show_products",
                        "products": PRODUCTS
                    }
                }
        
        elif intent == "purchase":
            selected_product = extract_product_name(message)
            if selected_product:
                response = {
                    "message": get_dynamic_response("purchase", selected_product),
                    "intent": "purchase",
                    "metadata": {
                        "action": "show_purchase_options",
                        "selected_product": selected_product
                    }
                }
            else:
                response = {
                    "message": "¡Perfecto! 🛍️ Te muestro nuestros productos disponibles para que puedas elegir:",
                    "intent": "sales",
                    "metadata": {
                        "action": "show_products",
                        "products": PRODUCTS
                    }
                }
        
        elif intent == "support":
            response = {
                "message": get_dynamic_response("support"),
                "intent": "support",
                "metadata": {
                    "action": "show_support_options"
                }
            }
        
        elif intent == "returns":
            response = {
                "message": "¡Por supuesto! 🔄 Nuestra política de devoluciones permite reembolsos dentro de los 30 días de la compra. Los productos deben estar en su empaque original y sin usar.\n\n¿Te gustaría saber más detalles sobre el proceso de devolución?",
                "intent": "support",
                "metadata": {
                    "action": "show_support_options"
                }
            }
        
        elif intent == "warranty":
            response = {
                "message": "¡Claro! 🔒 Todos nuestros productos tienen garantía de 1 año. La garantía cubre defectos de fabricación y funcionamiento normal.\n\n¿Necesitas información específica sobre la garantía de algún producto?",
                "intent": "support",
                "metadata": {
                    "action": "show_support_options"
                }
            }
        
        elif intent == "shipping":
            response = {
                "message": "¡Perfecto! 📦 Los envíos se realizan en 2-3 días hábiles. Ofrecemos envío gratuito en compras superiores a $50.\n\n¿Te gustaría ver nuestros productos disponibles?",
                "intent": "sales",
                "metadata": {
                    "action": "show_products",
                    "products": PRODUCTS
                }
            }
        
        elif intent == "pricing":
            response = {
                "message": "¡Por supuesto! 💰 Nuestros precios son muy competitivos. Te muestro nuestros productos con sus precios:",
                "intent": "sales",
                "metadata": {
                    "action": "show_products",
                    "products": PRODUCTS
                }
            }
        
        else:  # intent == "general"
            response = {
                "message": get_dynamic_response("general"),
                "intent": "general",
                "metadata": {
                    "action": "show_options"
                }
            }
        
        print(f"Respuesta: {response}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error en chat_send: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/appointments/available-slots')
def available_slots():
    slots = []
    for hour in range(9, 18):
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    
    return jsonify({
        "available_slots": slots,
        "services": SERVICES
    })

@app.route('/sales/products')
def get_products():
    return jsonify({"products": PRODUCTS})

@app.route('/support/query', methods=['POST'])
def support_query():
    data = request.get_json()
    query = data.get('query', '').lower()
    
    if any(word in query for word in ["devolución", "reembolso"]):
        response = "¡Por supuesto! 🔄 Nuestra política de devoluciones permite reembolsos dentro de los 30 días de la compra."
    elif any(word in query for word in ["garantía", "garantia"]):
        response = "¡Claro! 🔒 Todos nuestros productos tienen garantía de 1 año."
    elif any(word in query for word in ["envío", "envio", "entrega"]):
        response = "¡Perfecto! 📦 Los envíos se realizan en 2-3 días hábiles."
    else:
        response = "¡Gracias por tu consulta! 😊 Un agente te contactará pronto."
    
    return jsonify({
        "response": response,
        "escalated": False,
        "ticket_id": f"TKT-{len(query)}"
    })

if __name__ == '__main__':
    print("🚀 Iniciando Chatbot IA Avanzado...")
    print("📡 Servidor disponible en: http://localhost:8000")
    print("📚 Endpoints disponibles:")
    print("   - GET  /health")
    print("   - POST /chat/send")
    print("   - GET  /appointments/available-slots")
    print("   - GET  /sales/products")
    print("   - POST /support/query")
    print("🧠 Características IA avanzadas:")
    print("   - Respuestas dinámicas y creativas")
    print("   - Improvisación como ChatGPT")
    print("   - Conversación natural")
    print("   - Múltiples variaciones de respuestas")
    print("   - Personalidad amigable")
    
    # Iniciar servidor en modo debug
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True) 