import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

def run_clustering(df, n_clusters=4):
    """
    Clusters counties based on available demographic and health metrics to find strategic segments.
    """
    df_clustered = df.copy()
    features = ['Prevalence', 'Population_65_Plus', 'Median_Income', 'Urban_Density']
    available_features = [f for f in features if f in df_clustered.columns]
    
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
        
        # Simple heuristics based on z-scores
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
            
        cluster_names[i] = name
        
    df_clustered['Cluster_Name'] = df_clustered['Cluster'].map(cluster_names)
    return df_clustered

def train_and_predict_clinic_type(df):
    """
    Trains a predictive model to recommend clinic type.
    Creates a synthetic ground truth for 'Optimal_Clinic' to demonstrate the model 
    as an 'AI Strategy' system based on realistic county profiles.
    """
    df_ml = df.copy()
    
    features = ['Prevalence', 'Population_65_Plus', 'Median_Income', 'Urban_Density']
    available_features = [f for f in features if f in df_ml.columns]
    
    if len(available_features) == 0:
        df_ml['Predicted_Clinic_Type'] = "Hybrid Clinic"
        return df_ml, None, {}
        
    # Generate Synthetic Labels for Training (Rule-based surrogate for historical data)
    def determine_ground_truth(row):
        prev = row.get('Prevalence', 15) # Example national avg ~13-15%
        inc = row.get('Median_Income', 60000)
        dens = row.get('Urban_Density', 500) # Assume 500 people/sq mi
        
        # Heuristics mimicking business strategy:
        if prev > 20 and inc < 50000:
            return 'Denture Center'
        elif inc > 80000 and dens > 1000:
            return 'Implant Studio'
        else:
            return 'Hybrid Clinic'
            
    df_ml['Ground_Truth_Clinic'] = df_ml.apply(determine_ground_truth, axis=1)
    
    X = df_ml[available_features].fillna(df_ml[available_features].median())
    y = df_ml['Ground_Truth_Clinic']
    
    # Handle edge case where all are same class
    if len(y.unique()) < 2:
        df_ml['Predicted_Clinic_Type'] = y
        return df_ml, None, {}
        
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    clf.fit(X, y)
    
    df_ml['Predicted_Clinic_Type'] = clf.predict(X)
    
    # Feature importances
    importances = dict(zip(available_features, clf.feature_importances_))
    
    return df_ml, clf, importances

def get_recommendation_reasoning(row):
    """
    Rule-based reasoning text for the recommendations.
    """
    clinic_type = row.get('Predicted_Clinic_Type', 'Hybrid Clinic')
    prev = row.get('Prevalence', 0)
    cluster = row.get('Cluster_Name', '')
    
    if clinic_type == 'Denture Center':
        return f"High tooth loss prevalence ({prev:.1f}%) in {cluster} regions requires high-volume restorative care."
    elif clinic_type == 'Implant Studio':
        return f"Targets {cluster} demographics with purchasing power for premium implants and restorative products."
    else:
        return f"Balanced demographic profile (Prevalence: {prev:.1f}%) suggests a hybrid approach covering diverse dental needs."

