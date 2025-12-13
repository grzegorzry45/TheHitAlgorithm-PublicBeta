from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    presets = relationship("Preset", back_populates="owner")

class Preset(Base):
    __tablename__ = "presets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    profile = Column(JSON)  # Stores the statistical profile
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="presets")