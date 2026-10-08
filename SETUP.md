# PCBA Testing OEE Dashboard - Enhanced Version

A production-ready Flask-based OEE (Overall Equipment Effectiveness) dashboard for PCBA testing operations with real-time monitoring, data import/export, and comprehensive analytics.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Rafiudin8732/OEE-Dashboard-PCBA-Testing.git
cd OEE-Dashboard-PCBA-Testing
```

### 2. Switch to Enhancement Branch

```bash
git checkout enhance/data-integration
```

### 3. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
exit()
```

### 6. Run the Application

```bash
python run.py
```

The dashboard will be available at: **http://localhost:5000**

## Features

### Data Management
- **CSV/Excel Upload**: Import production data directly from Excel files
- **Database Storage**: SQLite by default, PostgreSQL for production
- **Live Data Streams**: Real-time production line metrics

### Analytics & Reporting
- **OEE Calculation**: Availability × Performance × Quality
- **Trend Analysis**: 14-day rolling KPI trends
- **Defect Tracking**: Categorized quality issues
- **Export Options**: Excel, PDF, and CSV report generation

### Industrial Dashboard UI
- KPI cards with real-time status
- Line performance comparison charts
- Defect distribution analysis
- Shift-by-shift performance table
- Filter by line, shift, and date range

## Project Structure

```
OEE-Dashboard-PCBA-Testing/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # SQLAlchemy database models
│   └── routes/
│       ├── dashboard.py         # UI routes
│       ├── api.py               # REST API endpoints
│       ├── upload.py            # File upload handlers
│       └── export.py            # Report export endpoints
├── templates/
│   ├── base.html                # Base template
│   ├── index.html               # Dashboard HTML
│   └── dashboard.html           # Main dashboard
├── static/
│   ├── css/                     # Industrial styling
│   └── js/                      # Dashboard logic
├── config.py                    # Flask configuration
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## API Endpoints

### Production Lines
```
GET    /api/lines                  # List all production lines
POST   /api/lines                  # Create new line
```

### Shift Records
```
GET    /api/shift-records          # Get shift data with filters
POST   /api/shift-records          # Create new shift record
```

### KPI Analytics
```
GET    /api/kpi-summary            # Get summary metrics
GET    /api/trend                  # Get trend data
GET    /api/defects                # Get defect analysis
```

### Data Import
```
POST   /api/upload/production-data # Import CSV/Excel production data
POST   /api/upload/defect-data     # Import defect data
```

### Report Export
```
POST   /api/export/excel           # Export to Excel
POST   /api/export/pdf             # Export to PDF
POST   /api/export/csv             # Export to CSV
```

### Live Data
```
GET    /api/live-data              # Get live stream data
POST   /api/live-data              # Post new live metrics
```

## File Upload Format

### Production Data (CSV/XLSX)

Required columns:
- `date` - YYYY-MM-DD format
- `line` - Production line name (e.g., "Line A")
- `shift` - Day, Swing, or Night
- `planned_minutes` - Planned shift duration
- `run_minutes` - Actual run time
- `target_units` - Target production
- `actual_units` - Actual units produced
- `good_units` - Defect-free units

**Example CSV:**
```csv
date,line,shift,planned_minutes,run_minutes,target_units,actual_units,good_units
2026-10-01,Line A,Day,480,450,450,420,405
2026-10-01,Line B,Day,480,460,450,430,410
2026-10-02,Line A,Swing,480,440,450,400,380
```

### Defect Data (CSV/XLSX)

Required columns:
- `date` - YYYY-MM-DD format
- `line` - Production line name
- `shift` - Day, Swing, or Night
- `defect_type` - AOI, ICT, Solder, Labeling, Mechanical
- `count` - Number of defects

**Example CSV:**
```csv
date,line,shift,defect_type,count
2026-10-01,Line A,Day,AOI,8
2026-10-01,Line A,Day,Solder,7
2026-10-01,Line B,Day,ICT,5
```

## Configuration

Edit `.env` to customize:

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///pcba_oee.db
ENABLE_LIVE_SIMULATION=true
LIVE_UPDATE_INTERVAL=30
```

### Database Options

**SQLite (Default - Development):**
```
DATABASE_URL=sqlite:///pcba_oee.db
```

**PostgreSQL (Production):**
```
DATABASE_URL=postgresql://username:password@localhost:5432/pcba_oee
```

## OEE Calculation

The dashboard calculates OEE using the standard formula:

```
OEE = Availability × Performance × Quality

Where:
  Availability = (Run Time / Planned Time) × 100
  Performance = (Actual Output / Target Output) × 100
  Quality = (Good Units / Total Units) × 100
```

## Dashboard Features

### KPI Cards
- **Availability**: Percentage of planned time the line was running
- **Performance**: Actual output vs. target capacity
- **Quality**: First-pass yield (good units / total units)
- **OEE**: Composite score combining all three metrics

### Charts
- **OEE Trend**: 14-day moving average
- **Line Comparison**: Performance across all production lines
- **Defect Mix**: Distribution of defect types

### Shift Summary Table
- Date-by-date breakdown of all metrics
- Sortable and filterable
- Export to Excel/PDF for reporting

## Troubleshooting

### Issue: "No such file or directory: 'requirements.txt'"

**Solution:** Make sure you're in the correct directory:
```bash
cd OEE-Dashboard-PCBA-Testing
ls  # or 'dir' on Windows
pip install -r requirements.txt
```

### Issue: Port 5000 already in use

**Solution:** Edit `run.py` and change the port:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### Issue: Database lock errors

**Solution:** Delete the old database and reinitialize:
```bash
rm pcba_oee.db
python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
exit()
```

## Deployment

For production deployment, use a proper WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or feature requests, please open a GitHub issue or contact the development team.

---

**Last Updated:** October 8, 2026
**Version:** 2.0.0 (Enhanced with Flask Backend)
