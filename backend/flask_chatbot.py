from flask import Flask, request, jsonify
from flask_cors import CORS
import json

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

# Endpoints básicos
@app.route("/")
def root():
    return jsonify({"message": "Chatbot Inteligente API", "status": "running"})

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "chatbot-api"})

@app.route("/status")
def api_status():
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "features": ["chat", "appointments", "sales", "support"]
    })

# Chat endpoints
@app.route("/chat/send", methods=["POST"])
def send_message():
    """Procesar mensaje del chat"""
    data = request.get_json()
    message = data.get("message", "").lower()
    user_id = data.get("user_id", "unknown")
    
    # Detección simple de intenciones
    if any(word in message for word in ["cita", "agendar", "reservar", "appointment"]):
        response = {
            "message": "Perfecto, te ayudo a agendar una cita. ¿Qué servicio te interesa?",
            "intent": "appointment",
            "metadata": {
                "action": "show_services",
                "services": SERVICES
            }
        }
    elif any(word in message for word in ["producto", "comprar", "venta", "precio"]):
        response = {
            "message": "Te muestro nuestros productos disponibles:",
            "intent": "sales",
            "metadata": {
                "action": "show_products",
                "products": PRODUCTS
            }
        }
    elif any(word in message for word in ["ayuda", "soporte", "problema", "consulta"]):
        response = {
            "message": "Te ayudo con tu consulta. ¿En qué puedo asistirte?",
            "intent": "support",
            "metadata": {
                "action": "show_support_options"
            }
        }
    else:
        response = {
            "message": "Hola! Soy tu asistente virtual. Puedo ayudarte con:\n- Agendar citas\n- Información de productos\n- Atención al cliente\n¿En qué te puedo ayudar?",
            "intent": "greeting",
            "metadata": {
                "action": "show_options"
            }
        }
    
    return jsonify(response)

# Appointment endpoints
@app.route("/appointments/available-slots")
def get_available_slots():
    """Obtener horarios disponibles"""
    slots = []
    for hour in range(9, 18):  # 9 AM a 6 PM
        slots.append(f"{hour:02d}:00")
        slots.append(f"{hour:02d}:30")
    
    return jsonify({
        "available_slots": slots,
        "services": SERVICES
    })

@app.route("/appointments/create", methods=["POST"])
def create_appointment():
    """Crear una nueva cita"""
    data = request.get_json()
    
    # Simular creación exitosa
    appointment_id = len(data) + 1000  # ID simulado
    
    return jsonify({
        "success": True,
        "appointment_id": appointment_id,
        "message": f"Cita creada exitosamente para el {data.get('date')} a las {data.get('time')}",
        "appointment": data
    })

@app.route("/appointments/user/<user_id>")
def get_user_appointments(user_id):
    """Obtener citas del usuario"""
    # Simular citas existentes
    appointments = [
        {
            "id": 1,
            "service": "Consulta General",
            "date": "2024-01-15",
            "time": "10:00",
            "status": "confirmed"
        }
    ]
    
    return jsonify({"appointments": appointments})

# Sales endpoints
@app.route("/sales/products")
def get_products():
    """Obtener catálogo de productos"""
    return jsonify({"products": PRODUCTS})

@app.route("/sales/products/<int:product_id>")
def get_product(product_id):
    """Obtener producto específico"""
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(product)

@app.route("/sales/purchase", methods=["POST"])
def process_purchase():
    """Procesar una compra"""
    data = request.get_json()
    
    return jsonify({
        "success": True,
        "order_id": f"ORD-{len(data)}",
        "message": "Compra procesada exitosamente",
        "total": data.get("total", 0)
    })

# Support endpoints
@app.route("/support/query", methods=["POST"])
def handle_support_query():
    """Manejar consulta de soporte"""
    data = request.get_json()
    query_text = data.get("query", "").lower()
    
    if any(word in query_text for word in ["devolución", "reembolso"]):
        response = "Nuestra política de devoluciones permite reembolsos dentro de los 30 días de la compra."
    elif any(word in query_text for word in ["garantía", "garantia"]):
        response = "Todos nuestros productos tienen garantía de 1 año."
    elif any(word in query_text for word in ["envío", "envio", "entrega"]):
        response = "Los envíos se realizan en 2-3 días hábiles."
    else:
        response = "Gracias por tu consulta. Un agente te contactará pronto."
    
    return jsonify({
        "response": response,
        "escalated": False,
        "ticket_id": f"TKT-{len(query_text)}"
    })

# Webhook endpoints
@app.route("/webhook/chat", methods=["POST"])
def webhook_chat():
    """Webhook para integración con redes sociales"""
    data = request.get_json()
    return jsonify({"status": "received", "platform": data.get("platform", "unknown")})

@app.route("/webhook/appointment", methods=["POST"])
def webhook_appointment():
    """Webhook para citas desde redes sociales"""
    data = request.get_json()
    return jsonify({"status": "appointment_processed", "data": data})

@app.route("/webhook/sales", methods=["POST"])
def webhook_sales():
    """Webhook para ventas desde redes sociales"""
    data = request.get_json()
    return jsonify({"status": "sale_processed", "data": data})

if __name__ == "__main__":
    print("🚀 Iniciando Chatbot API con Flask...")
    print("📡 Servidor disponible en: http://localhost:8000")
    print("📚 Endpoints disponibles:")
    print("   - GET  /health")
    print("   - POST /chat/send")
    print("   - GET  /appointments/available-slots")
    print("   - POST /appointments/create")
    print("   - GET  /sales/products")
    print("   - POST /support/query")
    app.run(host="0.0.0.0", port=8000, debug=True)