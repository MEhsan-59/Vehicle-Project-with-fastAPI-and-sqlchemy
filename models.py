# models.py
from sqlalchemy import (Column, Integer, String, Date, DateTime, ForeignKey,
                        UniqueConstraint, func)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = "Account"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False, unique=True, index=True)
    user_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_no = Column(String, nullable=False, unique=True, index=True)
    model = Column(String, nullable=False)
    company = Column(String, nullable=False)
    onground_km = Column(Integer, nullable=False, default=0)
    active_user = Column(String, ForeignKey("Account.user_id", ondelete="CASCADE"),
                         nullable=False, index=True)


class Part(Base):
    """Replaces the old `config` table."""
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    part = Column(String, nullable=False, unique=True)
    km_life = Column(Integer, nullable=False)
    month_life = Column(Integer, nullable=False)
    km_limit = Column(Integer, nullable=False)
    day_limit = Column(Integer, nullable=False)


class Maintenance(Base):
    __tablename__ = "maintenance"
    __table_args__ = (UniqueConstraint("vehicle_id", "part_id", name="uq_vehicle_part"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id", ondelete="CASCADE"), nullable=False)
    changed_km = Column(Integer, nullable=False)
    next_changed_km = Column(Integer, nullable=False)
    changed_date = Column(Date, nullable=False)
    next_changed_date = Column(Date, nullable=False)


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    car_no = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)
    part_name = Column(String, nullable=True)
    changed_km = Column(Integer, nullable=True)
    changed_date = Column(Date, nullable=True)
    action_timestamp = Column(DateTime(timezone=False), server_default=func.now())
    active_user = Column(String, nullable=False)
    details = Column(String, nullable=True)
