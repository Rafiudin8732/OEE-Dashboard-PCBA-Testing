# PCBA Testing OEE Dashboard

This project is a lightweight, production-ready style dashboard for monitoring Overall Equipment Effectiveness (OEE) in a PCBA testing environment.

## Features

- KPI cards for Availability, Performance, Quality, and OEE
- Trend chart for daily OEE movement
- Line comparison chart for performance by production line
- Defect mix breakdown for quality analysis
- Shift summary table with detailed metric visibility
- Filter controls for line and shift selection

## Run locally

Open `index.html` directly in a browser, or serve the folder with a local web server:

```bash
python -m http.server 8000
```

Then navigate to:

```text
http://localhost:8000
```

## Dashboard logic

The app calculates:

- Availability = Run time / Planned time
- Performance = Actual output / Target output
- Quality = Good units / Total units
- OEE = Availability × Performance × Quality

## Files

- `index.html` – dashboard structure
- `styles.css` – layout and visual styling
- `script.js` – sample production data and calculations

## Notes

The data in `script.js` is sample manufacturing data for demonstration purposes. You can replace it with live plant data or connect to an API for real-time updates.
