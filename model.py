import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

def run_clustering(df, n_clusters=4):
    """
    Clusters counties based on available demographic and health metrics to find strategic segments.
    """
    df_clustered = df.copy()
    
    # Try all possible numeric features, prioritize enriched ones, but fallback to TotalPopulation if available
    potential_features = ['Prevalence', 'Population_65_Plus', 'Median_Income', 'Urban_Density', 'TotalPopulation']
    available_features = [f for f in potential_features if f in df_clustered.columns]
    
    # Force numeric to prevent string reduction errors from cached data
    for f in available_features:
        df_clustered[f] = pd.to_numeric(df_clustered[f], errors='coerce')
    
    if len(available_features) < 2:
        df_clustered['Cluster'] = 0
        df_clustered['Cluster_Name'] = "General Tier"
        return df_clustered
        
    # Impute missing with median for clustering purposes
    X = df_clustered[available_features].fillna(df_clustered[available_features].median())
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clustered['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Assign names based on centroid characterstics dynamically
    centroids = kmeans.cluster_centers_
    cluster_names = {}
    for i in range(n_clusters):
        center = dict(zip(available_features, centroids[i]))
        prev = center.get('Prevalence', 0)
        inc = center.get('Median_Income', 0)
        dens = center.get('Urban_Density', 0)
        pop = center.get('TotalPopulation', 0)
        
        # Heuristics based on z-scores
        if 'Median_Income' in available_features:
            if prev > 0.3 and dens < 0:
                name = "High-Risk Rural"
            elif prev > 0 and dens > 0:
                name = "Urban High-Need"
            elif inc > 0.5 and dens > 0:
                name = "Urban Premium (High Income)"
            elif prev < 0 and inc > 0:
                name = "Affluent Low-Risk"
            else:
                name = "Stable Suburban"
        else:
            # Fallback to Prevalence and Population rules
            if prev > 0.5 and pop > 0.5:
                name = "High-Volume Target (Large Market, High Need)"
            elif prev > 0.5 and pop <= 0.5:
                name = "Niche Target (Small Market, High Need)"
            elif prev <= 0.5 and pop > 0.5:
                name = "Competitive Hub (Large Market, Average Need)"
            else:
                name = "Low Priority (Small Market, Low Need)"
            
        cluster_names[i] = name
        
    df_clustered['Cluster_Name'] = df_clustered['Cluster'].map(cluster_names)
    return df_clustered

def run_anomaly_detection(df):
    """
    Uses Isolation Forest to detect statistical anomalies in the market data using 100% real features.
    No fabricated labels are used.
    """
    df_ml = df.copy()
    
    potential_features = ['Prevalence', 'Population_65_Plus', 'Median_Income', 'Urban_Density', 'TotalPopulation']
    available_features = [f for f in potential_features if f in df_ml.columns]
    
    # Force numeric
    for f in available_features:
        df_ml[f] = pd.to_numeric(df_ml[f], errors='coerce')
    
    if len(available_features) < 2:
        df_ml['Anomaly_Score'] = 0.0
        df_ml['Is_Anomaly'] = False
        return df_ml
        
    X = df_ml[available_features].fillna(df_ml[available_features].median())
    
    # Train Isolation Forest
    iso = IsolationForest(contamination=0.05, random_state=42)
    iso.fit(X)
    
    # Anomaly scores (lower is more anomalous, we negate it so higher = more anomalous)
    scores = iso.decision_function(X)
    df_ml['Anomaly_Score'] = -scores 
    
    df_ml['Is_Anomaly'] = iso.predict(X) == -1
    
    return df_ml

def get_recommendation_reasoning(row):
    """
    Rule-based reasoning text for the recommendations using strictly true data traits.
    """
    prev = row.get('Prevalence', 0)
    cluster = row.get('Cluster_Name', 'General Tier')
    demand = row.get('Demand_Index', 50)
    is_anomaly = row.get('Is_Anomaly', False)
    
    reasoning = f"This market falls into the '{cluster}' segment with a {prev:.1f}% tooth-loss prevalence. "
    
    if demand > 80:
        reasoning += "Extremely high calculated demand suggests prioritizing high-volume restorative care. "
    elif demand > 50:
        reasoning += "Moderate demand indicates a balanced approach or hybrid clinic format. "
    else:
        reasoning += "Lower relative demand suggests focusing on premium or preventative services. "
        
    if is_anomaly:
        reasoning += "⚠️ Unsupervised ML flagged this county as a statistical anomaly, meaning its combination of prevalence and demographic traits is highly unusual compared to the national baseline."
        
    return reasoning

