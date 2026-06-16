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
RAW_FILE = DATA_DIR / "online_retail_II.xlsx"
CLEAN_FILE = DATA_DIR / "clean.csv"

# The xlsx uses slightly different column names to the documentation,
# so we normalise them here once so all downstream scripts stay consistent.
COLUMN_MAP = {
    "Invoice": "InvoiceNo",
    "Customer ID": "CustomerID",   # has a space in the actual file
    "Price": "UnitPrice",
}

# These StockCodes aren't real products — they're administrative entries
# (manual adjustments, postage, carriage, bank charges, etc). Left in, they
# skew monetary totals and pollute "top products" with non-product rows.
ADMIN_STOCK_CODES = {"POST", "D", "M", "BANK CHARGES", "C2", "DOT", "PADS", "S", "AMAZONFEE", "CRUK"}


def load_raw() -> pd.DataFrame:
    # Both year-sheets are loaded and stacked into one DataFrame.
    # dtype arg stops pandas reading CustomerID as 12345.0 instead of '12345'.
    log.info("Loading %s — two sheets, ~1M rows (allow ~60 seconds)…", RAW_FILE.name)
    sheets = pd.read_excel(RAW_FILE, sheet_name=None, dtype={"Customer ID": str})
    df = pd.concat(sheets.values(), ignore_index=True)
    log.info("Loaded %d rows across %d sheets", len(df), len(sheets))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Normalise column names before doing anything else
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})

    # Can't segment a transaction if we don't know who made it
    before = len(df)
    df = df.dropna(subset=["CustomerID"])
    log.info("Dropped %d rows with null CustomerID → %d remaining", before - len(df), len(df))

    # Invoices starting with 'C' are cancellations, not real purchases
    before = len(df)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    log.info("Dropped %d cancellation rows → %d remaining", before - len(df), len(df))

    # Negative quantity = return, zero/negative price = data error — drop both
    before = len(df)
    df = df[(df["Quantity"] >= 1) & (df["UnitPrice"] > 0)]
    log.info("Dropped %d return/error rows → %d remaining", before - len(df), len(df))

    # Dataset is ~90% UK — keeping just UK gives us a clean, focused sample
    before = len(df)
    df = df[df["Country"] == "United Kingdom"]
    log.info("Dropped %d non-UK rows → %d remaining", before - len(df), len(df))

    # Strip out admin entries (Manual, Postage, Carriage, etc.) — not real purchases
    before = len(df)
    df = df[~df["StockCode"].astype(str).str.upper().isin(ADMIN_STOCK_CODES)]
    log.info("Dropped %d admin/non-product rows → %d remaining", before - len(df), len(df))

    df["TotalValue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype(str).str.strip()

    log.info(
        "Clean complete: %d rows | %d unique customers | %s → %s",
        len(df),
        df["CustomerID"].nunique(),
        df["InvoiceDate"].min().date(),
        df["InvoiceDate"].max().date(),
    )
    return df.reset_index(drop=True)


def main() -> None:
    df = load_raw()
    clean_df = clean(df)
    clean_df.to_csv(CLEAN_FILE, index=False)
    log.info("Saved → %s", CLEAN_FILE)


if __name__ == "__main__":
    main()
