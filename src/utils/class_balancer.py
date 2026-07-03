"""
Class Balancing Module for Sustainable AI Diabetes Prediction
Handles class imbalance using SMOTE and other techniques
"""

import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTETomek
import matplotlib.pyplot as plt
import seaborn as sns

class ClassBalancer:
    def __init__(self):
        self.original_distribution = None
        self.balanced_distribution = None
        self.technique_used = None
    
    def check_class_balance(self, y):
        """Check class distribution in the dataset"""
        self.original_distribution = pd.Series(y).value_counts().to_dict()
        
        total_samples = len(y)
        balance_info = {
            'distribution': self.original_distribution,
            'total_samples': total_samples,
            'minority_class': min(self.original_distribution, key=self.original_distribution.get),
            'majority_class': max(self.original_distribution, key=self.original_distribution.get),
            'imbalance_ratio': max(self.original_distribution.values()) / min(self.original_distribution.values())
        }
        
        return balance_info
    
    def apply_smote(self, X, y, random_state=42):
        """Apply SMOTE to balance classes"""
        smote = SMOTE(random_state=random_state)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        
        self.technique_used = 'SMOTE'
        self.balanced_distribution = pd.Series(y_resampled).value_counts().to_dict()
        
        return X_resampled, y_resampled
    
    def apply_smote_tomek(self, X, y, random_state=42):
        """Apply SMOTE + Tomek links for better balance"""
        smote_tomek = SMOTETomek(random_state=random_state)
        X_resampled, y_resampled = smote_tomek.fit_resample(X, y)
        
        self.technique_used = 'SMOTE_Tomek'
        self.balanced_distribution = pd.Series(y_resampled).value_counts().to_dict()
        
        return X_resampled, y_resampled
    
    def apply_hybrid_sampling(self, X, y, random_state=42):
        """Apply hybrid sampling (SMOTE + undersampling)"""
        # First apply SMOTE to get some minority samples
        smote = SMOTE(sampling_strategy=0.5, random_state=random_state)
        X_smote, y_smote = smote.fit_resample(X, y)
        
        # Then undersample majority class
        undersampler = RandomUnderSampler(random_state=random_state)
        X_resampled, y_resampled = undersampler.fit_resample(X_smote, y_smote)
        
        self.technique_used = 'Hybrid_SMOTE_Undersampling'
        self.balanced_distribution = pd.Series(y_resampled).value_counts().to_dict()
        
        return X_resampled, y_resampled
    
    def auto_balance(self, X, y, technique='auto'):
        """Automatically choose and apply best balancing technique"""
        balance_info = self.check_class_balance(y)
        
        # Choose technique based on imbalance ratio
        if technique == 'auto':
            if balance_info['imbalance_ratio'] > 3:
                # High imbalance - use SMOTE + Tomek
                X_resampled, y_resampled = self.apply_smote_tomek(X, y)
            elif balance_info['imbalance_ratio'] > 1.5:
                # Moderate imbalance - use SMOTE
                X_resampled, y_resampled = self.apply_smote(X, y)
            else:
                # Low imbalance - no action needed
                X_resampled, y_resampled = X, y
                self.technique_used = 'None'
        elif technique == 'smote':
            X_resampled, y_resampled = self.apply_smote(X, y)
        elif technique == 'smote_tomek':
            X_resampled, y_resampled = self.apply_smote_tomek(X, y)
        elif technique == 'hybrid':
            X_resampled, y_resampled = self.apply_hybrid_sampling(X, y)
        else:
            raise ValueError(f"Unknown technique: {technique}")
        
        return X_resampled, y_resampled
    
    def plot_class_distribution(self, save_path=None):
        """Plot class distribution before and after balancing"""
        if self.original_distribution is None:
            raise ValueError("No class distribution data available")
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Original distribution
        axes[0].bar(self.original_distribution.keys(), self.original_distribution.values())
        axes[0].set_title('Original Class Distribution')
        axes[0].set_xlabel('Class')
        axes[0].set_ylabel('Count')
        axes[0].set_xticks(list(self.original_distribution.keys()))
        
        # Balanced distribution
        if self.balanced_distribution:
            axes[1].bar(self.balanced_distribution.keys(), self.balanced_distribution.values())
            axes[1].set_title(f'Balanced Distribution ({self.technique_used})')
            axes[1].set_xlabel('Class')
            axes[1].set_ylabel('Count')
            axes[1].set_xticks(list(self.balanced_distribution.keys()))
        else:
            axes[1].text(0.5, 0.5, 'No balancing applied', 
                        ha='center', va='center', transform=axes[1].transAxes)
            axes[1].set_title('No Balancing Applied')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def get_balancing_summary(self):
        """Get summary of balancing process"""
        summary = {
            'original_distribution': self.original_distribution,
            'balanced_distribution': self.balanced_distribution,
            'technique_used': self.technique_used,
            'original_samples': sum(self.original_distribution.values()) if self.original_distribution else 0,
            'balanced_samples': sum(self.balanced_distribution.values()) if self.balanced_distribution else 0
        }
        
        if self.original_distribution and self.balanced_distribution:
            summary['samples_added'] = summary['balanced_samples'] - summary['original_samples']
        
        return summary
