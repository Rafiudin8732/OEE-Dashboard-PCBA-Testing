from app import db
from datetime import datetime
import uuid

class ProductionLine(db.Model):
    __tablename__ = 'production_lines'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default='IDLE')  # IDLE, RUNNING, STOPPED, ERROR
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shift_records = db.relationship('ShiftRecord', backref='production_line', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ShiftRecord(db.Model):
    __tablename__ = 'shift_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    line_id = db.Column(db.String(36), db.ForeignKey('production_lines.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift = db.Column(db.String(50), nullable=False)  # Day, Swing, Night
    
    # Availability metrics
    planned_minutes = db.Column(db.Integer, default=480)
    run_minutes = db.Column(db.Integer, default=0)
    downtime_minutes = db.Column(db.Integer, default=0)
    
    # Performance metrics
    target_units = db.Column(db.Integer, default=0)
    actual_units = db.Column(db.Integer, default=0)
    
    # Quality metrics
    good_units = db.Column(db.Integer, default=0)
    defective_units = db.Column(db.Integer, default=0)
    
    # Calculated KPIs
    availability = db.Column(db.Float, default=0.0)
    performance = db.Column(db.Float, default=0.0)
    quality = db.Column(db.Float, default=0.0)
    oee = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    defects = db.relationship('Defect', backref='shift_record', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_kpis(self):
        """Calculate OEE and component metrics"""
        if self.planned_minutes > 0:
            self.availability = (self.run_minutes / self.planned_minutes) * 100
        
        if self.target_units > 0:
            self.performance = (self.actual_units / self.target_units) * 100
        else:
            self.performance = 0
        
        if self.actual_units > 0:
            self.quality = (self.good_units / self.actual_units) * 100
        else:
            self.quality = 0
        
        # OEE = Availability x Performance x Quality / 10000
        self.oee = (self.availability * self.performance * self.quality) / 10000
        
        return self
    
    def to_dict(self):
        return {
            'id': self.id,
            'line_id': self.line_id,
            'line_name': self.production_line.name,
            'date': self.date.isoformat(),
            'shift': self.shift,
            'planned_minutes': self.planned_minutes,
            'run_minutes': self.run_minutes,
            'downtime_minutes': self.downtime_minutes,
            'target_units': self.target_units,
            'actual_units': self.actual_units,
            'good_units': self.good_units,
            'defective_units': self.defective_units,
            'availability': round(self.availability, 2),
            'performance': round(self.performance, 2),
            'quality': round(self.quality, 2),
            'oee': round(self.oee, 2),
            'created_at': self.created_at.isoformat()
        }

class Defect(db.Model):
    __tablename__ = 'defects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shift_record_id = db.Column(db.String(36), db.ForeignKey('shift_records.id'), nullable=False)
    defect_type = db.Column(db.String(100), nullable=False)  # AOI, ICT, Solder, Labeling, Mechanical
    count = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'shift_record_id': self.shift_record_id,
            'defect_type': self.defect_type,
            'count': self.count,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class LiveDataStream(db.Model):
    __tablename__ = 'live_data_streams'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    line_id = db.Column(db.String(36), db.ForeignKey('production_lines.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Live metrics
    current_rate = db.Column(db.Float)  # units per hour
    temperature = db.Column(db.Float)  # Celsius
    humidity = db.Column(db.Float)  # Percentage
    line_status = db.Column(db.String(50))  # RUNNING, STOPPED, ERROR
    error_code = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'line_id': self.line_id,
            'timestamp': self.timestamp.isoformat(),
            'current_rate': self.current_rate,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'line_status': self.line_status,
            'error_code': self.error_code
        }
