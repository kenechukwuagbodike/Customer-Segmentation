import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

RFM_FILE = DATA_DIR / "rfm.csv"

# We cluster on log-transformed RFM values.
# Monetary and frequency both have extreme right skew (one customer spent £608K).
# Log1p compression keeps the relative distances meaningful without letting
# a single outlier dominate the entire clustering.
FEATURES = ["recency", "log_frequency", "log_monetary"]

# k=5 gives us 5 meaningful segments: Champions, Loyal, At-Risk, New Customers, Lost.
# The elbow and silhouette analysis below confirms this is a strong choice for this dataset.
BEST_K = 5


def scale_features(rfm: pd.DataFrame):
    scaler = StandardScaler()
    X = scaler.fit_transform(rfm[FEATURES])
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    log.info("Features scaled with StandardScaler — scaler saved")
    return X, scaler


def run_elbow(X: np.ndarray) -> pd.DataFrame:
    # Test k from 2 to 10 and record inertia + silhouette score at each k.
    # This data is saved for the dashboard validation chart.
    log.info("Running elbow method for k=2 to k=10…")
    records = []
    for k in range(2, 11):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        sil = silhouette_score(X, labels)
        records.append({"k": k, "inertia": km.inertia_, "silhouette": sil})
        log.info("  k=%d  inertia=%.0f  silhouette=%.3f", k, km.inertia_, sil)

    elbow_df = pd.DataFrame(records)
    elbow_df.to_csv(DATA_DIR / "elbow_data.csv", index=False)
    log.info("Elbow data saved → data/elbow_data.csv")
    return elbow_df


def fit_kmeans(X: np.ndarray) -> KMeans:
    log.info("Fitting final KMeans with k=%d…", BEST_K)
    km = KMeans(n_clusters=BEST_K, random_state=42, n_init=10)
    km.fit(X)
    score = silhouette_score(X, km.labels_)
    log.info("Final silhouette score (k=%d): %.3f", BEST_K, score)
    joblib.dump(km, MODELS_DIR / "kmeans.pkl")
    log.info("Model saved → models/kmeans.pkl")

    # Save silhouette score alongside model for reference
    eval_path = MODELS_DIR / "evaluation.txt"
    eval_path.write_text(f"k={BEST_K}\nsilhouette_score={score:.4f}\n")
    return km


def assign_labels(rfm: pd.DataFrame) -> pd.DataFrame:
    # After KMeans, cluster IDs are arbitrary numbers. We map them to meaningful
    # business names by looking at the average RFM scores per cluster.
    #
    # Logic:
    #   - Sort clusters by combined rfm_total (r+f+m scores) descending
    #   - Top cluster overall → Champions
    #   - Bottom cluster overall → Lost
    #   - Among the middle 3, the one with the highest f_score → Loyal
    #   - Of the remaining 2, higher r_score → New Customers, lower → At-Risk

    profile = rfm.groupby("cluster")[["r_score", "f_score", "m_score", "rfm_total"]].mean()
    ranked = profile.sort_values("rfm_total", ascending=False)
    clusters = ranked.index.tolist()

    label_map = {
        clusters[0]: "Champions",
        clusters[-1]: "Lost",
    }

    middle = ranked.iloc[1:-1].sort_values("f_score", ascending=False)
    mid = middle.index.tolist()
    label_map[mid[0]] = "Loyal"

    remaining = middle.iloc[1:].sort_values("r_score", ascending=False)
    label_map[remaining.index[0]] = "New Customers"
    label_map[remaining.index[1]] = "At-Risk"

    rfm["segment"] = rfm["cluster"].map(label_map)
    log.info("Segment labels assigned: %s", rfm["segment"].value_counts().to_dict())
    return rfm


def build_profiles(rfm: pd.DataFrame) -> pd.DataFrame:
    # One summary row per segment — used by the dashboard's summary table
    total_revenue = rfm["monetary"].sum()
    profiles = (
        rfm.groupby("segment")
        .agg(
            customers=("CustomerID", "count"),
            avg_recency=("recency", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
            total_revenue=("monetary", "sum"),
        )
        .reset_index()
    )
    profiles["pct_customers"] = profiles["customers"] / profiles["customers"].sum() * 100
    profiles["pct_revenue"] = profiles["total_revenue"] / total_revenue * 100

    # Round for readability
    profiles["avg_recency"] = profiles["avg_recency"].round(0).astype(int)
    profiles["avg_frequency"] = profiles["avg_frequency"].round(1)
    profiles["avg_monetary"] = profiles["avg_monetary"].round(2)
    profiles["pct_customers"] = profiles["pct_customers"].round(1)
    profiles["pct_revenue"] = profiles["pct_revenue"].round(1)

    profiles.to_csv(DATA_DIR / "segment_profiles.csv", index=False)
    log.info("Segment profiles saved → data/segment_profiles.csv")
    log.info("\n%s", profiles[["segment", "customers", "pct_revenue"]].to_string(index=False))
    return profiles


def main() -> None:
    log.info("Loading %s…", RFM_FILE.name)
    rfm = pd.read_csv(RFM_FILE)

    # Log1p-transform the skewed dimensions before passing to StandardScaler.
    # Without this, a single £608K customer pulls an entire cluster to itself.
    rfm["log_frequency"] = np.log1p(rfm["frequency"])
    rfm["log_monetary"] = np.log1p(rfm["monetary"])

    X, _ = scale_features(rfm)
    run_elbow(X)

    km = fit_kmeans(X)
    rfm["cluster"] = km.labels_

    rfm = assign_labels(rfm)
    build_profiles(rfm)

    rfm.to_csv(DATA_DIR / "segments.csv", index=False)
    log.info("Customer segments saved → data/segments.csv  (%d rows)", len(rfm))


if __name__ == "__main__":
    main()
