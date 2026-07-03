"""
Risk Classification Module for Sustainable AI Diabetes Prediction
Classifies diabetes risk into levels and provides detailed risk assessment
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

class RiskClassifier:
    def __init__(self):
        self.risk_thresholds = {
            'low_risk': (0.0, 0.3),
            'moderate_risk': (0.3, 0.6),
            'high_risk': (0.6, 1.0)
        }
        self.risk_colors = {
            'low_risk': '#2ecc71',      # Green
            'moderate_risk': '#f39c12', # Orange  
            'high_risk': '#e74c3c'      # Red
        }
        self.risk_descriptions = {
            'low_risk': "Low probability of diabetes. Maintain healthy lifestyle.",
            'moderate_risk': "Moderate probability of diabetes. Consider lifestyle changes.",
            'high_risk': "High probability of diabetes. Medical consultation recommended."
        }
        
    def classify_risk(self, probability: float) -> Dict[str, Any]:
        """Classify individual risk based on probability"""
        if not 0 <= probability <= 1:
            raise ValueError("Probability must be between 0 and 1")
        
        # Determine risk level
        risk_level = None
        for level, (min_prob, max_prob) in self.risk_thresholds.items():
            if min_prob <= probability < max_prob:
                risk_level = level
                break
        
        if risk_level is None:
            risk_level = 'high_risk'  # Default to high if probability = 1.0
        
        return {
            'probability': probability,
            'risk_level': risk_level,
            'risk_score': self._calculate_risk_score(probability),
            'color': self.risk_colors[risk_level],
            'description': self.risk_descriptions[risk_level],
            'urgency': self._get_urgency_level(risk_level),
            'confidence': self._calculate_confidence(probability)
        }
    
    def _calculate_risk_score(self, probability: float) -> int:
        """Calculate risk score (0-100)"""
        return int(probability * 100)
    
    def _get_urgency_level(self, risk_level: str) -> str:
        """Get urgency level based on risk classification"""
        urgency_map = {
            'low_risk': 'Routine',
            'moderate_risk': 'Soon',
            'high_risk': 'Immediate'
        }
        return urgency_map.get(risk_level, 'Routine')
    
    def _calculate_confidence(self, probability: float) -> str:
        """Calculate confidence in prediction"""
        if probability < 0.2 or probability > 0.8:
            return 'High'
        elif probability < 0.35 or probability > 0.65:
            return 'Medium'
        else:
            return 'Low'
    
    def batch_classify_risks(self, probabilities: List[float]) -> List[Dict]:
        """Classify risks for multiple predictions"""
        return [self.classify_risk(prob) for prob in probabilities]
    
    def analyze_risk_distribution(self, probabilities: List[float]) -> Dict:
        """Analyze distribution of risk levels in a population"""
        classifications = self.batch_classify_risks(probabilities)
        
        risk_counts = {}
        for classification in classifications:
            risk_level = classification['risk_level']
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        total_samples = len(classifications)
        risk_percentages = {
            level: (count / total_samples) * 100 
            for level, count in risk_counts.items()
        }
        
        return {
            'total_samples': total_samples,
            'risk_counts': risk_counts,
            'risk_percentages': risk_percentages,
            'average_risk_score': np.mean([c['risk_score'] for c in classifications]),
            'high_risk_percentage': risk_percentages.get('high_risk', 0),
            'population_risk_level': self._determine_population_risk(risk_percentages)
        }
    
    def _determine_population_risk(self, risk_percentages: Dict) -> str:
        """Determine overall population risk level"""
        high_risk_pct = risk_percentages.get('high_risk', 0)
        moderate_risk_pct = risk_percentages.get('moderate_risk', 0)
        
        if high_risk_pct > 30:
            return 'High Risk Population'
        elif high_risk_pct > 15 or moderate_risk_pct > 40:
            return 'Moderate Risk Population'
        else:
            return 'Low Risk Population'
    
    def create_risk_profile(self, patient_data: Dict, probability: float) -> Dict:
        """Create comprehensive risk profile for a patient"""
        risk_classification = self.classify_risk(probability)
        
        # Extract key health metrics
        key_metrics = {
            'glucose': patient_data.get('Glucose', 0),
            'bmi': patient_data.get('BMI', 0),
            'age': patient_data.get('Age', 0),
            'blood_pressure': patient_data.get('BloodPressure', 0),
            'family_history': patient_data.get('DiabetesPedigreeFunction', 0)
        }
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(key_metrics)
        
        # Create risk profile
        risk_profile = {
            'patient_info': {
                'age': key_metrics['age'],
                'bmi': key_metrics['bmi'],
                'glucose': key_metrics['glucose'],
                'blood_pressure': key_metrics['blood_pressure']
            },
            'risk_assessment': risk_classification,
            'risk_factors': risk_factors,
            'health_metrics': key_metrics,
            'recommendations': self._get_risk_specific_recommendations(risk_classification['risk_level'], risk_factors)
        }
        
        return risk_profile
    
    def _identify_risk_factors(self, metrics: Dict) -> List[Dict]:
        """Identify specific risk factors based on health metrics"""
        risk_factors = []
        
        # Glucose levels (Standard thresholds: Fasting > 100 is prediabetes, > 126 is diabetes)
        if metrics['glucose'] > 126:
            risk_factors.append({
                'factor': 'High Glucose',
                'value': metrics['glucose'],
                'severity': 'High',
                'description': 'Blood sugar levels are in the diabetic range.'
            })
        elif metrics['glucose'] > 99:
            risk_factors.append({
                'factor': 'Elevated Glucose',
                'value': metrics['glucose'],
                'severity': 'Medium',
                'description': 'Blood sugar levels are in the pre-diabetic range.'
            })
        
        # BMI
        if metrics['bmi'] >= 30:
            risk_factors.append({
                'factor': 'Obesity (BMI)',
                'value': metrics['bmi'],
                'severity': 'High',
                'description': 'Obesity significantly increases metabolic risk.'
            })
        elif metrics['bmi'] >= 25:
            risk_factors.append({
                'factor': 'Overweight (BMI)',
                'value': metrics['bmi'],
                'severity': 'Medium',
                'description': 'Being overweight increases the risk of insulin resistance.'
            })
        
        # Age
        if metrics['age'] >= 45:
            risk_factors.append({
                'factor': 'Age Group (45+)',
                'value': metrics['age'],
                'severity': 'Medium',
                'description': 'Risk increases significantly after age 45.'
            })
        
        # Blood Pressure
        if metrics['blood_pressure'] >= 140:
            risk_factors.append({
                'factor': 'Hypertension',
                'value': metrics['blood_pressure'],
                'severity': 'High',
                'description': 'High blood pressure is strongly associated with diabetes.'
            })
        elif metrics['blood_pressure'] >= 130:
            risk_factors.append({
                'factor': 'Elevated Blood Pressure',
                'value': metrics['blood_pressure'],
                'severity': 'Medium',
                'description': 'Blood pressure is above the healthy range.'
            })
        
        # Family History
        if metrics['family_history'] > 0.5:
            risk_factors.append({
                'factor': 'Genetic Predisposition',
                'value': metrics['family_history'],
                'severity': 'Medium',
                'description': 'Family history indicates higher genetic risk.'
            })
            
        # Pregnancies (if applicable)
        if metrics.get('pregnancies', 0) > 5:
            risk_factors.append({
                'factor': 'High Number of Pregnancies',
                'value': metrics['pregnancies'],
                'severity': 'Medium',
                'description': 'History of multiple pregnancies can increase risk.'
            })
        
        return risk_factors
    
    def _get_risk_specific_recommendations(self, risk_level: str, risk_factors: List[Dict]) -> List[str]:
        """Get recommendations based on risk level and specific factors"""
        recommendations = []
        
        # Base recommendations by risk level
        if risk_level == 'high_risk':
            recommendations.extend([
                "Consult healthcare provider immediately",
                "Comprehensive medical evaluation recommended",
                "Consider diabetes screening tests",
                "Implement aggressive lifestyle changes"
            ])
        elif risk_level == 'moderate_risk':
            recommendations.extend([
                "Schedule medical check-up soon",
                "Consider preventive screening",
                "Implement lifestyle modifications",
                "Monitor risk factors regularly"
            ])
        else:  # low_risk
            recommendations.extend([
                "Maintain current healthy habits",
                "Regular annual check-ups",
                "Continue monitoring health metrics",
                "Stay informed about diabetes prevention"
            ])
        
        # Specific recommendations based on risk factors
        for factor in risk_factors:
            if 'Glucose' in factor['factor']:
                recommendations.append("Reduce sugar and refined carbohydrate intake")
            elif 'BMI' in factor['factor']:
                recommendations.append("Focus on weight management through diet and exercise")
            elif 'Blood Pressure' in factor['factor']:
                recommendations.append("Implement sodium reduction and stress management")
            elif 'Family History' in factor['factor']:
                recommendations.append("Be vigilant about regular health monitoring")
        
        # Remove duplicates and limit to top recommendations
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:6]
    
    def plot_risk_distribution(self, probabilities: List[float], save_path=None):
        """Plot risk distribution visualization"""
        distribution = self.analyze_risk_distribution(probabilities)
        
        # Create pie chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Pie chart
        labels = list(distribution['risk_percentages'].keys())
        sizes = list(distribution['risk_percentages'].values())
        colors = [self.risk_colors[label] for label in labels]
        
        # Format labels for pie chart
        formatted_labels = [
            f"{label.replace('_', ' ').title()}\n({size:.1f}%)"
            for label, size in zip(labels, sizes)
        ]
        
        ax1.pie(sizes, labels=formatted_labels, colors=colors, autopct='', startangle=90)
        ax1.set_title('Risk Level Distribution')
        
        # Bar chart
        ax2.bar(labels, sizes, color=[self.risk_colors[label] for label in labels])
        ax2.set_title('Risk Level Distribution')
        ax2.set_ylabel('Percentage (%)')
        ax2.set_xlabel('Risk Level')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add percentage labels on bars
        for i, (label, size) in enumerate(zip(labels, sizes)):
            ax2.text(i, size + 1, f'{size:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_risk_gauge(self, probability: float, save_path=None):
        """Plot risk gauge for individual prediction"""
        risk_info = self.classify_risk(probability)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create gauge-like visualization
        theta = np.linspace(0, np.pi, 100)
        r = 1
        
        # Background arc
        ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=2)
        
        # Color-coded sections
        sections = [
            (0, np.pi/3, self.risk_colors['low_risk']),
            (np.pi/3, 2*np.pi/3, self.risk_colors['moderate_risk']),
            (2*np.pi/3, np.pi, self.risk_colors['high_risk'])
        ]
        
        for start, end, color in sections:
            section_theta = np.linspace(start, end, 50)
            ax.plot(np.cos(section_theta), np.sin(section_theta), color=color, linewidth=8, alpha=0.7)
        
        # Risk needle
        needle_angle = np.pi * (1 - probability)
        needle_x = [0, 0.9 * np.cos(needle_angle)]
        needle_y = [0, 0.9 * np.sin(needle_angle)]
        ax.plot(needle_x, needle_y, 'k-', linewidth=3)
        ax.plot(0, 0, 'ko', markersize=8)
        
        # Add labels
        ax.text(-0.5, -0.3, 'LOW', fontsize=12, fontweight='bold', color=self.risk_colors['low_risk'])
        ax.text(0, -0.3, 'MODERATE', fontsize=12, fontweight='bold', color=self.risk_colors['moderate_risk'])
        ax.text(0.5, -0.3, 'HIGH', fontsize=12, fontweight='bold', color=self.risk_colors['high_risk'])
        
        # Add probability text
        ax.text(0, 0.5, f'{probability:.1%}', fontsize=20, fontweight='bold', ha='center')
        ax.text(0, 0.3, risk_info['risk_level'].replace('_', ' ').title(), 
                fontsize=14, ha='center', color=risk_info['color'])
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.5, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title('Diabetes Risk Assessment', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_risk_report(self, patient_data: Dict, probability: float) -> Dict:
        """Generate comprehensive risk report"""
        risk_profile = self.create_risk_profile(patient_data, probability)
        
        report = {
            'patient_summary': {
                'risk_level': risk_profile['risk_assessment']['risk_level'],
                'risk_score': risk_profile['risk_assessment']['risk_score'],
                'probability': risk_profile['risk_assessment']['probability'],
                'urgency': risk_profile['risk_assessment']['urgency'],
                'confidence': risk_profile['risk_assessment']['confidence']
            },
            'key_findings': {
                'total_risk_factors': len(risk_profile['risk_factors']),
                'high_severity_factors': len([f for f in risk_profile['risk_factors'] if f['severity'] == 'High']),
                'primary_concerns': [f['factor'] for f in risk_profile['risk_factors'][:3]]
            },
            'risk_factors': risk_profile['risk_factors'],
            'recommendations': risk_profile['recommendations'],
            'next_steps': self._get_next_steps(risk_profile['risk_assessment']['risk_level'])
        }
        
        return report
    
    def _get_next_steps(self, risk_level: str) -> List[str]:
        """Get recommended next steps based on risk level"""
        if risk_level == 'high_risk':
            return [
                "Schedule appointment with healthcare provider within 1 week",
                "Request comprehensive diabetes screening",
                "Begin daily blood glucose monitoring",
                "Implement immediate dietary changes"
            ]
        elif risk_level == 'moderate_risk':
            return [
                "Schedule medical check-up within 1 month",
                "Consider preventive diabetes screening",
                "Implement gradual lifestyle changes",
                "Set up regular health monitoring"
            ]
        else:
            return [
                "Continue regular annual check-ups",
                "Maintain healthy lifestyle habits",
                "Stay informed about diabetes prevention",
                "Monitor for any changes in health"
            ]
