"""
Data Preprocessing Module for Sustainable AI Diabetes Prediction
Handles missing values, normalization, and data cleaning
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.target_column = 'Outcome'
        
    def load_data(self, file_path):
        """Load diabetes dataset"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        else:
            raise ValueError("Only CSV files are supported")
    
    def handle_missing_values(self, df):
        """Handle missing and invalid values (0s in medical features)"""
        # Features where 0 is invalid and should be replaced
        invalid_zero_features = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
        
        for feature in invalid_zero_features:
            if feature in df.columns:
                # Replace 0 with median of non-zero values
                median_value = df[df[feature] != 0][feature].median()
                df[feature] = df[feature].replace(0, median_value)
        
        return df
    
    def remove_duplicates(self, df):
        """Remove duplicate rows"""
        return df.drop_duplicates()
    
    def normalize_features(self, X_train, X_test=None):
        """Normalize numerical features using StandardScaler"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def split_data(self, df, test_size=0.2, random_state=42):
        """Split data into train and test sets"""
        X = df.drop(columns=[self.target_column])
        y = df[self.target_column]
        
        self.feature_columns = X.columns.tolist()
        
        return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)
    
    def preprocess_pipeline(self, file_path):
        """Complete preprocessing pipeline"""
        # Load data
        df = self.load_data(file_path)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Remove duplicates
        df = self.remove_duplicates(df)
        
        # Split data
        X_train, X_test, y_train, y_test = self.split_data(df)
        
        # Normalize features
        X_train_scaled, X_test_scaled = self.normalize_features(X_train, X_test)
        
        # Convert back to DataFrame for easier handling
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=self.feature_columns)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=self.feature_columns)
        
        return X_train_scaled, X_test_scaled, y_train, y_test, df
    
    def get_data_info(self, df):
        """Get basic information about the dataset"""
        info = {
            'shape': df.shape,
            'missing_values': df.isnull().sum().sum(),
            'duplicates': df.duplicated().sum(),
            'class_distribution': df[self.target_column].value_counts().to_dict(),
            'features': df.columns.tolist()
        }
        return info
