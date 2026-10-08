import os
from app import create_app, db
from app.models import ProductionLine, ShiftRecord, Defect, LiveDataStream

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'ProductionLine': ProductionLine,
        'ShiftRecord': ShiftRecord,
        'Defect': Defect,
        'LiveDataStream': LiveDataStream
    }

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_ENV') == 'development')
