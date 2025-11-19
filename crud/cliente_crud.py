from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import ClienteBD

class ClienteCRUD:
    @staticmethod
    def crear_cliente(db: Session, nombre: str, rut: str, telefono: str):
        """Crea un nuevo cliente validando RUT único"""
        cliente_existente = db.query(ClienteBD).filter_by(rut=rut).first()
        if cliente_existente:
            raise ValueError(f"El cliente con RUT '{rut}' ya existe.")
        
        cliente = ClienteBD(nombre=nombre, rut=rut, telefono=telefono)
        db.add(cliente)
        try:
            db.commit()
            db.refresh(cliente)
            return cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al crear el cliente: {e}")
#__________________________________________________________________________
    @staticmethod
    def leer_clientes(db: Session):
        """Obtiene todos los clientes"""
        return db.query(ClienteBD).all()

    @staticmethod
    def leer_cliente_por_id(db: Session, cliente_id: int):
        """Busca cliente por ID"""
        return db.query(ClienteBD).filter_by(id=cliente_id).first()
    
    @staticmethod
    def leer_cliente_por_rut(db: Session, rut: str):
        """Busca cliente por RUT"""
        return db.query(ClienteBD).filter_by(rut=rut).first()
#_____________________________________________________________________

    @staticmethod
    def actualizar_cliente(db: Session, rut_actual: str, nuevo_nombre: str = None, 
                          nuevo_telefono: str = None):
        """Actualiza cliente existente"""
        cliente = db.query(ClienteBD).filter_by(rut=rut_actual).first()
        if not cliente:
            raise ValueError(f"Cliente con RUT '{rut_actual}' no encontrado.")
        
        if nuevo_nombre:
            cliente.nombre = nuevo_nombre
        if nuevo_telefono:
            cliente.telefono = nuevo_telefono
            
        try:
            db.commit()
            db.refresh(cliente)
            return cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar cliente: {e}")
    
    @staticmethod
    def actualizar_cliente_por_id(db: Session, cliente_id: int, nuevo_nombre: str = None, 
                                 nuevo_telefono: str = None):
        """Actualiza cliente existente por ID"""
        cliente = db.query(ClienteBD).filter_by(id=cliente_id).first()
        if not cliente:
            raise ValueError(f"Cliente con ID {cliente_id} no encontrado.")
        
        if nuevo_nombre:
            cliente.nombre = nuevo_nombre
        if nuevo_telefono:
            cliente.telefono = nuevo_telefono
            
        try:
            db.commit()
            db.refresh(cliente)
            return cliente
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al actualizar cliente: {e}")
#________________________________________________________________________________
    @staticmethod
    def borrar_cliente(db: Session, rut: str):
        """Elimina cliente por RUT"""
        cliente = db.query(ClienteBD).filter_by(rut=rut).first()
        if not cliente:
            raise ValueError(f"Cliente con RUT '{rut}' no encontrado.")
        
        # Verificar si tiene pedidos asociados
        if cliente.pedidos:
            raise ValueError("No se puede eliminar cliente con pedidos asociados.")
            
        db.delete(cliente)
        try:
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise Exception(f"Error al eliminar cliente: {e}")