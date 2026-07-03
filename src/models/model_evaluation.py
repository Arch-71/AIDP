"""
Model Evaluation Module for Sustainable AI Diabetes Prediction
Evaluates models using multiple metrics and compares performance
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def __init__(self):
        self.evaluation_results = {}
        self.best_model = None
        self.best_model_name = None
        
    def evaluate_model(self, model_name, model, X_test, y_test):
        """Comprehensive evaluation of a single model"""
        print(f"Evaluating {model_name}...")
        
        # Get predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        # Add ROC-AUC if probabilities are available
        if y_pred_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
            metrics['roc_curve'] = {
                'fpr': roc_curve(y_test, y_pred_proba)[0].tolist(),
                'tpr': roc_curve(y_test, y_pred_proba)[1].tolist(),
                'thresholds': roc_curve(y_test, y_pred_proba)[2].tolist()
            }
            metrics['precision_recall_curve'] = {
                'precision': precision_recall_curve(y_test, y_pred_proba)[0].tolist(),
                'recall': precision_recall_curve(y_test, y_pred_proba)[1].tolist(),
                'thresholds': precision_recall_curve(y_test, y_pred_proba)[2].tolist()
            }
        else:
            metrics['roc_auc'] = None
            metrics['roc_curve'] = None
            metrics['precision_recall_curve'] = None
        
        self.evaluation_results[model_name] = metrics
        
        return metrics
    
    def evaluate_all_models(self, models, X_test, y_test):
        """Evaluate all trained models"""
        results = {}
        
        for model_name, model_info in models.items():
            if model_info['status'] == 'success' and model_info['model'] is not None:
                try:
                    metrics = self.evaluate_model(model_name, model_info['model'], X_test, y_test)
                    results[model_name] = {
                        'metrics': metrics,
                        'status': 'success'
                    }
                    print(f"✓ {model_name} evaluated successfully")
                except Exception as e:
                    print(f"✗ {model_name} evaluation failed: {str(e)}")
                    results[model_name] = {
                        'metrics': None,
                        'status': 'failed',
                        'error': str(e)
                    }
            else:
                results[model_name] = {
                    'metrics': None,
                    'status': 'skipped',
                    'reason': model_info.get('status', 'unknown')
                }
        
        return results
    
    def compare_models(self):
        """Compare all evaluated models and find the best one"""
        if not self.evaluation_results:
            return None
        
        comparison_df = pd.DataFrame()
        
        for model_name, metrics in self.evaluation_results.items():
            if metrics['accuracy'] is not None:
                comparison_df.loc[model_name, 'Accuracy'] = metrics['accuracy']
                comparison_df.loc[model_name, 'Precision'] = metrics['precision']
                comparison_df.loc[model_name, 'Recall'] = metrics['recall']
                comparison_df.loc[model_name, 'F1-Score'] = metrics['f1_score']
                comparison_df.loc[model_name, 'ROC-AUC'] = metrics['roc_auc'] if metrics['roc_auc'] else 0
        
        # Sort by F1-Score (primary metric for imbalanced datasets)
        comparison_df = comparison_df.sort_values('F1-Score', ascending=False)
        
        # Find best model
        self.best_model_name = comparison_df.index[0]
        self.best_model = self.evaluation_results[self.best_model_name]
        
        return comparison_df
    
    def plot_confusion_matrix(self, model_name, save_path=None):
        """Plot confusion matrix for a specific model"""
        if model_name not in self.evaluation_results:
            raise ValueError(f"Model {model_name} not evaluated")
        
        cm = np.array(self.evaluation_results[model_name]['confusion_matrix'])
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Non-Diabetic', 'Diabetic'],
                   yticklabels=['Non-Diabetic', 'Diabetic'])
        plt.title(f'Confusion Matrix - {model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_roc_curves(self, save_path=None):
        """Plot ROC curves for all models"""
        plt.figure(figsize=(10, 8))
        
        for model_name, metrics in self.evaluation_results.items():
            if metrics['roc_curve'] and metrics['roc_auc']:
                fpr = metrics['roc_curve']['fpr']
                tpr = metrics['roc_curve']['tpr']
                auc = metrics['roc_auc']
                
                plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.3f})')
        
        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves Comparison')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_model_comparison(self, save_path=None):
        """Plot model performance comparison"""
        comparison_df = self.compare_models()
        
        if comparison_df is None or comparison_df.empty:
            return
        
        # Melt the dataframe for plotting
        metrics_melted = comparison_df.reset_index().melt(
            id_vars='index', 
            var_name='Metric', 
            value_name='Score'
        )
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=metrics_melted, x='index', y='Score', hue='Metric')
        plt.title('Model Performance Comparison')
        plt.xlabel('Model')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.legend(title='Metric', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def get_evaluation_summary(self):
        """Get comprehensive evaluation summary"""
        if not self.evaluation_results:
            return None
        
        summary = {
            'total_models_evaluated': len(self.evaluation_results),
            'successful_evaluations': len([m for m in self.evaluation_results.values() if m['accuracy'] is not None]),
            'best_model': self.best_model_name,
            'best_model_metrics': self.best_model if self.best_model else None,
            'model_comparison': self.compare_models().to_dict() if self.compare_models() is not None else None,
            'detailed_results': self.evaluation_results
        }
        
        return summary
    
    def print_model_comparison(self):
        """Print formatted model comparison"""
        comparison_df = self.compare_models()
        
        if comparison_df is None:
            print("No models to compare")
            return
        
        print("\n" + "="*80)
        print("MODEL PERFORMANCE COMPARISON")
        print("="*80)
        print(comparison_df.to_string(float_format='%.3f'))
        print("="*80)
        print(f"Best Model: {self.best_model_name}")
        print("="*80)
