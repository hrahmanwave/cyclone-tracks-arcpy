# Cyclone-tracks-arcpy
Generate cyclone track polylines from latitude–longitude CSV data using ArcPy (ArcMap).

# Cyclone Track Generation using ArcPy

This repository contains an ArcPy workflow to generate **cyclone track polylines**
from latitude–longitude point data stored in a CSV file.

The script is designed for **ArcMap / ArcGIS Desktop (10.x)** and avoids
common `PointsToLine` failures caused by datetime and CSV issues.

---

## Features

- Converts CSV (Lat/Lon) to point features (WGS84)
- Automatically removes storms with fewer than 2 points
- Builds cyclone tracks **grouped by StormID**
- Robust against ArcMap SQL and datetime bugs
- Suitable for long-term cyclone best-track datasets

---

## Requirements

- ArcGIS Desktop 10.x
- Python 2.7 (ArcPy)
- Valid CSV with at least:
  - `Lat`
  - `Lon`
  - `StormID`

Optional:
- `DatetimeUTC_str_new` for time-based sorting

---

## Usage

1. Open **ArcMap**
2. Open **Python Window**
3. Edit input paths in the script:
   ```python
   in_csv = r"C:\path\to\your.csv"
