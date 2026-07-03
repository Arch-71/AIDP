"""
Main Pipeline for Sustainable AI Diabetes Prediction
Complete workflow from data loading to model evaluation and recommendations
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import all modules
from src.utils.data_preprocessing import DataPreprocessor
from src.utils.feature_selection import FeatureSelector
from src.utils.class_balancer import ClassBalancer
from src.models.ml_models import MLModelTrainer
from src.models.model_evaluation import ModelEvaluator
from src.models.sustainability_analysis import SustainabilityAnalyzer
from src.utils.explainable_ai import ExplainableAI
from src.utils.risk_classifier import RiskClassifier
from src.utils.recommendation_system import HealthRecommendationSystem
from src.visualization.visualizer import DiabetesVisualizer

import os
import joblib
import json

class SustainableAIDiabetesPipeline:
    def __init__(self, data_path="Pima/diabetes.csv"):
        """Initialize the complete pipeline"""
        self.data_path = data_path
        self.results = {}
        
        # Initialize all components
        self.preprocessor = DataPreprocessor()
        self.feature_selector = FeatureSelector()
        self.class_balancer = ClassBalancer()
        self.model_trainer = MLModelTrainer()
        self.model_evaluator = ModelEvaluator()
        self.sustainability_analyzer = SustainabilityAnalyzer()
        self.explainable_ai = ExplainableAI()
        self.risk_classifier = RiskClassifier()
        self.recommendation_system = HealthRecommendationSystem()
        self.visualizer = DiabetesVisualizer()
        
        print(" Sustainable AI Diabetes Prediction Pipeline Initialized")
    
    def run_complete_pipeline(self):
        """Run the complete pipeline from data to final results"""
        print("\n" + "="*80)
        print(" STARTING SUSTAINABLE AI DIABETES PREDICTION PIPELINE")
        print("="*80)
        
        # Step 1: Data Preprocessing
        print("\n Step 1: Data Preprocessing")
        X_train, X_test, y_train, y_test, df = self.preprocessor.preprocess_pipeline(self.data_path)
        self.results['raw_data'] = df
        self.results['dataset_info'] = self.preprocessor.get_data_info(df)
        
        print(f" Data loaded: {df.shape}")
        print(f" Class distribution: {dict(df['Outcome'].value_counts())}")
        
        # Step 2: Feature Selection
        print("\n Step 2: Sustainable Feature Selection")
        selected_features = self.feature_selector.select_sustainable_features(X_train, y_train)
        X_train_selected = X_train[selected_features]
        X_test_selected = X_test[selected_features]
        
        print(f" Selected {len(selected_features)} features: {selected_features}")
        self.results['selected_features'] = selected_features
        
        # Step 3: Class Imbalance Handling
        print("\n Step 3: Class Imbalance Handling")
        balance_info = self.class_balancer.check_class_balance(y_train)
        print(f" Original distribution: {balance_info['distribution']}")
        print(f" Imbalance ratio: {balance_info['imbalance_ratio']:.2f}")
        
        X_train_balanced, y_train_balanced = self.class_balancer.auto_balance(X_train_selected, y_train)
        balancing_summary = self.class_balancer.get_balancing_summary()
        
        print(f" Technique used: {balancing_summary['technique_used']}")
        print(f" Final distribution: {balancing_summary['balanced_distribution']}")
        
        self.results['balancing_summary'] = balancing_summary
        
        # Step 4: Model Training
        print("\n Step 4: ML Model Training")
        training_results = self.model_trainer.train_all_models(X_train_balanced, y_train_balanced)
        
        print(f" Trained {len([r for r in training_results.values() if r['status'] == 'success'])} models successfully")
        self.results['training_results'] = training_results
        self.results['training_stats'] = self.model_trainer.training_stats
        
        # Step 5: Model Evaluation
        print("\n Step 5: Model Evaluation")
        evaluation_results = self.model_evaluator.evaluate_all_models(training_results, X_test_selected, y_test)
        
        print(f" Evaluated {len([r for r in evaluation_results.values() if r['status'] == 'success'])} models")
        self.results['evaluation_results'] = evaluation_results
        
        # Get model comparison
        comparison_df = self.model_evaluator.compare_models()
        print(f" Best model: {comparison_df.index[0]} (F1-Score: {comparison_df.iloc[0]['F1-Score']:.3f})")
        self.results['model_comparison'] = comparison_df
        
        # Step 6: Sustainability Analysis
        print("\n Step 6: Sustainability Analysis")
        sustainability_df = self.sustainability_analyzer.compare_sustainability(training_results)
        sustainability_recommendations = self.sustainability_analyzer.generate_sustainability_recommendations(sustainability_df)
        
        print(f" Most sustainable: {sustainability_recommendations['most_sustainable']}")
        print(f" Sustainability score: {sustainability_recommendations['sustainability_score']:.1f}/100")
        
        self.results['sustainability_metrics'] = sustainability_df
        self.results['sustainability_recommendations'] = sustainability_recommendations
        
        # Step 7: Explainable AI
        print("\n🔍 Step 7: Explainable AI Analysis")
        best_model_name = comparison_df.index[0]
        best_model = training_results[best_model_name]['model']
        
        # Initialize SHAP explainer
        self.explainable_ai.initialize_explainer(best_model, X_train_balanced, selected_features)
        shap_values = self.explainable_ai.calculate_shap_values(X_test_selected)
        
        # Generate explanation report
        explanation_report = self.explainable_ai.generate_explanation_report(X_test_selected, y_test)
        
        print(f" SHAP analysis completed for {best_model_name}")
        print(f" Top features: {explanation_report['summary']['top_features']}")
        
        self.results['shap_analysis'] = explanation_report
        # Normalize feature importance to standard column names
        fi = self.explainable_ai.get_feature_importance()
        try:
            fi_df = pd.DataFrame(fi)
            if 'feature' in fi_df.columns and 'importance' in fi_df.columns:
                fi_df = fi_df.rename(columns={'feature': 'Feature', 'importance': 'Importance'})
        except Exception:
            fi_df = fi
        self.results['feature_importance'] = fi_df
        
        # Step 8: Risk Classification & Recommendations
        print("\n Step 8: Risk Classification & Health Recommendations")
        
        # Test with a sample patient
        sample_patient = X_test_selected.iloc[0].to_dict()
        sample_probability = best_model.predict_proba([X_test_selected.iloc[0]])[0][1]
        
        # Risk classification
        risk_assessment = self.risk_classifier.classify_risk(sample_probability)
        risk_profile = self.risk_classifier.create_risk_profile(sample_patient, sample_probability)
        
        # Health recommendations
        recommendations = self.recommendation_system.generate_personalized_recommendations(
            sample_patient, risk_assessment, explanation_report
        )
        
        print(f" Sample risk level: {risk_assessment['risk_level']}")
        print(f" Risk score: {risk_assessment['risk_score']}/100")
        print(f" Generated {len(recommendations['categories'])} recommendation categories")
        
        self.results['sample_risk_assessment'] = risk_assessment
        self.results['sample_recommendations'] = recommendations
        
        # Step 9: Save Best Model
        print("\n Step 9: Save Best Model")
        os.makedirs("data/models", exist_ok=True)
        self.model_trainer.save_model(best_model_name, "data/models/best_model.pkl")
        
        # Save results
        self.save_results()
        print(" Best model and results saved")
        
        # Step 10: Generate Visualizations
        print("\n Step 10: Generate Visualizations")
        self.visualizer.save_all_plots(self.results)
        print(" All visualizations saved to results/plots/")
        
        # Final Summary
        self.print_final_summary()
        
        return self.results
    
    def save_results(self):
        """Save all results to files"""
        os.makedirs("results", exist_ok=True)
        
        # Save numerical results
        numerical_results = {}
        for key, value in self.results.items():
            if isinstance(value, pd.DataFrame):
                numerical_results[key] = value.to_dict()
            elif hasattr(value, 'to_dict'):
                numerical_results[key] = value.to_dict()
            elif isinstance(value, (dict, list, str, int, float)):
                numerical_results[key] = value
        
        with open("results/pipeline_results.json", "w") as f:
            json.dump(numerical_results, f, indent=2, default=str)
        
        print(" Results saved to results/pipeline_results.json")
    
    def print_final_summary(self):
        """Print final summary of the pipeline"""
        print("\n" + "="*80)
        print(" SUSTAINABLE AI DIABETES PREDICTION PIPELINE COMPLETED")
        print("="*80)
        
        # Model Performance Summary
        if 'model_comparison' in self.results:
            comparison = self.results['model_comparison']
            best_model = comparison.index[0]
            print(f"\n BEST MODEL: {best_model}")
            print(f"    F1-Score: {comparison.iloc[0]['F1-Score']:.3f}")
            print(f"    Accuracy: {comparison.iloc[0]['Accuracy']:.3f}")
            print(f"    ROC-AUC: {comparison.iloc[0]['ROC-AUC']:.3f}")
        
        # Sustainability Summary
        if 'sustainability_recommendations' in self.results:
            sust_rec = self.results['sustainability_recommendations']
            print(f"\n SUSTAINABILITY:")
            print(f"     Most Sustainable: {sust_rec['most_sustainable']}")
            print(f"     Sustainability Score: {sust_rec['sustainability_score']:.1f}/100")
            print(f"    Total Carbon Footprint: {sust_rec.get('total_carbon_footprint', 0):.2f}g CO2")
        
        # Feature Importance
        if 'feature_importance' in self.results:
            importance = self.results['feature_importance']
            top_features = importance.head(3)['Feature'].tolist()
            print(f"\n TOP RISK FACTORS:")
            for i, feature in enumerate(top_features, 1):
                print(f"   {i}. {feature}")
        
        # Sample Risk Assessment
        if 'sample_risk_assessment' in self.results:
            risk = self.results['sample_risk_assessment']
            print(f"\nSAMPLE RISK ASSESSMENT:")
            print(f"    Risk Level: {risk['risk_level'].replace('_', ' ').title()}")
            print(f"    Risk Score: {risk['risk_score']}/100")
            print(f"    Probability: {risk['probability']:.1%}")
            print(f"    Urgency: {risk['urgency']}")
        
        print("\n OUTPUT FILES GENERATED:")
        print("    data/models/best_model.pkl - Trained model")
        print("    results/pipeline_results.json - Complete results")
        print("    results/plots/ - All visualizations")
        
        print("\n NEXT STEPS:")
        print("   1. Run 'streamlit run streamlit_app.py' for web interface")
        print("   2. Check results/plots/ for detailed visualizations")
        print("   3. Review results/pipeline_results.json for detailed metrics")
        
        print("\n" + "="*80)
        print(" PIPELINE SUCCESSFULLY COMPLETED")
        print("="*80)

def main():
    """Main function to run the pipeline"""
    # Check if data file exists
    data_path = "Pima/diabetes.csv"
    if not os.path.exists(data_path):
        # Fallback to common alternative locations (project root or data/)
        alt_paths = ["diabetes.csv", os.path.join("data", "diabetes.csv")]
        found = None
        for p in alt_paths:
            if os.path.exists(p):
                found = p
                break
        if found:
            print(f"ℹ️ Using data file: {found}")
            data_path = found
        else:
            print(f"❌ Data file not found: {data_path}")
            print("Please ensure the diabetes.csv file is in the Pima/ directory or project root")
            return
    
    # Create and run pipeline
    pipeline = SustainableAIDiabetesPipeline(data_path)
    results = pipeline.run_complete_pipeline()
    
    return results

if __name__ == "__main__":
    results = main()
