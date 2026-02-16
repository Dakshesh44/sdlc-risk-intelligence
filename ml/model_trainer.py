"""
XGBoost Model Training Pipeline - BALANCED VERSION
Target: 78-84% accuracy (not 98%, not 52%)
"""

import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb
from typing import Tuple, Dict
import os


class SDLCModelTrainer:
    """Train and evaluate SDLC prediction models - balanced approach"""
    
    def __init__(self, random_seed: int = 42):
        """Initialize trainer"""
        self.random_seed = random_seed
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.baseline_model = None
        self.xgb_model = None
        self.feature_names = None
        self.label_names = None
        
    def load_data(self, data_path: str) -> pd.DataFrame:
        """Load dataset from CSV"""
        print(f"[LOAD] Loading data from {data_path}...")
        df = pd.read_csv(data_path)
        print(f"   Loaded {len(df)} samples")
        print(f"   Columns: {len(df.columns)}")
        return df
    
    def prepare_data(self, df: pd.DataFrame, test_size: float = 0.15, 
                    val_size: float = 0.15) -> Tuple:
        """Prepare train/val/test splits with stratification"""
        print(f"\n[*] Preparing data splits...")
        
        # Separate features and target
        feature_cols = [col for col in df.columns 
                       if col not in ['sdlc_type', 'risk_score', 'optimal_sdlc', 'is_optimal']]
        
        X = df[feature_cols].values
        y = df['optimal_sdlc'].values
        
        self.feature_names = feature_cols
        self.label_names = sorted(df['optimal_sdlc'].unique())
        
        print(f"   Features: {len(feature_cols)}")
        print(f"   Classes: {len(self.label_names)}")
        print(f"   Class distribution:\n{pd.Series(y).value_counts(normalize=True).round(3)}")
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # First split: train+val vs test (stratified)
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y_encoded,
            test_size=test_size,
            stratify=y_encoded,
            random_state=self.random_seed
        )
        
        # Second split: train vs val (stratified)
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_ratio,
            stratify=y_temp,
            random_state=self.random_seed
        )
        
        # Scale features
        print(f"\n[*] Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"   Train: {len(X_train)} ({len(X_train)/len(X)*100:.1f}%)")
        print(f"   Val:   {len(X_val)} ({len(X_val)/len(X)*100:.1f}%)")
        print(f"   Test:  {len(X_test)} ({len(X_test)/len(X)*100:.1f}%)")
        
        return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test
    
    def train_baseline(self, X_train, y_train, X_val, y_val) -> Dict:
        """Train logistic regression baseline"""
        print(f"\n[*] Training Logistic Regression baseline...")
        
        self.baseline_model = LogisticRegression(
            max_iter=1000,
            random_state=self.random_seed,
            multi_class='multinomial'
        )
        
        self.baseline_model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = accuracy_score(y_train, self.baseline_model.predict(X_train))
        val_acc = accuracy_score(y_val, self.baseline_model.predict(X_val))
        
        print(f"   [OK] Train Accuracy: {train_acc:.4f}")
        print(f"   [OK] Val Accuracy:   {val_acc:.4f}")
        
        return {
            'model': 'Logistic Regression',
            'train_acc': train_acc,
            'val_acc': val_acc
        }
    
    def train_xgboost(self, X_train, y_train, X_val, y_val) -> Dict:
        """
        Train XGBoost with MODERATE regularization.
        
        BALANCED APPROACH:
        - Medium depth (5 instead of extreme 4 or 6)
        - Medium trees (150 instead of extreme 100 or 200)
        - Light regularization
        
        Target: 78-84% accuracy
        """
        print(f"\n[*] Training BALANCED XGBoost classifier...")
        
        # BALANCED PARAMETERS
        params = {
            'objective': 'multi:softprob',
            'num_class': len(self.label_names),
            'max_depth': 5,              # Medium depth
            'learning_rate': 0.1,        # Standard
            'n_estimators': 150,         # Medium count
            'subsample': 0.85,           # Light subsampling
            'colsample_bytree': 0.85,    # Light feature sampling
            'reg_alpha': 0.05,           # Light L1
            'reg_lambda': 0.5,           # Light L2
            'min_child_weight': 2,       # Moderate
            'random_state': self.random_seed,
            'eval_metric': 'mlogloss',
            'verbosity': 0
        }
        
        self.xgb_model = xgb.XGBClassifier(**params)
        
        # Train WITHOUT early stopping (causes CV issues)
        self.xgb_model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = accuracy_score(y_train, self.xgb_model.predict(X_train))
        val_acc = accuracy_score(y_val, self.xgb_model.predict(X_val))
        
        print(f"   [OK] Train Accuracy: {train_acc:.4f}")
        print(f"   [OK] Val Accuracy:   {val_acc:.4f}")
        
        # Check if target achieved (78-84%)
        if 0.78 <= val_acc <= 0.84:
            print(f"   [SUCCESS] TARGET RANGE ACHIEVED! (78-84%)")
        elif val_acc > 0.90:
            print(f"   [WARN] Still overfitting: {val_acc:.4f} > 0.90")
        elif val_acc < 0.78:
            print(f"   [INFO] Below target but acceptable: {val_acc:.4f}")
        
        return {
            'model': 'XGBoost',
            'train_acc': train_acc,
            'val_acc': val_acc,
            'n_estimators': params['n_estimators']
        }
    
    def evaluate_test_set(self, X_test, y_test) -> Dict:
        """Comprehensive evaluation on test set"""
        print(f"\n[EVAL] FINAL TEST SET EVALUATION")
        print("=" * 60)
        
        # Predictions
        y_pred_baseline = self.baseline_model.predict(X_test)
        y_pred_xgb = self.xgb_model.predict(X_test)
        
        # Accuracies
        baseline_acc = accuracy_score(y_test, y_pred_baseline)
        xgb_acc = accuracy_score(y_test, y_pred_xgb)
        gap = xgb_acc - baseline_acc
        
        print(f"\n[RESULTS] Test Set Performance:")
        print(f"   Baseline (Logistic): {baseline_acc:.4f}")
        print(f"   XGBoost:            {xgb_acc:.4f}")
        print(f"   Gap:                {gap:.4f} ({gap/baseline_acc*100:.1f}% improvement)")
        
        if 0.78 <= xgb_acc <= 0.88:
            print(f"   [SUCCESS] XGBoost in acceptable range!")
        
        if gap >= 0.20:
            print(f"   [SUCCESS] Good gap over baseline (>= 20%)")
        
        # Classification report
        print(f"\n[REPORT] XGBoost Classification Report:")
        print(classification_report(
            y_test, y_pred_xgb,
            target_names=self.label_names,
            digits=3
        ))
        
        # Confusion matrix
        print(f"\n[MATRIX] Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred_xgb)
        cm_df = pd.DataFrame(
            cm,
            index=self.label_names,
            columns=self.label_names
        )
        print(cm_df)
        
        return {
            'baseline_acc': baseline_acc,
            'xgb_acc': xgb_acc,
            'gap': gap,
            'confusion_matrix': cm
        }
    
    def save_models(self, output_dir: str = 'models'):
        """Save trained models and scaler"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n[SAVE] Saving models to {output_dir}/...")
        
        # Save XGBoost
        xgb_path = f'{output_dir}/xgboost_v1.pkl'
        with open(xgb_path, 'wb') as f:
            pickle.dump(self.xgb_model, f)
        print(f"   [OK] {xgb_path}")
        
        # Save scaler
        scaler_path = f'{output_dir}/scaler.pkl'
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"   [OK] {scaler_path}")
        
        # Save label encoder
        encoder_path = f'{output_dir}/label_encoder.pkl'
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        print(f"   [OK] {encoder_path}")
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'label_names': self.label_names,
            'n_features': len(self.feature_names),
            'n_classes': len(self.label_names)
        }
        metadata_path = f'{output_dir}/metadata.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"   [OK] {metadata_path}")


def main():
    """Complete training pipeline"""
    print("\n" + "="*60)
    print("[START] SDLC RISK MODEL - BALANCED TRAINING")
    print("="*60)
    
    # Initialize trainer
    trainer = SDLCModelTrainer(random_seed=42)
    
    # Load data
    df = trainer.load_data('data/risk_dataset_v1.csv')
    
    # Prepare splits
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(df)
    
    # Train baseline
    baseline_results = trainer.train_baseline(X_train, y_train, X_val, y_val)
    
    # Train balanced XGBoost
    xgb_results = trainer.train_xgboost(X_train, y_train, X_val, y_val)
    
    # Evaluate on test set
    test_results = trainer.evaluate_test_set(X_test, y_test)
    
    # Save models
    trainer.save_models('models')
    
    print("\n" + "="*60)
    print("[OK] BALANCED TRAINING COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()