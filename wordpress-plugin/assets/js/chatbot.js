/**
 * Chatbot Inteligente - JavaScript
 */

class ChatbotInteligente {
    constructor() {
        this.container = null;
        this.messagesContainer = null;
        this.inputField = null;
        this.sendButton = null;
        this.isMinimized = false;
        this.isMaximized = false;
        this.isTyping = false;
        this.userId = chatbot_ajax.user_id;
        this.platform = 'web';
        this.conversationHistory = [];
        this.currentContext = null;
        
        this.init();
    }
    
    init() {
        this.createChatbot();
        this.bindEvents();
        this.showWelcomeMessage();
    }
    
    createChatbot() {
        // Crear contenedor del chatbot
        this.container = document.createElement('div');
        this.container.className = 'chatbot-container';
        this.container.innerHTML = `
            <div class="chatbot-header">
                <h3>🤖 Chatbot Inteligente</h3>
                <div class="chatbot-controls">
                    <button class="minimize-btn" title="Minimizar">−</button>
                    <button class="maximize-btn" title="Maximizar">□</button>
                    <button class="close-btn" title="Cerrar">×</button>
                </div>
            </div>
            <div class="chatbot-body">
                <div class="chatbot-messages"></div>
                <div class="chatbot-input">
                    <input type="text" placeholder="Escribe tu mensaje..." maxlength="500">
                    <button class="send-btn" disabled>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22,2 15,22 11,13 2,9"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.container);
        
        // Obtener referencias a elementos
        this.messagesContainer = this.container.querySelector('.chatbot-messages');
        this.inputField = this.container.querySelector('.chatbot-input input');
        this.sendButton = this.container.querySelector('.send-btn');
    }
    
    bindEvents() {
        // Eventos del header
        this.container.querySelector('.minimize-btn').addEventListener('click', () => this.toggleMinimize());
        this.container.querySelector('.maximize-btn').addEventListener('click', () => this.toggleMaximize());
        this.container.querySelector('.close-btn').addEventListener('click', () => this.close());
        this.container.querySelector('.chatbot-header').addEventListener('click', (e) => {
            if (!e.target.closest('.chatbot-controls')) {
                this.toggleMinimize();
            }
        });
        
        // Eventos del input
        this.inputField.addEventListener('input', () => this.handleInputChange());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.sendButton.addEventListener('click', () => this.sendMessage());
    }
    
    showWelcomeMessage() {
        const welcomeMessage = {
            text: '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?',
            type: 'text',
            intent: 'greeting'
        };
        
        this.addBotMessage(welcomeMessage);
        this.showQuickReplies([
            'Agendar cita',
            'Ver productos',
            'Atención al cliente',
            'Cancelar cita'
        ]);
    }
    
    handleInputChange() {
        const hasText = this.inputField.value.trim().length > 0;
        this.sendButton.disabled = !hasText;
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message || this.isTyping) return;
        
        // Agregar mensaje del usuario
        this.addUserMessage(message);
        this.inputField.value = '';
        this.handleInputChange();
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        try {
            // Enviar mensaje al servidor
            const response = await this.sendMessageToServer(message);
            
            // Ocultar indicador de escritura
            this.hideTypingIndicator();
            
            // Procesar respuesta
            await this.processResponse(response);
            
        } catch (error) {
            console.error('Error enviando mensaje:', error);
            this.hideTypingIndicator();
            this.addBotMessage({
                text: 'Lo siento, tuve un problema procesando tu mensaje. ¿Puedes intentar de nuevo?',
                type: 'text',
                intent: 'error'
            });
        }
    }
    
    async sendMessageToServer(message) {
        const formData = new FormData();
        formData.append('action', 'chatbot_send_message');
        formData.append('nonce', chatbot_ajax.nonce);
        formData.append('user_id', this.userId);
        formData.append('message', message);
        formData.append('platform', this.platform);
        
        const response = await fetch(chatbot_ajax.ajax_url, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Error de red');
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.data || 'Error del servidor');
        }
        
        return data.data;
    }
    
    async processResponse(response) {
        // Agregar mensaje del bot
        this.addBotMessage(response);
        
        // Procesar metadatos si existen
        if (response.metadata) {
            await this.processMetadata(response.metadata);
        }
        
        // Guardar en historial
        this.conversationHistory.push({
            user: this.getLastUserMessage(),
            bot: response
        });
    }
    
    async processMetadata(metadata) {
        const action = metadata.action;
        
        switch (action) {
            case 'show_products':
                await this.showProducts();
                break;
            case 'show_appointment_form':
                this.showAppointmentForm();
                break;
            case 'confirm_appointment':
                this.showAppointmentConfirmation(metadata);
                break;
            case 'show_payment_form':
                this.showPaymentForm(metadata);
                break;
            case 'escalation':
                this.showEscalationMessage();
                break;
        }
    }
    
    async showProducts() {
        try {
            const response = await fetch(`${chatbot_ajax.api_url}/api/v1/sales/products`);
            const data = await response.json();
            
            if (data.products && data.products.length > 0) {
                this.addProductCards(data.products);
            } else {
                this.addBotMessage({
                    text: 'No hay productos disponibles en este momento.',
                    type: 'text'
                });
            }
        } catch (error) {
            console.error('Error obteniendo productos:', error);
            this.addBotMessage({
                text: 'Error obteniendo productos. Intenta más tarde.',
                type: 'text'
            });
        }
    }
    
    showAppointmentForm() {
        const formHtml = `
            <div class="chatbot-appointment-form">
                <h4>📅 Agendar Cita</h4>
                <div class="chatbot-form-group">
                    <label for="service-type">Tipo de servicio:</label>
                    <select id="service-type">
                        <option value="">Selecciona un servicio</option>
                        <option value="consulta">Consulta General</option>
                        <option value="revisión">Revisión Médica</option>
                        <option value="tratamiento">Tratamiento</option>
                        <option value="examen">Examen</option>
                        <option value="limpieza">Limpieza</option>
                    </select>
                </div>
                <div class="chatbot-form-group">
                    <label for="appointment-date">Fecha y hora:</label>
                    <input type="datetime-local" id="appointment-date" required>
                </div>
                <div class="chatbot-form-group">
                    <label for="appointment-notes">Notas adicionales:</label>
                    <textarea id="appointment-notes" rows="3" placeholder="Información adicional..."></textarea>
                </div>
                <div class="chatbot-form-buttons">
                    <button class="chatbot-btn chatbot-btn-primary" onclick="chatbot.createAppointment()">
                        📅 Agendar Cita
                    </button>
                    <button class="chatbot-btn chatbot-btn-secondary" onclick="chatbot.cancelForm()">
                        Cancelar
                    </button>
                </div>
            </div>
        `;
        
        this.addCustomMessage(formHtml, 'bot');
    }
    
    async createAppointment() {
        const serviceType = document.getElementById('service-type').value;
        const appointmentDate = document.getElementById('appointment-date').value;
        const notes = document.getElementById('appointment-notes').value;
        
        if (!serviceType || !appointmentDate) {
            this.addStatusMessage('Por favor completa todos los campos requeridos.', 'warning');
            return;
        }
        
        try {
            const formData = new FormData();
            formData.append('action', 'chatbot_create_appointment');
            formData.append('nonce', chatbot_ajax.nonce);
            formData.append('user_id', this.userId);
            formData.append('service_type', serviceType);
            formData.append('appointment_date', appointmentDate);
            formData.append('notes', notes);
            
            const response = await fetch(chatbot_ajax.ajax_url, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addStatusMessage('✅ Cita agendada exitosamente!', 'success');
                this.addBotMessage({
                    text: `Perfecto! Tu cita ha sido agendada para ${appointmentDate}. Te enviaremos una confirmación pronto.`,
                    type: 'text'
                });
            } else {
                this.addStatusMessage('❌ Error agendando la cita: ' + data.data, 'error');
            }
        } catch (error) {
            console.error('Error creando cita:', error);
            this.addStatusMessage('❌ Error agendando la cita. Intenta más tarde.', 'error');
        }
    }
    
    showPaymentForm(metadata) {
        const formHtml = `
            <div class="chatbot-appointment-form">
                <h4>💳 Procesar Pago</h4>
                <div class="chatbot-form-group">
                    <label for="payment-method">Método de pago:</label>
                    <select id="payment-method">
                        <option value="stripe">Tarjeta de crédito</option>
                        <option value="paypal">PayPal</option>
                    </select>
                </div>
                <div class="chatbot-form-buttons">
                    <button class="chatbot-btn chatbot-btn-success" onclick="chatbot.processPayment()">
                        💳 Pagar $${metadata.amount}
                    </button>
                    <button class="chatbot-btn chatbot-btn-secondary" onclick="chatbot.cancelForm()">
                        Cancelar
                    </button>
                </div>
            </div>
        `;
        
        this.addCustomMessage(formHtml, 'bot');
    }
    
    async processPayment() {
        const paymentMethod = document.getElementById('payment-method').value;
        
        try {
            // Aquí implementarías la lógica de pago
            this.addStatusMessage('💳 Procesando pago...', 'info');
            
            // Simular procesamiento
            setTimeout(() => {
                this.addStatusMessage('✅ Pago procesado exitosamente!', 'success');
                this.addBotMessage({
                    text: '¡Gracias por tu compra! Te enviaremos un email con los detalles.',
                    type: 'text'
                });
            }, 2000);
            
        } catch (error) {
            console.error('Error procesando pago:', error);
            this.addStatusMessage('❌ Error procesando el pago. Intenta más tarde.', 'error');
        }
    }
    
    showEscalationMessage() {
        this.addStatusMessage('👨‍💼 Un agente humano te contactará pronto para ayudarte mejor.', 'info');
    }
    
    addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chatbot-message user';
        messageElement.innerHTML = `
            <div class="chatbot-message-avatar">U</div>
            <div class="chatbot-message-content">${this.escapeHtml(message)}</div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    addBotMessage(response) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chatbot-message bot';
        
        let content = '';
        
        if (response.type === 'text') {
            content = this.escapeHtml(response.text);
        } else if (response.type === 'html') {
            content = response.text;
        }
        
        messageElement.innerHTML = `
            <div class="chatbot-message-avatar">🤖</div>
            <div class="chatbot-message-content">${content}</div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    addCustomMessage(html, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `chatbot-message ${sender}`;
        
        if (sender === 'user') {
            messageElement.innerHTML = `
                <div class="chatbot-message-avatar">U</div>
                <div class="chatbot-message-content">${html}</div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="chatbot-message-avatar">🤖</div>
                <div class="chatbot-message-content">${html}</div>
            `;
        }
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }
    
    addProductCards(products) {
        let productsHtml = '<div style="display: flex; flex-direction: column; gap: 10px;">';
        
        products.forEach(product => {
            productsHtml += `
                <div class="chatbot-product-card">
                    <div class="chatbot-product-image">
                        ${product.image_url ? `<img src="${product.image_url}" alt="${product.name}" style="width: 100%; height: 100%; object-fit: cover;">` : '🛍️'}
                    </div>
                    <div class="chatbot-product-title">${product.name}</div>
                    <div class="chatbot-product-description">${product.description}</div>
                    <div class="chatbot-product-price">$${product.price}</div>
                    <button class="chatbot-btn chatbot-btn-primary" onclick="chatbot.buyProduct('${product.id}')">
                        🛒 Comprar
                    </button>
                </div>
            `;
        });
        
        productsHtml += '</div>';
        
        this.addCustomMessage(productsHtml, 'bot');
    }
    
    async buyProduct(productId) {
        try {
            const formData = new FormData();
            formData.append('action', 'chatbot_process_purchase');
            formData.append('nonce', chatbot_ajax.nonce);
            formData.append('user_id', this.userId);
            formData.append('product_id', productId);
            formData.append('quantity', 1);
            
            const response = await fetch(chatbot_ajax.ajax_url, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addStatusMessage('✅ Producto agregado al carrito!', 'success');
                this.showPaymentForm({
                    amount: data.data.details.total
                });
            } else {
                this.addStatusMessage('❌ Error: ' + data.data, 'error');
            }
        } catch (error) {
            console.error('Error comprando producto:', error);
            this.addStatusMessage('❌ Error procesando la compra.', 'error');
        }
    }
    
    showQuickReplies(replies) {
        const quickRepliesContainer = document.createElement('div');
        quickRepliesContainer.className = 'chatbot-quick-replies';
        
        replies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'chatbot-quick-reply';
            button.textContent = reply;
            button.addEventListener('click', () => {
                this.inputField.value = reply;
                this.sendMessage();
                quickRepliesContainer.remove();
            });
            quickRepliesContainer.appendChild(button);
        });
        
        this.messagesContainer.appendChild(quickRepliesContainer);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        
        const typingElement = document.createElement('div');
        typingElement.className = 'chatbot-typing';
        typingElement.innerHTML = `
            <span>Escribiendo</span>
            <div class="chatbot-typing-dots">
                <div class="chatbot-typing-dot"></div>
                <div class="chatbot-typing-dot"></div>
                <div class="chatbot-typing-dot"></div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingElement);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        const typingElement = this.messagesContainer.querySelector('.chatbot-typing');
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    addStatusMessage(message, type) {
        const statusElement = document.createElement('div');
        statusElement.className = `chatbot-status ${type}`;
        statusElement.textContent = message;
        
        this.messagesContainer.appendChild(statusElement);
        this.scrollToBottom();
    }
    
    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        this.container.classList.toggle('minimized', this.isMinimized);
        
        if (this.isMinimized) {
            this.container.querySelector('.maximize-btn').textContent = '□';
        } else {
            this.container.querySelector('.maximize-btn').textContent = '□';
        }
    }
    
    toggleMaximize() {
        this.isMaximized = !this.isMaximized;
        this.container.classList.toggle('maximized', this.isMaximized);
        
        if (this.isMaximized) {
            this.container.querySelector('.maximize-btn').textContent = '❐';
        } else {
            this.container.querySelector('.maximize-btn').textContent = '□';
        }
    }
    
    close() {
        this.container.remove();
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    getLastUserMessage() {
        const userMessages = this.messagesContainer.querySelectorAll('.chatbot-message.user');
        if (userMessages.length > 0) {
            return userMessages[userMessages.length - 1].querySelector('.chatbot-message-content').textContent;
        }
        return '';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    cancelForm() {
        const form = this.messagesContainer.querySelector('.chatbot-appointment-form');
        if (form) {
            form.remove();
        }
    }
}

// Inicializar chatbot cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotInteligente();
});