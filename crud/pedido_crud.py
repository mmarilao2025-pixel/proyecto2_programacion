from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import PedidoBD, ClienteBD
from datetime import datetime

class PedidoCRUD:
    @staticmethod
    def crear_pedido(db: Session, cliente_rut: str, total: float):
        """Crea nuevo pedido asociado a cliente"""
        cliente = db.query(ClienteBD).filter_by(rut=cliente_rut).first()
        if not cliente:
            raise ValueError(f"Cliente con RUT '{cliente_rut}' no encontrado.")
        
        if total <= 0:
            raise ValueError("El total debe ser mayor a 0.")
            
        pedido = PedidoBD(cliente_id=cliente.id, total=total, fecha=datetime.now())
        db.add(pedido)
        try:
            db.commit()
            db.refresh(pedido)
            return pedido
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al crear pedido: {e}")
#_______________________________________________________________-
    @staticmethod
    def leer_pedidos(db: Session):
        """Obtiene todos los pedidos con información de cliente"""
        return db.query(PedidoBD).join(ClienteBD).all()

    @staticmethod
    def leer_pedido_por_id(db: Session, pedido_id: int):
        """Busca pedido por ID"""
        return db.query(PedidoBD).filter_by(id=pedido_id).first()

    @staticmethod
    def leer_pedidos_por_cliente(db: Session, cliente_rut: str):
        """Filtra pedidos por cliente"""
        cliente = db.query(ClienteBD).filter_by(rut=cliente_rut).first()
        if not cliente:
            raise ValueError(f"Cliente con RUT '{cliente_rut}' no encontrado.")
            
        return db.query(PedidoBD).filter_by(cliente_id=cliente.id).all()

    @staticmethod
    def leer_pedidos_por_fecha(db: Session, fecha: datetime):
        """Filtra pedidos por fecha específica"""
        return db.query(PedidoBD).filter(
            db.func.date(PedidoBD.fecha) == fecha.date()
        ).all()
#_______________________________________________________________________
    @staticmethod
    def actualizar_pedido(db: Session, pedido_id: int, nuevo_total: float = None):
        """Actualiza total de pedido"""
        pedido = db.query(PedidoBD).get(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido con ID {pedido_id} no encontrado.")
        
        if nuevo_total is not None:
            if nuevo_total <= 0:
                raise ValueError("El total debe ser mayor a 0.")
            pedido.total = nuevo_total
            
        try:
            db.commit()
            db.refresh(pedido)
            return pedido
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar pedido: {e}")
#_____________________________________________________________
    @staticmethod
    def eliminar_pedido(db: Session, pedido_id: int):
        """Elimina pedido por ID"""
        pedido = db.query(PedidoBD).get(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido con ID {pedido_id} no encontrado.")
            
        db.delete(pedido)
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar pedido: {e}")