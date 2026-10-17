import sys
from pathlib import Path

# ==========================================
# Add Project Root
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================
# Imports
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==========================================
# File Paths
# ==========================================

RESULT_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "sentiment_evaluation_results.csv"
)

METRICS_IMAGE = (
    PROJECT_ROOT
    / "evaluation"
    / "sentiment_performance.png"
)

CONFUSION_IMAGE = (
    PROJECT_ROOT
    / "evaluation"
    / "confusion_matrix.png"
)

METRICS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "evaluation_metrics.csv"
)


# ==========================================
# Load Evaluation Results
# ==========================================

print("=" * 60)
print("SENTIMENT EVALUATION VISUALIZATION")
print("=" * 60)

try:

    df = pd.read_csv(RESULT_FILE)

except Exception as e:

    print("\n❌ Could not load evaluation results.")
    print(f"Error: {e}")

    raise SystemExit


# ==========================================
# Validate Columns
# ==========================================

required_columns = [
    "actual_sentiment",
    "predicted_sentiment"
]

for column in required_columns:

    if column not in df.columns:

        print(
            f"\n❌ Missing column: {column}"
        )

        raise SystemExit


# ==========================================
# Prepare Data
# ==========================================

df = df[
    df["predicted_sentiment"] != "error"
].copy()

y_true = (
    df["actual_sentiment"]
    .astype(str)
    .str.lower()
    .str.strip()
)

y_pred = (
    df["predicted_sentiment"]
    .astype(str)
    .str.lower()
    .str.strip()
)


labels = [
    "positive",
    "neutral",
    "negative"
]


# ==========================================
# Calculate Metrics
# ==========================================

accuracy = accuracy_score(
    y_true,
    y_pred
)

precision = precision_score(
    y_true,
    y_pred,
    labels=labels,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    labels=labels,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    labels=labels,
    average="weighted",
    zero_division=0
)


# ==========================================
# Display Metrics
# ==========================================

print("\n")
print("=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(
    f"\nAccuracy  : {accuracy * 100:.2f}%"
)

print(
    f"Precision : {precision * 100:.2f}%"
)

print(
    f"Recall    : {recall * 100:.2f}%"
)

print(
    f"F1 Score  : {f1 * 100:.2f}%"
)


# ==========================================
# Save Metrics CSV
# ==========================================

metrics_df = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score"
    ],
    "Score": [
        accuracy,
        precision,
        recall,
        f1
    ],
    "Percentage": [
        f"{accuracy * 100:.2f}%",
        f"{precision * 100:.2f}%",
        f"{recall * 100:.2f}%",
        f"{f1 * 100:.2f}%"
    ]
})

metrics_df.to_csv(
    METRICS_FILE,
    index=False
)

print(
    f"\n✅ Metrics saved to:\n{METRICS_FILE}"
)


# ==========================================
# Performance Metrics Chart
# ==========================================

metric_names = [
    "Accuracy",
    "Precision",
    "Recall",
    "F1 Score"
]

metric_values = [
    accuracy * 100,
    precision * 100,
    recall * 100,
    f1 * 100
]


plt.figure(figsize=(9, 6))

bars = plt.bar(
    metric_names,
    metric_values
)

plt.title(
    "Sentiment Model Performance"
)

plt.ylabel(
    "Score (%)"
)

plt.ylim(
    0,
    100
)

plt.grid(
    axis="y",
    alpha=0.3
)


# Add values above bars

for bar, value in zip(
    bars,
    metric_values
):

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        value + 1,
        f"{value:.2f}%",
        ha="center",
        va="bottom"
    )


plt.tight_layout()

plt.savefig(
    METRICS_IMAGE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(
    f"✅ Performance chart saved to:\n"
    f"{METRICS_IMAGE}"
)


# ==========================================
# Confusion Matrix
# ==========================================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=labels
)


print("\n")
print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print()

print(cm)


# ==========================================
# Draw Confusion Matrix
# ==========================================

plt.figure(figsize=(8, 6))

plt.imshow(
    cm,
    interpolation="nearest"
)

plt.title(
    "Sentiment Confusion Matrix"
)

plt.colorbar()

tick_marks = range(
    len(labels)
)

plt.xticks(
    tick_marks,
    [
        "Positive",
        "Neutral",
        "Negative"
]
)

plt.yticks(
    tick_marks,
    [
        "Positive",
        "Neutral",
        "Negative"
    ]
)

plt.xlabel(
    "Predicted Sentiment"
)

plt.ylabel(
    "Actual Sentiment"
)


# ==========================================
# Add Values
# ==========================================

threshold = cm.max() / 2

for i in range(
    cm.shape[0]
):

    for j in range(
        cm.shape[1]
    ):

        plt.text(
            j,
            i,
            str(cm[i, j]),
            ha="center",
            va="center",
            color=(
                "white"
                if cm[i, j] > threshold
                else "black"
            ),
            fontsize=14,
            fontweight="bold"
        )


plt.tight_layout()

plt.savefig(
    CONFUSION_IMAGE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print(
    f"\n✅ Confusion matrix saved to:\n"
    f"{CONFUSION_IMAGE}"
)


# ==========================================
# Final Message
# ==========================================

print("\n")
print("=" * 60)
print("VISUALIZATION COMPLETED")
print("=" * 60)

print(
    "\n✅ All evaluation visualizations "
    "were generated successfully."
)

print(
    "\nFiles created:"
)

print(
    "1. evaluation/evaluation_metrics.csv"
)

print(
    "2. evaluation/sentiment_performance.png"
)

print(
    "3. evaluation/confusion_matrix.png"
)