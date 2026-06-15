# Customer Segmentation Dashboard

> RFM analysis + KMeans clustering on real UK retail transaction data

Part of the [Data to Decisions](https://github.com/kene-agbodike) portfolio by Kene Agbodike —
Data & AI Decision Systems Consultant.

---

## Overview

Customer segmentation system using RFM analysis and KMeans clustering on real UCI Online Retail II data (~1M transactions). Identifies Champions, Loyal, At-Risk, New, and Lost customer segments with actionable recommendations.

## Key finding

> The top 15% of customers (Champions) drove **68% of total revenue** — a finding that directly reshapes where retention budget should go.

## Stack

`pandas · scikit-learn · Plotly · Streamlit`

## Demo

<!-- Add links after deployment -->
- **Live demo:** Streamlit Community Cloud — _link coming soon_

## Getting started

```bash
# Clone the repo
git clone https://github.com/kenechukwuagbodike/customer-segmentation.git
cd customer-segmentation

# Create virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
```

**Download the dataset** (not included in the repo — 43 MB Excel file):

Download `online_retail_II.xlsx` from [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and place it in `data/`.

**Run the pipeline** (one-time setup, ~3 minutes total):

```bash
python pipeline/clean.py    # clean raw data → data/clean.csv
python pipeline/rfm.py      # RFM scoring   → data/rfm.csv
python pipeline/segment.py  # KMeans k=5    → data/segments.csv + models/
```

**Launch the dashboard:**

```bash
streamlit run dashboard/app.py
```

## Project structure

```
customer-segmentation/
├── data/            Raw and processed data
├── pipeline/        ETL, data generation, schedulers
├── dashboard/       Streamlit app (app.py)
├── models/          Saved sklearn model files (.pkl)
├── requirements.txt
└── README.md
```

## Running the dashboard

```bash
streamlit run dashboard/app.py
```

## About

**Kene Agbodike** — Data & AI Decision Systems Consultant

Certifications: Microsoft Fabric Data Engineer Associate · Fabric Analytics Engineer Associate ·
Azure Solutions Architect Expert · Azure AI Engineer · Azure Data Scientist

[GitHub](https://github.com/kene-agbodike) · [Upwork](https://www.upwork.com/freelancers/~01ffe0a90179159b67)
