"""Train the Iris classifier and save it as model.joblib."""
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42, stratify=iris.target
)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
print(f"Test accuracy: {accuracy_score(y_test, predictions):.3f}")
model.classes_ = iris.target_names[model.classes_]
joblib.dump(model, "model.joblib")
print("Saved trained model to model.joblib")
