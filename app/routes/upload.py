from flask import Blueprint, request, jsonify, current_app
from app.models import ProductionLine, ShiftRecord, Defect
from app import db
import pandas as pd
import os
from datetime import datetime
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload/production-data', methods=['POST'])
def upload_production_data():
    """Upload production data from CSV or Excel"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File format not allowed. Use CSV or XLSX'}), 400
    
    try:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Read file
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Validate required columns
        required_cols = {'date', 'line', 'shift', 'planned_minutes', 'run_minutes',
                        'target_units', 'actual_units', 'good_units'}
        if not required_cols.issubset(set(df.columns)):
            return jsonify({
                'error': f'Missing required columns. Expected: {required_cols}'
            }), 400
        
        # Import data
        records_created = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Get or create line
                line = ProductionLine.query.filter_by(name=row['line']).first()
                if not line:
                    line = ProductionLine(name=row['line'])
                    db.session.add(line)
                    db.session.flush()
                
                # Parse date
                if isinstance(row['date'], str):
                    record_date = datetime.fromisoformat(row['date']).date()
                else:
                    record_date = row['date']
                
                # Create shift record
                existing = ShiftRecord.query.filter_by(
                    line_id=line.id,
                    date=record_date,
                    shift=row['shift']
                ).first()
                
                if existing:
                    # Update existing record
                    existing.planned_minutes = int(row['planned_minutes'])
                    existing.run_minutes = int(row['run_minutes'])
                    existing.target_units = int(row['target_units'])
                    existing.actual_units = int(row['actual_units'])
                    existing.good_units = int(row['good_units'])
                    existing.defective_units = int(row['actual_units']) - int(row['good_units'])
                    existing.calculate_kpis()
                else:
                    # Create new record
                    shift_record = ShiftRecord(
                        line_id=line.id,
                        date=record_date,
                        shift=row['shift'],
                        planned_minutes=int(row['planned_minutes']),
                        run_minutes=int(row['run_minutes']),
                        target_units=int(row['target_units']),
                        actual_units=int(row['actual_units']),
                        good_units=int(row['good_units']),
                        defective_units=int(row['actual_units']) - int(row['good_units'])
                    )
                    shift_record.calculate_kpis()
                    db.session.add(shift_record)
                
                records_created += 1
            
            except Exception as e:
                errors.append(f'Row {idx + 1}: {str(e)}')
        
        db.session.commit()
        os.remove(filepath)  # Clean up temp file
        
        return jsonify({
            'success': True,
            'records_imported': records_created,
            'errors': errors,
            'total_rows': len(df)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/upload/defect-data', methods=['POST'])
def upload_defect_data():
    """Upload defect data from CSV or Excel"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File format not allowed. Use CSV or XLSX'}), 400
    
    try:
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Read file
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
        
        # Validate required columns
        required_cols = {'date', 'line', 'shift', 'defect_type', 'count'}
        if not required_cols.issubset(set(df.columns)):
            return jsonify({
                'error': f'Missing required columns. Expected: {required_cols}'
            }), 400
        
        # Import data
        defects_created = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Find shift record
                if isinstance(row['date'], str):
                    record_date = datetime.fromisoformat(row['date']).date()
                else:
                    record_date = row['date']
                
                line = ProductionLine.query.filter_by(name=row['line']).first()
                if not line:
                    errors.append(f'Row {idx + 1}: Line {row["line"]} not found')
                    continue
                
                shift_record = ShiftRecord.query.filter_by(
                    line_id=line.id,
                    date=record_date,
                    shift=row['shift']
                ).first()
                
                if not shift_record:
                    errors.append(f'Row {idx + 1}: Shift record not found for {row["line"]} on {record_date}')
                    continue
                
                # Create or update defect
                defect = Defect.query.filter_by(
                    shift_record_id=shift_record.id,
                    defect_type=row['defect_type']
                ).first()
                
                if defect:
                    defect.count = int(row['count'])
                else:
                    defect = Defect(
                        shift_record_id=shift_record.id,
                        defect_type=row['defect_type'],
                        count=int(row['count']),
                        description=row.get('description', '')
                    )
                    db.session.add(defect)
                
                defects_created += 1
            
            except Exception as e:
                errors.append(f'Row {idx + 1}: {str(e)}')
        
        db.session.commit()
        os.remove(filepath)  # Clean up temp file
        
        return jsonify({
            'success': True,
            'defects_imported': defects_created,
            'errors': errors,
            'total_rows': len(df)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
