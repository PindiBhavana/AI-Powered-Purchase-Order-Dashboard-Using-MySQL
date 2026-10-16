
import os

import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_db_config():
    config = {
        "host": st.secrets.get("DB_HOST", os.getenv("DB_HOST", "localhost")),
        "port": int(st.secrets.get("DB_PORT", os.getenv("DB_PORT", "3306"))),
        "user": st.secrets.get("DB_USER", os.getenv("DB_USER", "")),
        "password": st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
        "database": st.secrets.get("DB_NAME", os.getenv("DB_NAME", "")),
    }

    missing = [
        key for key in ["user", "password", "database"]
        if not config[key]
    ]

    if missing:
        names = {
            "user": "DB_USER",
            "password": "DB_PASSWORD",
            "database": "DB_NAME",
        }
        raise ValueError(
            "Missing database environment variables: "
            + ", ".join(names[key] for key in missing)
        )

    return config


st.set_page_config(
    page_title="Purchase Order Dashboard",
    page_icon="📊",
    layout="wide",
)


# Professional Sage Green + Pastel Pink Theme
st.markdown(
    """
<style>
    .stApp { background-color: #FAF8F3; color: #344337; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem; max-width: 1600px; }
    h1, h2, h3 { color: #3B5B42; font-weight: 750; }
    h1 { letter-spacing: -0.6px; }
    div[data-testid="stMetric"] { background-color: #FFFFFF; border: 1px solid #E5E8DF; border-radius: 14px; padding: 18px 20px; box-shadow: 0 4px 12px rgba(59, 91, 66, 0.07); text-align: center !important; width: 100%; }
    div[data-testid="stMetricLabel"] { color: #68766A; font-size: 14px; font-weight: 600; width: 100%; display: flex; justify-content: center !important; align-items: center; text-align: center !important; }
    div[data-testid="stMetricValue"] { color: #3B5B42; font-weight: 750; width: 100%; justify-content: center !important; text-align: center !important; }
    [data-testid="stMetric"] > div { align-items: center !important; text-align: center !important; }
    div[data-testid="stDataFrame"] { background-color: #FFFFFF; border: 1px solid #E5E8DF; border-radius: 12px; padding: 5px; }
    section[data-testid="stSidebar"] { background-color: #3B5B42; }
    section[data-testid="stSidebar"] * { color: #FFFFFF; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { border-radius: 9px; border-color: #D7DFD3; }
    .stButton > button { background-color: #3B5B42; color: #FFFFFF; border: 1px solid #3B5B42; border-radius: 9px; font-weight: 600; transition: all 0.2s ease; }
    .stButton > button:hover { background-color: #2E4934; color: #FFFFFF; border-color: #2E4934; }
    .stDownloadButton > button { background-color: #F6DCE5; color: #744458; border: 1px solid #E8C4D1; border-radius: 9px; font-weight: 600; }
    .stDownloadButton > button:hover { background-color: #EFCBD8; color: #5E3547; border-color: #DFAFC1; }
    a { color: #3B5B42; }
    hr { border-color: #E5E8DF; margin-top: 1.5rem; margin-bottom: 1.5rem; }
    .stCaption { color: #68766A; }
    div[data-testid="stAlert"] { border-radius: 10px; }
    div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border-color: #D7DFD3 !important; border-radius: 9px !important; }
    div[data-baseweb="popover"], div[role="listbox"] { background-color: #FFFFFF !important; }
    div[role="option"] { background-color: #FFFFFF !important; color: #344337 !important; }
    div[role="option"]:hover, div[role="option"][aria-selected="true"] { background-color: #F6DCE5 !important; color: #3B5B42 !important; }
    [data-baseweb="tag"] { background: #F6DCE5 !important; background-color: #F6DCE5 !important; border: 1px solid #E8C4D1 !important; border-radius: 7px !important; box-shadow: none !important; }
    [data-baseweb="tag"] span, [data-baseweb="tag"] div, [data-baseweb="tag"] svg { color: #3B5B42 !important; fill: #3B5B42 !important; stroke: #3B5B42 !important; }
    [data-baseweb="tag"]:hover { background: #F6DCE5 !important; background-color: #F6DCE5 !important; }
</style>
""",
    unsafe_allow_html=True,
)

