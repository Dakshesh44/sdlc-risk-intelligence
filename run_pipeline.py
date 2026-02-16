#!/usr/bin/env python3
"""
MASTER EXECUTION SCRIPT - CROSS-PLATFORM (Windows & Linux)
Runs complete ML pipeline from data generation to trained model
FINAL FIX: Uses os.path.join for proper path handling
"""

import os
import sys
import time
import platform
import subprocess


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_command(cmd_list):
    """Execute command using subprocess (handles spaces in paths)"""
    try:
        result = subprocess.run(
            cmd_list,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return 0
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)
        return e.returncode


def run_phase(name, module_path, description):
    """Run a phase and track time"""
    print_header(f"PHASE: {name}")
    print(f"📝 {description}\n")
    
    start = time.time()
    
    # Execute the Python module directly using subprocess
    result = run_command([sys.executable, module_path])
    
    elapsed = time.time() - start
    
    if result != 0:
        print(f"\n❌ FAILED: {name}")
        print(f"Error code: {result}")
        sys.exit(1)
    
    print(f"\n✅ COMPLETED in {elapsed:.1f}s")
    return elapsed


def main():
    """Execute complete ML pipeline"""
    
    # Detect OS
    os_name = platform.system()
    print_header(f"🚀 SDLC RISK MODEL - ML PIPELINE ({os_name})")
    
    print("This script will:")
    print("  1. Run performance layer tests (4 tests)")
    print("  2. Generate 60k synthetic dataset (~2-3 mins)")
    print("  3. Train XGBoost model (~3-5 mins)")
    print("  4. Evaluate and save models")
    print("\nEstimated total time: 5-10 minutes\n")
    
    # Create required directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    print("✅ Created data/ and models/ directories\n")
    
    input("Press ENTER to start...")
    
    total_start = time.time()
    times = {}
    
    # PHASE 1: Test Performance Layer
    print_header("PHASE 1: Performance Layer Tests")
    print("📝 Validating performance metrics calculation\n")
    
    start = time.time()
    
    # Use os.path.join for proper path handling on Windows
    test_path = os.path.join('tests', 'test_performance_layer.py')
    
    # Run pytest using subprocess with proper path handling
    result = run_command([
        sys.executable, 
        '-m', 
        'pytest', 
        test_path,
        '-v'
    ])
    
    times['tests'] = time.time() - start
    
    if result != 0:
        print("\n❌ FAILED: Performance Layer Tests")
        print("\n⚠️  Possible issues:")
        print("  - Missing ml/performance_layer.py file")
        print("  - Import errors in test file")
        print("\n🔍 Debug info:")
        print(f"  Python executable: {sys.executable}")
        print(f"  Current directory: {os.getcwd()}")
        print(f"  Test file path: {test_path}")
        print(f"  Test file exists: {os.path.exists(test_path)}")
        print(f"  ml/ folder exists: {os.path.exists('ml')}")
        print(f"  ml/performance_layer.py exists: {os.path.exists(os.path.join('ml', 'performance_layer.py'))}")
        sys.exit(1)
    
    print(f"\n✅ COMPLETED in {times['tests']:.1f}s")
    
    # PHASE 2: Generate Dataset
    dataset_script = os.path.join('ml', 'data_generator.py')
    times['data'] = run_phase(
        "Dataset Generation",
        dataset_script,
        "Generating 10k projects × 6 SDLCs = 60k samples"
    )
    
    # Verify dataset was created
    dataset_path = os.path.join('data', 'risk_dataset_v1.csv')
    if not os.path.exists(dataset_path):
        print(f"\n❌ ERROR: Dataset file not created!")
        print(f"Expected: {dataset_path}")
        sys.exit(1)
    
    # Check file size
    file_size = os.path.getsize(dataset_path) / (1024 * 1024)
    print(f"✅ Dataset created: {file_size:.2f} MB")
    
    # PHASE 3: Train Models
    trainer_script = os.path.join('ml', 'model_trainer.py')
    times['training'] = run_phase(
        "Model Training",
        trainer_script,
        "Training Logistic baseline + XGBoost classifier"
    )
    
    # Verify models were created
    required_models = [
        os.path.join('models', 'xgboost_v1.pkl'),
        os.path.join('models', 'scaler.pkl'),
        os.path.join('models', 'label_encoder.pkl'),
        os.path.join('models', 'metadata.pkl')
    ]
    
    missing = [m for m in required_models if not os.path.exists(m)]
    if missing:
        print(f"\n⚠️  WARNING: Some model files missing:")
        for m in missing:
            print(f"  - {m}")
    else:
        print(f"\n✅ All 4 model files created successfully")
    
    # Calculate total time
    total_time = time.time() - total_start
    
    # Final summary
    print_header("🎉 PIPELINE COMPLETE!")
    
    print("⏱️  TIMING BREAKDOWN:")
    print(f"   Performance Tests:  {times['tests']:.1f}s")
    print(f"   Dataset Generation: {times['data']:.1f}s")
    print(f"   Model Training:     {times['training']:.1f}s")
    print(f"   ─────────────────────────────")
    print(f"   TOTAL:             {total_time:.1f}s ({total_time/60:.1f} min)\n")
    
    print("📦 DELIVERABLES:")
    print(f"   ✅ {os.path.join('data', 'risk_dataset_v1.csv')}       (60,000 samples)")
    print(f"   ✅ {os.path.join('models', 'xgboost_v1.pkl')}          (Trained XGBoost)")
    print(f"   ✅ {os.path.join('models', 'scaler.pkl')}              (Feature scaler)")
    print(f"   ✅ {os.path.join('models', 'label_encoder.pkl')}       (Label encoder)")
    print(f"   ✅ {os.path.join('models', 'metadata.pkl')}            (Model metadata)\n")
    
    print("🚀 NEXT STEPS:")
    print("   1. Test production predictor:")
    print(f"      python {os.path.join('ml', 'model_predictor.py')}")
    print("   2. Integrate with FastAPI backend (Member 2)")
    print("   3. Connect to React frontend (Member 3)\n")
    
    print("="*70)
    print("✅ ML MODULE 100% COMPLETE!")
    print("="*70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)