import sys
from pathlib import Path

# ==========================================
# Add Project Root to Python Path
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================
# Imports
# ==========================================

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from services.analyzer import analyze_sentiment


# ==========================================
# Configuration
# ==========================================

DATASET = (
    PROJECT_ROOT
    / "evaluation"
    / "sentiment_test.csv"
)

RESULT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "sentiment_evaluation_results.csv"
)


# ==========================================
# Load Dataset
# ==========================================

print("=" * 60)
print("SENTIMENT MODEL EVALUATION")
print("=" * 60)

print(f"\nDataset: {DATASET}")

try:

    df = pd.read_csv(DATASET)

except Exception as e:

    print("\n❌ Unable to load evaluation dataset.")
    print(f"Error: {e}")

    raise SystemExit


# ==========================================
# Validate Dataset
# ==========================================

required_columns = [
    "text",
    "actual_sentiment"
]

for column in required_columns:

    if column not in df.columns:

        print(
            f"\n❌ Missing required column: {column}"
        )

        print(
            "Required columns are:"
        )

        print(
            "text, actual_sentiment"
        )

        raise SystemExit


if df.empty:

    print("\n❌ Evaluation dataset is empty.")

    raise SystemExit


print(
    f"\nTotal test samples: {len(df)}"
)


# ==========================================
# Display Class Distribution
# ==========================================

print("\nActual sentiment distribution:")

print(
    df["actual_sentiment"]
    .value_counts()
)


# ==========================================
# Run Sentiment Model
# ==========================================

predictions = []

print("\n")
print("=" * 60)
print("RUNNING SENTIMENT MODEL")
print("=" * 60)

print()


for index, row in df.iterrows():

    text = str(row["text"])

    actual = str(
        row["actual_sentiment"]
    ).lower().strip()

    try:

        result = analyze_sentiment(text)

        prediction = str(
            result["label"]
        ).lower().strip()

        predictions.append(prediction)

        print(
            f"{index + 1:02d}. "
            f"Actual: {actual:<8} "
            f"Predicted: {prediction:<8} "
            f"Confidence: "
            f"{result['score']:.2%}"
        )

    except Exception as e:

        print(
            f"{index + 1:02d}. "
            f"Actual: {actual:<8} "
            f"ERROR: {e}"
        )

        predictions.append("error")


# ==========================================
# Add Predictions to DataFrame
# ==========================================

df["predicted_sentiment"] = predictions


# ==========================================
# Remove Failed Predictions
# ==========================================

valid_df = df[
    df["predicted_sentiment"] != "error"
].copy()


failed_count = len(df) - len(valid_df)


print("\n")
print("=" * 60)
print("PREDICTION SUMMARY")
print("=" * 60)

print(
    f"Total samples       : {len(df)}"
)

print(
    f"Successful predictions: {len(valid_df)}"
)

print(
    f"Failed predictions  : {failed_count}"
)


if valid_df.empty:

    print(
        "\n❌ No valid predictions were produced."
    )

    print(
        "\nThe model could not produce any "
        "valid predictions."
    )

    print(
        "Check the Hugging Face model "
        "connection and try again."
    )

    raise SystemExit


# ==========================================
# Prepare Actual and Predicted Labels
# ==========================================

y_true = (
    valid_df["actual_sentiment"]
    .astype(str)
    .str.lower()
    .str.strip()
)

y_pred = (
    valid_df["predicted_sentiment"]
    .astype(str)
    .str.lower()
    .str.strip()
)


# ==========================================
# Labels
# ==========================================

labels = [
    "positive",
    "neutral",
    "negative"
]


# ==========================================
# Calculate Accuracy
# ==========================================

accuracy = accuracy_score(
    y_true,
    y_pred
)


# ==========================================
# Calculate Precision
# ==========================================

precision = precision_score(
    y_true,
    y_pred,
    labels=labels,
    average="weighted",
    zero_division=0
)


# ==========================================
# Calculate Recall
# ==========================================

recall = recall_score(
    y_true,
    y_pred,
    labels=labels,
    average="weighted",
    zero_division=0
)


# ==========================================
# Calculate F1 Score
# ==========================================

f1 = f1_score(
    y_true,
    y_pred,
    labels=labels,
    average="weighted",
    zero_division=0
)


# ==========================================
# Display Main Results
# ==========================================

print("\n")
print("=" * 60)
print("EVALUATION RESULTS")
print("=" * 60)

print(
    f"\nAccuracy  : "
    f"{accuracy:.4f} "
    f"({accuracy * 100:.2f}%)"
)

print(
    f"Precision : "
    f"{precision:.4f} "
    f"({precision * 100:.2f}%)"
)

print(
    f"Recall    : "
    f"{recall:.4f} "
    f"({recall * 100:.2f}%)"
)

print(
    f"F1 Score  : "
    f"{f1:.4f} "
    f"({f1 * 100:.2f}%)"
)


# ==========================================
# Classification Report
# ==========================================

print("\n")
print("=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

report = classification_report(
    y_true,
    y_pred,
    labels=labels,
    zero_division=0
)

print(report)


# ==========================================
# Confusion Matrix
# ==========================================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=labels
)


cm_df = pd.DataFrame(
    cm,
    index=[
        "Actual Positive",
        "Actual Neutral",
        "Actual Negative"
    ],
    columns=[
        "Predicted Positive",
        "Predicted Neutral",
        "Predicted Negative"
    ]
)


print("\n")
print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print()

print(cm_df)


# ==========================================
# Save Detailed Results
# ==========================================

try:

    df.to_csv(
        RESULT_FILE,
        index=False
    )

    print("\n")
    print(
        "✅ Detailed predictions saved to:"
    )

    print(
        RESULT_FILE
    )

except Exception as e:

    print("\n⚠ Could not save results.")

    print(
        f"Error: {e}"
    )


# ==========================================
# Final Message
# ==========================================

print("\n")
print("=" * 60)
print("EVALUATION COMPLETED")
print("=" * 60)

print(
    "\n✅ Sentiment model evaluation finished."
)