from flask import Blueprint, request, jsonify
from app.models import ProductionLine, ShiftRecord, Defect, LiveDataStream
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Production Lines
@api_bp.route('/lines', methods=['GET'])
def get_lines():
    lines = ProductionLine.query.all()
    return jsonify([l.to_dict() for l in lines])

@api_bp.route('/lines', methods=['POST'])
def create_line():
    data = request.get_json()
    line = ProductionLine(
        name=data.get('name'),
        location=data.get('location')
    )
    db.session.add(line)
    db.session.commit()
    return jsonify(line.to_dict()), 201

# Shift Records
@api_bp.route('/shift-records', methods=['GET'])
def get_shift_records():
    line_id = request.args.get('line_id')
    shift = request.args.get('shift')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    limit = request.args.get('limit', 100, type=int)
    
    query = ShiftRecord.query
    
    if line_id:
        query = query.filter_by(line_id=line_id)
    if shift:
        query = query.filter_by(shift=shift)
    if date_from:
        query = query.filter(ShiftRecord.date >= date_from)
    if date_to:
        query = query.filter(ShiftRecord.date <= date_to)
    
    records = query.order_by(ShiftRecord.date.desc()).limit(limit).all()
    return jsonify([r.to_dict() for r in records])

@api_bp.route('/shift-records', methods=['POST'])
def create_shift_record():
    data = request.get_json()
    
    record = ShiftRecord(
        line_id=data.get('line_id'),
        date=datetime.fromisoformat(data.get('date')).date(),
        shift=data.get('shift'),
        planned_minutes=data.get('planned_minutes', 480),
        run_minutes=data.get('run_minutes', 0),
        downtime_minutes=data.get('downtime_minutes', 0),
        target_units=data.get('target_units', 0),
        actual_units=data.get('actual_units', 0),
        good_units=data.get('good_units', 0),
        defective_units=data.get('defective_units', 0)
    )
    
    record.calculate_kpis()
    db.session.add(record)
    db.session.commit()
    
    return jsonify(record.to_dict()), 201

# KPI Summary
@api_bp.route('/kpi-summary', methods=['GET'])
def get_kpi_summary():
    line_id = request.args.get('line_id')
    days = request.args.get('days', 14, type=int)
    
    date_from = (datetime.now() - timedelta(days=days)).date()
    
    query = ShiftRecord.query.filter(ShiftRecord.date >= date_from)
    if line_id:
        query = query.filter_by(line_id=line_id)
    
    records = query.all()
    
    if not records:
        return jsonify({
            'availability': 0,
            'performance': 0,
            'quality': 0,
            'oee': 0,
            'total_units': 0,
            'good_units': 0,
            'defective_units': 0
        })
    
    total_run_minutes = sum(r.run_minutes for r in records)
    total_planned_minutes = sum(r.planned_minutes for r in records)
    total_actual_units = sum(r.actual_units for r in records)
    total_target_units = sum(r.target_units for r in records)
    total_good_units = sum(r.good_units for r in records)
    total_defective = sum(r.defective_units for r in records)
    
    availability = (total_run_minutes / total_planned_minutes * 100) if total_planned_minutes > 0 else 0
    performance = (total_actual_units / total_target_units * 100) if total_target_units > 0 else 0
    quality = (total_good_units / total_actual_units * 100) if total_actual_units > 0 else 0
    oee = (availability * performance * quality) / 10000
    
    return jsonify({
        'availability': round(availability, 2),
        'performance': round(performance, 2),
        'quality': round(quality, 2),
        'oee': round(oee, 2),
        'total_units': total_actual_units,
        'good_units': total_good_units,
        'defective_units': total_defective,
        'period_days': days
    })

# Trend Data
@api_bp.route('/trend', methods=['GET'])
def get_trend():
    line_id = request.args.get('line_id')
    days = request.args.get('days', 14, type=int)
    
    date_from = (datetime.now() - timedelta(days=days)).date()
    
    query = ShiftRecord.query.filter(ShiftRecord.date >= date_from)
    if line_id:
        query = query.filter_by(line_id=line_id)
    
    records = query.order_by(ShiftRecord.date).all()
    
    # Group by date
    daily_data = {}
    for record in records:
        date_key = record.date.isoformat()
        if date_key not in daily_data:
            daily_data[date_key] = []
        daily_data[date_key].append(record)
    
    trend = []
    for date_key in sorted(daily_data.keys()):
        records = daily_data[date_key]
        avg_oee = sum(r.oee for r in records) / len(records)
        trend.append({
            'date': date_key,
            'oee': round(avg_oee, 2),
            'availability': round(sum(r.availability for r in records) / len(records), 2),
            'performance': round(sum(r.performance for r in records) / len(records), 2),
            'quality': round(sum(r.quality for r in records) / len(records), 2)
        })
    
    return jsonify(trend)

# Defect Analysis
@api_bp.route('/defects', methods=['GET'])
def get_defects():
    line_id = request.args.get('line_id')
    days = request.args.get('days', 14, type=int)
    
    date_from = (datetime.now() - timedelta(days=days)).date()
    
    query = Defect.query.join(ShiftRecord).filter(
        ShiftRecord.date >= date_from
    )
    if line_id:
        query = query.filter(ShiftRecord.line_id == line_id)
    
    defects = query.all()
    
    # Aggregate by type
    defect_summary = {}
    for defect in defects:
        defect_type = defect.defect_type
        if defect_type not in defect_summary:
            defect_summary[defect_type] = 0
        defect_summary[defect_type] += defect.count
    
    return jsonify(defect_summary)

# Live Data Stream
@api_bp.route('/live-data', methods=['GET'])
def get_live_data():
    line_id = request.args.get('line_id')
    limit = request.args.get('limit', 100, type=int)
    
    query = LiveDataStream.query
    if line_id:
        query = query.filter_by(line_id=line_id)
    
    data = query.order_by(LiveDataStream.timestamp.desc()).limit(limit).all()
    return jsonify([d.to_dict() for d in data])

@api_bp.route('/live-data', methods=['POST'])
def create_live_data():
    data = request.get_json()
    
    stream = LiveDataStream(
        line_id=data.get('line_id'),
        current_rate=data.get('current_rate'),
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        line_status=data.get('line_status'),
        error_code=data.get('error_code')
    )
    
    db.session.add(stream)
    db.session.commit()
    
    return jsonify(stream.to_dict()), 201
