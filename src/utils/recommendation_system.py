"""
Health Recommendation System for Sustainable AI Diabetes Prediction
Provides personalized health recommendations based on diabetes risk and health metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns

class HealthRecommendationSystem:
    def __init__(self):
        self.recommendation_categories = {
            'diet': 'Nutrition and Dietary Guidelines',
            'exercise': 'Physical Activity Recommendations',
            'lifestyle': 'Lifestyle Modifications',
            'monitoring': 'Health Monitoring Guidelines',
            'medical': 'Medical Consultation Guidelines'
        }
        
        self.risk_intensity_levels = {
            'low': 'Preventive',
            'moderate': 'Corrective', 
            'high': 'Intensive'
        }
    
    def generate_personalized_recommendations(self, patient_data: Dict, 
                                            risk_assessment: Dict, 
                                            shap_explanation: Dict = None) -> Dict:
        """Generate comprehensive personalized health recommendations"""
        
        # Base recommendations by risk level
        risk_level = risk_assessment.get('risk_level', 'low_risk')
        intensity = self._get_intensity_level(risk_level)
        
        recommendations = {
            'risk_level': risk_level,
            'intensity_level': intensity,
            'priority_actions': self._get_priority_actions(risk_level),
            'categories': {},
            'timeline': self._create_implementation_timeline(risk_level),
            'success_metrics': self._define_success_metrics(patient_data, risk_level)
        }
        
        # Generate category-specific recommendations
        for category in self.recommendation_categories.keys():
            recommendations['categories'][category] = self._generate_category_recommendations(
                category, patient_data, risk_level, shap_explanation
            )
        
        # Add personalized insights
        recommendations['personalized_insights'] = self._generate_personalized_insights(
            patient_data, shap_explanation
        )
        
        return recommendations
    
    def _get_intensity_level(self, risk_level: str) -> str:
        """Get recommendation intensity based on risk level"""
        risk_mapping = {
            'low_risk': 'low',
            'moderate_risk': 'moderate',
            'high_risk': 'high'
        }
        return self.risk_intensity_levels.get(risk_mapping.get(risk_level, 'low'), 'Preventive')
    
    def _get_priority_actions(self, risk_level: str) -> List[str]:
        """Get priority actions based on risk level"""
        if risk_level == 'high_risk':
            return [
                "Immediate medical consultation required",
                "Implement aggressive lifestyle changes",
                "Start daily blood glucose monitoring",
                "Medication review with healthcare provider"
            ]
        elif risk_level == 'moderate_risk':
            return [
                "Schedule medical check-up within 1 month",
                "Implement structured lifestyle modifications",
                "Begin regular health monitoring",
                "Consider preventive screening"
            ]
        else:  # low_risk
            return [
                "Maintain current healthy habits",
                "Schedule regular annual check-ups",
                "Continue preventive health monitoring",
                "Stay informed about diabetes prevention"
            ]
    
    def _generate_category_recommendations(self, category: str, patient_data: Dict, 
                                        risk_level: str, shap_explanation: Dict = None) -> Dict:
        """Generate recommendations for a specific category"""
        
        if category == 'diet':
            return self._generate_diet_recommendations(patient_data, risk_level, shap_explanation)
        elif category == 'exercise':
            return self._generate_exercise_recommendations(patient_data, risk_level, shap_explanation)
        elif category == 'lifestyle':
            return self._generate_lifestyle_recommendations(patient_data, risk_level, shap_explanation)
        elif category == 'monitoring':
            return self._generate_monitoring_recommendations(patient_data, risk_level, shap_explanation)
        elif category == 'medical':
            return self._generate_medical_recommendations(patient_data, risk_level, shap_explanation)
        else:
            return {'recommendations': [], 'priority': 'low'}
    
    def _generate_diet_recommendations(self, patient_data: Dict, risk_level: str, 
                                     shap_explanation: Dict = None) -> Dict:
        """Generate dietary recommendations"""
        recommendations = []
        
        # Base recommendations by risk level
        if risk_level == 'high_risk':
            recommendations.extend([
                "Eliminate refined sugars and processed foods",
                "Follow low-glycemic index diet",
                "Portion control: smaller, frequent meals",
                "Limit carbohydrate intake to 45-60g per meal"
            ])
        elif risk_level == 'moderate_risk':
            recommendations.extend([
                "Reduce sugar intake by 50%",
                "Choose whole grains over refined grains",
                "Increase fiber intake to 25-30g daily",
                "Practice portion control"
            ])
        else:
            recommendations.extend([
                "Maintain balanced diet with variety",
                "Limit added sugars to <25g daily",
                "Choose whole foods over processed",
                "Maintain current healthy eating patterns"
            ])
        
        # Specific recommendations based on health metrics
        glucose = patient_data.get('Glucose', 0)
        bmi = patient_data.get('BMI', 0)
        
        if glucose > 140:
            recommendations.append("Strict carbohydrate monitoring required")
            recommendations.append("Consider consultation with registered dietitian")
        elif glucose > 100:
            recommendations.append("Monitor carbohydrate intake closely")
        
        if bmi > 30:
            recommendations.append("Calorie deficit of 500-750 calories daily")
            recommendations.append("Focus on nutrient-dense, low-calorie foods")
        elif bmi > 25:
            recommendations.append("Maintain calorie balance or slight deficit")
        
        # SHAP-based recommendations
        if shap_explanation:
            glucose_shap = self._get_shap_feature_impact(shap_explanation, 'Glucose')
            if glucose_shap > 0.1:
                recommendations.insert(0, "Glucose levels are major risk factor - immediate dietary intervention needed")
        
        return {
            'recommendations': recommendations[:6],  # Top 6 recommendations
            'priority': 'high' if risk_level == 'high_risk' else 'medium',
            'category': self.recommendation_categories['diet']
        }
    
    def _generate_exercise_recommendations(self, patient_data: Dict, risk_level: str,
                                        shap_explanation: Dict = None) -> Dict:
        """Generate exercise recommendations"""
        recommendations = []
        
        age = patient_data.get('Age', 0)
        bmi = patient_data.get('BMI', 0)
        
        # Base recommendations by risk level
        if risk_level == 'high_risk':
            recommendations.extend([
                "Start with 10-15 minute walks, 3 times daily",
                "Progress to 150 minutes moderate exercise weekly",
                "Include strength training 2-3 times weekly",
                "Monitor blood glucose before and after exercise"
            ])
        elif risk_level == 'moderate_risk':
            recommendations.extend([
                "Aim for 150 minutes moderate exercise weekly",
                "Include both cardio and strength training",
                "Add flexibility and balance exercises",
                "Gradually increase intensity and duration"
            ])
        else:
            recommendations.extend([
                "Maintain 150 minutes moderate exercise weekly",
                "Include variety of physical activities",
                "Focus on consistency and enjoyment",
                "Add strength training 2 times weekly"
            ])
        
        # Age-specific recommendations
        if age > 65:
            recommendations.append("Include balance and flexibility exercises")
            recommendations.append("Consider low-impact activities like swimming")
        elif age > 45:
            recommendations.append("Include weight-bearing exercises")
        
        # BMI-specific recommendations
        if bmi > 30:
            recommendations.append("Start with low-impact exercises to reduce joint stress")
            recommendations.append("Gradually increase duration before intensity")
        
        return {
            'recommendations': recommendations[:5],
            'priority': 'high' if risk_level in ['high_risk', 'moderate_risk'] else 'medium',
            'category': self.recommendation_categories['exercise']
        }
    
    def _generate_lifestyle_recommendations(self, patient_data: Dict, risk_level: str,
                                          shap_explanation: Dict = None) -> Dict:
        """Generate lifestyle recommendations"""
        recommendations = []
        
        # Base recommendations by risk level
        if risk_level == 'high_risk':
            recommendations.extend([
                "Implement stress management techniques daily",
                "Ensure 7-8 hours quality sleep nightly",
                "Quit smoking and limit alcohol completely",
                "Establish consistent daily routine"
            ])
        elif risk_level == 'moderate_risk':
            recommendations.extend([
                "Practice stress management 3-4 times weekly",
                "Maintain regular sleep schedule",
                "Limit alcohol to moderate levels",
                "Create structured daily routine"
            ])
        else:
            recommendations.extend([
                "Continue healthy stress management",
                "Maintain good sleep hygiene",
                "Moderate alcohol consumption if applicable",
                "Keep active social connections"
            ])
        
        # Add specific lifestyle factors
        recommendations.extend([
            "Stay hydrated with 8-10 glasses water daily",
            "Practice mindful eating",
            "Maintain social connections and activities",
            "Regular health screenings and check-ups"
        ])
        
        return {
            'recommendations': recommendations[:6],
            'priority': 'medium',
            'category': self.recommendation_categories['lifestyle']
        }
    
    def _generate_monitoring_recommendations(self, patient_data: Dict, risk_level: str,
                                           shap_explanation: Dict = None) -> Dict:
        """Generate health monitoring recommendations"""
        recommendations = []
        
        if risk_level == 'high_risk':
            recommendations.extend([
                "Daily blood glucose monitoring",
                "Weekly blood pressure checks",
                "Monthly weight tracking",
                "Quarterly A1c testing"
            ])
        elif risk_level == 'moderate_risk':
            recommendations.extend([
                "Weekly blood glucose checks",
                "Bi-weekly blood pressure monitoring",
                "Monthly weight tracking",
                "Semi-annual A1c testing"
            ])
        else:
            recommendations.extend([
                "Monthly blood glucose checks",
                "Monthly blood pressure monitoring",
                "Weekly weight tracking",
                "Annual A1c testing"
            ])
        
        # Add specific monitoring based on health metrics
        if patient_data.get('BloodPressure', 0) > 130:
            recommendations.insert(0, "Daily blood pressure monitoring required")
        
        if patient_data.get('Glucose', 0) > 140:
            recommendations.insert(0, "Fasting and post-meal glucose monitoring")
        
        return {
            'recommendations': recommendations[:5],
            'priority': 'high' if risk_level == 'high_risk' else 'medium',
            'category': self.recommendation_categories['monitoring']
        }
    
    def _generate_medical_recommendations(self, patient_data: Dict, risk_level: str,
                                        shap_explanation: Dict = None) -> Dict:
        """Generate medical consultation recommendations"""
        recommendations = []
        
        if risk_level == 'high_risk':
            recommendations.extend([
                "Immediate consultation with primary care physician",
                "Referral to endocrinologist recommended",
                "Comprehensive diabetes screening required",
                "Consider medication evaluation"
            ])
        elif risk_level == 'moderate_risk':
            recommendations.extend([
                "Schedule medical appointment within 1 month",
                "Discuss preventive diabetes screening",
                "Review current medications with doctor",
                "Consider nutritionist consultation"
            ])
        else:
            recommendations.extend([
                "Annual medical check-up recommended",
                "Discuss diabetes risk at next visit",
                "Review preventive care options",
                "Maintain current medical care plan"
            ])
        
        # Family history considerations
        if patient_data.get('DiabetesPedigreeFunction', 0) > 0.5:
            recommendations.append("Discuss genetic risk factors with doctor")
        
        return {
            'recommendations': recommendations[:4],
            'priority': 'high' if risk_level == 'high_risk' else 'medium',
            'category': self.recommendation_categories['medical']
        }
    
    def _get_shap_feature_impact(self, shap_explanation: Dict, feature_name: str) -> float:
        """Extract SHAP value for a specific feature"""
        if not shap_explanation or 'feature_contributions' not in shap_explanation:
            return 0.0
        
        return shap_explanation['feature_contributions'].get(feature_name, {}).get('shap_value', 0.0)
    
    def _generate_personalized_insights(self, patient_data: Dict, shap_explanation: Dict = None) -> List[str]:
        """Generate personalized insights based on data"""
        insights = []
        
        # Analyze key metrics
        glucose = patient_data.get('Glucose', 0)
        bmi = patient_data.get('BMI', 0)
        age = patient_data.get('Age', 0)
        bp = patient_data.get('BloodPressure', 0)
        
        # Glucose insights
        if glucose > 140:
            insights.append("Your glucose level indicates immediate medical attention is needed")
        elif glucose > 100:
            insights.append("Your glucose level is elevated and requires monitoring")
        else:
            insights.append("Your glucose level is within normal range")
        
        # BMI insights
        if bmi > 30:
            insights.append("Weight management is critical for reducing diabetes risk")
        elif bmi > 25:
            insights.append("Moderate weight loss could significantly reduce your risk")
        else:
            insights.append("Your weight is in a healthy range")
        
        # Age insights
        if age > 65:
            insights.append("Age increases diabetes risk - regular monitoring is essential")
        elif age > 45:
            insights.append("Your age group has increased diabetes risk")
        
        # SHAP-based insights
        if shap_explanation and 'top_positive_features' in shap_explanation:
            top_factors = [f['feature'] for f in shap_explanation['top_positive_features'][:3]]
            insights.append(f"Your main risk factors are: {', '.join(top_factors)}")
        
        return insights
    
    def _create_implementation_timeline(self, risk_level: str) -> Dict:
        """Create implementation timeline based on risk level"""
        if risk_level == 'high_risk':
            return {
                'immediate': ['Medical consultation', 'Start glucose monitoring', 'Eliminate sugars'],
                '1_week': ['Implement dietary changes', 'Start gentle exercise', 'Medication review'],
                '1_month': ['Establish exercise routine', 'Weight management plan', 'Regular monitoring'],
                '3_months': ['Comprehensive lifestyle changes', 'Specialist consultations', 'Advanced monitoring']
            }
        elif risk_level == 'moderate_risk':
            return {
                'immediate': ['Schedule medical appointment', 'Start dietary modifications'],
                '1_week': ['Begin exercise program', 'Implement monitoring routine'],
                '1_month': ['Establish healthy habits', 'Regular health tracking'],
                '3_months': ['Lifestyle optimization', 'Preventive care plan']
            }
        else:
            return {
                'immediate': ['Maintain current healthy habits'],
                '1_week': ['Schedule annual check-up'],
                '1_month': ['Continue preventive measures'],
                '3_months': ['Regular health maintenance']
            }
    
    def _define_success_metrics(self, patient_data: Dict, risk_level: str) -> List[str]:
        """Define success metrics for tracking progress"""
        metrics = [
            "Blood glucose levels within target range",
            "Weight management progress",
            "Exercise consistency (150 minutes/week)",
            "Dietary adherence goals"
        ]
        
        if risk_level == 'high_risk':
            metrics.extend([
                "A1c reduction by 1% within 3 months",
                "Blood pressure control",
                "Medication compliance",
                "Daily glucose log maintenance"
            ])
        elif risk_level == 'moderate_risk':
            metrics.extend([
                "A1c stable or improving",
                "Weight loss of 5-10% if overweight",
                "Regular monitoring adherence",
                "Lifestyle change consistency"
            ])
        
        return metrics
    
    def generate_action_plan(self, recommendations: Dict) -> Dict:
        """Generate structured action plan from recommendations"""
        action_plan = {
            'immediate_actions': [],
            'short_term_goals': [],
            'long_term_objectives': [],
            'tracking_methods': [],
            'support_resources': []
        }
        
        # Extract immediate actions from priority actions
        action_plan['immediate_actions'] = recommendations.get('priority_actions', [])
        
        # Extract short-term goals from timeline
        timeline = recommendations.get('timeline', {})
        action_plan['short_term_goals'] = timeline.get('1_week', []) + timeline.get('1_month', [])
        
        # Extract long-term objectives
        action_plan['long_term_objectives'] = timeline.get('3_months', [])
        
        # Add tracking methods
        action_plan['tracking_methods'] = [
            "Daily symptom and glucose log",
            "Weekly weight and blood pressure tracking",
            "Monthly progress review",
            "Quarterly medical check-ups"
        ]
        
        # Add support resources
        action_plan['support_resources'] = [
            "Healthcare provider team",
            "Diabetes education programs",
            "Nutrition counseling services",
            "Support groups and communities",
            "Digital health tracking apps"
        ]
        
        return action_plan
    
    def visualize_recommendations(self, recommendations: Dict, save_path=None):
        """Visualize recommendations breakdown"""
        categories = list(recommendations['categories'].keys())
        priorities = [recommendations['categories'][cat]['priority'] for cat in categories]
        counts = [len(recommendations['categories'][cat]['recommendations']) for cat in categories]
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Priority breakdown
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for priority in priorities:
            priority_counts[priority] += 1
        
        colors_priority = {'high': '#e74c3c', 'medium': '#f39c12', 'low': '#2ecc71'}
        ax1.bar(priority_counts.keys(), priority_counts.values(), 
                color=[colors_priority[p] for p in priority_counts.keys()])
        ax1.set_title('Recommendation Priority Distribution')
        ax1.set_ylabel('Number of Categories')
        
        # Category recommendation counts
        category_labels = [cat.replace('_', ' ').title() for cat in categories]
        ax2.bar(category_labels, counts, color='skyblue')
        ax2.set_title('Recommendations by Category')
        ax2.set_ylabel('Number of Recommendations')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
