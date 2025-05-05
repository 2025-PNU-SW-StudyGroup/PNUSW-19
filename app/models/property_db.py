from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Numeric, Float
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class PropertyCCTVMap(Base):
    __tablename__ = "property_cctv_map"
    property_id = Column(BigInteger, primary_key=True)
    cctv_id = Column(BigInteger, primary_key=True)
    distance_meters = Column(Float)

class PropertyRestFoodPermitMap(Base):
    __tablename__ = "property_rest_food_permit_map"
    property_id = Column(BigInteger, primary_key=True)
    rest_food_permit_id = Column(BigInteger, primary_key=True)
    distance_meters = Column(Float)

class PropertyBusStopMap(Base):
    __tablename__ = "property_bus_stop_map"
    property_id = Column(BigInteger, primary_key=True)
    bus_stop_id = Column(BigInteger, primary_key=True)
    distance_meters = Column(Float)

class PropertySubwayMap(Base):
    __tablename__ = "property_subway_map"
    property_id = Column(BigInteger, primary_key=True)
    subway_id = Column(BigInteger, primary_key=True)
    distance_meters = Column(Float)

class Property(Base):
    __tablename__ = "property"

    id = Column(BigInteger, primary_key=True)
    monthly_rent_cost = Column(BigInteger)
    deposit = Column(BigInteger)
    address = Column(String)
    area = Column(Numeric(10, 2))
    floor = Column(Integer)
    property_type = Column(String(50))
    features = Column(String)
    direction = Column(String(10))
    residential_area = Column(String)
    location = Column(Geometry("POINT", srid=4326))
    lot_number = Column(String(100))
    description = Column(String)
    agent_name = Column(String(100))
    agent_office = Column(String(100))
    agent_phone = Column(String(30))
    agent_address = Column(String)
    agent_registration_no = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    property_number = Column(String(100))
    administrative_code = Column(String(20))
    property_name = Column(String)
    transaction_type = Column(String(50))
    confirmation_type = Column(String(50))
    supply_area = Column(Numeric(10, 2))
    property_confirmation_date = Column(DateTime)
    main_image_url = Column(String)
    maintenance_cost = Column(BigInteger)
    rooms_bathrooms = Column(String(50))
    duplex = Column(Boolean, default=False)
    available_move_in_date = Column(String)
    parking_spaces = Column(Integer)
    total_floor = Column(Integer)
    room_type = Column(String)
    elevator_count = Column(Integer)
    household_count = Column(Integer)
    family_count = Column(Integer)
    main_purpose = Column(String(100))
    etc_purpose = Column(String)
    structure_code = Column(String(100))
    approval_date = Column(DateTime)