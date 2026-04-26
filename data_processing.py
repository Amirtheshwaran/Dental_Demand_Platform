import pandas as pd
import numpy as np

def load_and_clean_data(file_path_or_buffer):
    """
    Loads CDC PLACES dataset combined with demographics.
    Filters to: MeasureId == TEETHLOST, DataValueTypeID == CrdPrv, Year == 2022.
    """
    df = pd.read_csv(file_path_or_buffer)
    
    # Filter CDC PLACES conditions if columns exist
    if 'MeasureId' in df.columns:
        df = df[df['MeasureId'] == 'TEETHLOST']
    if 'DataValueTypeID' in df.columns:
        df = df[df['DataValueTypeID'] == 'CrdPrv']
    if 'Year' in df.columns:
        df = df[df['Year'] == 2022]
        
    # Standardize column names
    col_mapping = {
        'StateAbbr': 'State',
        'StateDesc': 'State_Name',
        'Data_Value': 'Prevalence',
        'Pop65Plus': 'Population_65_Plus',
        'Population 65+': 'Population_65_Plus',
        'MedianIncome': 'Median_Income',
        'Median Income': 'Median_Income',
        'UrbanDensity': 'Urban_Density',
        'Urban Density': 'Urban_Density',
        'LocationID': 'FIPS' # Useful for mapping
    }
    df.rename(columns=col_mapping, inplace=True)
    
    # Handle County Name for both County-level and Tract-level datasets
    if 'CountyName' in df.columns:
        df.rename(columns={'CountyName': 'County'}, inplace=True)
    elif 'LocationName' in df.columns:
        df.rename(columns={'LocationName': 'County'}, inplace=True)
        
    # Clean TotalPopulation if it exists to unlock 2D clustering and anomaly detection
    if 'TotalPopulation' in df.columns:
        df['TotalPopulation'] = df['TotalPopulation'].astype(str).str.replace(',', '', regex=False).str.replace('"', '', regex=False).str.strip()
        df['TotalPopulation'] = pd.to_numeric(df['TotalPopulation'], errors='coerce')
    
    # Drop rows with missing Prevalence
    if 'Prevalence' in df.columns:
        df = df.dropna(subset=['Prevalence'])
        
    # Ensure FIPS is a 5 digit string (extracting county from tract if needed)
    if 'FIPS' in df.columns:
        df['FIPS'] = df['FIPS'].astype(str).str.replace(r'\.0$', '', regex=True)
        def fix_fips(x):
            if x == 'nan' or pd.isna(x): return x
            x = x.strip()
            if len(x) > 5:
                # It's a tract: pad to 11 zeros, then take first 5 digits (State+County)
                return x.zfill(11)[:5]
            else:
                # It's a county: pad to 5 zeros
                return x.zfill(5)
        df['FIPS'] = df['FIPS'].apply(fix_fips)
        
    return df

def calculate_demand_index(df, weights):
    """
    Calculates the combined Dental Demand Index based on weighted features.
    Weights is a dict: {'prevalence': 0.4, 'pop65': 0.3, 'income': 0.2, 'density': 0.1}
    """
    df_scored = df.copy()
    
    def safe_normalize(series, invert=False):
        if series.isna().all(): return pd.Series(50.0, index=series.index)
        mn, mx = series.min(), series.max()
        if mx == mn: return pd.Series(50.0, index=series.index)
        val = (series - mn) / (mx - mn) * 100
        return 100 - val if invert else val

    if 'Prevalence' in df_scored.columns:
        norm_prev = safe_normalize(df_scored['Prevalence'])
    else:
        norm_prev = pd.Series(50.0, index=df_scored.index)
        
    if 'Population_65_Plus' in df_scored.columns:
        norm_pop = safe_normalize(df_scored['Population_65_Plus'])
    else:
        norm_pop = pd.Series(50.0, index=df_scored.index)

    if 'Median_Income' in df_scored.columns:
        # Lower median income = higher baseline demand scoring conventionally, 
        # so we invert the income.
        norm_inc = safe_normalize(df_scored['Median_Income'], invert=True) 
    else:
        norm_inc = pd.Series(50.0, index=df_scored.index)

    if 'Urban_Density' in df_scored.columns:
        norm_dens = safe_normalize(df_scored['Urban_Density'])
    else:
        norm_dens = pd.Series(50.0, index=df_scored.index)

    df_scored['Demand_Index'] = (
        norm_prev * weights.get('prevalence', 0.4) +
        norm_pop * weights.get('pop65', 0.3) +
        norm_inc * weights.get('income', 0.2) +
        norm_dens * weights.get('density', 0.1)
    )
    
    df_scored['Demand_Index'] = df_scored['Demand_Index'].round(2)
    return df_scored
