"""
Machine Learning Models Module for Sustainable AI Diabetes Prediction
Trains and manages multiple ML models with sustainability metrics
"""

import pandas as pd
import numpy as np
import time
import psutil
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
import lightgbm as lgb
import pickle
import json
try:
    from memory_profiler import profile
except ImportError:
    profile = None

class MLModelTrainer:
    def __init__(self):
        self.models = {}
        self.training_stats = {}
        self.best_model = None
        self.best_model_name = None
        
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    def train_logistic_regression(self, X_train, y_train, random_state=42):
        """Train Logistic Regression model"""
        print("Training Logistic Regression...")
        
        # Start timing and memory tracking
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        # Train model
        model = LogisticRegression(random_state=random_state, max_iter=1000)
        model.fit(X_train, y_train)
        
        # Calculate training stats
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        training_stats = {
            'training_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'model_size': len(pickle.dumps(model)) / 1024 / 1024,  # MB
            'parameters': model.get_params()
        }
        
        self.models['Logistic_Regression'] = model
        self.training_stats['Logistic_Regression'] = training_stats
        
        return model, training_stats
    
    def train_random_forest(self, X_train, y_train, n_estimators=100, random_state=42):
        """Train Random Forest model"""
        print("Training Random Forest...")
        
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        model = RandomForestClassifier(
            n_estimators=n_estimators, 
            random_state=random_state,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        training_stats = {
            'training_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'model_size': len(pickle.dumps(model)) / 1024 / 1024,
            'parameters': model.get_params(),
            'n_features': model.n_features_in_,
            'n_trees': n_estimators
        }
        
        self.models['Random_Forest'] = model
        self.training_stats['Random_Forest'] = training_stats
        
        return model, training_stats
    
    def train_xgboost(self, X_train, y_train, random_state=42):
        """Train XGBoost model"""
        print("Training XGBoost...")
        
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        model = XGBClassifier(
            random_state=random_state,
            use_label_encoder=False,
            eval_metric='logloss',
            n_estimators=100
        )
        model.fit(X_train, y_train)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        training_stats = {
            'training_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'model_size': len(pickle.dumps(model)) / 1024 / 1024,
            'parameters': model.get_params()
        }
        
        self.models['XGBoost'] = model
        self.training_stats['XGBoost'] = training_stats
        
        return model, training_stats
    
    def train_svm(self, X_train, y_train, random_state=42):
        """Train Support Vector Machine model"""
        print("Training SVM...")
        
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        model = SVC(random_state=random_state, probability=True)
        model.fit(X_train, y_train)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        training_stats = {
            'training_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'model_size': len(pickle.dumps(model)) / 1024 / 1024,
            'parameters': model.get_params()
        }
        
        self.models['SVM'] = model
        self.training_stats['SVM'] = training_stats
        
        return model, training_stats
    
    def train_lightgbm(self, X_train, y_train, random_state=42):
        """Train LightGBM model"""
        print("Training LightGBM...")
        
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        model = lgb.LGBMClassifier(random_state=random_state, verbose=-1, n_jobs=1)
        model.fit(X_train, y_train)
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        training_stats = {
            'training_time': end_time - start_time,
            'memory_used': end_memory - start_memory,
            'model_size': len(pickle.dumps(model)) / 1024 / 1024,
            'parameters': model.get_params()
        }
        
        self.models['LightGBM'] = model
        self.training_stats['LightGBM'] = training_stats
        
        return model, training_stats
    
    def train_all_models(self, X_train, y_train):
        """Train all models and return results"""
        results = {}
        
        # Train each model
        models_to_train = [
            ('Logistic_Regression', self.train_logistic_regression),
            ('Random_Forest', self.train_random_forest),
            ('XGBoost', self.train_xgboost),
            ('SVM', self.train_svm),
            ('LightGBM', self.train_lightgbm)
        ]
        
        for model_name, train_func in models_to_train:
            try:
                model, stats = train_func(X_train, y_train)
                results[model_name] = {
                    'model': model,
                    'training_stats': stats,
                    'status': 'success'
                }
                print(f"✓ {model_name} trained successfully")
            except Exception as e:
                print(f"✗ {model_name} training failed: {str(e)}")
                results[model_name] = {
                    'model': None,
                    'training_stats': None,
                    'status': 'failed',
                    'error': str(e)
                }
        
        return results
    
    def predict_proba(self, model_name, X):
        """Get prediction probabilities for a model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        return model.predict_proba(X)
    
    def predict(self, model_name, X):
        """Get predictions for a model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        return model.predict(X)
    
    def save_model(self, model_name, file_path):
        """Save a trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        with open(file_path, 'wb') as f:
            pickle.dump(self.models[model_name], f)
    
    def load_model(self, model_name, file_path):
        """Load a trained model"""
        with open(file_path, 'rb') as f:
            self.models[model_name] = pickle.load(f)
    
    def get_sustainability_report(self):
        """Get sustainability metrics for all trained models"""
        if not self.training_stats:
            return None
        
        sustainability_report = {}
        
        for model_name, stats in self.training_stats.items():
            sustainability_report[model_name] = {
                'training_time_seconds': stats['training_time'],
                'memory_usage_mb': stats['memory_used'],
                'model_size_mb': stats['model_size'],
                'sustainability_score': self._calculate_sustainability_score(stats)
            }
        
        return sustainability_report
    
    def _calculate_sustainability_score(self, stats):
        """Calculate sustainability score (higher is more sustainable)"""
        # Normalize metrics (lower is better for all)
        time_score = 1 / (1 + stats['training_time'])
        memory_score = 1 / (1 + stats['memory_used'])
        size_score = 1 / (1 + stats['model_size'])
        
        # Weighted average (equal weights for simplicity)
        sustainability_score = (time_score + memory_score + size_score) / 3
        
        return sustainability_score * 100  # Scale to 0-100
    
    def get_model_summary(self):
        """Get summary of all trained models"""
        summary = {
            'total_models': len(self.models),
            'trained_models': list(self.models.keys()),
            'training_stats': self.training_stats,
            'sustainability_report': self.get_sustainability_report()
        }
        
        return summary
