import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Analytics App", layout="wide")

st.title("🚀 Omer Eliyahu Levi – Social Media Analytics App")
st.caption("Streamlit App | Social Media Users Dataset")

@st.cache_data
def load_data():
    df = pd.read_excel("Social Media Users.xlsx")

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    # Parse Date Joined
    if "Date Joined" in df.columns:
        df["Date Joined"] = pd.to_datetime(df["Date Joined"], errors="coerce")

    # Parse Daily Time Spent
    if "Daily Time Spent (min)" in df.columns:
        df["Daily Time Spent (min)"] = pd.to_numeric(df["Daily Time Spent (min)"], errors="coerce")

    return df

df = load_data()

# ---------------- Tabs ----------------
tab_dashboard, tab_about_project, tab_why, tab_about_me = st.tabs(
    ["📊 Dashboard", "📁 About the Project", "💡 Why", "👤 About Me"]
)

# ===================== ABOUT PROJECT =====================
with tab_about_project:
    st.header("About the Dataset (Daily Social Media Active Users)")

    st.markdown(
        """
The dataset provides a broad view of user activity across social media platforms worldwide and simulates real-world usage patterns across **13 popular platforms** (e.g., Facebook, YouTube, WhatsApp, Instagram, TikTok, Telegram, Reddit, LinkedIn, and more).  
It contains **10,000 rows** with key fields that support analysis of demographics, engagement, and behavioral differences across countries and platforms.

**Main columns included:**
- **Platform** – the social platform where activity is tracked  
- **Owner** – the company that operates/owns the platform  
- **Primary Usage** – primary use-case (messaging, social networking, multimedia, professional networking, etc.)  
- **Country** – user location  
- **Daily Time Spent (min)** – daily minutes spent (core engagement metric)  
- **Verified Account** – whether the account is verified  
- **Date Joined** – the user’s registration date

This is a **synthetic (privacy-friendly)** dataset designed for analytics, research, dashboards, and machine learning experimentation — it contains **no real user data or personally identifiable information (PII)**.  
Since it simulates real-world patterns, insights should be interpreted carefully and treated as educational/experimental.
        """
    )

# ===================== WHY =====================
with tab_why:
    st.header("Why This Project Exists")

    st.markdown(
        """
This project was built as part of my professional growth journey in Data Analytics.

The goal was twofold:
1. **Improve my data analysis skills** — working with real datasets, defining KPIs, building visualizations, and extracting insights.  
2. **Build my first analytics web app** — strengthening my technical skills by developing an end-to-end application using Python and Streamlit.

During my job search process, I consistently work on hands-on projects that help me sharpen my skills, practice an end-to-end analytics workflow, and build a portfolio that reflects real capabilities.

This app is one step in that process — combining analytics, product thinking, and technical development.
        """
    )

# ===================== ABOUT ME =====================
with tab_about_me:
    st.header("About Me")

    st.markdown(
        """
I am a third-year Management & Information Systems (MIS) student with a strong focus on Data Analytics, currently in my final semester of my B.A. degree.

Throughout my studies and independent learning, I have been developing practical analytical and technical skills, including data analysis with **SQL, Excel, and Python**, as well as data visualization and dashboard development using **Power BI and Streamlit**.

My work emphasizes an end-to-end analytics workflow — from data cleaning and transformation to KPI definition, exploratory analysis, and insight-driven visualization. I actively build hands-on projects to strengthen both my analytical thinking and technical capabilities.

In parallel to my academic studies, I continuously expand my skill set through self-driven projects and professional training, including advanced coursework in data analysis tools and methodologies.

I am currently seeking an entry-level or student position as a **Data Analyst**, where I can contribute analytical value, grow within a data-driven environment, and continue refining my technical and business-oriented perspective.
        """
    )

# ===================== DASHBOARD =====================
with tab_dashboard:
    # ---- Sidebar Filters ----
    st.sidebar.header("Filters")

    platform_col = "Platform" if "Platform" in df.columns else None
    country_col = "Country" if "Country" in df.columns else None
    verified_col = "Verified Account" if "Verified Account" in df.columns else None
    date_col = "Date Joined" if "Date Joined" in df.columns else None
    time_col = "Daily Time Spent (min)" if "Daily Time Spent (min)" in df.columns else None

    # Platform filter
    if platform_col:
        platforms = sorted(df[platform_col].dropna().unique())
        platform_sel = st.sidebar.multiselect("Platform", platforms, default=platforms)
    else:
        platform_sel = None

    # Country filter
    if country_col:
        countries = sorted(df[country_col].dropna().unique())
        country_sel = st.sidebar.multiselect("Country", countries, default=countries)
    else:
        country_sel = None

    # Verified
    verified_only = st.sidebar.checkbox("Verified only", value=False)

    # Date range
    date_range = None
    if date_col and df[date_col].notna().any():
        min_d = df[date_col].min().date()
        max_d = df[date_col].max().date()
        date_range = st.sidebar.date_input(
            "Date joined range",
            value=(min_d, max_d),
            min_value=min_d,
            max_value=max_d
        )

    # Apply filters
    filtered = df.copy()

    if platform_sel is not None and platform_col:
        filtered = filtered[filtered[platform_col].isin(platform_sel)]

    if country_sel is not None and country_col:
        filtered = filtered[filtered[country_col].isin(country_sel)]

    if verified_col and verified_only:
        filtered = filtered[
            filtered[verified_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes", "verified"])
        ]

    if date_col and date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered[date_col] >= start) & (filtered[date_col] <= end)]

    st.divider()

    # ---- KPIs ----
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Users (rows)", len(filtered))

    if time_col and filtered[time_col].notna().any():
        k2.metric("Avg daily time (min)", round(filtered[time_col].mean(), 1))
        k3.metric("Median daily time (min)", round(filtered[time_col].median(), 1))
    else:
        k2.metric("Avg daily time (min)", "N/A")
        k3.metric("Median daily time (min)", "N/A")

    if verified_col and filtered[verified_col].notna().any():
        v = (
            filtered[verified_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes", "verified"])
        )
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
    st.download_button(
        "Download filtered data (CSV)",
        data=csv,
        file_name="filtered_social_media_users.csv",
        mime="text/csv"
    )
