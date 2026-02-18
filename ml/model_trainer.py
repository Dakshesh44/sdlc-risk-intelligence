import os
import warnings
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")
np.random.seed(42)

# --------------------------------------------------
# 🔹 PATH CONFIGURATION (ROBUST)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sdlc_dataset_1800.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")

os.makedirs(MODEL_DIR, exist_ok=True)

# --------------------------------------------------
# 1️⃣ Load Dataset
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# 2️⃣ Integrity Check
# --------------------------------------------------
assert df.groupby("project_id")["is_best"].sum().eq(1).all(), \
    "Integrity error: More than one optimal SDLC per project!"

print("✅ Integrity check passed.")

# --------------------------------------------------
# 3️⃣ Project-Level Aggregation
# --------------------------------------------------
project_best = df[df["is_best"] == 1].copy()
project_best = project_best.set_index("project_id")
project_best["optimal_sdlc"] = project_best["sdlc_type"]

print(f"✅ {len(project_best)} unique projects detected.")

# --------------------------------------------------
# 4️⃣ Explicit Feature Selection
# --------------------------------------------------
FEATURES = [
    col for col in df.columns
    if col not in ["project_id", "sdlc_type", "suitability_score", "is_best"]
]

print(f"Using {len(FEATURES)} features.")

X = project_best[FEATURES]
y = project_best["optimal_sdlc"]

# --------------------------------------------------
# 5️⃣ Stratified Project Split
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"✅ Train: {len(X_train)} | Test: {len(X_test)}")

# --------------------------------------------------
# 6️⃣ Encode Labels
# --------------------------------------------------
label_enc = LabelEncoder()
y_train_enc = label_enc.fit_transform(y_train)
y_test_enc = label_enc.transform(y_test)

print(f"Classes: {list(label_enc.classes_)}")

# --------------------------------------------------
# 7️⃣ Train Multi-Class XGBoost
# --------------------------------------------------
model = XGBClassifier(
    objective="multi:softprob",
    num_class=len(label_enc.classes_),
    n_estimators=150,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=42,
    eval_metric="mlogloss"
)

model.fit(
    X_train,
    y_train_enc,
    eval_set=[(X_test, y_test_enc)],
    verbose=False
)

print("✅ Model training complete.")

# --------------------------------------------------
# 8️⃣ Evaluation (Project-Level)
# --------------------------------------------------
proba = model.predict_proba(X_test)
pred_idx = np.argmax(proba, axis=1)

top1_acc = (pred_idx == y_test_enc).mean()

# Top-2 Accuracy
top2 = np.argsort(proba, axis=1)[:, -2:]
top2_acc = np.mean([y_test_enc[i] in top2[i] for i in range(len(y_test_enc))])

print(f"\n🎯 PROJECT TOP-1 ACCURACY: {top1_acc:.2%}")
print(f"🎯 PROJECT TOP-2 ACCURACY: {top2_acc:.2%}")

print("\nClassification Report:")
print(classification_report(y_test_enc, pred_idx, target_names=label_enc.classes_))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test_enc, pred_idx)
print(pd.DataFrame(cm, index=label_enc.classes_, columns=label_enc.classes_))

# --------------------------------------------------
# 9️⃣ Stability Test (Consistent Hyperparameters)
# --------------------------------------------------
seeds = [42, 123, 456]
scores = []

for seed in seeds:
    m = XGBClassifier(
        objective="multi:softprob",
        num_class=len(label_enc.classes_),
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=seed,
        eval_metric="mlogloss"
    )
    m.fit(X_train, y_train_enc)
    p = m.predict_proba(X_test).argmax(axis=1)
    scores.append((p == y_test_enc).mean())

print(f"\nStability: {np.mean(scores):.2%} ± {np.std(scores):.3f}")
print("Seed Scores:", [f"{s:.2%}" for s in scores])

# --------------------------------------------------
# 🔟 Save Model + Encoder
# --------------------------------------------------
model_path = os.path.join(MODEL_DIR, "xgb_sdlc_model.pkl")
encoder_path = os.path.join(MODEL_DIR, "label_encoder.pkl")

joblib.dump(model, model_path)
joblib.dump(label_enc, encoder_path)

print("\n✅ Model and encoder saved to /model folder.")
print("📦 TRAINING PIPELINE VERIFIED & PRODUCTION READY.")
