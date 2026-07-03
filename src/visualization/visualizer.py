"""
Visualization Module for Sustainable AI Diabetes Prediction
Creates comprehensive charts and graphs for data analysis and results
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class DiabetesVisualizer:
    def __init__(self):
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        self.colors = {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#9b59b6',
            'dark': '#2c3e50'
        }

    def _normalize_importance_df(self, importance_df):
        """Normalize incoming importance data to have 'Feature' and 'Importance' columns."""
        df = pd.DataFrame(importance_df)
        # Rename lowercase keys if present
        if 'feature' in df.columns and 'importance' in df.columns:
            df = df.rename(columns={'feature': 'Feature', 'importance': 'Importance'})
        return df
    
    def plot_dataset_overview(self, df, save_path=None):
        """Create comprehensive dataset overview visualization"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Class distribution
        class_counts = df['Outcome'].value_counts()
        axes[0, 0].pie(class_counts.values, labels=['Non-Diabetic', 'Diabetic'], 
                       autopct='%1.1f%%', colors=[self.colors['secondary'], self.colors['danger']])
        axes[0, 0].set_title('Class Distribution')
        
        # 2. Age distribution by class
        sns.histplot(data=df, x='Age', hue='Outcome', kde=True, ax=axes[0, 1])
        axes[0, 1].set_title('Age Distribution by Diabetes Status')
        
        # 3. BMI distribution
        sns.histplot(data=df, x='BMI', hue='Outcome', kde=True, ax=axes[0, 2])
        axes[0, 2].set_title('BMI Distribution by Diabetes Status')
        
        # 4. Glucose levels
        sns.boxplot(data=df, x='Outcome', y='Glucose', ax=axes[1, 0])
        axes[1, 0].set_title('Glucose Levels by Diabetes Status')
        axes[1, 0].set_xticklabels(['Non-Diabetic', 'Diabetic'])
        
        # 5. Correlation heatmap
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1, 1])
        axes[1, 1].set_title('Feature Correlation Matrix')
        
        # 6. Feature distributions
        feature_cols = ['BloodPressure', 'SkinThickness', 'Insulin', 'DiabetesPedigreeFunction']
        for i, col in enumerate(feature_cols[:2]):
            sns.violinplot(data=df, x='Outcome', y=col, ax=axes[1, 2] if i == 0 else axes[1, 2])
        
        axes[1, 2].set_title('Key Feature Distributions')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_feature_importance(self, importance_df, title="Feature Importance", save_path=None):
        """Plot feature importance with enhanced visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar plot
        df = self._normalize_importance_df(importance_df)
        df.head(10).plot(kind='barh', x='Feature', y='Importance', 
                      color=self.colors['primary'], ax=ax1)
        ax1.set_title(title)
        ax1.set_xlabel('Importance Score')
        
        # Pie chart for top 5 features
        top_5 = df.head(5)
        ax2.pie(top_5['Importance'], labels=top_5['Feature'], autopct='%1.1f%%',
               colors=sns.color_palette("husl", 5))
        ax2.set_title('Top 5 Features Distribution')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_model_comparison(self, comparison_df, save_path=None):
        """Create comprehensive model comparison visualization"""
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Overall performance radar-style comparison
        comparison_df[metrics].plot(kind='bar', ax=axes[0, 0])
        axes[0, 0].set_title('Model Performance Comparison')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 2. F1-Score comparison (primary metric)
        comparison_df['F1-Score'].plot(kind='bar', color=self.colors['primary'], ax=axes[0, 1])
        axes[0, 1].set_title('F1-Score Comparison')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Accuracy vs F1-Score scatter
        axes[1, 0].scatter(comparison_df['Accuracy'], comparison_df['F1-Score'], 
                          s=100, alpha=0.7, c=self.colors['info'])
        
        for i, model in enumerate(comparison_df.index):
            axes[1, 0].annotate(model, (comparison_df.iloc[i]['Accuracy'], 
                                       comparison_df.iloc[i]['F1-Score']),
                              xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        axes[1, 0].set_xlabel('Accuracy')
        axes[1, 0].set_ylabel('F1-Score')
        axes[1, 0].set_title('Accuracy vs F1-Score')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Overall ranking
        ranking = comparison_df.sort_values('F1-Score', ascending=True)
        axes[1, 1].barh(ranking.index, ranking['F1-Score'], color=self.colors['secondary'])
        axes[1, 1].set_title('Model Ranking by F1-Score')
        axes[1, 1].set_xlabel('F1-Score')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_sustainability_analysis(self, sustainability_df, save_path=None):
        """Create sustainability analysis visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Overall sustainability score
        sustainability_df['sustainability_score'].sort_values().plot(
            kind='barh', color=self.colors['secondary'], ax=axes[0, 0])
        axes[0, 0].set_title('Sustainability Score Ranking')
        axes[0, 0].set_xlabel('Sustainability Score')
        
        # 2. Resource efficiency components
        resource_metrics = ['time_efficiency', 'memory_efficiency', 'size_efficiency']
        sustainability_df[resource_metrics].plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('Resource Efficiency Components')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 3. Performance vs Sustainability
        axes[1, 0].scatter(sustainability_df['performance_score'], 
                          sustainability_df['sustainability_score'],
                          s=100, alpha=0.7, c=self.colors['warning'])
        
        for i, model in enumerate(sustainability_df.index):
            axes[1, 0].annotate(model, 
                              (sustainability_df.iloc[i]['performance_score'], 
                               sustainability_df.iloc[i]['sustainability_score']),
                              xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        axes[1, 0].set_xlabel('Performance Score')
        axes[1, 0].set_ylabel('Sustainability Score')
        axes[1, 0].set_title('Performance vs Sustainability Trade-off')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Carbon footprint
        sustainability_df['carbon_footprint_estimate'].sort_values().plot(
            kind='barh', color=self.colors['danger'], ax=axes[1, 1])
        axes[1, 1].set_title('Estimated Carbon Footprint')
        axes[1, 1].set_xlabel('CO2 (grams)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_interactive_dashboard(self, data_dict, save_path=None):
        """Create interactive dashboard using Plotly"""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Model Performance', 'Risk Distribution', 
                          'Feature Importance', 'Sustainability Analysis',
                          'ROC Curves', 'Prediction Confidence'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # 1. Model Performance
        if 'model_comparison' in data_dict:
            comparison_df = data_dict['model_comparison']
            fig.add_trace(
                go.Bar(x=comparison_df.index, y=comparison_df['F1-Score'],
                      name='F1-Score', marker_color='lightblue'),
                row=1, col=1
            )
        
        # 2. Risk Distribution
        if 'risk_distribution' in data_dict:
            risk_dist = data_dict['risk_distribution']
            fig.add_trace(
                go.Pie(labels=list(risk_dist.keys()), 
                      values=list(risk_dist.values()),
                      name="Risk Distribution"),
                row=1, col=2
            )
        
        # 3. Feature Importance
        if 'feature_importance' in data_dict:
            importance_df = data_dict['feature_importance']
            df = self._normalize_importance_df(importance_df)
            fig.add_trace(
                go.Bar(x=df['Feature'].head(10), 
                      y=df['Importance'].head(10),
                      name='Feature Importance', marker_color='lightgreen'),
                row=2, col=1
            )
        
        # 4. Sustainability Analysis
        if 'sustainability_metrics' in data_dict:
            sust_df = data_dict['sustainability_metrics']
            fig.add_trace(
                go.Scatter(x=sust_df['performance_score'], 
                          y=sust_df['sustainability_score'],
                          mode='markers+text',
                          text=sust_df.index,
                          textposition="top center",
                          name='Sustainability', marker_color='orange'),
                row=2, col=2
            )
        
        # 5. ROC Curves
        if 'roc_curves' in data_dict:
            for model_name, roc_data in data_dict['roc_curves'].items():
                fig.add_trace(
                    go.Scatter(x=roc_data['fpr'], y=roc_data['tpr'],
                              mode='lines', name=f'{model_name} ROC'),
                    row=3, col=1
                )
        
        # 6. Prediction Confidence
        if 'prediction_confidence' in data_dict:
            confidences = data_dict['prediction_confidence']
            fig.add_trace(
                go.Histogram(x=confidences, nbinsx=20, name='Confidence'),
                row=3, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Diabetes Prediction Dashboard",
            showlegend=True,
            height=1200
        )
        
        if save_path:
            fig.write_html(save_path)
        
        fig.show()
    
    def plot_shap_explanations(self, shap_values, feature_names, save_path=None):
        """Create SHAP explanation visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Feature importance (bar)
        mean_shap = np.mean(np.abs(shap_values), axis=0)
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': mean_shap
        }).sort_values('importance', ascending=True)
        
        axes[0, 0].barh(feature_importance['feature'], feature_importance['importance'])
        axes[0, 0].set_title('SHAP Feature Importance')
        axes[0, 0].set_xlabel('Mean |SHAP Value|')
        
        # 2. SHAP summary (beeswarm-like)
        # Sample for visualization if too many instances
        sample_indices = np.random.choice(len(shap_values), 
                                        min(100, len(shap_values)), replace=False)
        sample_shap = shap_values[sample_indices]
        
        for i, feature in enumerate(feature_names[:8]):  # Top 8 features
            shap_values_feature = sample_shap[:, i]
            axes[0, 1].scatter(shap_values_feature, [i] * len(shap_values_feature), 
                              alpha=0.5, s=20)
        
        axes[0, 1].set_yticks(range(len(feature_names[:8])))
        axes[0, 1].set_yticklabels(feature_names[:8])
        axes[0, 1].set_title('SHAP Summary Plot')
        axes[0, 1].set_xlabel('SHAP Value')
        axes[0, 1].axvline(x=0, color='red', linestyle='--', alpha=0.5)
        
        # 3. Single prediction explanation
        if len(shap_values) > 0:
            instance_idx = 0
            instance_shap = shap_values[instance_idx]
            
            # Sort by SHAP value
            sorted_idx = np.argsort(instance_shap)
            top_features = 8
            top_idx = sorted_idx[-top_features:]
            
            colors = ['red' if v > 0 else 'blue' for v in instance_shap[top_idx]]
            axes[1, 0].barh(range(top_features), instance_shap[top_idx], color=colors)
            axes[1, 0].set_yticks(range(top_features))
            axes[1, 0].set_yticklabels([feature_names[i] for i in top_idx])
            axes[1, 0].set_title(f'Single Prediction Explanation (Instance {instance_idx})')
            axes[1, 0].set_xlabel('SHAP Value')
            axes[1, 0].axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        # 4. SHAP value distribution
        for i, feature in enumerate(feature_names[:5]):
            shap_values_feature = shap_values[:, i]
            axes[1, 1].hist(shap_values_feature, alpha=0.7, label=feature, bins=20)
        
        axes[1, 1].set_title('SHAP Value Distributions')
        axes[1, 1].set_xlabel('SHAP Value')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].axvline(x=0, color='red', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_risk_analysis(self, risk_data, save_path=None):
        """Create comprehensive risk analysis visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Risk distribution
        if 'risk_distribution' in risk_data:
            risk_dist = risk_data['risk_distribution']
            labels = list(risk_dist.keys())
            sizes = list(risk_dist.values())
            colors = [self.colors['secondary'], self.colors['warning'], self.colors['danger']]
            
            axes[0, 0].pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
            axes[0, 0].set_title('Risk Level Distribution')
        
        # 2. Risk factors analysis
        if 'risk_factors' in risk_data:
            factors = risk_data['risk_factors']
            factor_names = [f['factor'] for f in factors]
            factor_scores = [f.get('score', 1) for f in factors]
            
            axes[0, 1].barh(factor_names, factor_scores, color=self.colors['warning'])
            axes[0, 1].set_title('Risk Factors Impact')
            axes[0, 1].set_xlabel('Risk Score')
        
        # 3. Risk probability distribution
        if 'probabilities' in risk_data:
            probs = risk_data['probabilities']
            axes[1, 0].hist(probs, bins=30, color=self.colors['info'], alpha=0.7)
            axes[1, 0].set_title('Risk Probability Distribution')
            axes[1, 0].set_xlabel('Probability')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].axvline(x=0.3, color='green', linestyle='--', alpha=0.5, label='Low Risk')
            axes[1, 0].axvline(x=0.6, color='orange', linestyle='--', alpha=0.5, label='Moderate Risk')
            axes[1, 0].legend()
        
        # 4. Risk gauge visualization
        if 'average_risk' in risk_data:
            avg_risk = risk_data['average_risk']
            
            # Create gauge-like visualization
            theta = np.linspace(0, np.pi, 100)
            
            # Background arc
            axes[1, 1].plot(np.cos(theta), np.sin(theta), 'k-', linewidth=2)
            
            # Color-coded sections
            sections = [
                (0, np.pi/3, self.colors['secondary']),
                (np.pi/3, 2*np.pi/3, self.colors['warning']),
                (2*np.pi/3, np.pi, self.colors['danger'])
            ]
            
            for start, end, color in sections:
                section_theta = np.linspace(start, end, 50)
                axes[1, 1].plot(np.cos(section_theta), np.sin(section_theta), 
                               color=color, linewidth=8, alpha=0.7)
            
            # Risk needle
            needle_angle = np.pi * (1 - avg_risk)
            axes[1, 1].plot([0, 0.9 * np.cos(needle_angle)], 
                          [0, 0.9 * np.sin(needle_angle)], 'k-', linewidth=3)
            axes[1, 1].plot(0, 0, 'ko', markersize=8)
            
            axes[1, 1].text(-0.5, -0.3, 'LOW', fontsize=12, fontweight='bold', 
                          color=self.colors['secondary'])
            axes[1, 1].text(0, -0.3, 'MODERATE', fontsize=12, fontweight='bold', 
                          color=self.colors['warning'])
            axes[1, 1].text(0.5, -0.3, 'HIGH', fontsize=12, fontweight='bold', 
                          color=self.colors['danger'])
            axes[1, 1].text(0, 0.5, f'{avg_risk:.1%}', fontsize=20, fontweight='bold', ha='center')
            
            axes[1, 1].set_xlim(-1.2, 1.2)
            axes[1, 1].set_ylim(-0.5, 1.2)
            axes[1, 1].set_aspect('equal')
            axes[1, 1].axis('off')
            axes[1, 1].set_title('Average Risk Level')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_comprehensive_report(self, all_results, save_path=None):
        """Create comprehensive visualization report"""
        # Create a large figure with multiple subplots
        fig = plt.figure(figsize=(20, 24))
        
        # Define subplot layout
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
        
        # 1. Dataset Overview
        ax1 = fig.add_subplot(gs[0, 0])
        if 'dataset_info' in all_results:
            info = all_results['dataset_info']
            ax1.text(0.1, 0.9, f"Total Samples: {info.get('shape', [0])[0]}", 
                    transform=ax1.transAxes, fontsize=12)
            ax1.text(0.1, 0.7, f"Features: {len(info.get('features', []))}", 
                    transform=ax1.transAxes, fontsize=12)
            ax1.text(0.1, 0.5, f"Missing Values: {info.get('missing_values', 0)}", 
                    transform=ax1.transAxes, fontsize=12)
            ax1.set_title('Dataset Information')
            ax1.axis('off')
        
        # 2. Model Performance
        ax2 = fig.add_subplot(gs[0, 1])
        if 'model_comparison' in all_results:
            comparison_df = all_results['model_comparison']
            comparison_df['F1-Score'].plot(kind='bar', ax=ax2, color=self.colors['primary'])
            ax2.set_title('Model Performance (F1-Score)')
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. Sustainability
        ax3 = fig.add_subplot(gs[0, 2])
        if 'sustainability_metrics' in all_results:
            sust_df = all_results['sustainability_metrics']
            sust_df['sustainability_score'].plot(kind='bar', ax=ax3, color=self.colors['secondary'])
            ax3.set_title('Sustainability Score')
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. Feature Importance
        ax4 = fig.add_subplot(gs[1, :2])
        if 'feature_importance' in all_results:
            importance_df = all_results['feature_importance']
            df = self._normalize_importance_df(importance_df)
            df.head(10).plot(kind='barh', x='Feature', y='Importance', ax=ax4)
            ax4.set_title('Top 10 Feature Importance')
        
        # 5. Risk Distribution
        ax5 = fig.add_subplot(gs[1, 2])
        if 'risk_distribution' in all_results:
            risk_dist = all_results['risk_distribution']
            ax5.pie(list(risk_dist.values()), labels=list(risk_dist.keys()), autopct='%1.1f%%')
            ax5.set_title('Risk Distribution')
        
        # 6. Confusion Matrix (for best model)
        ax6 = fig.add_subplot(gs[2, 0])
        if 'best_model_metrics' in all_results:
            cm = all_results['best_model_metrics'].get('confusion_matrix', [[0, 0], [0, 0]])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax6)
            ax6.set_title('Confusion Matrix (Best Model)')
        
        # 7. ROC Curves
        ax7 = fig.add_subplot(gs[2, 1])
        if 'roc_curves' in all_results:
            for model_name, roc_data in all_results['roc_curves'].items():
                ax7.plot(roc_data['fpr'], roc_data['tpr'], label=f'{model_name}')
            ax7.plot([0, 1], [0, 1], 'k--')
            ax7.set_xlabel('False Positive Rate')
            ax7.set_ylabel('True Positive Rate')
            ax7.set_title('ROC Curves')
            ax7.legend()
        
        # 8. Training Time Comparison
        ax8 = fig.add_subplot(gs[2, 2])
        if 'training_stats' in all_results:
            training_times = {name: stats['training_time'] 
                            for name, stats in all_results['training_stats'].items()}
            pd.Series(training_times).plot(kind='bar', ax=ax8, color=self.colors['warning'])
            ax8.set_title('Training Time (seconds)')
            ax8.tick_params(axis='x', rotation=45)
        
        # 9. Summary Statistics
        ax9 = fig.add_subplot(gs[3, :])
        summary_text = "SUSTAINABLE AI DIABETES PREDICTION - SUMMARY\n\n"
        
        if 'model_comparison' in all_results:
            best_model = all_results['model_comparison'].index[0]
            best_f1 = all_results['model_comparison'].iloc[0]['F1-Score']
            summary_text += f"Best Model: {best_model} (F1-Score: {best_f1:.3f})\n"
        
        if 'sustainability_metrics' in all_results:
            most_sustainable = all_results['sustainability_metrics']['sustainability_score'].idxmax()
            sust_score = all_results['sustainability_metrics']['sustainability_score'].max()
            summary_text += f"Most Sustainable: {most_sustainable} (Score: {sust_score:.1f})\n"
        
        if 'feature_importance' in all_results:
            importance_df = all_results['feature_importance']
            df = self._normalize_importance_df(importance_df)
            top_feature = df.iloc[0]['Feature']
            summary_text += f"Top Risk Factor: {top_feature}\n"
        
        ax9.text(0.1, 0.8, summary_text, transform=ax9.transAxes, fontsize=14, 
                verticalalignment='top', fontfamily='monospace')
        ax9.axis('off')
        
        plt.suptitle('Sustainable AI Diabetes Prediction - Comprehensive Report', 
                    fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def save_all_plots(self, all_results, output_dir='results/plots'):
        """Save all visualization plots to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual plots
        if 'dataset_info' in all_results:
            self.plot_dataset_overview(all_results.get('raw_data'), 
                                     f'{output_dir}/dataset_overview.png')
        
        if 'feature_importance' in all_results:
            self.plot_feature_importance(all_results['feature_importance'], 
                                       f'{output_dir}/feature_importance.png')
        
        if 'model_comparison' in all_results:
            self.plot_model_comparison(all_results['model_comparison'], 
                                     f'{output_dir}/model_comparison.png')
        
        if 'sustainability_metrics' in all_results:
            self.plot_sustainability_analysis(all_results['sustainability_metrics'], 
                                           f'{output_dir}/sustainability_analysis.png')
        
        if 'risk_distribution' in all_results:
            self.plot_risk_analysis(all_results, f'{output_dir}/risk_analysis.png')
        
        # Save comprehensive report
        self.create_comprehensive_report(all_results, f'{output_dir}/comprehensive_report.png')
        
        print(f"All plots saved to {output_dir}/")
