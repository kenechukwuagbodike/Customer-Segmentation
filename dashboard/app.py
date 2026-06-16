import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Customer Segmentation",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parents[1]
DATA_DIR = BASE_DIR / "data"

# ---------------------------------------------------------------------------
# Colour palette: one colour per segment, used consistently across all charts
# ---------------------------------------------------------------------------
COLORS = {
    "Champions": "#2196F3",      # blue
    "Loyal": "#4CAF50",          # green
    "At-Risk": "#FF9800",        # orange
    "New Customers": "#9C27B0",  # purple
    "Lost": "#F44336",           # red
}

# Rules-based recommendations, one per segment
RECOMMENDATIONS = {
    "Champions": (
        "🏆 **Protect and reward.** These customers generate the bulk of your revenue. "
        "Give them VIP early access, referral bonuses, and exclusive bundles. "
        "Any churn here hurts disproportionately, so make them feel seen."
    ),
    "Loyal": (
        "💚 **Upsell and nudge upward.** High frequency, solid spend, they're one "
        "great experience away from Champion status. Introduce bundle deals, "
        "purchase milestone rewards, and personalised cross-sell recommendations."
    ),
    "At-Risk": (
        "⚠️ **Win-back before they're gone.** These customers used to buy regularly "
        "but have gone quiet. Send a personalised 'we miss you' email with a "
        "time-limited 15% discount. Act within the next 30 days."
    ),
    "New Customers": (
        "🌱 **Onboard into a second purchase.** They bought recently but haven't "
        "established a habit yet. Send a welcome sequence highlighting your best "
        "products and offer a second-purchase incentive within 30 days."
    ),
    "Lost": (
        "❄️ **One last shot, then retire.** Try a single high-value reactivation "
        "email. If there's no response, remove from active campaigns: continued "
        "outreach hurts deliverability and wastes budget."
    ),
}

# ---------------------------------------------------------------------------
# Data loading, cached so Streamlit doesn't reload on every interaction
# ---------------------------------------------------------------------------
@st.cache_data
def load_segments():
    return pd.read_csv(DATA_DIR / "segments.csv")

@st.cache_data
def load_profiles():
    return pd.read_csv(DATA_DIR / "segment_profiles.csv")

@st.cache_data
def load_elbow():
    return pd.read_csv(DATA_DIR / "elbow_data.csv")

@st.cache_data
def load_top_products():
    # Pre-aggregated per segment by pipeline/segment.py, avoids shipping the
    # full transaction log to the deployed app.
    return pd.read_csv(DATA_DIR / "segment_products.csv")

segments = load_segments()
profiles = load_profiles()
elbow_df = load_elbow()
top_products_all = load_top_products()

# ---------------------------------------------------------------------------
# Sidebar: segment filter (applies to scatter + deep-dive)
# ---------------------------------------------------------------------------
st.sidebar.image(
    "https://img.icons8.com/fluency/96/customer-insight.png", width=60
)
st.sidebar.title("Customer Segmentation")
st.sidebar.caption("UCI Online Retail II · UK customers · 2009–2011")
st.sidebar.divider()

all_segments = list(COLORS.keys())
selected_segments = st.sidebar.multiselect(
    "Show segments",
    options=all_segments,
    default=all_segments,
)

st.sidebar.divider()
st.sidebar.markdown(
    "**How to read this dashboard**\n\n"
    "Each customer is scored on Recency, Frequency, and Monetary value, "
    "then grouped into 5 segments by KMeans clustering.\n\n"
    "Use the tabs to explore segment profiles, drill into individual segments, "
    "or review how the cluster count was validated."
)

# Filter data to selected segments
seg_filtered = segments[segments["segment"].isin(selected_segments)]
prof_filtered = profiles[profiles["segment"].isin(selected_segments)]

# ---------------------------------------------------------------------------
# KPI row: headline numbers across the top
# ---------------------------------------------------------------------------
st.title("🧊 Customer Segmentation Dashboard")
st.caption(
    f"Analysing **{len(segments):,} UK customers** across "
    f"**{segments['segment'].nunique()} segments** · UCI Online Retail II"
)

