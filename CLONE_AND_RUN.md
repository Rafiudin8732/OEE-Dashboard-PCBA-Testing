# PCBA Testing OEE Dashboard - Complete Setup Guide

## Clone the Repository

### Step 1: Open Command Prompt or PowerShell

**Windows CMD:**
```cmd
win + r
cmd
```

**Windows PowerShell:**
```powershell
win + x
a  (select PowerShell)
```

### Step 2: Clone the Repository

Copy and paste this command:

```bash
git clone https://github.com/Rafiudin8732/OEE-Dashboard-PCBA-Testing.git
```

Expected output:
```
Cloning into 'OEE-Dashboard-PCBA-Testing'...
remote: Enumerating objects...
remote: Counting objects...
...
Unpacking objects: 100%
Done.
```

### Step 3: Navigate to the Project Folder

```bash
cd OEE-Dashboard-PCBA-Testing
```

Verify the files are there:
```bash
dir
```

You should see:
```
requirements.txt
config.py
run.py
app/
static/
templates/
```

### Step 4: Switch to Enhancement Branch

```bash
git checkout enhance/data-integration
```

You should see:
```
Branch 'enhance/data-integration' set up to track remote branch 'enhance/data-integration' from 'origin'.
Switched to a new branch 'enhance/data-integration'
```

## Install Python Dependencies

### Step 5: Create Virtual Environment

**Windows CMD:**
```cmd
python -m venv venv
```

**Windows PowerShell:**
```powershell
python -m venv venv
```

### Step 6: Activate Virtual Environment

**Windows CMD:**
```cmd
venv\Scripts\activate
```

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

*Note: If you get an error in PowerShell about execution policies, run:*
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` at the start of your prompt:
```
(venv) C:\Users\your-username\OEE-Dashboard-PCBA-Testing>
```

### Step 7: Install Requirements

Now copy and paste this command:

```bash
pip install -r requirements.txt
```

This will install all needed packages. It may take 2-5 minutes.

## Initialize Database

### Step 8: Create the Database

Run Python interactively:

```bash
python
```

Then copy and paste this:

```python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
print("Database created successfully!")
exit()
```

Expected output:
```
Database created successfully!
```

## Start the Application

### Step 9: Run the Flask Server

```bash
python run.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 10: Open in Browser

Copy this URL and paste it in your browser:
```
http://localhost:5000
```

**You should now see the PCBA Testing OEE Dashboard!**

## Troubleshooting

### Problem: "git is not recognized"
**Solution:** Install Git from https://git-scm.com/download/win

### Problem: "python is not recognized"
**Solution:** Install Python from https://www.python.org/downloads/ (check "Add Python to PATH")

### Problem: PowerShell execution policy error
**Solution:** Run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Port 5000 already in use"
**Solution:** Either:
1. Kill the process using port 5000
2. Or change the port in `run.py` line 14:
   ```python
   if __name__ == '__main__':
       app.run(debug=True, port=5001)  # Change to 5001 or any free port
   ```

### Problem: Database lock errors
**Solution:** 
```bash
del pcba_oee.db
python
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
exit()
```

## Next Steps

### Upload Sample Data

1. Download sample CSV from the repo
2. Go to Production → Upload Production Data
3. Select your CSV file
4. Click upload
5. Check the dashboard for updated metrics

### Sample CSV Format

Create a file named `sample_data.csv`:

```csv
date,line,shift,planned_minutes,run_minutes,target_units,actual_units,good_units
2026-10-01,Line A,Day,480,450,450,420,405
2026-10-02,Line A,Day,480,460,450,430,410
2026-10-01,Line B,Day,480,440,450,400,380
2026-10-02,Line B,Swing,480,430,450,390,365
```

## Dashboard Features

### Main Dashboard
- Real-time KPI cards (Availability, Performance, Quality, OEE)
- 14-day OEE trend chart
- Line performance comparison
- Defect distribution analysis
- Shift summary table with export

### Production Data
- Upload CSV/Excel files
- Live production stream monitoring
- Data validation and error reporting

### Quality Analysis
- Defect tracking by type
- Quality trends over time
- Root cause analysis

### Reports & Export
- Export to Excel (.xlsx)
- Export to PDF (.pdf)
- Export to CSV (.csv)
- Date range filtering

## API Endpoints (For Advanced Users)

```
GET  /api/lines                    - Get all production lines
GET  /api/shift-records            - Get shift data
GET  /api/kpi-summary              - Get KPI metrics
GET  /api/trend                    - Get trend data
GET  /api/defects                  - Get defect data
POST /api/upload/production-data   - Import CSV/Excel
POST /api/export/excel             - Export to Excel
POST /api/export/pdf               - Export to PDF
POST /api/export/csv               - Export to CSV
GET  /api/live-data                - Get live metrics
```

## Configuration (.env file)

The `.env.example` file shows available settings:

```env
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///pcba_oee.db
UPLOAD_FOLDER=./uploads
```

## Deactivate Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## Run Next Time

To run the app again later:

1. Open Command Prompt in the project folder
2. Activate venv: `venv\Scripts\activate` (Windows CMD)
3. Run: `python run.py`
4. Open: `http://localhost:5000`

---

**Congratulations! Your PCBA Testing OEE Dashboard is ready!** 🎉
