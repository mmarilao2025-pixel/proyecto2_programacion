from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import ClienteBD

class ClienteCRUD:
    @staticmethod
    def crear_cliente(db: Session, nombre: str, rut: str, telefono: str):
        cliente_existente = db.query(ClienteBD).filter_by(rut=rut).first()
        if cliente_existente:
            print(f"El cliente con el email '{rut}' ya existe.")
            return cliente_existente
        cliente = ClienteBD(nombre=nombre, rut=rut, telefono=telefono)
        db.add(cliente)
        try:
            db.commit()
            db.refresh(cliente)
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al crear el cliente: {e}")
            return None
        return cliente

    @staticmethod
    def leer_clientes(db: Session):
        """Obtiene todos los clientes en la base de datos."""
        return db.query(ClienteBD).all()

    @staticmethod
    def actualizar_cliente(db: Session, nuevo_nombre, nuevo_rut, actual_rut= str, nuevo_telefono= str):
        cliente = db.query(ClienteBD).get(actual_rut)
        if not cliente:
            print(f"No se encontró el cliente con el rut '{actual_rut}'.")
            return None

        if nuevo_rut and nuevo_rut != actual_rut:
            nuevo_cliente = ClienteBD(nombre=nuevo_nombre, rut=nuevo_rut, telefono= nuevo_telefono)
            db.add(nuevo_cliente)
            try:
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al actualizar el cliente con nuevo rut: {e}")
                return None

            db.delete(cliente)
            try:
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al eliminar el cliente antiguo: {e}")
                return None

            return nuevo_cliente
        else:
            cliente.nombre = nuevo_nombre
            cliente.telefono = nuevo_telefono
            try:
                db.commit()
                db.refresh(cliente)
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al actualizar el cliente: {e}")
                return None
            return cliente

    @staticmethod
    def borrar_cliente(db: Session, rut: str):
        cliente = db.query(ClienteBD).get(rut)
        if cliente:
            db.delete(cliente)
            try:
                db.commit()
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Error al borrar el cliente: {e}")
                return None
            return cliente
        return None   