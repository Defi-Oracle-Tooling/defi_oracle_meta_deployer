import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# Generate a random dataset for training
X, y = make_classification(n_samples=1000, n_features=5, random_state=42)

# Train a RandomForestClassifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the trained model to a file
joblib.dump(model, 'ml_model.pkl')
