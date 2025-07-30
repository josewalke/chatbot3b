# 📖 Guía de Instalación - Chatbot Inteligente

## 🚀 Instalación Rápida

### Requisitos Previos

- **Python 3.8+** - Para el backend
- **WordPress 5.0+** - Para el plugin
- **MySQL/SQLite** - Base de datos
- **Node.js 14+** (opcional) - Para desarrollo

### 1. Backend (Python)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/chatbot-inteligente.git
cd chatbot-inteligente

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar el servidor
python main.py
```

### 2. Plugin WordPress

```bash
# Copiar plugin a WordPress
cp -r wordpress-plugin /ruta/a/tu/wordpress/wp-content/plugins/chatbot-inteligente

# Activar desde el panel de administración
# WordPress Admin > Plugins > Chatbot Inteligente > Activar
```

### 3. Configuración Inicial

1. **Configurar API Keys**:
   - OpenAI API Key
   - Stripe Keys (para pagos)
   - PayPal Credentials
   - Tokens de redes sociales

2. **Configurar Base de Datos**:
   - Crear base de datos SQLite (automático)
   - O configurar MySQL/PostgreSQL

3. **Configurar Dominio**:
   - Actualizar URLs en configuración
   - Configurar SSL para producción

## 🔧 Configuración Detallada

### Variables de Entorno (.env)

```env
# Configuración de la aplicación
APP_NAME=Chatbot Inteligente
APP_VERSION=1.0.0
DEBUG=True

# Base de datos
DATABASE_URL=sqlite:///./chatbot.db

# OpenAI
OPENAI_API_KEY=tu-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=150
OPENAI_TEMPERATURE=0.7

# Stripe (pagos)
STRIPE_SECRET_KEY=tu-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=tu-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=tu-stripe-webhook-secret

# PayPal
PAYPAL_CLIENT_ID=tu-paypal-client-id
PAYPAL_CLIENT_SECRET=tu-paypal-client-secret
PAYPAL_MODE=sandbox

# Redes sociales
TELEGRAM_BOT_TOKEN=tu-telegram-bot-token
FACEBOOK_PAGE_ACCESS_TOKEN=tu-facebook-page-access-token
WHATSAPP_BUSINESS_TOKEN=tu-whatsapp-business-token

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-email-password

# Seguridad
SECRET_KEY=tu-secret-key-muy-seguro
```

### Configuración de WordPress

1. **Panel de Administración**:
   - Ir a `Chatbot > Configuración`
   - Configurar URL de la API
   - Agregar API keys

2. **Shortcodes Disponibles**:
   ```php
   [chatbot] // Chatbot completo
   [chatbot_widget] // Widget del chatbot
   ```

3. **Widget**:
   - Ir a `Apariencia > Widgets`
   - Agregar "Chatbot Inteligente" a la barra lateral

## 🌐 Configuración para Redes Sociales

### Telegram

1. **Crear Bot**:
   - Hablar con @BotFather en Telegram
   - Crear nuevo bot con `/newbot`
   - Obtener token

2. **Configurar Webhook**:
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://tu-dominio.com/webhook/telegram"}'
   ```

### Facebook Messenger

1. **Crear App**:
   - Ir a [Facebook Developers](https://developers.facebook.com)
   - Crear nueva aplicación
   - Configurar Messenger

2. **Configurar Webhook**:
   - URL: `https://tu-dominio.com/webhook/facebook`
   - Verify Token: tu-token-secreto

### WhatsApp Business

1. **Configurar API**:
   - Obtener credenciales de WhatsApp Business API
   - Configurar webhook

2. **Verificar Conexión**:
   ```bash
   curl -X POST "https://tu-dominio.com/webhook/whatsapp" \
        -H "Content-Type: application/json" \
        -d '{"test": "message"}'
   ```

## 🗄️ Configuración de Base de Datos

### SQLite (Recomendado para desarrollo)

```python
# Automático - se crea al ejecutar
DATABASE_URL = "sqlite:///./chatbot.db"
```

### MySQL

```python
DATABASE_URL = "mysql+pymysql://usuario:password@localhost/chatbot_db"
```

### PostgreSQL

```python
DATABASE_URL = "postgresql://usuario:password@localhost/chatbot_db"
```

## 🔒 Configuración de Seguridad

### SSL/HTTPS

```nginx
# Nginx configuration
server {
    listen 443 ssl;
    server_name tu-dominio.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall

```bash
# Configurar firewall
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000  # Solo para desarrollo
```

## 📊 Monitoreo y Logs

### Logs de Aplicación

```bash
# Ver logs en tiempo real
tail -f chatbot.log

# Logs de errores
grep "ERROR" chatbot.log
```

### Métricas

```bash
# Estado de la API
curl https://tu-dominio.com/health

# Estadísticas
curl https://tu-dominio.com/api/status
```

## 🚀 Despliegue en Producción

### Usando Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Construir y ejecutar
docker build -t chatbot .
docker run -p 8000:8000 chatbot
```

### Usando Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./chatbot.db
    volumes:
      - ./data:/app/data
```

### Usando PM2

```bash
# Instalar PM2
npm install -g pm2

# Configurar aplicación
pm2 start "python main.py" --name chatbot

# Configurar auto-start
pm2 startup
pm2 save
```

## 🔧 Troubleshooting

### Problemas Comunes

1. **Error de conexión a la API**:
   ```bash
   # Verificar que el servidor esté corriendo
   curl http://localhost:8000/health
   ```

2. **Error de base de datos**:
   ```bash
   # Recrear base de datos
   rm chatbot.db
   python main.py
   ```

3. **Error de permisos**:
   ```bash
   # Dar permisos de escritura
   chmod 755 /ruta/al/chatbot
   chmod 666 chatbot.db
   ```

4. **Error de SSL**:
   ```bash
   # Verificar certificados
   openssl s_client -connect tu-dominio.com:443
   ```

### Logs de Debug

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Soporte

- **Documentación**: [docs/README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/chatbot-inteligente/issues)
- **Email**: soporte@tu-dominio.com

---

**¡Tu chatbot está listo para usar!** 🎉