"""
Sustainability Analysis Module for Sustainable AI Diabetes Prediction
Analyzes model efficiency and sustainability metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class SustainabilityAnalyzer:
    def __init__(self):
        self.sustainability_metrics = {}
        self.efficiency_scores = {}
        self.recommendations = {}
    
    def analyze_model_sustainability(self, training_stats: Dict, evaluation_metrics: Dict) -> Dict:
        """Analyze sustainability of a single model"""
        
        # Resource efficiency metrics
        time_efficiency = self._calculate_time_efficiency(training_stats['training_time'])
        memory_efficiency = self._calculate_memory_efficiency(training_stats['memory_used'])
        size_efficiency = self._calculate_size_efficiency(training_stats['model_size'])
        
        # Performance efficiency
        accuracy = evaluation_metrics.get('accuracy', 0)
        f1_score = evaluation_metrics.get('f1_score', 0)
        
        # Calculate overall sustainability score
        sustainability_score = self._calculate_overall_sustainability(
            time_efficiency, memory_efficiency, size_efficiency, accuracy, f1_score
        )
        
        sustainability_info = {
            'time_efficiency': time_efficiency,
            'memory_efficiency': memory_efficiency,
            'size_efficiency': size_efficiency,
            'performance_score': (accuracy + f1_score) / 2,
            'sustainability_score': sustainability_score,
            'training_time_seconds': training_stats['training_time'],
            'memory_usage_mb': training_stats['memory_used'],
            'model_size_mb': training_stats['model_size'],
            'carbon_footprint_estimate': self._estimate_carbon_footprint(training_stats['training_time'])
        }
        
        return sustainability_info
    
    def _calculate_time_efficiency(self, training_time: float) -> float:
        """Calculate time efficiency score (0-100)"""
        # Lower training time = higher efficiency
        # Normalize: 0-10 seconds = 100, 10-60 seconds = 60-100, >60 seconds = <60
        if training_time <= 10:
            return 100
        elif training_time <= 60:
            return 100 - (training_time - 10) * 40 / 50
        else:
            return max(20, 60 - (training_time - 60) * 40 / 120)
    
    def _calculate_memory_efficiency(self, memory_usage: float) -> float:
        """Calculate memory efficiency score (0-100)"""
        # Lower memory usage = higher efficiency
        # Normalize: <50MB = 100, 50-200MB = 80-100, 200-500MB = 60-80, >500MB = <60
        if memory_usage <= 50:
            return 100
        elif memory_usage <= 200:
            return 100 - (memory_usage - 50) * 20 / 150
        elif memory_usage <= 500:
            return 80 - (memory_usage - 200) * 20 / 300
        else:
            return max(20, 60 - (memory_usage - 500) * 40 / 500)
    
    def _calculate_size_efficiency(self, model_size: float) -> float:
        """Calculate model size efficiency score (0-100)"""
        # Smaller model size = higher efficiency
        # Normalize: <1MB = 100, 1-10MB = 80-100, 10-50MB = 60-80, >50MB = <60
        if model_size <= 1:
            return 100
        elif model_size <= 10:
            return 100 - (model_size - 1) * 20 / 9
        elif model_size <= 50:
            return 80 - (model_size - 10) * 20 / 40
        else:
            return max(20, 60 - (model_size - 50) * 40 / 50)
    
    def _calculate_overall_sustainability(self, time_eff: float, memory_eff: float, 
                                        size_eff: float, accuracy: float, f1_score: float) -> float:
        """Calculate overall sustainability score"""
        # Weight different components
        # Performance: 40%, Resource efficiency: 60% (20% each for time, memory, size)
        performance_weight = 0.4
        resource_weight = 0.6
        
        performance_score = (accuracy + f1_score) / 2 * 100  # Convert to 0-100 scale
        resource_score = (time_eff + memory_eff + size_eff) / 3
        
        overall_score = performance_score * performance_weight + resource_score * resource_weight
        return round(overall_score, 2)
    
    def _estimate_carbon_footprint(self, training_time: float) -> float:
        """Estimate carbon footprint in grams of CO2"""
        # Rough estimation: 0.5g CO2 per second of training on average hardware
        # This is a simplified calculation
        co2_per_second = 0.5
        return training_time * co2_per_second
    
    def compare_sustainability(self, models_data: Dict) -> pd.DataFrame:
        """Compare sustainability across all models"""
        sustainability_data = []
        
        for model_name, model_info in models_data.items():
            if model_info['status'] == 'success' and 'training_stats' in model_info:
                training_stats = model_info['training_stats']
                evaluation_metrics = model_info.get('evaluation_metrics', {})
                
                sustainability_info = self.analyze_model_sustainability(training_stats, evaluation_metrics)
                sustainability_info['model_name'] = model_name
                sustainability_data.append(sustainability_info)
        
        if not sustainability_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(sustainability_data)
        df = df.set_index('model_name')
        df = df.sort_values('sustainability_score', ascending=False)
        
        self.sustainability_metrics = df.to_dict('index')
        
        return df
    
    def generate_sustainability_recommendations(self, sustainability_df: pd.DataFrame) -> Dict:
        """Generate sustainability recommendations"""
        recommendations = {}
        
        if sustainability_df.empty:
            return recommendations
        
        # Find most sustainable model
        best_model = sustainability_df.index[0]
        best_score = sustainability_df.loc[best_model, 'sustainability_score']
        
        # Analyze trade-offs
        best_performance = sustainability_df['performance_score'].max()
        best_sustainability = sustainability_df['sustainability_score'].max()
        
        recommendations['most_sustainable'] = best_model
        recommendations['sustainability_score'] = best_score
        
        # Performance vs Sustainability trade-off analysis
        performance_leaders = sustainability_df[sustainability_df['performance_score'] >= best_performance * 0.95]
        sustainability_leaders = sustainability_df[sustainability_df['sustainability_score'] >= best_sustainability * 0.95]
        
        recommendations['performance_leaders'] = performance_leaders.index.tolist()
        recommendations['sustainability_leaders'] = sustainability_leaders.index.tolist()
        
        # Specific recommendations based on metrics
        recs = []
        
        # Time efficiency recommendations
        slow_models = sustainability_df[sustainability_df['time_efficiency'] < 50].index.tolist()
        if slow_models:
            recs.append(f"Consider optimizing {', '.join(slow_models)} for faster training")
        
        # Memory efficiency recommendations
        memory_heavy = sustainability_df[sustainability_df['memory_efficiency'] < 50].index.tolist()
        if memory_heavy:
            recs.append(f"Consider reducing memory usage for {', '.join(memory_heavy)}")
        
        # Size efficiency recommendations
        large_models = sustainability_df[sustainability_df['size_efficiency'] < 50].index.tolist()
        if large_models:
            recs.append(f"Consider model compression for {', '.join(large_models)}")
        
        recommendations['specific_recommendations'] = recs
        
        # Overall recommendation
        if best_score >= 80:
            recommendations['overall'] = f"Excellent sustainability achieved with {best_model}"
        elif best_score >= 60:
            recommendations['overall'] = f"Good sustainability with {best_model}, but room for improvement"
        else:
            recommendations['overall'] = f"Sustainability concerns with {best_model}, consider optimization"
        
        self.recommendations = recommendations
        return recommendations
    
    def plot_sustainability_comparison(self, sustainability_df: pd.DataFrame, save_path=None):
        """Plot sustainability comparison"""
        if sustainability_df.empty:
            print("No sustainability data to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Overall sustainability score
        sustainability_df['sustainability_score'].sort_values().plot(
            kind='barh', ax=axes[0, 0], color='green'
        )
        axes[0, 0].set_title('Overall Sustainability Score')
        axes[0, 0].set_xlabel('Score')
        
        # Resource efficiency components
        resource_metrics = ['time_efficiency', 'memory_efficiency', 'size_efficiency']
        sustainability_df[resource_metrics].plot(
            kind='bar', ax=axes[0, 1], figsize=(10, 6)
        )
        axes[0, 1].set_title('Resource Efficiency Components')
        axes[0, 1].set_ylabel('Efficiency Score')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Performance vs Sustainability
        axes[1, 0].scatter(
            sustainability_df['performance_score'],
            sustainability_df['sustainability_score'],
            s=100, alpha=0.7
        )
        
        for i, model in enumerate(sustainability_df.index):
            axes[1, 0].annotate(
                model, 
                (sustainability_df.iloc[i]['performance_score'], 
                 sustainability_df.iloc[i]['sustainability_score']),
                xytext=(5, 5), textcoords='offset points', fontsize=8
            )
        
        axes[1, 0].set_xlabel('Performance Score')
        axes[1, 0].set_ylabel('Sustainability Score')
        axes[1, 0].set_title('Performance vs Sustainability')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Carbon footprint
        sustainability_df['carbon_footprint_estimate'].sort_values().plot(
            kind='barh', ax=axes[1, 1], color='red'
        )
        axes[1, 1].set_title('Estimated Carbon Footprint (g CO2)')
        axes[1, 1].set_xlabel('CO2 (grams)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def get_sustainability_status(self, score: float) -> str:
        """Categorize sustainability based on score"""
        if score >= 80:
            return "Highly Sustainable"
        elif score >= 60:
            return "Moderately Sustainable"
        else:
            return "Low Sustainability"

    def generate_detailed_report(self, model_name: str, metrics: Dict, baseline_metrics: Dict = None) -> str:
        """Generate a formatted sustainability report for a model"""
        score = metrics.get('sustainability_score', 0)
        status = self.get_sustainability_status(score)
        
        report = []
        report.append(f"### Sustainability Analysis: {model_name} Model")
        report.append(f"\n1. Computational Efficiency")
        report.append(f"   - Training Time: {metrics.get('training_time_seconds', 0):.4f} seconds")
        report.append(f"   - Memory Usage: {metrics.get('memory_usage_mb', 0):.2f} MB")
        
        report.append(f"\n2. Predictive Performance")
        report.append(f"   - Accuracy: {metrics.get('performance_score', 0):.3f}") # Simplified for display
        
        report.append(f"\n3. Trade-off Evaluation")
        report.append(f"   - Sustainability Score: {score}/100")
        report.append(f"   - Rating: **{status}**")
        
        if baseline_metrics and model_name != "Logistic_Regression":
            report.append(f"\n4. Comparison with Baseline (Logistic Regression)")
            report.append(f"   - Performance Diff: {metrics.get('performance_score', 0) - baseline_metrics.get('performance_score', 0):+.3f}")
            report.append(f"   - Memory Diff: {metrics.get('memory_usage_mb', 0) - baseline_metrics.get('memory_usage_mb', 0):+.2f} MB")

        return "\n".join(report)

    def get_sustainability_report(self) -> Dict:
        """Get comprehensive sustainability report"""
        if not self.sustainability_metrics:
            return {"error": "No sustainability analysis performed"}
        
        report = {
            'sustainability_metrics': self.sustainability_metrics,
            'recommendations': self.recommendations,
            'summary': {
                'total_models_analyzed': len(self.sustainability_metrics),
                'average_sustainability_score': np.mean([m['sustainability_score'] for m in self.sustainability_metrics.values()]),
                'best_sustainable_model': max(self.sustainability_metrics.keys(), 
                                            key=lambda k: self.sustainability_metrics[k]['sustainability_score']),
                'total_carbon_footprint': sum([m['carbon_footprint_estimate'] for m in self.sustainability_metrics.values()])
            }
        }
        
        return report
