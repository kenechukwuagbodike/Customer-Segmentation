import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "data"
CLEAN_FILE = DATA_DIR / "clean.csv"
RFM_FILE = DATA_DIR / "rfm.csv"


def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Snapshot = one day after the last transaction in the dataset.
    # Every customer's recency is measured from this fixed point so
    # all customers are compared on the same timeline.
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    log.info("Snapshot date: %s", snapshot.date())

    rfm = (
        df.groupby("CustomerID")
        .agg(
            recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
            frequency=("InvoiceNo", "nunique"),   # unique invoices, not line items
            monetary=("TotalValue", "sum"),
        )
        .reset_index()
    )

    log.info(
        "RFM features computed for %d customers  |  "
        "recency %d–%d days  |  frequency %d–%d invoices  |  "
        "monetary £%.0f–£%.0f",
        len(rfm),
        rfm.recency.min(), rfm.recency.max(),
        rfm.frequency.min(), rfm.frequency.max(),
        rfm.monetary.min(), rfm.monetary.max(),
    )
    return rfm


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    # Recency: LOWER days = more recent = better → reverse the labels (5 is best)
    rfm["r_score"] = pd.qcut(
        rfm["recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop"
    ).astype(int)

    # Frequency: rank first to break ties (many customers have identical invoice counts)
    rfm["f_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Monetary: straightforward quintile — higher spend = higher score
    rfm["m_score"] = pd.qcut(
        rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5], duplicates="drop"
    ).astype(int)

    # Combined RFM string (e.g. '555' = best customer on all three dimensions)
    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )
    rfm["rfm_total"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

    log.info(
        "Scores assigned  |  rfm_total range: %d–%d  |  '555' Champions: %d customers",
        rfm.rfm_total.min(),
        rfm.rfm_total.max(),
        (rfm.rfm_score == "555").sum(),
    )
    return rfm


def main() -> None:
    log.info("Loading %s…", CLEAN_FILE.name)
    df = pd.read_csv(CLEAN_FILE)
    rfm = compute_rfm(df)
    rfm = score_rfm(rfm)
    rfm.to_csv(RFM_FILE, index=False)
    log.info("Saved → %s  (%d rows)", RFM_FILE, len(rfm))


if __name__ == "__main__":
    main()
