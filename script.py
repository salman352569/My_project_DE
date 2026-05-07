"""
Bike lakehouse sales dashboard
runnig with streamlit 

"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Bike Lakehouse Dashboard",
    page_icon=" 🚴",
    layout="wide",
    initial_sidebar_state = "expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main {background-color:#f8f9fa;}
    .st.metric {background:white;border-radius: 12px; padding: 16px; border: 1px solid #e9ecef;}
    .metric-delta-positive{color: #2ecc71 !important}
    div[data-testid="metric-container"]{
            background: white;
            border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 24px 0 12px;
    }
</style> }
"""
,unsafe_allow_html =True)
# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    fact=pd.read_csv("data/fact_sales-2026-05-06.csv",   parse_dates=["order_date","ship_date","due_date"])

    cust=pd.read_csv("data/dim_customers-2026-05-06.csv",  parse_dates=["birthdate","create_date"])

    prod=pd.read_csv("data/dim_products-2026-05-06.csv",  parse_dates=["start_date"])

    # clean country
    cust["country"] = cust["country"].str.strip().str.lower()

    # join all tables into one flat dataframe 
    df =(
        fact
        .merge(prod, on="product_key", how="left")
        .merge(cust, on="customer_key",how="left" )
    )

    #derived columns 
    df["year"]  = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    df["month_dt"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    df["ship_days"] =(df["ship_date"] - df["order_date"]).dt.days
    df["late_flag"] =df["ship_date"] > df["due_date"]
    df["age"] =df["order_date"].dt.year - pd.to_datetime(df["birthdate"]).dt.year

    # Age Bucket 
    def age_bucket(a):
        if a < 30: return "under 30"
        elif a < 40: return "30-39"
        elif a < 50: return "40–49"
        elif a < 60: return "50–59"
        else:        return "60+"
    df["age_group"]= df["age"].apply(age_bucket)

    return df ,fact,cust,prod
df,fact,cust,prod =load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=60)
    st.title("🚴 Bike Lakehouse")
    st.markdown("----")

    st.markdown("### Filters ")

    years=sorted(df["year"].dropna().unique())
    sel_years= st.multiselect("year",years,default=years)

    countries=sorted(df["country"].dropna().unique())
    sel_countries=st.multiselect("country",countries,default=countries)

    categories= sorted(df["category"].dropna().unique())
    sel_categories=st.multiselect("category",categories,default=categories)

    product_lines=sorted(df["product_line"].dropna().unique())
    sel_lines=st.multiselect("product line",product_lines,default=product_lines)

    st.markdown("-----")
    st.caption("Data: 2010 - 2014  | 89,833 orders")

# ── Apply filters ─────────────────────────────────────────────────────────────
mask = (
    df["year"].isin(sel_years) &
    df["country"].isin(sel_countries) &
    df["category"].isin(sel_categories) &
    df["product_line"].isin(sel_lines)
)
fdf = df[mask].copy()
 
# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🚴 Bike Sales Performance Dashboard")
st.caption("Adventure Works Lakehouse  ·  Explore sales, products, customers & delivery")
 
# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Key metrics</div>', unsafe_allow_html=True)

total_rev = fdf["sales_amount"].sum()
total_orders = fdf["order_number"].nunique()
avg_order = fdf.groupby("order_number")["sales_amount"].sum().mean()
avg_ship = fdf["ship_days"].mean()
late_pct = fdf["late_flag"].mean() * 100
unique_cust= fdf["customer_key"].nunique()

col1,col2,col3,col4,col5,col6=st.columns(6)
col1.metric("Total Revenue",   f"${total_rev:,.0f}")
col2.metric("Total orders", f"{total_orders:,}")
col3.metric("🛒 Avg Order Value", f"${avg_order:,.0f}")
col4.metric("🚚 Avg Ship Days",   f"{avg_ship:.1f}d")
col5.metric("⚠️ Late Delivery %", f"{late_pct:.1f}%")
col6.metric("👤 Unique Customers",f"{unique_cust:,}")

st.markdown("-----")

# ═══════════════════════════════════════════════════════════
# TAB LAYOUT
# ═══════════════════════════════════════════════════════════

tab1,tab2,tab3,tab4= st.tabs([
    "📈 Sales Trends",
    "🏆 Products",
    "👥 Customers",
    "🚚 Delivery",
])
# ─────────────────────────────────────────────────────────
# TAB 1 — SALES TRENDS
# ─────────────────────────────────────────────────────────

