"""
Synthetic Dataset Generator v1.0
Generates 10,000 projects × 6 SDLCs = 60,000 training samples
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from risk_engine import generate_risk, FEATURE_LIST


class DatasetGenerator:
    """Generate realistic synthetic SDLC project data"""
    
    SDLC_MODELS = ['Waterfall', 'Agile', 'Spiral', 'V-Model', 'DevOps', 'Hybrid']
    
    def __init__(self, n_projects: int = 10000, random_seed: int = 42):
        """
        Initialize dataset generator.
        
        Args:
            n_projects: Number of unique projects to generate
            random_seed: Random seed for reproducibility
        """
        self.n_projects = n_projects
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def generate_feature_distributions(self) -> Dict[str, np.ndarray]:
        """
        Generate realistic feature distributions using Beta/Normal distributions.
        
        Returns:
            Dictionary mapping feature name to array of values [0,1]
        """
        n = self.n_projects
        features = {}
        
        # STRUCTURE & SCALE - Beta distributions for bounded [0,1]
        features['project_scale_index'] = np.random.beta(2, 2, n)  # Balanced
        features['budget_adequacy_ratio'] = np.random.beta(3, 2, n)  # Slightly higher
        features['schedule_pressure_index'] = np.random.beta(2, 3, n)  # Lower pressure
        features['team_capacity_index'] = np.random.beta(3, 2, n)  # Good capacity
        features['team_experience_score'] = np.random.beta(2.5, 2, n)  # Moderate exp
        features['domain_familiarity_score'] = np.random.beta(2.5, 2.5, n)  # Balanced
        
        # REQUIREMENTS & SCOPE - Higher volatility bias
        features['requirements_volatility'] = np.random.beta(2, 3, n)  # Lower volatility
        features['requirements_clarity_score'] = np.random.beta(2.5, 2, n)  # Decent clarity
        features['scope_complexity_index'] = np.random.beta(2, 2, n)  # Balanced
        features['stakeholder_alignment_score'] = np.random.beta(2, 2.5, n)  # Slightly lower
        features['change_request_intensity'] = np.random.beta(2, 3, n)  # Lower CR rate
        
        # PROCESS & GOVERNANCE - Moderate maturity
        features['process_maturity_score'] = np.random.beta(2.5, 2.5, n)  # Balanced
        features['sprint_discipline_score'] = np.random.beta(2, 2, n)  # Balanced
        features['decision_latency_index'] = np.random.beta(2, 3, n)  # Lower latency
        features['risk_management_maturity'] = np.random.beta(2, 2.5, n)  # Slightly lower
        features['client_engagement_score'] = np.random.beta(2.5, 2, n)  # Good engagement
        
        # TECHNICAL RISK - Balanced complexity
        features['technical_complexity_index'] = np.random.beta(2, 2, n)  # Balanced
        features['integration_risk_index'] = np.random.beta(2, 2.5, n)  # Slightly lower
        features['automation_maturity_score'] = np.random.beta(2, 2.5, n)  # Moderate auto
        features['toolchain_reliability_score'] = np.random.beta(3, 2, n)  # Good tools
        features['legacy_dependency_index'] = np.random.beta(2, 3, n)  # Lower legacy
        
        # ENVIRONMENT - Lower regulatory pressure
        features['regulatory_risk_index'] = np.random.beta(2, 4, n)  # Lower regulatory
        features['domain_criticality_index'] = np.random.beta(2, 2, n)  # Balanced
        features['external_dependency_risk'] = np.random.beta(2, 3, n)  # Lower external
        
        # DELIVERY PRESSURE - Moderate pressure
        features['time_to_market_pressure'] = np.random.beta(2, 2.5, n)  # Moderate
        features['resource_stability_index'] = np.random.beta(3, 2, n)  # Good stability
        features['risk_tolerance_index'] = np.random.beta(2, 2, n)  # Balanced
        features['overall_uncertainty_index'] = np.random.beta(2, 2.5, n)  # Moderate
        
        # Clip all to [0, 1] (Beta should already be bounded)
        for key in features:
            features[key] = np.clip(features[key], 0, 1)
        
        return features
    
    def generate_projects_dataset(self) -> pd.DataFrame:
        """
        Generate complete dataset with risk scores for all SDLCs.
        
        Returns:
            DataFrame with columns: [28 features, Waterfall_risk, Agile_risk, ..., optimal_sdlc]
        """
        print(f"[*] Generating {self.n_projects} projects...")
        
        # Generate feature distributions
        features_dict = self.generate_feature_distributions()
        
        # Convert to DataFrame
        df = pd.DataFrame(features_dict)
        
        print(f"[OK] Generated {len(df)} projects with {len(FEATURE_LIST)} features")
        print(f"[*] Calculating risk scores for 6 SDLCs...")
        
        # Calculate risk for each SDLC
        risk_columns = {}
        for sdlc in self.SDLC_MODELS:
            risks = []
            for idx, row in df.iterrows():
                project_features = row.to_dict()
                risk = generate_risk(project_features, sdlc)
                risks.append(risk)
            
            risk_columns[f'{sdlc}_risk'] = risks
            print(f"  [OK] {sdlc}: mean={np.mean(risks):.3f}, std={np.std(risks):.3f}")
        
        # Add risk columns to dataframe
        for col, values in risk_columns.items():
            df[col] = values
        
        # Determine optimal SDLC (lowest risk)
        risk_cols = [f'{sdlc}_risk' for sdlc in self.SDLC_MODELS]
        df['optimal_sdlc'] = df[risk_cols].idxmin(axis=1).str.replace('_risk', '')
        
        print(f"\n[DATA] SDLC Distribution:")
        print(df['optimal_sdlc'].value_counts(normalize=True).round(3))
        
        return df
    
    def generate_full_dataset(self) -> pd.DataFrame:
        """
        Generate full 60k dataset (10k projects × 6 SDLCs).
        
        Each project appears 6 times, once for each SDLC with its risk score.
        
        Returns:
            DataFrame with 60,000 rows: [28 features, sdlc_type, risk_score, optimal_sdlc]
        """
        print(f"\n[*] GENERATING FULL 60K DATASET")
        print("=" * 60)
        
        # Generate base projects
        projects_df = self.generate_projects_dataset()
        
        print(f"\n[*] Expanding to 60k samples (10k x 6 SDLCs)...")
        
        # Expand each project to 6 rows (one per SDLC)
        expanded_rows = []
        
        for idx, row in projects_df.iterrows():
            # Get features only (first 28 columns)
            project_features = row[FEATURE_LIST].to_dict()
            optimal_sdlc = row['optimal_sdlc']
            
            # Create one row per SDLC
            for sdlc in self.SDLC_MODELS:
                new_row = project_features.copy()
                new_row['sdlc_type'] = sdlc
                new_row['risk_score'] = row[f'{sdlc}_risk']
                new_row['optimal_sdlc'] = optimal_sdlc
                new_row['is_optimal'] = 1 if sdlc == optimal_sdlc else 0
                expanded_rows.append(new_row)
        
        # Create final dataframe
        final_df = pd.DataFrame(expanded_rows)
        
        print(f"\n[OK] DATASET COMPLETE!")
        print(f"   Total samples: {len(final_df)}")
        print(f"   Features: {len(FEATURE_LIST)}")
        print(f"   Target: optimal_sdlc")
        
        print(f"\n[DATA] Risk Score Statistics:")
        print(final_df.groupby('sdlc_type')['risk_score'].describe()[['mean', 'std', 'min', 'max']])
        
        print(f"\n[DATA] Optimal SDLC Distribution:")
        print(final_df['optimal_sdlc'].value_counts(normalize=True).round(3))
        
        return final_df
    
    def save_dataset(self, output_path: str = 'data/risk_dataset_v1.csv'):
        """Generate and save dataset to CSV"""
        df = self.generate_full_dataset()
        df.to_csv(output_path, index=False)
        print(f"\n[SAVE] Dataset saved to: {output_path}")
        print(f"   Size: {len(df)} rows x {len(df.columns)} columns")
        return df


def main():
    """Generate dataset"""
    import os
    os.makedirs('data', exist_ok=True)
    
    generator = DatasetGenerator(n_projects=10000, random_seed=42)
    df = generator.save_dataset('data/risk_dataset_v1.csv')
    
    print("\n[OK] DATASET GENERATION COMPLETE!")
    print(f"   Ready for XGBoost training")


if __name__ == '__main__':
    main()