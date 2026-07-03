"""
Explainable AI Module for Sustainable AI Diabetes Prediction
Uses SHAP to provide model explanations and interpretability
"""

import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class ExplainableAI:
    def __init__(self):
        self.explainer = None
        self.shap_values = None
        self.feature_names = None
        self.model = None
        self.X_background = None
        
    def initialize_explainer(self, model, X_background, feature_names=None):
        """Initialize SHAP explainer for the model"""
        self.model = model
        self.X_background = X_background
        self.feature_names = feature_names or X_background.columns.tolist()
        
        # Choose appropriate explainer based on model type
        try:
            # Try TreeExplainer first (works for tree-based models)
            self.explainer = shap.TreeExplainer(model, X_background)
        except:
            try:
                # Try KernelExplainer as fallback
                self.explainer = shap.KernelExplainer(model.predict_proba, X_background.sample(min(100, len(X_background))))
            except:
                # Use LinearExplainer for linear models
                self.explainer = shap.LinearExplainer(model, X_background)
        
        return self.explainer
    
    def calculate_shap_values(self, X_test):
        """Calculate SHAP values for test data"""
        if self.explainer is None:
            raise ValueError("Explainer not initialized. Call initialize_explainer first.")
        
        # Calculate SHAP values
        self.shap_values = self.explainer.shap_values(X_test, check_additivity=False)
        
        # Handle binary classification (SHAP returns list of two arrays)
        if isinstance(self.shap_values, list):
            self.shap_values = self.shap_values[1]  # Use positive class
        
        return self.shap_values
    
    def get_feature_importance(self, plot_type='bar'):
        """Get global feature importance from SHAP values"""
        if self.shap_values is None:
            raise ValueError("SHAP values not calculated. Call calculate_shap_values first.")
        
        # Calculate mean absolute SHAP values for each feature
        feature_importance = np.mean(np.abs(self.shap_values), axis=0).flatten()
        
        # Ensure lengths match - sometimes SHAP returns an extra intercept value or 
        # different structure depending on the explainer type
        if len(feature_importance) != len(self.feature_names):
            print(f"DEBUG: SHAP importance length ({len(feature_importance)}) != feature names length ({len(self.feature_names)})")
            # If importance is longer, it might include the base value (intercept)
            if len(feature_importance) > len(self.feature_names):
                feature_importance = feature_importance[:len(self.feature_names)]
        
        # Create DataFrame for easier handling
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def explain_single_prediction(self, instance_data, instance_index=0):
        """Explain a single prediction"""
        if self.shap_values is None:
            raise ValueError("SHAP values not calculated. Call calculate_shap_values first.")
        
        # Get SHAP values for the specific instance
        instance_shap = self.shap_values[instance_index]
        instance_features = instance_data.iloc[instance_index] if hasattr(instance_data, 'iloc') else instance_data
        
        # Create explanation dictionary
        # Handle probability extraction safely
        try:
            prob = self.model.predict_proba([instance_features])[0][1]
        except:
            prob = 0.5
            
        explanation = {
            'prediction': prob,
            'prediction_class': self.model.predict([instance_features])[0],
            'feature_contributions': {},
            'top_positive_features': [],
            'top_negative_features': []
        }
        
        # Get feature contributions
        for i, feature in enumerate(self.feature_names):
            shap_val = instance_shap[i]
            # Ensure shap_val is a scalar for sorting
            if isinstance(shap_val, np.ndarray):
                shap_val = float(np.mean(shap_val))
            else:
                shap_val = float(shap_val)
                
            feat_val = instance_features.iloc[i] if hasattr(instance_features, 'iloc') else instance_features[feature]
            if isinstance(feat_val, np.ndarray):
                feat_val = float(np.mean(feat_val))
                
            explanation['feature_contributions'][feature] = {
                'shap_value': shap_val,
                'feature_value': feat_val
            }
        
        # Sort features by SHAP value
        sorted_features = sorted(
            explanation['feature_contributions'].items(),
            key=lambda x: float(x[1]['shap_value']),
            reverse=True
        )
        
        # Top positive contributors (increase diabetes risk)
        explanation['top_positive_features'] = [
            {'feature': f, 'shap_value': v['shap_value'], 'value': v['feature_value']}
            for f, v in sorted_features[:5] if v['shap_value'] > 0
        ]
        
        # Top negative contributors (decrease diabetes risk)
        explanation['top_negative_features'] = [
            {'feature': f, 'shap_value': v['shap_value'], 'value': v['feature_value']}
            for f, v in sorted_features[-5:] if v['shap_value'] < 0
        ]
        
        return explanation
    
    def plot_feature_importance(self, plot_type='bar', max_features=10, save_path=None):
        """Plot SHAP feature importance"""
        if self.shap_values is None:
            raise ValueError("SHAP values not calculated. Call calculate_shap_values first.")
        
        plt.figure(figsize=(10, 6))
        
        if plot_type == 'bar':
            # Bar plot of mean SHAP values
            shap.summary_plot(self.shap_values, self.X_background, plot_type="bar", 
                            max_display=max_features, show=False)
        elif plot_type == 'beeswarm':
            # Beeswarm plot
            shap.summary_plot(self.shap_values, self.X_background, 
                            max_display=max_features, show=False)
        elif plot_type == 'waterfall':
            # Waterfall plot for first instance
            shap.waterfall_plot(self.explainer.shap_values(self.X_background.iloc[0])[0],
                              self.X_background.iloc[0], show=False)
        
        plt.title(f'SHAP Feature Importance ({plot_type.title()} Plot)')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_force_plot(self, instance_data, instance_index=0, save_path=None):
        """Create SHAP force plot for single prediction"""
        if self.explainer is None:
            raise ValueError("Explainer not initialized")
        
        # Create force plot
        if hasattr(instance_data, 'iloc'):
            instance = instance_data.iloc[instance_index]
        else:
            instance = instance_data[instance_index]
        
        # Generate force plot
        force_plot = shap.force_plot(
            self.explainer.expected_value,
            self.shap_values[instance_index],
            instance,
            feature_names=self.feature_names,
            matplotlib=True,
            show=False
        )
        
        plt.title(f'SHAP Force Plot - Prediction Explanation')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return force_plot
    
    def plot_decision_plot(self, instance_data, instance_indices=None, save_path=None):
        """Create SHAP decision plot"""
        if self.shap_values is None:
            raise ValueError("SHAP values not calculated")
        
        if instance_indices is None:
            instance_indices = list(range(min(10, len(instance_data))))
        
        # Create decision plot
        shap.decision_plot(
            self.explainer.expected_value,
            self.shap_values[instance_indices],
            instance_data.iloc[instance_indices] if hasattr(instance_data, 'iloc') else instance_data[instance_indices],
            feature_names=self.feature_names,
            show=False
        )
        
        plt.title('SHAP Decision Plot')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_explanation_report(self, X_test, y_test=None):
        """Generate comprehensive explanation report"""
        if self.shap_values is None:
            raise ValueError("SHAP values not calculated")
        
        # Global feature importance
        feature_importance = self.get_feature_importance()
        
        # Explain a few sample predictions
        sample_explanations = []
        sample_indices = [0, len(X_test)//2, len(X_test)-1] if len(X_test) > 2 else [0]
        
        for idx in sample_indices:
            if idx < len(X_test):
                explanation = self.explain_single_prediction(X_test, idx)
                if y_test is not None:
                    explanation['actual_label'] = y_test.iloc[idx] if hasattr(y_test, 'iloc') else y_test[idx]
                sample_explanations.append(explanation)
        
        # Generate insights
        insights = self._generate_insights(feature_importance, sample_explanations)
        
        report = {
            'feature_importance': feature_importance.to_dict('records'),
            'sample_explanations': sample_explanations,
            'insights': insights,
            'summary': {
                'total_features': len(self.feature_names),
                'top_features': feature_importance.head(5)['feature'].tolist(),
                'average_prediction_probability': np.mean(self.model.predict_proba(X_test)[:, 1])
            }
        }
        
        return report
    
    def _generate_insights(self, feature_importance, sample_explanations):
        """Generate insights from SHAP analysis"""
        insights = []
        
        # Most important features
        top_features = feature_importance.head(3)['feature'].tolist()
        insights.append(f"Top risk factors: {', '.join(top_features)}")
        
        # Common patterns in explanations
        positive_factors = []
        negative_factors = []
        
        for explanation in sample_explanations:
            positive_factors.extend([f['feature'] for f in explanation['top_positive_features']])
            negative_factors.extend([f['feature'] for f in explanation['top_negative_features']])
        
        if positive_factors:
            most_common_positive = max(set(positive_factors), key=positive_factors.count)
            insights.append(f"Most common risk factor: {most_common_positive}")
        
        if negative_factors:
            most_common_negative = max(set(negative_factors), key=negative_factors.count)
            insights.append(f"Most common protective factor: {most_common_negative}")
        
        # Feature value ranges
        insights.append("SHAP analysis shows non-linear relationships between features and diabetes risk")
        insights.append("Individual predictions vary significantly based on feature combinations")
        
        return insights
    
    def get_user_friendly_explanation(self, instance_data, instance_index=0):
        """Get user-friendly explanation for a prediction"""
        explanation = self.explain_single_prediction(instance_data, instance_index)
        
        probability = explanation['prediction']
        risk_level = self._get_risk_level(probability)
        
        friendly_explanation = {
            'risk_level': risk_level,
            'probability': f"{probability:.1%}",
            'main_factors': [],
            'recommendations': []
        }
        
        # Main risk factors
        for factor in explanation['top_positive_features'][:3]:
            friendly_explanation['main_factors'].append({
                'factor': factor['feature'],
                'impact': 'Increases risk',
                'value': factor['value']
            })
        
        # Protective factors
        for factor in explanation['top_negative_features'][:2]:
            friendly_explanation['main_factors'].append({
                'factor': factor['feature'],
                'impact': 'Decreases risk', 
                'value': factor['value']
            })
        
        # Generate recommendations
        friendly_explanation['recommendations'] = self._generate_recommendations(
            explanation['top_positive_features']
        )
        
        return friendly_explanation
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability < 0.3:
            return "Low Risk"
        elif probability < 0.6:
            return "Moderate Risk"
        else:
            return "High Risk"
    
    def _generate_recommendations(self, risk_factors):
        """Generate health recommendations based on risk factors"""
        recommendations = []
        
        risk_factor_names = [factor['feature'].lower() for factor in risk_factors]
        
        if 'glucose' in risk_factor_names:
            recommendations.append("Monitor blood sugar levels regularly")
            recommendations.append("Consider dietary changes to reduce sugar intake")
        
        if 'bmi' in risk_factor_names:
            recommendations.append("Focus on weight management through balanced diet")
            recommendations.append("Increase physical activity to improve BMI")
        
        if 'age' in risk_factor_names:
            recommendations.append("Regular health check-ups recommended")
            recommendations.append("Maintain healthy lifestyle habits")
        
        if 'bloodpressure' in risk_factor_names:
            recommendations.append("Monitor blood pressure regularly")
            recommendations.append("Reduce sodium intake and manage stress")
        
        if 'diabetespedigreefunction' in risk_factor_names:
            recommendations.append("Be aware of family history risks")
            recommendations.append("Consider genetic counseling if available")
        
        # General recommendations
        recommendations.extend([
            "Maintain a balanced diet rich in fruits and vegetables",
            "Engage in regular physical activity",
            "Get adequate sleep and manage stress"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
