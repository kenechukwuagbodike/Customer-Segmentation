# documentation/scripts/generate_case_study.py
# Builds samples/customer-segmentation-case-study.pdf for the GitHub portfolio.
# Run from the project root:
#     python documentation/scripts/generate_case_study.py

from pathlib import Path

import pandas as pd
from fpdf import FPDF, XPos, YPos

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SAMPLES = ROOT / "samples"
SAMPLES.mkdir(exist_ok=True)

_PURPLE = (124, 58, 237)
_DARK = (17, 24, 39)
_GREY = (75, 85, 99)
_WHITE = (255, 255, 255)
_BLUE = (33, 150, 243)
_GREEN = (76, 175, 80)
_ORANGE = (255, 152, 0)
_PINK = (156, 39, 176)
_RED = (244, 67, 54)
_SEGMENT_COLOR = {
    "Champions": _BLUE,
    "Loyal": _GREEN,
    "At-Risk": _ORANGE,
    "New Customers": _PINK,
    "Lost": _RED,
}


class Doc(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*_GREY)
        self.cell(0, 8, "Customer Segmentation Dashboard  |  Case Study",
                  new_x=XPos.LMARGIN, new_y=YPos.TOP)
        self.cell(0, 8, f"Page {self.page_no()}",
                  align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        self.set_draw_color(209, 213, 219)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*_GREY)
        self.cell(0, 8, "Kene Agbodike  |  Data & AI Decision Systems Consultant",
                  align="C")

    def cover(self):
        self.add_page()
        self.set_fill_color(*_PURPLE)
        self.rect(0, 0, 210, 90, "F")
        self.set_y(22)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*_WHITE)
        self.cell(0, 12, "Customer Segmentation Dashboard",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 13)
        self.cell(0, 8, "Case Study & Segment Reference Guide",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 7, "How RFM analysis and KMeans clustering turn raw transactions into targeting decisions",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(100)
        self.set_text_color(*_DARK)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, "Kene Agbodike",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*_GREY)
        self.cell(0, 6, "Data & AI Decision Systems Consultant",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, "github.com/kenechukwuagbodike",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)
        self.set_draw_color(*_PURPLE)
        self.set_line_width(0.5)
        self.line(30, self.get_y(), 180, self.get_y())
        self.ln(8)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*_DARK)
        self.cell(0, 7, "Contents",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        for item in [
            "1.  The Business Problem",
            "2.  What the Dashboard Does",
            "3.  The Segments Story  -  What Each Segment Means",
            "4.  How the Dashboard Supports Decisions",
            "5.  Technical Architecture",
            "6.  Segment Results Snapshot",
        ]:
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*_GREY)
            self.cell(0, 7, item,
                      align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section(self, title):
        self.ln(4)
        self.set_fill_color(*_PURPLE)
        self.set_text_color(*_WHITE)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 9, f"  {title}",
                  fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*_DARK)

    def sub(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*_PURPLE)
        self.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*_PURPLE)
        self.line(10, self.get_y(), 100, self.get_y())
        self.ln(3)
        self.set_text_color(*_DARK)

    def body(self, text):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*_GREY)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def segment_block(self, name, profile_line, desc, action):
        color = _SEGMENT_COLOR.get(name, _GREY)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*color)
        self.cell(0, 6, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(*_GREY)
        self.set_x(self.l_margin)
        self.cell(0, 5, profile_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*_DARK)
        self.set_x(self.l_margin)
        self.multi_cell(0, 5, desc)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(*_PURPLE)
        self.set_x(self.l_margin)
        self.multi_cell(0, 5, f"Recommended action: {action}")
        self.ln(3)


def build_case_study():
    profiles = pd.read_csv(DATA_DIR / "segment_profiles.csv")
    elbow = pd.read_csv(DATA_DIR / "elbow_data.csv")
    silhouette = elbow.loc[elbow["k"] == 5, "silhouette"].iloc[0]
    total_customers = int(profiles["customers"].sum())
    total_revenue = profiles["total_revenue"].sum()

    pdf = Doc()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.cover()

    # Section 1
    pdf.add_page()
    pdf.section("1.  The Business Problem")
    pdf.body(
        "Most online retailers treat their customer base as one undifferentiated group. "
        "Every customer gets the same email, the same discount, the same re-engagement "
        "campaign, regardless of whether they spent £20 once or £600,000 across three "
        "hundred orders. This wastes marketing budget on customers who were never going "
        "to respond, and under-serves the small group of customers actually driving "
        "the business."
    )
    pdf.body(
        "Knowing average revenue per customer is not enough. An average hides the fact "
        "that a small number of customers may be responsible for the majority of "
        "revenue, while a large number contribute almost nothing and may already be gone."
    )
    pdf.body(
        "This dashboard solves that problem. It scores every customer on Recency, "
        "Frequency, and Monetary value (RFM), groups them into five behavioural "
        "segments using KMeans clustering, and recommends a specific marketing action "
        "for each segment."
    )

    pdf.section("2.  What the Dashboard Does")
    pdf.body(
        "The Customer Segmentation Dashboard is a three-tab interactive application "
        "built on real UK transaction data from the UCI Online Retail II dataset."
    )
    pdf.sub("Tab 1 - Segment Overview")
    pdf.body(
        "A scatter plot of every customer (recency vs monetary value, coloured by "
        "segment), a segment profile table, and a revenue-by-segment bar chart. "
        "Answers the question 'which segments actually matter?' at a glance."
    )
    pdf.sub("Tab 2 - Deep Dive")
    pdf.body(
        "Select a segment to see its top 10 products by revenue, its purchase "
        "frequency distribution, and the specific recommended marketing action for "
        "that group."
    )
    pdf.sub("Tab 3 - Model Validation")
    pdf.body(
        "The elbow plot and silhouette score chart used to justify choosing k=5 "
        "clusters, included so the segmentation is not a black box."
    )

    # Section 3
    pdf.add_page()
    pdf.section("3.  The Segments Story  -  What Each Segment Means")

    pdf.segment_block(
        "Champions",
        "801 customers (15.0% of base)  |  68.4% of total revenue",
        "Bought recently, buy often, and spend the most. This small group is "
        "responsible for more than two thirds of all revenue in the dataset.",
        "Protect and reward. VIP early access, referral bonuses, exclusive bundles. "
        "Any churn here hurts disproportionately.",
    )
    pdf.segment_block(
        "Loyal",
        "1,530 customers (28.7% of base)  |  20.0% of total revenue",
        "High purchase frequency with solid spend, just below Champion level. The "
        "largest segment by customer count and the second largest by revenue.",
        "Upsell and nudge upward with bundle deals, milestone rewards, and "
        "personalised cross-sell recommendations.",
    )
    pdf.segment_block(
        "At-Risk",
        "755 customers (14.1% of base)  |  6.4% of total revenue",
        "Used to buy regularly and spent well, but have gone quiet recently. "
        "A clear win-back opportunity before they are lost for good.",
        "Send a personalised win-back email with a time-limited discount. Act "
        "within 30 days.",
    )
    pdf.segment_block(
        "New Customers",
        "1,239 customers (23.2% of base)  |  3.5% of total revenue",
        "Bought recently but have not yet established a habit. Frequency and "
        "spend are both still low.",
        "Onboard into a second purchase with a welcome sequence and a "
        "second-purchase incentive within 30 days.",
    )
    pdf.segment_block(
        "Lost",
        "1,011 customers (18.9% of base)  |  1.7% of total revenue",
        "Have not purchased in over a year and never spent much when they did. "
        "Nearly a fifth of the customer base by headcount, but barely visible "
        "in revenue.",
        "One last reactivation email, then retire from active campaigns. "
        "Continued outreach wastes budget and hurts deliverability.",
    )

    # Section 4
    pdf.add_page()
    pdf.section("4.  How the Dashboard Supports Decisions")

    pdf.sub("Where to spend the marketing budget")
    pdf.body(
        "Champions are 15% of customers and 68.4% of revenue. This single number "
        "justifies reallocating retention budget away from blanket campaigns and "
        "toward protecting this group specifically."
    )
    pdf.sub("Where win-back campaigns will actually work")
    pdf.body(
        "At-Risk customers have a meaningfully higher average spend (£1,243) than "
        "New Customers (£410) or Lost customers (£248). Win-back spend is better "
        "targeted here than at the Lost segment, which historically never spent much."
    )
    pdf.sub("Where to stop spending")
    pdf.body(
        "The Lost segment is 18.9% of the customer base but only 1.7% of revenue. "
        "Continued marketing spend on this group has a poor return and risks "
        "deliverability problems for the rest of the email program."
    )
    pdf.sub("Validating the segmentation itself")
    pdf.body(
        f"The Model Validation tab shows a silhouette score of {silhouette:.3f} at "
        "k=5, alongside the elbow plot used to select that value. This lets a "
        "stakeholder check the segmentation is statistically defensible rather "
        "than taking it on faith."
    )

    # Section 5
    pdf.add_page()
    pdf.section("5.  Technical Architecture")

    pdf.sub("Data pipeline")
    pdf.body(
        "Three pipeline scripts run in sequence:\n\n"
        "pipeline/clean.py: loads both sheets of the raw UCI Online Retail II "
        "Excel file (~1.06M rows), drops null customer IDs, cancellations, "
        "returns, non-UK transactions, and administrative entries (postage, "
        "discounts, bank charges).\n\n"
        "pipeline/rfm.py: calculates Recency, Frequency, and Monetary value per "
        "customer and scores each dimension 1-5 using quintile binning "
        "(pandas.qcut).\n\n"
        "pipeline/segment.py: log1p-transforms frequency and monetary, scales "
        "with StandardScaler, fits KMeans at k=5, and labels each cluster with a "
        "business name based on its average RFM scores."
    )
    pdf.sub("Handling the outlier problem")
    pdf.body(
        "Raw frequency and monetary values are heavily right-skewed: one customer "
        "spent over £600,000 against a median spend in the hundreds of pounds. "
        "Clustering on raw values let that single outlier dominate its own "
        "cluster, collapsing the Champions segment to one customer. Log1p "
        "transformation before scaling fixed this and produced the balanced, "
        "business-meaningful segments shown in this report."
    )
    pdf.sub("Keeping the deployed app lightweight")
    pdf.body(
        "The dashboard never reads the full 67MB cleaned transaction file. "
        "pipeline/segment.py pre-aggregates the top 15 products per segment at "
        "build time into a small CSV, which is what the deployed Streamlit app "
        "reads. Streamlit Community Cloud only runs dashboard/app.py, never the "
        "pipeline, so every file the dashboard depends on is generated ahead of "
        "time and committed to the repository."
    )
    pdf.sub("Stack")
    pdf.body("Python 3.12  |  pandas  |  scikit-learn  |  Plotly  |  Streamlit")

    # Section 6
    pdf.add_page()
    pdf.section("6.  Segment Results Snapshot")
    pdf.body(
        f"UCI Online Retail II, UK customers, December 2009 to December 2011. "
        f"{total_customers:,} customers, £{total_revenue:,.0f} total revenue."
    )

    for _, row in profiles.sort_values("pct_revenue", ascending=False).iterrows():
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*_SEGMENT_COLOR.get(row["segment"], _GREY))
        pdf.cell(
            0, 6,
            f"{row['segment']}  -  {int(row['customers']):,} customers "
            f"({row['pct_customers']:.1f}%)  -  {row['pct_revenue']:.1f}% of revenue",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*_GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(
            0, 5,
            f"Avg recency {int(row['avg_recency'])} days, "
            f"avg frequency {row['avg_frequency']:.1f} orders, "
            f"avg spend £{row['avg_monetary']:,.0f}",
        )
        pdf.ln(2)

    out = SAMPLES / "customer-segmentation-case-study.pdf"
    pdf.output(str(out))
    print(f"Case study saved -> {out}")


if __name__ == "__main__":
    build_case_study()
