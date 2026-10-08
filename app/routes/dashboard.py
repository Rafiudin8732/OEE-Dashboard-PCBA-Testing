from flask import Blueprint, render_template
from app.models import ProductionLine, ShiftRecord
from app import db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def main_dashboard():
    # Get latest data for dashboard
    today = datetime.now().date()
    
    lines = ProductionLine.query.all()
    today_records = ShiftRecord.query.filter(
        ShiftRecord.date == today
    ).all()
    
    context = {
        'lines': [l.to_dict() for l in lines],
        'today_records': [r.to_dict() for r in today_records],
        'current_date': today.isoformat()
    }
    
    return render_template('dashboard.html', **context)
