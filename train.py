"""
Treinamento do modelo de classificação de patologias da coluna vertebral.

Dataset: questao_01.csv
Features: V1, V2, V3, V4, V5, V6
Target: diagnostic (Normal, Disk Hernia, Spondylolisthesis)
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# Carregar dados
CSV_PATH = "questao_01.csv"
try:
    df = pd.read_csv(CSV_PATH, index_col=0)
except FileNotFoundError:
    raise SystemExit(
        f"Dataset não encontrado: '{CSV_PATH}'. "
        "Execute este script a partir do diretório raiz do repositório."
    )
except Exception as exc:
    raise SystemExit(f"Erro ao ler '{CSV_PATH}': {exc}") from exc

FEATURES = ["V1", "V2", "V3", "V4", "V5", "V6"]
TARGET = "diagnostic"

X = df[FEATURES]
y = df[TARGET]

# Codificar labels
le = LabelEncoder()
y_enc = le.fit_transform(y)

# Dividir em treino e teste
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# Treinar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Avaliar
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print()
print(classification_report(y_test, y_pred, target_names=le.classes_))

# Salvar modelo e encoder
os.makedirs("deploy_ml", exist_ok=True)
joblib.dump({"model": model, "label_encoder": le}, "deploy_ml/modelo.pkl")
print("Modelo salvo em deploy_ml/modelo.pkl")
