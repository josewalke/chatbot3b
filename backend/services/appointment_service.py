import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, Appointment, Service, Schedule
import json

logger = logging.getLogger(__name__)

class AppointmentService:
    def __init__(self):
        # Servicios disponibles
        self.services = {
            "consulta": {"name": "Consulta General", "duration": 30, "price": 50},
            "revisión": {"name": "Revisión Médica", "duration": 60, "price": 80},
            "tratamiento": {"name": "Tratamiento", "duration": 90, "price": 120},
            "examen": {"name": "Examen", "duration": 45, "price": 60},
            "limpieza": {"name": "Limpieza", "duration": 30, "price": 40}
        }
        
        # Horarios disponibles (ejemplo)
        self.schedule = {
            0: [{"start": "09:00", "end": "17:00"}],  # Lunes
            1: [{"start": "09:00", "end": "17:00"}],  # Martes
            2: [{"start": "09:00", "end": "17:00"}],  # Miércoles
            3: [{"start": "09:00", "end": "17:00"}],  # Jueves
            4: [{"start": "09:00", "end": "17:00"}],  # Viernes
            5: [{"start": "09:00", "end": "13:00"}],  # Sábado
            6: []  # Domingo cerrado
        }

    async def create_appointment(self, user_id: str, appointment_data: Dict) -> Dict:
        """Crear una nueva cita"""
        try:
            service_type = appointment_data.get("service_type")
            appointment_date = appointment_data.get("appointment_date")
            notes = appointment_data.get("notes", "")
            
            # Validar datos
            if not service_type or not appointment_date:
                return {
                    "success": False,
                    "message": "Faltan datos requeridos: service_type y appointment_date"
                }
            
            # Validar que el servicio existe
            if service_type not in self.services:
                return {
                    "success": False,
                    "message": f"Servicio '{service_type}' no disponible"
                }
            
            # Validar disponibilidad
            availability = await self._check_availability(appointment_date, service_type)
            if not availability["available"]:
                return {
                    "success": False,
                    "message": f"No hay disponibilidad para {appointment_date}. Horarios disponibles: {availability['alternatives']}"
                }
            
            # Crear cita (aquí implementarías la lógica de base de datos)
            appointment_id = await self._save_appointment(user_id, service_type, appointment_date, notes)
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "message": f"Cita creada exitosamente para {appointment_date}",
                "details": {
                    "service": self.services[service_type]["name"],
                    "duration": self.services[service_type]["duration"],
                    "price": self.services[service_type]["price"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error creando cita: {e}")
            return {
                "success": False,
                "message": "Error interno creando la cita"
            }

    async def cancel_appointment(self, user_id: str, appointment_id: str) -> Dict:
        """Cancelar una cita"""
        try:
            # Validar que la cita existe y pertenece al usuario
            appointment = await self._get_appointment(appointment_id, user_id)
            if not appointment:
                return {
                    "success": False,
                    "message": "Cita no encontrada o no tienes permisos para cancelarla"
                }
            
            # Validar que se puede cancelar (no muy próxima)
            if await self._is_appointment_too_close(appointment["appointment_date"]):
                return {
                    "success": False,
                    "message": "No se puede cancelar una cita con menos de 24 horas de anticipación"
                }
            
            # Cancelar cita
            await self._update_appointment_status(appointment_id, "cancelled")
            
            return {
                "success": True,
                "message": f"Cita #{appointment_id} cancelada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error cancelando cita: {e}")
            return {
                "success": False,
                "message": "Error interno cancelando la cita"
            }

    async def reschedule_appointment(self, user_id: str, appointment_id: str, new_datetime: str) -> Dict:
        """Reprogramar una cita"""
        try:
            # Validar que la cita existe y pertenece al usuario
            appointment = await self._get_appointment(appointment_id, user_id)
            if not appointment:
                return {
                    "success": False,
                    "message": "Cita no encontrada o no tienes permisos para reprogramarla"
                }
            
            # Validar disponibilidad para la nueva fecha
            availability = await self._check_availability(new_datetime, appointment["service_type"])
            if not availability["available"]:
                return {
                    "success": False,
                    "message": f"No hay disponibilidad para {new_datetime}. Horarios disponibles: {availability['alternatives']}"
                }
            
            # Reprogramar cita
            await self._update_appointment_datetime(appointment_id, new_datetime)
            
            return {
                "success": True,
                "message": f"Cita #{appointment_id} reprogramada para {new_datetime}",
                "new_datetime": new_datetime
            }
            
        except Exception as e:
            logger.error(f"Error reprogramando cita: {e}")
            return {
                "success": False,
                "message": "Error interno reprogramando la cita"
            }

    async def confirm_appointment(self, user_id: str, appointment_id: str) -> Dict:
        """Confirmar una cita"""
        try:
            # Validar que la cita existe y pertenece al usuario
            appointment = await self._get_appointment(appointment_id, user_id)
            if not appointment:
                return {
                    "success": False,
                    "message": "Cita no encontrada o no tienes permisos para confirmarla"
                }
            
            # Confirmar cita
            await self._update_appointment_status(appointment_id, "confirmed")
            
            return {
                "success": True,
                "message": f"Cita #{appointment_id} confirmada exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error confirmando cita: {e}")
            return {
                "success": False,
                "message": "Error interno confirmando la cita"
            }

    async def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Obtener citas del usuario"""
        try:
            # Aquí implementarías la consulta a la base de datos
            # Por ahora retornamos datos mock
            appointments = [
                {
                    "id": "1",
                    "service_type": "consulta",
                    "appointment_date": "2024-01-15 10:00:00",
                    "status": "confirmed",
                    "service_name": "Consulta General"
                },
                {
                    "id": "2", 
                    "service_type": "revisión",
                    "appointment_date": "2024-01-20 14:00:00",
                    "status": "pending",
                    "service_name": "Revisión Médica"
                }
            ]
            
            return appointments
            
        except Exception as e:
            logger.error(f"Error obteniendo citas: {e}")
            return []

    async def get_available_slots(self, date: str, service_type: str) -> List[str]:
        """Obtener horarios disponibles para una fecha y servicio"""
        try:
            # Obtener día de la semana
            appointment_date = datetime.strptime(date, "%Y-%m-%d")
            day_of_week = appointment_date.weekday()
            
            # Obtener horarios del día
            day_schedule = self.schedule.get(day_of_week, [])
            
            if not day_schedule:
                return []
            
            # Generar slots disponibles
            slots = []
            service_duration = self.services[service_type]["duration"]
            
            for schedule in day_schedule:
                start_time = datetime.strptime(schedule["start"], "%H:%M")
                end_time = datetime.strptime(schedule["end"], "%H:%M")
                
                current_time = start_time
                while current_time + timedelta(minutes=service_duration) <= end_time:
                    slot_time = current_time.strftime("%H:%M")
                    slots.append(slot_time)
                    current_time += timedelta(minutes=30)  # Intervalos de 30 min
            
            return slots
            
        except Exception as e:
            logger.error(f"Error obteniendo slots disponibles: {e}")
            return []

    async def _check_availability(self, appointment_date: str, service_type: str) -> Dict:
        """Verificar disponibilidad para una fecha y servicio"""
        try:
            # Parsear fecha
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
            day_of_week = date_obj.weekday()
            
            # Verificar si el día tiene horarios
            day_schedule = self.schedule.get(day_of_week, [])
            if not day_schedule:
                return {
                    "available": False,
                    "alternatives": "Día no disponible"
                }
            
            # Verificar si la hora está dentro del horario
            time_str = date_obj.strftime("%H:%M")
            service_duration = self.services[service_type]["duration"]
            
            for schedule in day_schedule:
                start_time = datetime.strptime(schedule["start"], "%H:%M")
                end_time = datetime.strptime(schedule["end"], "%H:%M")
                appointment_time = datetime.strptime(time_str, "%H:%M")
                
                if start_time <= appointment_time and appointment_time + timedelta(minutes=service_duration) <= end_time:
                    return {"available": True}
            
            # Si no está disponible, sugerir alternativas
            alternatives = await self.get_available_slots(date_obj.strftime("%Y-%m-%d"), service_type)
            
            return {
                "available": False,
                "alternatives": alternatives[:5]  # Primeros 5 slots disponibles
            }
            
        except Exception as e:
            logger.error(f"Error verificando disponibilidad: {e}")
            return {"available": False, "alternatives": "Error verificando disponibilidad"}

    async def _is_appointment_too_close(self, appointment_date: str) -> bool:
        """Verificar si una cita está muy próxima (menos de 24 horas)"""
        try:
            appointment_datetime = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
            now = datetime.now()
            time_diff = appointment_datetime - now
            
            return time_diff.total_seconds() < 24 * 3600  # 24 horas en segundos
            
        except Exception as e:
            logger.error(f"Error verificando proximidad de cita: {e}")
            return False

    async def _save_appointment(self, user_id: str, service_type: str, appointment_date: str, notes: str) -> str:
        """Guardar cita en base de datos"""
        # Aquí implementarías la lógica de base de datos
        # Por ahora retornamos un ID mock
        appointment_id = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Cita guardada: {appointment_id} - {service_type} - {appointment_date}")
        return appointment_id

    async def _get_appointment(self, appointment_id: str, user_id: str) -> Optional[Dict]:
        """Obtener cita por ID y usuario"""
        # Aquí implementarías la consulta a la base de datos
        # Por ahora retornamos datos mock
        return {
            "id": appointment_id,
            "user_id": user_id,
            "service_type": "consulta",
            "appointment_date": "2024-01-15 10:00:00",
            "status": "confirmed"
        }

    async def _update_appointment_status(self, appointment_id: str, status: str):
        """Actualizar estado de una cita"""
        # Aquí implementarías la lógica de base de datos
        logger.info(f"Estado de cita actualizado: {appointment_id} - {status}")

    async def _update_appointment_datetime(self, appointment_id: str, new_datetime: str):
        """Actualizar fecha/hora de una cita"""
        # Aquí implementarías la lógica de base de datos
        logger.info(f"Fecha de cita actualizada: {appointment_id} - {new_datetime}")