CHART_GREEN = "#6F8F72"
CHART_PINK = "#F6DCE5"
CHART_DARK_GREEN = "#3B5B42"
CHART_DUSTY_PINK = "#E8C4D1"
CHART_COLORS = [CHART_GREEN, CHART_PINK, CHART_DARK_GREEN, CHART_DUSTY_PINK]


def style_chart(fig, height=400):
    """Apply the shared Sage Green and Pastel Pink chart theme."""
    fig.update_layout(
        template="plotly_white",
        colorway=CHART_COLORS,
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", size=12, color="#344337"),
        title=dict(font=dict(size=17, color=CHART_DARK_GREEN), x=0.02, xanchor="left"),
        margin=dict(l=25, r=25, t=65, b=45),
        hoverlabel=dict(bgcolor="#F6DCE5", bordercolor="#E8C4D1", font=dict(color="#3B5B42", size=12)),
        legend=dict(bgcolor="rgba(255,255,255,0)", font=dict(color="#344337")),
    )
    fig.update_xaxes(showline=True, linecolor="#D7DFD3", tickfont=dict(color="#344337"), automargin=True)
    fig.update_yaxes(showline=False, showgrid=True, gridcolor="#E8EDE6", zerolinecolor="#D7DFD3", tickfont=dict(color="#344337"), automargin=True)
    return fig


def delivery_classification(data, today):
    """Return eligibility and delivery-status masks aligned to data's index."""
    eligible = ~data["po_status"].astype(str).str.contains(
        r"cancelled|draft|pending approval", case=False, na=False, regex=True
    )
    delivered = data["actual_delivery_date"].notna() & eligible
    overdue = (
        data["actual_delivery_date"].isna()
        & data["delivery_date"].notna()
        & (data["delivery_date"] < today)
        & eligible
    )
    pending = data["actual_delivery_date"].isna() & ~overdue & eligible
    return eligible, delivered, pending, overdue