with tab1:
    st.markdown('<div class="section-header">Revenue Over Time</div>',unsafe_allow_html=True)

    # Monthly revenue line chart
    monthly=(
        fdf.groupby("month_dt")["sales_amount"]
        .sum()
        .reset_index()
        .rename(columns={"sales_amount":"revenue"})
    )
    fig_line=px.line(
        monthly,x="month_dt", y="revenue",
        labels={"month_dt":"Month","revenue":"Revenue ($)"},
        template="plotly_white",
        color_discrete_sequence=["#2563eb"],
    )
    fig_line.update_traces(line_width=2.5,mode="lines+markers",marker_size=4)
    fig_line.update_layout(height=300,margin=dict(t=10,b=10))
    st.plotly_chart(fig_line,use_container_width=True)

    col_a,col_b=st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">Revenue by country</div>', unsafe_allow_html=True)
        by_country = (
            fdf.groupby("country")["sales_amount"].sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig_country = px.bar(
            by_country, x="sales_amount", y="country", orientation="h",
            labels={"sales_amount": "Revenue ($)", "country": ""},
            template="plotly_white",
            color_discrete_sequence=["#3b82f6"],
        )
        fig_country.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_country, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-header">Revenue by year</div>', unsafe_allow_html=True)
        by_year = fdf.groupby("year")["sales_amount"].sum().reset_index()
        fig_year = px.bar(
            by_year, x="year", y="sales_amount",
            labels={"sales_amount": "Revenue ($)", "year": "Year"},
            template="plotly_white",
            color_discrete_sequence=["#6366f1"],
            text_auto=".2s",
        )
        fig_year.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_year, use_container_width=True)

