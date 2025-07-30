from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime

class User(Base):
    """Modelo de usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    platform = Column(String, default="web")  # web, telegram, whatsapp, facebook
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    appointments = relationship("Appointment", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    sales = relationship("Sale", back_populates="user")

class Appointment(Base):
    """Modelo de cita"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_type = Column(String)  # consulta, revisión, etc.
    appointment_date = Column(DateTime)
    duration = Column(Integer, default=60)  # minutos
    status = Column(String, default="pending")  # pending, confirmed, cancelled, completed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="appointments")

class Product(Base):
    """Modelo de producto"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Sale(Base):
    """Modelo de venta"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, completed, cancelled
    payment_method = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="sales")
    product = relationship("Product")

class Conversation(Base):
    """Modelo de conversación"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, nullable=False)
    platform = Column(String, default="web")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    """Modelo de mensaje"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, file, button
    sender = Column(String, default="user")  # user, bot
    metadata = Column(JSON, nullable=True)  # Para datos adicionales
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    conversation = relationship("Conversation", back_populates="messages")

class BotResponse(Base):
    """Modelo de respuesta del bot"""
    __tablename__ = "bot_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    intent = Column(String, nullable=False)
    response_text = Column(Text, nullable=False)
    response_type = Column(String, default="text")  # text, button, image, quick_reply
    metadata = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Service(Base):
    """Modelo de servicio disponible"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, default=60)  # minutos
    price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Schedule(Base):
    """Modelo de horario disponible"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Lunes, 6=Domingo
    start_time = Column(String, nullable=False)  # HH:MM
    end_time = Column(String, nullable=False)  # HH:MM
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())