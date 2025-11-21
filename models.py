from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from conexion import Base

class IngredienteBD(Base):
    __tablename__ = "ingredientes"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    unidad = Column(String)
    cantidad = Column(Integer, default=0)
    menu_associations = relationship("MenuIngredienteBD", back_populates="ingrediente")

class ClienteBD(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String, nullable=False)
    rut = Column(String, unique=True)
    telefono = Column(String)
    correo = Column(String, unique=True)  
    pedidos = relationship("PedidoBD", back_populates="cliente")

class MenuBD(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String, unique=True, nullable=False)
    precio = Column(Float, nullable=False)
    categoria = Column(String)
    menu_associations = relationship("MenuIngredienteBD", back_populates="menu")

class PedidoBD(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha = Column(DateTime)
    total = Column(Float)
    cliente = relationship("ClienteBD", back_populates="pedidos")

class MenuIngredienteBD(Base):
    __tablename__ = "menu_ingredientes"
    menu_id = Column(Integer, ForeignKey("menus.id", ondelete='CASCADE'), primary_key=True)
    ingrediente_id = Column(Integer, ForeignKey("ingredientes.id", ondelete='CASCADE'), primary_key=True)
    cantidad_necesaria = Column(Integer, nullable=False, default=1)
    menu = relationship("MenuBD", back_populates="menu_associations")
    ingrediente = relationship("IngredienteBD", back_populates="menu_associations")