# Centered dashboard heading
st.markdown("""
<div style="text-align: center; padding: 10px 0 25px 0;">
    <h1 style="
        text-align: center;
        color: #3B5B42;
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 10px;
    ">
        📊 AI-Powered Purchase Order Dashboard
    </h1>
    <p style="
        text-align: center;
        color: #6B756B;
        font-size: 1.1rem;
        margin-top: 0;
    ">
        Purchase order analysis and spending intelligence
    </p>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data():
    """Load purchase orders and related vendor/department information from MySQL."""
   
    
    conn = mysql.connector.connect(**get_db_config())

    try:
        query = """
            SELECT
                po.po_id, po.po_number, po.vendor_id, po.department_id,
                po.po_date, po.delivery_date, po.actual_delivery_date,
                po.approval_date, po.item_description, po.quantity,
                po.unit_price, po.total_po_amount, po.po_status,
                po.payment_terms, po.currency, po.created_at,
                v.vendor_name, d.department_name
            FROM purchase_orders po
            LEFT JOIN vendors v ON po.vendor_id = v.vendor_id
            LEFT JOIN departments d ON po.department_id = d.department_id
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()



try:
    df = load_data()

    if df.empty:
        st.warning("No purchase orders found.")
        st.stop()

    for date_column in ["po_date", "delivery_date", "actual_delivery_date", "approval_date", "created_at"]:
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

    df["total_po_amount"] = pd.to_numeric(df["total_po_amount"], errors="coerce").fillna(0)
    df["po_status"] = df["po_status"].fillna("Unknown").astype(str)

    departments = sorted(df["department_name"].dropna().unique().tolist())
    vendors = sorted(df["vendor_name"].dropna().unique().tolist())
    statuses = sorted(df["po_status"].dropna().unique().tolist())
    date_min = df["po_date"].min()
    date_max = df["po_date"].max()
    delivery_options = ["Delivered", "Pending Delivery", "Potentially Overdue"]

    # Initialize filter widgets once per session.
    if "_filters_initialized" not in st.session_state:
        st.session_state["top_department_slicer"] = departments.copy()
        st.session_state["top_vendor_slicer"] = vendors.copy()
        st.session_state["top_status_slicer"] = statuses.copy()
        st.session_state["top_delivery_slicer"] = delivery_options.copy()
        if pd.notna(date_min) and pd.notna(date_max):
            st.session_state["top_date_slicer"] = (date_min.date(), date_max.date())
        st.session_state["_filters_initialized"] = True

    def reset_filters():
        st.session_state["top_department_slicer"] = departments.copy()
        st.session_state["top_vendor_slicer"] = vendors.copy()
        st.session_state["top_status_slicer"] = statuses.copy()
        st.session_state["top_delivery_slicer"] = delivery_options.copy()
        if pd.notna(date_min) and pd.notna(date_max):
            st.session_state["top_date_slicer"] = (date_min.date(), date_max.date())

    st.subheader("Dashboard Filters")
    st.button("🔄 Reset Filters", on_click=reset_filters, key="reset_filters_button")

    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
    with filter_col1:
        selected_departments = st.multiselect("Department", options=departments, key="top_department_slicer")
    with filter_col2:
        selected_vendors = st.multiselect("Vendor", options=vendors, key="top_vendor_slicer")
    with filter_col3:
        selected_statuses = st.multiselect("PO Status", options=statuses, key="top_status_slicer")
    with filter_col4:
        if pd.notna(date_min) and pd.notna(date_max):
            selected_dates = st.date_input(
                "PO Date Range", min_value=date_min.date(), max_value=date_max.date(), key="top_date_slicer"
            )
        else:
            selected_dates = ()
    with filter_col5:
        delivery_status = st.multiselect("Delivery Status", options=delivery_options, key="top_delivery_slicer")

    # Apply department, vendor, PO status, and date filters first.
    filtered = df.copy()
    filtered = filtered[filtered["department_name"].isin(selected_departments)] if selected_departments else filtered.iloc[0:0]
    filtered = filtered[filtered["vendor_name"].isin(selected_vendors)] if selected_vendors else filtered.iloc[0:0]
    filtered = filtered[filtered["po_status"].isin(selected_statuses)] if selected_statuses else filtered.iloc[0:0]

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered = filtered[filtered["po_date"].dt.date.between(start_date, end_date)]

    # Keep a copy before the delivery slicer for vendor performance and concentration.
    vendor_analysis_data = filtered.copy()
    today = pd.Timestamp.today().normalize()

    eligible_status, is_delivered, is_pending, is_overdue = delivery_classification(filtered, today)
    delivered_count = int(is_delivered.sum())
    pending_delivery = int(is_pending.sum())
    overdue_count = int(is_overdue.sum())

    # Delivery slicer filters the main order-level dashboard visuals.
    delivery_mask = pd.Series(False, index=filtered.index)
    if "Delivered" in delivery_status:
        delivery_mask |= is_delivered
    if "Pending Delivery" in delivery_status:
        delivery_mask |= is_pending
    if "Potentially Overdue" in delivery_status:
        delivery_mask |= is_overdue
    filtered = filtered.loc[delivery_mask].copy()

    # KPI cards: main totals follow all slicers; delivery KPIs show the breakdown
    # before the delivery slicer, so users can see the full status distribution.
    total_orders = len(filtered)
    total_value = filtered["total_po_amount"].sum()
    average_value = total_value / total_orders if total_orders else 0
    vendor_count = filtered["vendor_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Purchase Orders", f"{total_orders:,}")
    col2.metric("Total PO Value", f"₹{total_value:,.2f}")
    col3.metric("Average PO Value", f"₹{average_value:,.2f}")
    col4.metric("Vendors", f"{vendor_count:,}")
    col5, col6, col7 = st.columns(3)
    col5.metric("Delivered Orders", f"{delivered_count:,}")
    col6.metric("Pending Delivery", f"{pending_delivery:,}")
    col7.metric("Overdue Deliveries", f"{overdue_count:,}")

    st.divider()

    # Executive Insights
    st.subheader("📌 Executive Insights")
    if not filtered.empty:
        total_spending = filtered["total_po_amount"].sum()
        top_vendor_data = filtered.groupby("vendor_name")["total_po_amount"].sum().sort_values(ascending=False)
        top_department_data = filtered.groupby("department_name")["total_po_amount"].sum().sort_values(ascending=False)
        insight_col1, insight_col2 = st.columns(2)
        with insight_col1:
            if not top_vendor_data.empty:
                st.info(f"**Highest-spending vendor:** {top_vendor_data.index[0]} (₹{top_vendor_data.iloc[0]:,.0f})")
            if not top_department_data.empty:
                st.info(f"**Highest-spending department:** {top_department_data.index[0]} (₹{top_department_data.iloc[0]:,.0f})")
        with insight_col2:
            st.info(f"**Purchase orders in current selection:** {len(filtered):,}")
            st.info(f"**Total purchase order value:** ₹{total_spending:,.0f}")
    else:
        st.info("No purchase orders match the current filters.")

    # Spending by Department and Vendor
    left, right = st.columns(2)
    with left:
        st.subheader("Spending by Department")
        dept_data = filtered.groupby("department_name", as_index=False)["total_po_amount"].sum().sort_values("total_po_amount", ascending=False)
        if not dept_data.empty:
            fig = px.bar(dept_data, x="department_name", y="total_po_amount", labels={"department_name": "Department", "total_po_amount": "Purchase Order Value (₹)"}, title="Purchase Order Value by Department", color_discrete_sequence=[CHART_GREEN], text="total_po_amount")
            fig.update_traces(marker_line_color=CHART_DARK_GREEN, marker_line_width=0.7, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
            fig.update_layout(xaxis_title="Department", yaxis_title="Purchase Order Value (₹)")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        else:
            st.info("No department data for these filters.")

    with right:
        st.subheader("Spending by Vendor")
        vendor_data = filtered.groupby("vendor_name", as_index=False)["total_po_amount"].sum().sort_values("total_po_amount", ascending=False)
        if not vendor_data.empty:
            fig = px.bar(vendor_data, x="vendor_name", y="total_po_amount", title="Purchase Order Value by Vendor", labels={"vendor_name": "Vendor", "total_po_amount": "Purchase Order Value (₹)"}, color_discrete_sequence=[CHART_PINK], text="total_po_amount")
            fig.update_traces(marker_line_color=CHART_DUSTY_PINK, marker_line_width=0.7, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
            fig.update_layout(xaxis_title="Vendor", yaxis_title="Purchase Order Value (₹)", xaxis_tickangle=-35)
            st.plotly_chart(style_chart(fig), use_container_width=True)
        else:
            st.info("No vendor data for these filters.")

    # Department-wise Average PO Value
    st.subheader("🏢 Department-wise Average PO Value")
    department_avg = filtered.groupby("department_name", as_index=False).agg(average_po_value=("total_po_amount", "mean"), total_orders=("po_number", "count")).sort_values("average_po_value", ascending=False)
    if not department_avg.empty:
        fig = px.bar(department_avg, x="department_name", y="average_po_value", title="Department-wise Average PO Value", labels={"department_name": "Department", "average_po_value": "Average PO Value (₹)"}, color_discrete_sequence=[CHART_GREEN], text="average_po_value")
        fig.update_traces(marker_line_color=CHART_DARK_GREEN, marker_line_width=0.7, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_title="Department", yaxis_title="Average PO Value (₹)")
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else:
        st.info("No department data available for the selected filters.")

    # Department Procurement Summary
    st.subheader("📑 Department Procurement Summary")
    department_summary = filtered.groupby("department_name", as_index=False).agg(total_orders=("po_number", "count"), total_spending=("total_po_amount", "sum"), average_po_value=("total_po_amount", "mean")).sort_values("total_spending", ascending=False)
    if not department_summary.empty:
        st.dataframe(department_summary, use_container_width=True, hide_index=True, column_config={
            "department_name": "Department", "total_orders": "Total Orders",
            "total_spending": st.column_config.NumberColumn("Total Spending (₹)", format="₹%.2f"),
            "average_po_value": st.column_config.NumberColumn("Average PO Value (₹)", format="₹%.2f"),
        })
        st.download_button("📥 Download Department Summary", data=department_summary.to_csv(index=False).encode("utf-8-sig"), file_name="department_procurement_summary.csv", mime="text/csv")
    else:
        st.info("No department data available for the selected filters.")

    # Purchase Order Status Summary
    st.subheader("📋 Purchase Order Status Summary")
    status_summary = filtered.groupby("po_status", as_index=False).agg(total_orders=("po_number", "count"))
    total_status_orders = status_summary["total_orders"].sum()
    if total_status_orders > 0:
        status_summary["percentage"] = (status_summary["total_orders"] / total_status_orders * 100).round(1)
        status_summary = status_summary.sort_values("total_orders", ascending=False)
        status_color_map = {"Approved": CHART_GREEN, "Pending": CHART_PINK, "Rejected": CHART_DUSTY_PINK, "Completed": CHART_DARK_GREEN, "Ordered": CHART_GREEN, "Partially Received": CHART_DUSTY_PINK, "Cancelled": "#B8BDB5", "Draft": "#D9DED6", "Unknown": "#B8BDB5"}
        fig = px.bar(status_summary, x="po_status", y="total_orders", title="Purchase Order Status Summary", labels={"po_status": "Purchase Order Status", "total_orders": "Number of Orders"}, color="po_status", color_discrete_map=status_color_map, color_discrete_sequence=CHART_COLORS, text="total_orders")
        fig.update_traces(marker_line_color="#D7DFD3", marker_line_width=0.7, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_title="Purchase Order Status", yaxis_title="Number of Orders", showlegend=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)
        st.dataframe(status_summary, use_container_width=True, hide_index=True, column_config={"po_status": "PO Status", "total_orders": "Number of Orders", "percentage": st.column_config.NumberColumn("Percentage (%)", format="%.1f%%")})
    else:
        st.info("No purchase orders match the selected filters.")

    # Monthly Purchase Order Spending Trend
    st.subheader("📈 Monthly Purchase Order Spending Trend")
    monthly_data = (filtered.dropna(subset=["po_date"]).assign(purchase_month=lambda x: x["po_date"].dt.to_period("M").astype(str)).groupby("purchase_month", as_index=False).agg(monthly_spending=("total_po_amount", "sum"), total_orders=("po_number", "count")).sort_values("purchase_month"))
    if not monthly_data.empty:
        fig_monthly = px.line(monthly_data, x="purchase_month", y="monthly_spending", title="Monthly Purchase Order Spending Trend", labels={"purchase_month": "Month", "monthly_spending": "Purchase Order Spending (₹)"}, markers=True, color_discrete_sequence=[CHART_GREEN])
        fig_monthly.update_traces(line=dict(width=3, color=CHART_GREEN), marker=dict(size=8, color=CHART_PINK, line=dict(width=2, color=CHART_DARK_GREEN)), hovertemplate="Month: %{x}<br>Spending: ₹%{y:,.2f}<extra></extra>")
        fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Purchase Order Spending (₹)")
        st.plotly_chart(style_chart(fig_monthly), use_container_width=True)
    else:
        st.info("No monthly spending data for the selected filters.")

    # Month-over-month spending: compare consecutive calendar months.
    monthly_source = filtered.dropna(subset=["po_date"]).copy()
    if not monthly_source.empty:
        monthly_source["Month"] = monthly_source["po_date"].dt.to_period("M").dt.to_timestamp()
        monthly_spending = monthly_source.groupby("Month")["total_po_amount"].sum().sort_index()
        full_month_range = pd.date_range(monthly_spending.index.min(), monthly_spending.index.max(), freq="MS")
        monthly_spending = monthly_spending.reindex(full_month_range, fill_value=0)
        if len(monthly_spending) >= 2:
            current_month_spending = monthly_spending.iloc[-1]
            previous_month_spending = monthly_spending.iloc[-2]
            if previous_month_spending != 0:
                spending_change = ((current_month_spending - previous_month_spending) / previous_month_spending) * 100
                st.metric("Latest Month vs Previous Month", f"₹{current_month_spending:,.0f}", delta=f"{spending_change:+.1f}%", help="Compares the latest month in the selected data with the preceding calendar month.")
            else:
                st.info("The previous calendar month has zero spending, so percentage change cannot be calculated.")
        else:
            st.info("At least two calendar months are needed for comparison.")
    else:
        st.info("No valid PO dates are available for monthly comparison.")

    # Vendor Performance Analysis uses records before the delivery slicer.
    st.subheader("🏢 Vendor Performance Analysis")
    vendor_eligible_status = ~vendor_analysis_data["po_status"].astype(str).str.contains(r"cancelled|draft|pending approval", case=False, na=False, regex=True)
    vendor_base = vendor_analysis_data.loc[vendor_eligible_status].copy()
    vendor_performance = vendor_analysis_data.groupby("vendor_name", as_index=False).agg(total_orders=("po_number", "count"), total_spending=("total_po_amount", "sum"))
    delivered_by_vendor = vendor_base.loc[vendor_base["actual_delivery_date"].notna()].groupby("vendor_name").size()
    eligible_by_vendor = vendor_base.groupby("vendor_name").size()
    vendor_overdue_mask = vendor_base["actual_delivery_date"].isna() & vendor_base["delivery_date"].notna() & (vendor_base["delivery_date"] < today)
    overdue_by_vendor = vendor_base.loc[vendor_overdue_mask].groupby("vendor_name").size()
    vendor_performance["eligible_orders"] = vendor_performance["vendor_name"].map(eligible_by_vendor).fillna(0).astype(int)
    vendor_performance["delivered_orders"] = vendor_performance["vendor_name"].map(delivered_by_vendor).fillna(0).astype(int)
    vendor_performance["potentially_overdue"] = vendor_performance["vendor_name"].map(overdue_by_vendor).fillna(0).astype(int)
    vendor_performance["delivery_completion_pct"] = (vendor_performance["delivered_orders"].div(vendor_performance["eligible_orders"].replace(0, float("nan"))).mul(100).fillna(0).round(1))
    vendor_performance = vendor_performance.sort_values("total_spending", ascending=False)
    if vendor_performance.empty:
        st.info("No vendor performance data for the selected filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            fig_vendor_spending = px.bar(vendor_performance, x="vendor_name", y="total_spending", title="Total PO Value by Vendor", labels={"vendor_name": "Vendor", "total_spending": "Total PO Value (₹)"}, color_discrete_sequence=[CHART_GREEN], hover_data=["total_orders", "potentially_overdue", "delivery_completion_pct"], text="total_spending")
            fig_vendor_spending.update_traces(marker_line_color=CHART_DARK_GREEN, marker_line_width=0.7, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
            fig_vendor_spending.update_layout(xaxis_title="Vendor", yaxis_title="Total PO Value (₹)", xaxis_tickangle=-35)
            st.plotly_chart(style_chart(fig_vendor_spending), use_container_width=True)
        with col2:
            fig_vendor_delays = px.bar(vendor_performance, x="vendor_name", y="potentially_overdue", title="Potentially Overdue Orders by Vendor", labels={"vendor_name": "Vendor", "potentially_overdue": "Overdue Orders"}, color_discrete_sequence=[CHART_PINK], hover_data=["total_orders", "delivery_completion_pct"], text="potentially_overdue")
            fig_vendor_delays.update_traces(marker_line_color=CHART_DUSTY_PINK, marker_line_width=0.7, textposition="outside", cliponaxis=False)
            fig_vendor_delays.update_layout(xaxis_title="Vendor", yaxis_title="Overdue Orders", xaxis_tickangle=-35)
            st.plotly_chart(style_chart(fig_vendor_delays), use_container_width=True)
        st.dataframe(vendor_performance, use_container_width=True, hide_index=True, column_config={
            "vendor_name": "Vendor", "total_orders": "Total Orders", "eligible_orders": "Eligible Delivery Orders",
            "total_spending": st.column_config.NumberColumn("Total Spending (₹)", format="₹%.2f"),
            "delivered_orders": "Delivered Orders", "potentially_overdue": "Potentially Overdue Orders",
            "delivery_completion_pct": st.column_config.NumberColumn("Delivery Completion (%)", format="%.1f%%"),
        })

    # Vendor Spending Concentration
    st.subheader("📊 Vendor Spending Concentration")
    vendor_spending = vendor_analysis_data.groupby("vendor_name")["total_po_amount"].sum().sort_values(ascending=False)
    total_vendor_spending = vendor_spending.sum()
    if total_vendor_spending > 0:
        top_vendor_spending = vendor_spending.head(3).sum()
        top_three_share = top_vendor_spending / total_vendor_spending * 100
        col1, col2 = st.columns(2)
        col1.metric("Top 3 Vendors' Spending", f"₹{top_vendor_spending:,.0f}")
        col2.metric("Top 3 Vendors' Share", f"{top_three_share:.1f}%")
        top_vendors = vendor_spending.head(10).rename_axis("vendor_name").reset_index(name="total_po_amount")
        fig_vendor_concentration = px.bar(top_vendors, x="vendor_name", y="total_po_amount", title="Top 10 Vendors by Purchase Order Spending", labels={"vendor_name": "Vendor", "total_po_amount": "Purchase Order Spending (₹)"}, color_discrete_sequence=[CHART_GREEN], text="total_po_amount")
        fig_vendor_concentration.update_traces(marker_line_color=CHART_DARK_GREEN, marker_line_width=0.7, texttemplate="₹%{y:,.0f}", textposition="outside", cliponaxis=False)
        fig_vendor_concentration.update_layout(xaxis_title="Vendor", yaxis_title="Purchase Order Spending (₹)", xaxis_tickangle=-35)
        st.plotly_chart(style_chart(fig_vendor_concentration), use_container_width=True)
    else:
        st.info("No vendor spending data is available for the current filters.")

    # Delivery Overview: shows counts before the delivery-status slicer.
    st.subheader("🚚 Delivery Overview")
    delivery_overview = pd.DataFrame({"Delivery Status": ["Delivered", "Pending Delivery", "Potentially Overdue"], "Orders": [delivered_count, pending_delivery, overdue_count]})
    fig_delivery = px.bar(delivery_overview, x="Delivery Status", y="Orders", title="Delivery Overview", labels={"Delivery Status": "Delivery Status", "Orders": "Number of Orders"}, color="Delivery Status", color_discrete_map={"Delivered": CHART_GREEN, "Pending Delivery": CHART_PINK, "Potentially Overdue": CHART_DUSTY_PINK}, text="Orders")
    fig_delivery.update_traces(marker_line_color=CHART_DARK_GREEN, marker_line_width=0.7, textposition="outside", cliponaxis=False)
    fig_delivery.update_layout(xaxis_title="Delivery Status", yaxis_title="Number of Orders", showlegend=False)
    st.plotly_chart(style_chart(fig_delivery), use_container_width=True)

    # Overdue Purchase Order Action Center follows the delivery-status slicer.
    st.subheader("⚠️ Overdue Purchase Order Action Center")
    _, _, _, overdue_mask_filtered = delivery_classification(filtered, today)
    overdue_data = filtered.loc[overdue_mask_filtered].copy()
    if not overdue_data.empty:
        overdue_data["days_overdue"] = (today - overdue_data["delivery_date"]).dt.days
        total_overdue_orders = len(overdue_data)
        total_overdue_value = overdue_data["total_po_amount"].sum()
        affected_vendors = overdue_data["vendor_name"].nunique()
        max_days_overdue = int(overdue_data["days_overdue"].max())
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overdue Orders", f"{total_overdue_orders:,}")
        col2.metric("Overdue PO Value", f"₹{total_overdue_value:,.0f}")
        col3.metric("Affected Vendors", f"{affected_vendors:,}")
        col4.metric("Oldest Delay", f"{max_days_overdue:,} days")
        overdue_data["Urgency"] = overdue_data["days_overdue"].apply(lambda days: "Critical" if days > 60 else "High" if days > 30 else "Medium" if days > 7 else "Low")
        st.markdown("### Order Urgency Breakdown")
        urgency_order = ["Critical", "High", "Medium", "Low"]
        urgency_summary = overdue_data["Urgency"].value_counts().reindex(urgency_order, fill_value=0).rename_axis("Urgency").reset_index(name="Orders")
        fig_urgency = px.bar(urgency_summary, x="Urgency", y="Orders", title="Order Urgency Breakdown", labels={"Urgency": "Urgency Level", "Orders": "Number of Overdue Orders"}, color="Urgency", color_discrete_map={"Critical": "#C76B78", "High": CHART_DUSTY_PINK, "Medium": CHART_PINK, "Low": CHART_GREEN}, category_orders={"Urgency": urgency_order}, text="Orders")
        fig_urgency.update_traces(marker_line_color=CHART_DARK_GREEN, marker_line_width=0.7, textposition="outside", cliponaxis=False)
        fig_urgency.update_layout(xaxis_title="Urgency Level", yaxis_title="Number of Overdue Orders", showlegend=False)
        st.plotly_chart(style_chart(fig_urgency), use_container_width=True)
    else:
        st.success("No potentially overdue orders in the current selection.")

    # Overdue Purchase Orders table
    st.subheader("⚠️ Overdue Purchase Orders")
    _, _, _, overdue_mask_table = delivery_classification(filtered, today)
    overdue_orders = filtered.loc[overdue_mask_table].copy()
    if not overdue_orders.empty:
        overdue_orders["Days Overdue"] = (today - overdue_orders["delivery_date"]).dt.days
        overdue_orders["Urgency"] = overdue_orders["Days Overdue"].apply(lambda days: "Critical" if days > 60 else "High" if days > 30 else "Medium" if days > 7 else "Low")
        overdue_orders["Recommended Action"] = overdue_orders["po_status"].apply(lambda status: "Confirm partial delivery" if status == "Partially Received" else "Confirm delivery schedule with vendor" if status == "Ordered" else "Check approval and delivery status" if status == "Approved" else "Review purchase order status")
        overdue_orders = overdue_orders.sort_values("Days Overdue", ascending=False)
        overdue_columns = ["po_number", "vendor_name", "department_name", "delivery_date", "Days Overdue", "Urgency", "po_status", "total_po_amount", "Recommended Action"]
        st.dataframe(overdue_orders[overdue_columns], use_container_width=True, hide_index=True, column_config={
            "po_number": "PO Number", "vendor_name": "Vendor", "department_name": "Department",
            "delivery_date": st.column_config.DateColumn("Expected Delivery"),
            "Days Overdue": st.column_config.NumberColumn("Days Overdue", format="%d days"),
            "Urgency": "Urgency", "po_status": "PO Status",
            "total_po_amount": st.column_config.NumberColumn("PO Value (₹)", format="₹%.2f"),
            "Recommended Action": "Recommended Action",
        })
        st.download_button("📥 Download Overdue Orders Report", data=overdue_orders[overdue_columns].to_csv(index=False).encode("utf-8-sig"), file_name="overdue_purchase_orders.csv", mime="text/csv")
        st.warning(f"{len(overdue_orders)} purchase orders have passed their expected delivery date and have no recorded actual delivery date. Review the recommended actions below.")
    else:
        st.success("No overdue purchase orders found for the selected filters.")

    # Purchase Order Details table with search
    st.subheader("Purchase Order Details")
    search = st.text_input("Search PO number, vendor, or item description")
    display_df = filtered.copy()
    if search:
        search_mask = (
            display_df["po_number"].astype(str).str.contains(search, case=False, na=False)
            | display_df["vendor_name"].astype(str).str.contains(search, case=False, na=False)
            | display_df["item_description"].astype(str).str.contains(search, case=False, na=False)
        )
        display_df = display_df.loc[search_mask]

    columns = ["po_number", "po_date", "vendor_name", "department_name", "item_description", "quantity", "unit_price", "total_po_amount", "po_status", "delivery_date", "actual_delivery_date"]
    st.dataframe(display_df[columns], use_container_width=True, hide_index=True, column_config={
        "po_number": "PO Number", "po_date": st.column_config.DateColumn("PO Date"),
        "vendor_name": "Vendor", "department_name": "Department", "item_description": "Item Description",
        "quantity": "Quantity", "unit_price": st.column_config.NumberColumn("Unit Price", format="%.2f"),
        "total_po_amount": st.column_config.NumberColumn("Total PO Value", format="₹%.2f"),
        "po_status": "PO Status", "delivery_date": st.column_config.DateColumn("Expected Delivery"),
        "actual_delivery_date": st.column_config.DateColumn("Actual Delivery"),
    })
    st.caption(f"Showing {len(display_df)} purchase orders.")
    st.download_button("📥 Download Purchase Order Report (CSV)", data=display_df.to_csv(index=False).encode("utf-8-sig"), file_name="purchase_order_report.csv", mime="text/csv")

except mysql.connector.Error as error:
    st.error(f"Database connection or query error: {error}")
    st.info("Check that MySQL is running, the database credentials are correct, and the required tables and columns exist.")
except Exception as error:
    st.error(f"Dashboard error: {error}")
    st.info("Check the traceback in the terminal running Streamlit to identify the exact line that needs correction.")
