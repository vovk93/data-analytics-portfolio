"""
PDF Extraction Script for RHMZ Meteorological Data (1998–2024)

Description:
This script extracts daily meteorological data from annual PDF reports
published by the Republic Hydrometeorological Service of Serbia (RHMZ).

The PDFs contain tabular data for multiple cities and months, split
across multiple tables and pages. This script parses those tables and
combines them into a unified dataset.

Output:
- CSV file containing raw extracted data (before final cleaning/labeling, which I performed later)

Notes:
- The PDF format varies slightly across years
- Some station names appear in Cyrillic or corrupted Latin encoding
- Data rows are sometimes split across two tables and merged here

Author: Ivan Vovk
Year: 2026
"""
import pdfplumber
import re
import os
import pandas as pd

# ------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
PDF_DIR = os.path.join(SCRIPT_DIR, "pdfs")
PDF_FILES = [
    os.path.join(PDF_DIR, f"MG{year}.pdf") for year in range(1998, 2025)
]

# ------------------------------------------------------
# STATIONS (Cyrillic + Latin → unified Latin)
# ------------------------------------------------------

STATION_MAP = {
    # Cyrillic
    "БЕОГРАД": "BEOGRAD",
    "НОВИ САД": "NOVI SAD",
    "ВРАЊЕ": "VRANJE",
    "ЗЛАТИБОР": "ZLATIBOR",
    "ЛОЗНИЦА": "LOZNICA",
    "НИШ": "NIS",
    "NI[": "NIS",
    "ПРИШТИНА": "PRISTINA",
    "PRI[TINA": "PRISTINA",
    "VRAWE": "VRANJE",

    # Latin
    "BEOGRAD": "BEOGRAD",
    "NOVI SAD": "NOVI SAD",
    "VRANJE": "VRANJE",
    "ZLATIBOR": "ZLATIBOR",
    "LOZNICA": "LOZNICA",
    "NIS": "NIS",
    "PRISTINA": "PRISTINA"
}

# Pre-normalized keys for robust matching
STATION_KEYS = {
    k.replace(" ", ""): v for k, v in STATION_MAP.items()
}

# ------------------------------------------------------
# MONTHS (Cyrillic + Latin)
# ------------------------------------------------------

MONTH_NUM = {
    # Cyrillic
    "ЈАНУАР": 1, "ФЕБРУАР": 2, "МАРТ": 3, "АПРИЛ": 4,
    "МАЈ": 5, "ЈУН": 6, "ЈУЛ": 7, "АВГУСТ": 8,
    "СЕПТЕМБАР": 9, "ОКТОБАР": 10, "НОВЕМБАР": 11, "ДЕЦЕМБАР": 12,

    # Latin
    "JANUAR": 1, "FEBRUAR": 2, "MART": 3, "APRIL": 4,
    "MAJ": 5, "JUN": 6, "JUL": 7, "AVGUST": 8,
    "SEPTEMBAR": 9, "OKTOBAR": 10, "NOVEMBAR": 11, "DECEMBAR": 12
}

MONTH_KEYS = list(MONTH_NUM.keys())

# ------------------------------------------------------
# DAILY ROW PATTERN
# ------------------------------------------------------

ROW_PATTERN = re.compile(r"^\s*(\d{1,2})\s+(.+)$")

# ------------------------------------------------------
# PARSE PDFs
# ------------------------------------------------------

all_rows = []
last_row_index = {}
december_31_seen = {}

for pdf_file in PDF_FILES:
    pdf_path = os.path.join(SCRIPT_DIR, pdf_file)

    year_match = re.search(r"(\d{4})", pdf_file)
    year = int(year_match.group(1)) if year_match else None

    current_station = None
    current_month = None
    station_finished = False

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines = text.split("\n")

                for line in lines:
                    raw = line.strip()
                    upper = raw.upper()
                    compact = upper.replace(" ", "")

                    # -----------------------------
                    # Detect station
                    # -----------------------------
                    for key, station in STATION_KEYS.items():
                        if key in compact:
                            current_station = station
                            current_month = None
                            station_finished = False
                            break

                    # -----------------------------
                    # Detect month
                    # -----------------------------
                    for m in MONTH_KEYS:
                        if m in upper:
                            current_month = MONTH_NUM[m]
                            break

                    # -----------------------------
                    # Detect daily rows
                    # -----------------------------
                    match = ROW_PATTERN.match(upper)
                    if not match:
                        continue

                    day = int(match.group(1))

                    if station_finished:
                        continue

                    if current_station and current_month:
                        cleaned = re.sub(r"\s+", " ", upper)
                        parts = cleaned.split(" ")

                        key = (current_station, year, current_month, day)

                        # First occurrence of this day → create row
                        if key not in last_row_index:
                            all_rows.append(
                                [current_station, current_month, year] + parts
                            )
                            last_row_index[key] = len(all_rows) - 1
                        else:
                            # Second table → append extra columns
                            # Each day appears in two separate tables in the PDF.
                            # The first occurrence initializes the row,
                            # the second occurrence appends additional variables.
                            idx = last_row_index[key]
                            all_rows[idx].extend(parts[1:])  # skip day number

                        # Stop after Dec 31 for this station
                        if current_month == 12 and day == 31:
                            dec_key = (current_station, year)
                            december_31_seen[dec_key] = december_31_seen.get(dec_key, 0) + 1

                            # Stop only after BOTH tables (day 31 seen twice)
                            if december_31_seen[dec_key] >= 2:
                                station_finished = True


    except Exception as e:
        print(f"Error reading {pdf_file}: {e}")

# ------------------------------------------------------
# SAVE TO CSV
# ------------------------------------------------------

if all_rows:
    df = pd.DataFrame(all_rows)
    num_data_columns = len(df.columns) - 3

    df.columns = ["Station", "Month", "Year"] + [
        f"Data{i}" for i in range(1, num_data_columns + 1)
    ]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "raw_weather_data.csv")
    df.to_csv(output_file, index=False, encoding="utf-8")

    print("PDF parsing finished! All data saved in:", output_file)
else:
    print("No data extracted from PDFs.")
