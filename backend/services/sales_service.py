import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, Product, Sale
import json
import stripe
import paypalrestsdk

logger = logging.getLogger(__name__)

class SalesService:
    def __init__(self):
        # Configurar Stripe (gratuito con límites)
        stripe.api_key = "your-stripe-secret-key"  # Configurar en .env
        
        # Configurar PayPal (gratuito)
        paypalrestsdk.configure({
            "mode": "sandbox",  # Cambiar a "live" para producción
            "client_id": "your-paypal-client-id",
            "client_secret": "your-paypal-client-secret"
        })
        
        # Catálogo de productos (ejemplo)
        self.products = {
            "1": {
                "id": "1",
                "name": "Producto Premium",
                "description": "Producto de alta calidad con garantía",
                "price": 99.99,
                "stock": 50,
                "category": "premium",
                "image_url": "https://example.com/product1.jpg"
            },
            "2": {
                "id": "2", 
                "name": "Servicio Básico",
                "description": "Servicio esencial para tus necesidades",
                "price": 29.99,
                "stock": 100,
                "category": "basic",
                "image_url": "https://example.com/product2.jpg"
            },
            "3": {
                "id": "3",
                "name": "Paquete Completo",
                "description": "Todo lo que necesitas en un solo paquete",
                "price": 149.99,
                "stock": 25,
                "category": "package",
                "image_url": "https://example.com/product3.jpg"
            }
        }

    async def get_products(self) -> List[Dict]:
        """Obtener catálogo de productos"""
        try:
            # Aquí implementarías la consulta a la base de datos
            # Por ahora retornamos productos mock
            return list(self.products.values())
            
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            return []

    async def get_product(self, product_id: str) -> Optional[Dict]:
        """Obtener producto específico"""
        try:
            return self.products.get(product_id)
            
        except Exception as e:
            logger.error(f"Error obteniendo producto: {e}")
            return None

    async def process_purchase(self, user_id: str, product_id: str, quantity: int = 1) -> Dict:
        """Procesar compra de producto"""
        try:
            # Obtener producto
            product = await self.get_product(product_id)
            if not product:
                return {
                    "success": False,
                    "message": "Producto no encontrado"
                }
            
            # Verificar stock
            if product["stock"] < quantity:
                return {
                    "success": False,
                    "message": f"Stock insuficiente. Disponible: {product['stock']}"
                }
            
            # Calcular total
            total_amount = product["price"] * quantity
            
            # Crear venta
            sale_id = await self._create_sale(user_id, product_id, quantity, total_amount)
            
            return {
                "success": True,
                "sale_id": sale_id,
                "message": f"Compra procesada exitosamente",
                "details": {
                    "product": product["name"],
                    "quantity": quantity,
                    "total": total_amount,
                    "payment_url": await self._create_payment_link(sale_id, total_amount)
                }
            }
            
        except Exception as e:
            logger.error(f"Error procesando compra: {e}")
            return {
                "success": False,
                "message": "Error interno procesando la compra"
            }

    async def process_payment(self, sale_id: str, payment_method: str, payment_data: Dict) -> Dict:
        """Procesar pago"""
        try:
            # Obtener venta
            sale = await self._get_sale(sale_id)
            if not sale:
                return {
                    "success": False,
                    "message": "Venta no encontrada"
                }
            
            # Procesar pago según método
            if payment_method == "stripe":
                result = await self._process_stripe_payment(sale, payment_data)
            elif payment_method == "paypal":
                result = await self._process_paypal_payment(sale, payment_data)
            else:
                return {
                    "success": False,
                    "message": "Método de pago no soportado"
                }
            
            if result["success"]:
                # Actualizar estado de venta
                await self._update_sale_status(sale_id, "completed", result["payment_id"])
                
                # Actualizar stock
                await self._update_product_stock(sale["product_id"], sale["quantity"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error procesando pago: {e}")
            return {
                "success": False,
                "message": "Error interno procesando el pago"
            }

    async def get_user_purchases(self, user_id: str) -> List[Dict]:
        """Obtener compras del usuario"""
        try:
            # Aquí implementarías la consulta a la base de datos
            # Por ahora retornamos datos mock
            purchases = [
                {
                    "id": "1",
                    "product_name": "Producto Premium",
                    "quantity": 1,
                    "total_amount": 99.99,
                    "status": "completed",
                    "created_at": "2024-01-10 15:30:00"
                },
                {
                    "id": "2",
                    "product_name": "Servicio Básico", 
                    "quantity": 2,
                    "total_amount": 59.98,
                    "status": "pending",
                    "created_at": "2024-01-12 10:15:00"
                }
            ]
            
            return purchases
            
        except Exception as e:
            logger.error(f"Error obteniendo compras: {e}")
            return []

    async def _create_sale(self, user_id: str, product_id: str, quantity: int, total_amount: float) -> str:
        """Crear venta en base de datos"""
        # Aquí implementarías la lógica de base de datos
        # Por ahora retornamos un ID mock
        sale_id = f"SALE{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Venta creada: {sale_id} - Producto: {product_id} - Cantidad: {quantity}")
        return sale_id

    async def _get_sale(self, sale_id: str) -> Optional[Dict]:
        """Obtener venta por ID"""
        # Aquí implementarías la consulta a la base de datos
        # Por ahora retornamos datos mock
        return {
            "id": sale_id,
            "user_id": "user123",
            "product_id": "1",
            "quantity": 1,
            "total_amount": 99.99,
            "status": "pending"
        }

    async def _process_stripe_payment(self, sale: Dict, payment_data: Dict) -> Dict:
        """Procesar pago con Stripe"""
        try:
            # Crear intent de pago
            payment_intent = stripe.PaymentIntent.create(
                amount=int(sale["total_amount"] * 100),  # Stripe usa centavos
                currency="usd",
                metadata={
                    "sale_id": sale["id"],
                    "product_id": sale["product_id"]
                }
            )
            
            return {
                "success": True,
                "payment_id": payment_intent.id,
                "client_secret": payment_intent.client_secret
            }
            
        except Exception as e:
            logger.error(f"Error procesando pago con Stripe: {e}")
            return {
                "success": False,
                "message": "Error procesando pago con Stripe"
            }

    async def _process_paypal_payment(self, sale: Dict, payment_data: Dict) -> Dict:
        """Procesar pago con PayPal"""
        try:
            # Crear pago de PayPal
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(sale["total_amount"]),
                        "currency": "USD"
                    },
                    "description": f"Compra {sale['id']}"
                }]
            })
            
            if payment.create():
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "approval_url": payment.links[1].href
                }
            else:
                return {
                    "success": False,
                    "message": "Error creando pago con PayPal"
                }
            
        except Exception as e:
            logger.error(f"Error procesando pago con PayPal: {e}")
            return {
                "success": False,
                "message": "Error procesando pago con PayPal"
            }

    async def _create_payment_link(self, sale_id: str, amount: float) -> str:
        """Crear enlace de pago"""
        try:
            # Crear enlace de pago con Stripe
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Compra {sale_id}",
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }],
                metadata={
                    "sale_id": sale_id
                }
            )
            
            return payment_link.url
            
        except Exception as e:
            logger.error(f"Error creando enlace de pago: {e}")
            return ""

    async def _update_sale_status(self, sale_id: str, status: str, payment_id: str = None):
        """Actualizar estado de venta"""
        # Aquí implementarías la lógica de base de datos
        logger.info(f"Estado de venta actualizado: {sale_id} - {status}")

    async def _update_product_stock(self, product_id: str, quantity: int):
        """Actualizar stock de producto"""
        # Aquí implementarías la lógica de base de datos
        logger.info(f"Stock actualizado: Producto {product_id} - Cantidad: -{quantity}")

    async def get_categories(self) -> List[str]:
        """Obtener categorías de productos"""
        try:
            categories = set()
            for product in self.products.values():
                categories.add(product["category"])
            return list(categories)
            
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {e}")
            return []

    async def get_products_by_category(self, category: str) -> List[Dict]:
        """Obtener productos por categoría"""
        try:
            products = []
            for product in self.products.values():
                if product["category"] == category:
                    products.append(product)
            return products
            
        except Exception as e:
            logger.error(f"Error obteniendo productos por categoría: {e}")
            return []