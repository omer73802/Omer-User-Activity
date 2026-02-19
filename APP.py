import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Analytics App", layout="wide")

st.title("🚀 Omer Eliyahu Levi – Social Media Analytics App")
st.caption("Streamlit App | Social Media Users Dataset")

@st.cache_data
def load_data():
    df = pd.read_excel("Social Media Users.xlsx")
    # ננקה שמות עמודות מרווחים מיותרים
    df.columns = [c.strip() for c in df.columns]

    # נהפוך Date Joined לתאריך אם קיים
    if "Date Joined" in df.columns:
        df["Date Joined"] = pd.to_datetime(df["Date Joined"], errors="coerce")

    # נהפוך Daily Time Spent (min) למספר אם קיים
    if "Daily Time Spent (min)" in df.columns:
        df["Daily Time Spent (min)"] = pd.to_numeric(df["Daily Time Spent (min)"], errors="coerce")

    return df

df = load_data()

# ---- Sidebar Filters ----
st.sidebar.header("Filters")

# Platform
platform_col = "Platform" if "Platform" in df.columns else None
if platform_col:
    platforms = sorted(df[platform_col].dropna().unique())
    platform_sel = st.sidebar.multiselect("Platform", platforms, default=platforms)
else:
    platform_sel = None

# Country
country_col = "Country" if "Country" in df.columns else None
if country_col:
    countries = sorted(df[country_col].dropna().unique())
    country_sel = st.sidebar.multiselect("Country", countries, default=countries)
else:
    country_sel = None

# Verified
verified_col = "Verified Account" if "Verified Account" in df.columns else None
verified_only = st.sidebar.checkbox("Verified only", value=False)

# Date range (Date Joined)
date_col = "Date Joined" if "Date Joined" in df.columns else None
date_range = None
if date_col and df[date_col].notna().any():
    min_d = df[date_col].min().date()
    max_d = df[date_col].max().date()
    date_range = st.sidebar.date_input("Date joined range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

# Apply filters
filtered = df.copy()

if platform_sel is not None:
    filtered = filtered[filtered[platform_col].isin(platform_sel)]

if country_sel is not None:
    filtered = filtered[filtered[country_col].isin(country_sel)]

if verified_col and verified_only:
    # תומך גם True/False וגם Yes/No
    filtered = filtered[
        filtered[verified_col].astype(str).str.lower().isin(["true", "1", "yes", "verified"])
    ]

if date_col and date_range and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered[date_col] >= start) & (filtered[date_col] <= end)]

st.divider()

# ---- KPIs ----
time_col = "Daily Time Spent (min)" if "Daily Time Spent (min)" in filtered.columns else None

k1, k2, k3, k4 = st.columns(4)

k1.metric("Users (rows)", len(filtered))

if time_col and filtered[time_col].notna().any():
    k2.metric("Avg daily time (min)", round(filtered[time_col].mean(), 1))
    k3.metric("Median daily time (min)", round(filtered[time_col].median(), 1))
else:
    k2.metric("Avg daily time (min)", "N/A")
    k3.metric("Median daily time (min)", "N/A")

if verified_col and filtered[verified_col].notna().any():
    # אחוז verified בצורה גמישה
    v = filtered[verified_col].astype(str).str.lower().isin(["true", "1", "yes", "verified"])
    k4.metric("Verified %", f"{round(100 * v.mean(), 1)}%")
else:
    k4.metric("Verified %", "N/A")

st.divider()

# ---- Charts ----
left, right = st.columns(2)

with left:
    st.subheader("Daily time by platform")
    if platform_col and time_col and filtered[time_col].notna().any():
        fig1 = px.box(filtered, x=platform_col, y=time_col, points="outliers")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Missing columns for this chart (Platform / Daily Time Spent).")

with right:
    st.subheader("Top countries by average daily time")
    if country_col and time_col and filtered[time_col].notna().any():
        agg = (
            filtered.groupby(country_col, as_index=False)[time_col]
            .mean()
            .sort_values(time_col, ascending=False)
            .head(15)
        )
        fig2 = px.bar(agg, x=time_col, y=country_col, orientation="h")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Missing columns for this chart (Country / Daily Time Spent).")

st.subheader("Filtered data")
st.dataframe(filtered, use_container_width=True)

# Download filtered data
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data (CSV)", data=csv, file_name="filtered_social_media_users.csv", mime="text/csv")


