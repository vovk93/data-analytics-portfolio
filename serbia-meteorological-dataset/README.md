# Serbia Meteorological Dataset (1998–2024) | RHMZ Data
## Overview

This repository contains a structured daily meteorological dataset for Serbia, covering the period **1998–2024.**

The dataset was created by extracting and processing data from annual PDF reports published by the Republic Hydrometeorological Service of Serbia (RHMZ), transforming unstructured historical records into a clean, analysis-ready format.

📥 The dataset is also publicly available on Zenodo:
→ https://zenodo.org/records/19239744

## 📊 Key Features
- 27 years of daily meteorological data
- Multiple cities: Belgrade, Novi Sad, Niš, Vranje, Loznica, Zlatibor (+ Priština for 1998)
- Cleaned and validated dataset (CSV format)
- Includes temperature, precipitation, wind, humidity, and more
- Fully reproducible pipeline (PDF → extraction → cleaning)

## 📄 Data Source

The original data was obtained from annual reports published by the Republic Hydrometeorological Service of Serbia (RHMZ).

Due to file size, the original PDF reports are not included in this repository.

They are available via:
- the official RHMZ website
- the full dataset archive on Zenodo → https://zenodo.org/records/19239744

## 📂 Project Structure
- *extract_data.py* — script to extract data from PDFs
- *cleaning.py* — script to clean and validate extracted data
- *raw_weather_data.csv* — raw extracted dataset
- *cleaned_dataset.csv* — final cleaned dataset
- *README.md* — documentation

## ⚙️ Requirements
pip install pdfplumber pandas

## ▶️ Usage

Run the extraction script:

*python extract_data.py*

Then clean and validate the data:

*python cleaning.py*

## 🔍 Notes on Data Extraction
- Some PDFs split daily data into two tables; rows are merged programmatically
- Station names appear in Cyrillic or Latin and are normalized
- Minor inconsistencies in source data are handled during cleaning

## 🧹 Data Cleaning and Validation

The *cleaning.py* script ensures data quality and transparency:

- Numeric columns converted and validated
- Outliers handled using realistic thresholds
- Misaligned rows corrected
- Missing values treated consistently
- Manual corrections documented in code comments

## 📏 Units and Calculations

- Temperature: °C
- Average temperature:
avg_temp = (temp_07h + temp_14h + 2 * temp_21h) / 4
- Pressure: hPa
- Humidity: %
- Wind speed: m/s
- Insolation: hours
- Precipitation / Snow: mm / cm

## 📌 Use Cases
- Climate analysis and trend detection
- Time series modeling
- Environmental and geospatial research
- Data analytics and visualization projects

## 📖 Citation

If you use this dataset, please cite:

Ivan Vovk (2026). *RHMZ Meteorological Dataset (1998–2024)*.
Republic Hydrometeorological Service of Serbia (RHMZ).
Zenodo. https://doi.org/10.5281/zenodo.19239744