total_customers = len(segments)
total_revenue = profiles["total_revenue"].sum()
top_seg = profiles.sort_values("pct_revenue", ascending=False).iloc[0]
avg_monetary = segments["monetary"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Customers", f"{total_customers:,}")
k2.metric("Total Revenue", f"£{total_revenue:,.0f}")
k3.metric("Avg Customer Spend", f"£{avg_monetary:,.0f}")
k4.metric(
    f"{top_seg['segment']} Revenue Share",
    f"{top_seg['pct_revenue']:.1f}%",
    help=f"The {top_seg['segment']} segment drives {top_seg['pct_revenue']:.1f}% of total revenue "
         f"despite being {top_seg['pct_customers']:.1f}% of customers.",
)

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Segment Overview", "🔍 Deep Dive", "📐 Model Validation"])

# ===========================  TAB 1 - OVERVIEW  ============================
with tab1:
    col_scatter, col_table = st.columns([3, 2], gap="large")

    with col_scatter:
        st.subheader("Recency vs Monetary by segment")
        st.caption(
            "Each dot is a customer. Segments in the top-left bought recently and spent the most. "
            "Note the log scale on spend: the range spans £3 to £608K."
        )

        fig_scatter = px.scatter(
            seg_filtered,
            x="recency",
            y="monetary",
            color="segment",
            color_discrete_map=COLORS,
            log_y=True,
            opacity=0.55,
            labels={
                "recency": "Days since last purchase (lower = more recent)",
                "monetary": "Total spend £ (log scale)",
                "segment": "Segment",
            },
            hover_data={"CustomerID": True, "frequency": True},
        )
        fig_scatter.update_traces(marker=dict(size=5))
        fig_scatter.update_layout(
            margin=dict(t=10, b=20, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        )
        st.plotly_chart(fig_scatter, width="stretch")

    with col_table:
        st.subheader("Segment profiles")
        display_cols = {
            "segment": "Segment",
            "customers": "Customers",
            "pct_customers": "% of Base",
            "avg_recency": "Avg Recency (days)",
            "avg_frequency": "Avg Frequency",
            "avg_monetary": "Avg Spend £",
            "pct_revenue": "% Revenue",
        }
        display_df = prof_filtered[list(display_cols)].rename(columns=display_cols)

        # Colour-code the % Revenue column
        st.dataframe(
            display_df.style.background_gradient(
                subset=["% Revenue"], cmap="Blues"
            ).format({
                "% of Base": "{:.1f}%",
                "Avg Spend £": "£{:,.0f}",
                "% Revenue": "{:.1f}%",
            }),
            width="stretch",
            hide_index=True,
        )

        # Revenue distribution bar chart
        st.subheader("Revenue by segment")
        fig_bar = px.bar(
            prof_filtered.sort_values("pct_revenue", ascending=True),
            x="pct_revenue",
            y="segment",
            orientation="h",
            color="segment",
            color_discrete_map=COLORS,
            labels={"pct_revenue": "% of total revenue", "segment": ""},
            text="pct_revenue",
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_bar.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=40),
        )
        st.plotly_chart(fig_bar, width="stretch")

# ===========================  TAB 2 - DEEP DIVE  ===========================
with tab2:
    chosen = st.selectbox(
        "Select a segment to explore",
        options=all_segments,
        format_func=lambda s: f"{s}  ({len(segments[segments['segment'] == s]):,} customers)",
    )

    seg_data = segments[segments["segment"] == chosen]
    seg_prof = profiles[profiles["segment"] == chosen].iloc[0]

    # Recommendation card
    st.info(RECOMMENDATIONS[chosen])

    # Segment stats
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Customers", f"{int(seg_prof['customers']):,}")
    m2.metric("Avg Recency", f"{int(seg_prof['avg_recency'])} days")
    m3.metric("Avg Frequency", f"{seg_prof['avg_frequency']:.1f} orders")
    m4.metric("Avg Spend", f"£{seg_prof['avg_monetary']:,.0f}")

    col_products, col_hist = st.columns(2, gap="large")

    with col_products:
        st.subheader(f"Top 10 products: {chosen}")

        # Pre-aggregated per segment by the pipeline, just filter and take top 10
        top_products = (
            top_products_all[top_products_all["segment"] == chosen]
            .sort_values("TotalValue", ascending=False)
            .head(10)[["Description", "TotalValue"]]
        )
        top_products.columns = ["Product", "Revenue £"]

        fig_products = px.bar(
            top_products.sort_values("Revenue £"),
            x="Revenue £",
            y="Product",
            orientation="h",
            color_discrete_sequence=[COLORS[chosen]],
            text="Revenue £",
        )
        fig_products.update_traces(
            texttemplate="£%{x:,.0f}",
            textposition="outside",
        )
        fig_products.update_xaxes(title="", showticklabels=False, showgrid=False)
        fig_products.update_yaxes(title="")
        fig_products.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=100),
            yaxis=dict(tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_products, width="stretch")

    with col_hist:
        st.subheader(f"Purchase frequency distribution: {chosen}")
        st.caption("How many orders did customers in this segment place?")

        # Compute bins manually so we can suppress "0" labels on empty bars
        counts, bin_edges = np.histogram(seg_data["frequency"].values, bins=15)
        x_labels = [
            f"{int(bin_edges[i]):.0f}–{int(bin_edges[i + 1]):.0f}"
            for i in range(len(counts))
        ]
        texts = [str(int(c)) if c > 0 else "" for c in counts]

        fig_hist = go.Figure(
            go.Bar(
                x=x_labels,
                y=counts,
                text=texts,
                textposition="outside",
                marker_color=COLORS[chosen],
            )
        )
        fig_hist.update_xaxes(title="Number of orders", tickangle=-45)
        fig_hist.update_yaxes(title="", showticklabels=False, showgrid=False)
        fig_hist.update_layout(
            showlegend=False,
            margin=dict(t=30, b=60, l=10, r=10),
            bargap=0.1,
        )
        st.plotly_chart(fig_hist, width="stretch")

