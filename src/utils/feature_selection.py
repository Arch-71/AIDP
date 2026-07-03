"""
Feature Selection Module for Sustainable AI Diabetes Prediction
Selects important features for sustainable and efficient models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns

class FeatureSelector:
    def __init__(self):
        self.selected_features = None
        self.feature_importance = None
        self.sustainable_features = [
            'Age', 'BMI', 'Glucose', 'BloodPressure', 'DiabetesPedigreeFunction'
        ]
    
    def random_forest_importance(self, X, y, n_estimators=100):
        """Get feature importance using Random Forest"""
        if y is None:
            raise ValueError("Target variable 'y' must be provided for Random Forest importance.")
        rf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        rf.fit(X, y)
        
        importance_df = pd.DataFrame({
            'Feature': X.columns,
            'Importance': rf.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        self.feature_importance = importance_df
        return importance_df
    
    def recursive_feature_elimination(self, X, y, n_features=5):
        """Select features using Recursive Feature Elimination"""
        estimator = LogisticRegression(random_state=42, max_iter=1000)
        rfe = RFE(estimator=estimator, n_features_to_select=n_features)
        rfe = rfe.fit(X, y)
        
        selected_features = X.columns[rfe.support_].tolist()
        ranking = pd.DataFrame({
            'Feature': X.columns,
            'Rank': rfe.ranking_
        }).sort_values('Rank')
        
        return selected_features, ranking
    
    def select_sustainable_features(self, X, y, importance_threshold=0.05):
        """Select features based on importance and sustainability criteria"""
        # Get feature importance
        importance_df = self.random_forest_importance(X, y)
        
        # Filter by importance threshold
        important_features = importance_df[
            importance_df['Importance'] >= importance_threshold
        ]['Feature'].tolist()
        
        # Prioritize sustainable features if they meet threshold
        sustainable_important = [
            feature for feature in self.sustainable_features 
            if feature in important_features
        ]
        
        # Add other important features if needed
        other_important = [
            feature for feature in important_features 
            if feature not in sustainable_important
        ]
        
        # Combine: prioritize sustainable features
        final_features = sustainable_important + other_important
        
        # Ensure we have at least 3 features
        if len(final_features) < 3:
            final_features = importance_df.head(3)['Feature'].tolist()
        
        self.selected_features = final_features
        return final_features
    
    def plot_feature_importance(self, save_path=None):
        """Plot feature importance"""
        if self.feature_importance is None:
            raise ValueError("Feature importance not calculated. Run random_forest_importance first.")
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=self.feature_importance.head(10), x='Importance', y='Feature')
        plt.title('Top 10 Feature Importance')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def get_feature_selection_summary(self, X, y):
        """Get comprehensive feature selection summary"""
        # Random Forest importance
        rf_importance = self.random_forest_importance(X, y)
        
        # RFE selection
        rfe_features, rfe_ranking = self.recursive_feature_elimination(X, y)
        
        # Sustainable selection
        sustainable_features = self.select_sustainable_features(X)
        
        summary = {
            'total_features': len(X.columns),
            'rf_top_features': rf_importance.head(5)['Feature'].tolist(),
            'rfe_selected_features': rfe_features,
            'sustainable_selected_features': sustainable_features,
            'feature_importance': rf_importance.to_dict('records'),
            'rfe_ranking': rfe_ranking.to_dict('records')
        }
        
        return summary
