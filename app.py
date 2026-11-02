import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from pathlib import Path

# -------------------- PAGE SETUP --------------------
st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide"
)

FILE_NAME = Path(__file__).parent / "expenses.csv"
CATEGORIES = [
    "Food", "Travel", "Shopping", "Education",
    "Bills", "Entertainment", "Health", "Other"
]

# -------------------- FILE HANDLING --------------------
def initialize_file():
    if not FILE_NAME.exists():
        empty_df = pd.DataFrame(
            columns=["Date", "Category", "Description", "Amount"]
        )
        empty_df.to_csv(FILE_NAME, index=False)


def load_expenses():
    initialize_file()
    df = pd.read_csv(FILE_NAME)

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(
            df["Amount"], errors="coerce"
        ).fillna(0)
        df = df.dropna(subset=["Date"])

    return df


def save_expenses(df):
    output = df.copy()
    if not output.empty:
        output["Date"] = pd.to_datetime(output["Date"]).dt.strftime("%Y-%m-%d")
    output.to_csv(FILE_NAME, index=False)


# -------------------- CUSTOM DESIGN --------------------
st.markdown("""
<style>
    .stApp {
        background: #f5f7fb;
    }
    .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.8rem 2rem;
        border-radius: 18px;
        background: linear-gradient(115deg, #172554, #3349a5);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        color: white;
        margin: 0;
        font-size: 2.1rem;
    }
    .hero p {
        color: #dbeafe;
        margin: .45rem 0 0 0;
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 14px;
    }
    div[data-testid="stForm"] {
        background: white;
        padding: 1.2rem;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.title("💰 Expense Tracker")
    st.caption("Manage your money smartly")
    page = st.radio(
        "MENU",
        [
            "Dashboard",
            "Add Expense",
            "View Expenses",
            "Monthly Report",
            "Category Report",
            "Delete Expense"
        ]
    )
    st.divider()
    st.caption("Personal Expense Tracker")
    st.caption("Python • Pandas • Streamlit")

df = load_expenses()

# -------------------- HEADER --------------------
st.markdown("""
<div class="hero">
    <h1>Personal Expense Tracker</h1>
    <p>Track your spending, understand your habits, and stay in control.</p>
</div>
""", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------
if page == "Dashboard":
    st.subheader("Overview")

    total = float(df["Amount"].sum()) if not df.empty else 0
    today_total = (
        float(df.loc[df["Date"].dt.date == date.today(), "Amount"].sum())
        if not df.empty else 0
    )
    count = len(df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expenses", f"₹{total:,.2f}")
    c2.metric("Today's Spending", f"₹{today_total:,.2f}")
    c3.metric("Number of Entries", count)

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Spending by Category")
        if not df.empty:
            category_total = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            st.bar_chart(category_total)
        else:
            st.info("Add an expense to see your category chart.")

    with right:
        st.subheader("Recent Expenses")
        if not df.empty:
            recent = df.sort_values("Date", ascending=False).head(5).copy()
            recent["Date"] = recent["Date"].dt.strftime("%d-%m-%Y")
            recent["Amount"] = recent["Amount"].map(lambda x: f"₹{x:,.2f}")
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded yet.")

# -------------------- ADD EXPENSE --------------------
elif page == "Add Expense":
    st.subheader("➕ Add a New Expense")
    st.write("Enter the details below to save a new expense.")

    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Category", CATEGORIES)
        with col2:
            description = st.text_input("Description", placeholder="e.g. Lunch, bus ticket")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")

        submitted = st.form_submit_button("Save Expense", use_container_width=True)

    if submitted:
        if not description.strip():
            st.error("Please enter an expense description.")
        elif amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            new_row = pd.DataFrame([{
                "Date": pd.Timestamp(expense_date),
                "Category": category,
                "Description": description.strip(),
                "Amount": float(amount)
            }])
            updated = pd.concat([df, new_row], ignore_index=True)
            save_expenses(updated)
            st.success("Expense added successfully!")
            st.rerun()

# -------------------- VIEW EXPENSES --------------------
elif page == "View Expenses":
    st.subheader("📋 All Expenses")

    if df.empty:
        st.info("No expenses found. Add your first expense.")
    else:
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            chosen_categories = st.multiselect(
                "Filter by category",
                CATEGORIES,
                default=CATEGORIES
            )
        with filter_col2:
            search_text = st.text_input("Search description")

        filtered = df[df["Category"].isin(chosen_categories)]
        if search_text.strip():
            filtered = filtered[
                filtered["Description"].str.contains(
                    search_text.strip(), case=False, na=False
                )
            ]

        display = filtered.sort_values("Date", ascending=False).copy()
        display["Date"] = display["Date"].dt.strftime("%d-%m-%Y")
        display["Amount"] = display["Amount"].map(lambda x: f"₹{x:,.2f}")
        st.dataframe(display, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} of {len(df)} expenses.")

# -------------------- MONTHLY REPORT --------------------
elif page == "Monthly Report":
    st.subheader("📅 Monthly Report")

    if df.empty:
        st.info("No expenses available for a monthly report.")
    else:
        available_months = sorted(
            df["Date"].dt.to_period("M").dropna().unique(),
            reverse=True
        )
        selected_month = st.selectbox(
            "Select month",
            available_months,
            format_func=lambda x: x.strftime("%B %Y")
        )
        monthly_df = df[df["Date"].dt.to_period("M") == selected_month]
        total = monthly_df["Amount"].sum()
        st.metric(f"Total Expense - {selected_month.strftime('%B %Y')}", f"₹{total:,.2f}")

        category_total = monthly_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Category-wise spending (Bar Chart)**")
            st.bar_chart(category_total)

        with col2:
            st.markdown("**Expense distribution (Pie Chart)**")
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.pie(
                category_total.values,
                labels=category_total.index,
                autopct="%1.1f%%",
                startangle=90
            )
            ax.axis("equal")
            st.pyplot(fig)
            plt.close(fig)

        st.markdown("**Transactions for selected month**")
        monthly_display = monthly_df.sort_values("Date", ascending=False).copy()
        monthly_display["Date"] = monthly_display["Date"].dt.strftime("%d-%m-%Y")
        st.dataframe(monthly_display, use_container_width=True, hide_index=True)

# -------------------- CATEGORY REPORT --------------------
elif page == "Category Report":
    st.subheader("📊 Category Report")

    if df.empty:
        st.info("No expenses available for a category report.")
    else:
        category_total = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        st.bar_chart(category_total)
        st.markdown("**Total spending by category**")
        report = category_total.reset_index()
        report.columns = ["Category", "Total Amount (₹)"]
        st.dataframe(report, use_container_width=True, hide_index=True)

# -------------------- DELETE EXPENSE --------------------
elif page == "Delete Expense":
    st.subheader("🗑️ Delete an Expense")
    st.warning("Deleting an expense is permanent.")

    if df.empty:
        st.info("No expenses available to delete.")
    else:
        options = df.index.tolist()

        def expense_label(index):
            row = df.loc[index]
            return (
                f"{row['Date'].strftime('%d-%m-%Y')} | "
                f"{row['Category']} | {row['Description']} | "
                f"₹{row['Amount']:,.2f}"
            )

        selected_index = st.selectbox(
            "Select the expense to delete",
            options,
            format_func=expense_label
        )

        if st.button("Delete Selected Expense", type="primary"):
            updated = df.drop(index=selected_index).reset_index(drop=True)
            save_expenses(updated)
            st.success("Expense deleted successfully!")
            st.rerun()

st.divider()
st.caption("Personal Expense Tracker • Built using Python, Pandas, Matplotlib and Streamlit")
