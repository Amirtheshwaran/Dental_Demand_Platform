# Dental Demand Platform

## Project Description
This Streamlit app helps explore dental health demand and access patterns using county-level public health data. The dashboard includes data processing, visual summaries, and demand-focused views for understanding dental service needs.

## App Deployment URL
[Link to deployed Streamlit app]

## Dataset Compatibility
The platform supports two types of data uploads:
- **CDC-Only Mode (Raw PLACES Data):** If you upload a raw CDC PLACES dataset (like the 2025 County Data release), the app automatically detects that demographic variables (like Income, Age, Density) are missing. It will gracefully switch to "CDC-Only Mode," hiding the demographic sliders and ranking counties based purely on a normalized Tooth-Loss Prevalence demand index.
- **Enriched Mode:** If your uploaded CSV has been merged with US Census/ACS variables (e.g., `MedianIncome`, `Pop65Plus`, `UrbanDensity`), the app unlocks demographic weighting sliders, allowing for full multi-variable ML inference.

## Local Setup Instructions

```bash
git clone https://github.com/Amirtheshwaran/Dental_Demand_Platform.git
cd Dental_Demand_Platform
python -m venv .venv
# On Windows: .\.venv\Scripts\Activate.ps1
# On Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```