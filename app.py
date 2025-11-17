import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Sports Deal Tracker", page_icon="📊", layout="wide")

@st.cache_data
def load_deals(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Make sure key columns exist even if blank
    for col in [
        "property", "sport", "rights_type", "deal_name", "sponsor_brand",
        "sponsor_category", "region", "country", "currency",
        "deal_value_usd", "start_date", "end_date"
    ]:
        if col not in df.columns:
            df[col] = None

    # Types
    df["deal_value_usd"] = pd.to_numeric(df["deal_value_usd"], errors="coerce")
    for c in ["start_date", "end_date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df

st.title("📊 Sports Deal Tracker (MVP)")

st.sidebar.header("Filters")

# Load data
df = load_deals("data/sample_deals.csv")

# Sidebar filters
sports = sorted(df["sport"].dropna().unique().tolist())
sport_sel = st.sidebar.multiselect("Sport", options=sports, default=[])

rights_types = sorted(df["rights_type"].dropna().unique().tolist())
rights_sel = st.sidebar.multiselect("Rights type", options=rights_types, default=[])

regions = sorted(df["region"].dropna().unique().tolist())
region_sel = st.sidebar.multiselect("Region", options=regions, default=[])

value_min = float(df["deal_value_usd"].min() or 0)
value_max = float(df["deal_value_usd"].max() or 0)
value_range = st.sidebar.slider(
    "Deal value (USD)",
    min_value=0.0,
    max_value=max(value_max, 1.0),
    value=(0.0, max(value_max, 1.0)),
)

active_only = st.sidebar.checkbox("Active today only", value=False)

# Apply filters
f = df.copy()

if sport_sel:
    f = f[f["sport"].isin(sport_sel)]

if rights_sel:
    f = f[f["rights_type"].isin(rights_sel)]

if region_sel:
    f = f[f["region"].isin(region_sel)]

f = f[
    (f["deal_value_usd"].fillna(0) >= value_range[0])
    & (f["deal_value_usd"].fillna(0) <= value_range[1])
]

if active_only:
    today = pd.to_datetime(date.today())
    f = f[
        (f["start_date"] <= today)
        & (f["end_date"] >= today)
    ]

st.subheader("Deals table")
st.dataframe(f, use_container_width=True)

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Deals shown", len(f))
with col2:
    st.metric("Total value (USD)", f["deal_value_usd"].sum())
with col3:
    avg = f["deal_value_usd"].mean() if len(f) else 0
    st.metric("Avg deal (USD)", round(avg, 2))

st.markdown("---")

# Charts
if not f.empty:
    col_a, col_b = st.columns(2)

    with col_a:
        by_cat = (
            f.groupby("sponsor_category", as_index=False)["deal_value_usd"]
            .sum()
            .sort_values("deal_value_usd", ascending=False)
        )
        fig_cat = px.bar(
            by_cat,
            x="sponsor_category",
            y="deal_value_usd",
            title="Total value by sponsor category",
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_b:
        by_brand = (
            f.groupby("sponsor_brand", as_index=False)["deal_value_usd"]
            .sum()
            .sort_values("deal_value_usd", ascending=False)
            .head(10)
        )
        fig_brand = px.bar(
            by_brand,
            x="sponsor_brand",
            y="deal_value_usd",
            title="Top 10 brands by deal value",
        )
        st.plotly_chart(fig_brand, use_container_width=True)

    by_region = (
        f.groupby("region", as_index=False)["deal_value_usd"]
        .sum()
        .sort_values("deal_value_usd", ascending=False)
    )
    fig_region = px.bar(
        by_region,
        x="region",
        y="deal_value_usd",
        title="Total value by region",
    )
    st.plotly_chart(fig_region, use_container_width=True)
else:
    st.info("No deals match the current filters.")