# ========================  TAB 3 - MODEL VALIDATION  ======================
with tab3:
    st.subheader("How we chose k = 5 clusters")
    st.caption(
        "We tested k from 2 to 10. The elbow shows where adding more clusters "
        "gives diminishing returns on within-cluster variance. The silhouette "
        "score confirms k=5 produces well-separated segments."
    )

    col_elbow, col_sil = st.columns(2, gap="large")

    with col_elbow:
        st.markdown("**Elbow method: inertia vs k**")
        fig_elbow, ax = plt.subplots(figsize=(5, 3))
        ax.plot(elbow_df["k"], elbow_df["inertia"], marker="o", color="#2196F3", linewidth=2)
        ax.axvline(x=5, color="#FF9800", linestyle="--", linewidth=1.5, label="k=5 chosen")
        ax.set_xlabel("Number of clusters (k)")
        ax.set_ylabel("Inertia")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        fig_elbow.tight_layout()
        st.pyplot(fig_elbow, width="stretch")

    with col_sil:
        st.markdown("**Silhouette score vs k**")
        fig_sil, ax2 = plt.subplots(figsize=(5, 3))
        ax2.plot(elbow_df["k"], elbow_df["silhouette"], marker="o", color="#4CAF50", linewidth=2)
        ax2.axvline(x=5, color="#FF9800", linestyle="--", linewidth=1.5, label="k=5 chosen")
        ax2.set_xlabel("Number of clusters (k)")
        ax2.set_ylabel("Silhouette score")
        ax2.legend()
        ax2.grid(axis="y", alpha=0.3)
        fig_sil.tight_layout()
        st.pyplot(fig_sil, width="stretch")

    st.caption(
        f"Final model silhouette score: **{elbow_df[elbow_df['k']==5]['silhouette'].values[0]:.3f}** · "
        "Scores above 0.3 indicate meaningful cluster separation for this type of retail data."
    )