# ─────────────────────────────────────────────────────────
# TAB 2 — PRODUCTS
# ─────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)
 
    with col_a:
        st.markdown('<div class="section-header">Revenue by category</div>', unsafe_allow_html=True)
        by_cat = fdf.groupby("category")["sales_amount"].sum().reset_index()
        fig_cat = px.pie(
            by_cat, values="sales_amount", names="category",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_white",
        )
        fig_cat.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig_cat, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-header">Revenue by product line</div>', unsafe_allow_html=True)
        by_line = fdf.groupby("product_line")["sales_amount"].sum().reset_index().sort_values("sales_amount", ascending=False)
        fig_line2 = px.bar(
            by_line, x="product_line", y="sales_amount",
            labels={"sales_amount": "Revenue ($)", "product_line": "Product Line"},
            template="plotly_white",
            color_discrete_sequence=["#10b981"],
            text_auto=".2s",
        )
        fig_line2.update_layout(height=300, margin=dict(t=10, b=10))
        st.plotly_chart(fig_line2, use_container_width=True)
 
    st.markdown('<div class="section-header">Top 15 products by revenue</div>', unsafe_allow_html=True)
    top_prod = (
        fdf.groupby("product_name")
        .agg(revenue=("sales_amount","sum"), orders=("order_number","nunique"), units=("quantity","sum"))
        .sort_values("revenue", ascending=False)
        .head(15)
        .reset_index()
    )
    fig_top = px.bar(
        top_prod, x="revenue", y="product_name", orientation="h",
        labels={"revenue": "Revenue ($)", "product_name": ""},
        template="plotly_white",
        color_discrete_sequence=["#f59e0b"],
    )
    fig_top.update_layout(height=400, margin=dict(t=10, b=10), yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_top, use_container_width=True)
 
    # Category × Year heatmap
    st.markdown('<div class="section-header">Category revenue heatmap by year</div>', unsafe_allow_html=True)
    heat_df = fdf.groupby(["year","category"])["sales_amount"].sum().reset_index()
    heat_pivot = heat_df.pivot(index="category", columns="year", values="sales_amount").fillna(0)
    fig_heat = px.imshow(
        heat_pivot,
        labels=dict(x="Year", y="Category", color="Revenue"),
        color_continuous_scale="Blues",
        template="plotly_white",
        text_auto=".2s",
    )
    fig_heat.update_layout(height=250, margin=dict(t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)
 
 
# ─────────────────────────────────────────────────────────
# TAB 3 — CUSTOMERS
# ─────────────────────────────────────────────────────────
with tab3:
    col_a, col_b = st.columns(2)
 
    with col_a:
        st.markdown('<div class="section-header">Revenue by gender</div>', unsafe_allow_html=True)
        by_gender = fdf.groupby("gender")["sales_amount"].sum().reset_index()
        fig_g = px.pie(
            by_gender, values="sales_amount", names="gender",
            hole=0.4,
            color_discrete_sequence=["#6366f1","#f472b6"],
            template="plotly_white",
        )
        fig_g.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_g, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-header">Revenue by marital status</div>', unsafe_allow_html=True)
        by_ms = fdf.groupby("martial_status")["sales_amount"].sum().reset_index()
        fig_ms = px.bar(
            by_ms, x="martial_status", y="sales_amount",
            labels={"sales_amount": "Revenue ($)", "martial_status": ""},
            template="plotly_white",
            color_discrete_sequence=["#14b8a6"],
            text_auto=".2s",
        )
        fig_ms.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_ms, use_container_width=True)
 
    col_c, col_d = st.columns(2)
 
    with col_c:
        st.markdown('<div class="section-header">Revenue by age group</div>', unsafe_allow_html=True)
        by_age = (
            fdf.groupby("age_group")["sales_amount"].sum()
            .reindex(["Under 30","30–39","40–49","50–59","60+"])
            .reset_index()
        )
        fig_age = px.bar(
            by_age, x="age_group", y="sales_amount",
            labels={"sales_amount": "Revenue ($)", "age_group": "Age group"},
            template="plotly_white",
            color_discrete_sequence=["#f97316"],
            text_auto=".2s",
        )
        fig_age.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_age, use_container_width=True)
 
    with col_d:
        st.markdown('<div class="section-header">Top 10 customers by spend</div>', unsafe_allow_html=True)
        top_cust = (
            fdf.groupby(["customer_key","first_name","last_name","country"])["sales_amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top_cust["name"] = top_cust["first_name"] + " " + top_cust["last_name"]
        fig_cust = px.bar(
            top_cust, x="sales_amount", y="name", orientation="h",
            labels={"sales_amount": "Revenue ($)", "name": ""},
            template="plotly_white",
            color_discrete_sequence=["#8b5cf6"],
        )
        fig_cust.update_layout(height=280, margin=dict(t=10, b=10), yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_cust, use_container_width=True)
 
    # Gender × Category breakdown
    st.markdown('<div class="section-header">Category preference by gender</div>', unsafe_allow_html=True)
    gender_cat = fdf.groupby(["gender","category"])["sales_amount"].sum().reset_index()
    fig_gc = px.bar(
        gender_cat, x="category", y="sales_amount", color="gender",
        barmode="group",
        labels={"sales_amount": "Revenue ($)", "category": ""},
        template="plotly_white",
        color_discrete_sequence=["#6366f1","#f472b6"],
    )
    fig_gc.update_layout(height=300, margin=dict(t=10, b=10))
    st.plotly_chart(fig_gc, use_container_width=True)
 
 
# ─────────────────────────────────────────────────────────
# TAB 4 — DELIVERY
# ─────────────────────────────────────────────────────────
with tab4:
    col_a, col_b = st.columns(2)
 
    with col_a:
        st.markdown('<div class="section-header">On-time vs late deliveries</div>', unsafe_allow_html=True)
        late_summary = fdf["late_flag"].value_counts().reset_index()
        late_summary.columns = ["Status", "Count"]
        late_summary["Status"] = late_summary["Status"].map({True: "Late", False: "On Time"})
        fig_late = px.pie(
            late_summary, values="Count", names="Status",
            hole=0.45,
            color_discrete_sequence=["#ef4444","#22c55e"],
            template="plotly_white",
        )
        fig_late.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_late, use_container_width=True)
 
    with col_b:
        st.markdown('<div class="section-header">Avg ship days by country</div>', unsafe_allow_html=True)
        ship_country = fdf.groupby("country")["ship_days"].mean().sort_values().reset_index()
        fig_ship = px.bar(
            ship_country, x="ship_days", y="country", orientation="h",
            labels={"ship_days": "Avg days to ship", "country": ""},
            template="plotly_white",
            color_discrete_sequence=["#0ea5e9"],
        )
        fig_ship.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_ship, use_container_width=True)
 
    st.markdown('<div class="section-header">Avg ship days by product category</div>', unsafe_allow_html=True)
    ship_cat = fdf.groupby("category")["ship_days"].mean().reset_index().sort_values("ship_days", ascending=False)
    fig_sc = px.bar(
        ship_cat, x="category", y="ship_days",
        labels={"ship_days": "Avg days to ship", "category": ""},
        template="plotly_white",
        color_discrete_sequence=["#f97316"],
        text_auto=".1f",
    )
    fig_sc.update_layout(height=280, margin=dict(t=10, b=10))
    st.plotly_chart(fig_sc, use_container_width=True)
 
    # Distribution of ship days
    st.markdown('<div class="section-header">Distribution of shipping days</div>', unsafe_allow_html=True)
    fig_hist = px.histogram(
        fdf[fdf["ship_days"].between(0,30)],
        x="ship_days", nbins=30,
        labels={"ship_days": "Days from order to ship", "count": "Orders"},
        template="plotly_white",
        color_discrete_sequence=["#6366f1"],
    )
    fig_hist.update_layout(height=260, margin=dict(t=10, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)
 
 
# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Bike Lakehouse Dashboard · Built with Streamlit & Plotly · Data: Adventure Works 2010–2014")
