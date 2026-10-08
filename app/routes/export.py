from flask import Blueprint, request, jsonify, send_file
from app.models import ShiftRecord, Defect
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO, StringIO
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

export_bp = Blueprint('export', __name__, url_prefix='/api/export')

@export_bp.route('/excel', methods=['POST'])
def export_excel():
    """Export shift data to Excel"""
    data = request.get_json()
    
    line_id = data.get('line_id')
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    
    # Query data
    query = ShiftRecord.query
    if line_id:
        query = query.filter_by(line_id=line_id)
    if date_from:
        query = query.filter(ShiftRecord.date >= date_from)
    if date_to:
        query = query.filter(ShiftRecord.date <= date_to)
    
    records = query.order_by(ShiftRecord.date).all()
    
    # Convert to DataFrame
    data_list = [r.to_dict() for r in records]
    df = pd.DataFrame(data_list)
    
    # Create Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Production Data')
        
        # Defect data
        defects = []
        for record in records:
            for defect in record.defects:
                defects.append({
                    'date': record.date,
                    'line': record.production_line.name,
                    'shift': record.shift,
                    'defect_type': defect.defect_type,
                    'count': defect.count
                })
        
        if defects:
            df_defects = pd.DataFrame(defects)
            df_defects.to_excel(writer, index=False, sheet_name='Defects')
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'OEE_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@export_bp.route('/pdf', methods=['POST'])
def export_pdf():
    """Export shift data to PDF"""
    data = request.get_json()
    
    line_id = data.get('line_id')
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    
    # Query data
    query = ShiftRecord.query
    if line_id:
        query = query.filter_by(line_id=line_id)
    if date_from:
        query = query.filter(ShiftRecord.date >= date_from)
    if date_to:
        query = query.filter(ShiftRecord.date <= date_to)
    
    records = query.order_by(ShiftRecord.date).all()
    
    # Create PDF
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0b1220'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph('PCBA Testing OEE Report', title_style))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Summary info
    if records:
        total_oee = sum(r.oee for r in records) / len(records)
        total_availability = sum(r.availability for r in records) / len(records)
        total_performance = sum(r.performance for r in records) / len(records)
        total_quality = sum(r.quality for r in records) / len(records)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Period', f"{date_from or 'N/A'} to {date_to or 'N/A'}"],
            ['Average OEE', f"{total_oee:.2f}%"],
            ['Average Availability', f"{total_availability:.2f}%"],
            ['Average Performance', f"{total_performance:.2f}%"],
            ['Average Quality', f"{total_quality:.2f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b1220')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(PageBreak())
        
        # Detailed data table
        table_data = [['Date', 'Line', 'Shift', 'Avail. %', 'Perf. %', 'Quality %', 'OEE %']]
        for record in records:
            table_data.append([
                str(record.date),
                record.production_line.name,
                record.shift,
                f"{record.availability:.1f}",
                f"{record.performance:.1f}",
                f"{record.quality:.1f}",
                f"{record.oee:.1f}"
            ])
        
        detail_table = Table(table_data, colWidths=[1 * inch, 1.2 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b1220')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(detail_table)
    
    doc.build(elements)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'OEE_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

@export_bp.route('/csv', methods=['POST'])
def export_csv():
    """Export shift data to CSV"""
    data = request.get_json()
    
    line_id = data.get('line_id')
    date_from = data.get('date_from')
    date_to = data.get('date_to')
    
    # Query data
    query = ShiftRecord.query
    if line_id:
        query = query.filter_by(line_id=line_id)
    if date_from:
        query = query.filter(ShiftRecord.date >= date_from)
    if date_to:
        query = query.filter(ShiftRecord.date <= date_to)
    
    records = query.order_by(ShiftRecord.date).all()
    
    # Convert to CSV
    data_list = [r.to_dict() for r in records]
    df = pd.DataFrame(data_list)
    
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'OEE_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
