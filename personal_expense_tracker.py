import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

FILE_NAME = "expenses.csv"


# -------------------- FILE HANDLING --------------------

def initialize_file():
    """Create the expense CSV file if it does not exist."""
    file = Path(FILE_NAME)

    if not file.exists():
        df = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
        df.to_csv(FILE_NAME, index=False)


def load_expenses():
    """Load expenses from CSV."""
    initialize_file()
    df = pd.read_csv(FILE_NAME)

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

    return df


# -------------------- ADD EXPENSE --------------------

def add_expense():
    print("\n========== ADD EXPENSE ==========")

    date_input = input("Enter date (DD-MM-YYYY) or press Enter for today: ").strip()

    if date_input == "":
        date = datetime.today().strftime("%Y-%m-%d")
    else:
        try:
            date = datetime.strptime(date_input, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date format!")
            return

    categories = [
        "Food",
        "Travel",
        "Shopping",
        "Education",
        "Bills",
        "Entertainment",
        "Health",
        "Other"
    ]

    print("\nCategories:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    try:
        choice = int(input("Choose category number: "))
        category = categories[choice - 1]
    except (ValueError, IndexError):
        print("Invalid category!")
        return

    description = input("Enter description: ").strip()

    try:
        amount = float(input("Enter amount (₹): "))
        if amount <= 0:
            print("Amount must be greater than zero.")
            return
    except ValueError:
        print("Please enter a valid amount.")
        return

    new_expense = pd.DataFrame([{
        "Date": date,
        "Category": category,
        "Description": description,
        "Amount": amount
    }])

    new_expense.to_csv(FILE_NAME, mode="a", header=False, index=False)

    print("\nExpense added successfully!")


# -------------------- VIEW EXPENSES --------------------

def view_expenses():
    df = load_expenses()

    print("\n========== ALL EXPENSES ==========")

    if df.empty:
        print("No expenses found.")
        return

    display_df = df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%d-%m-%Y")
    display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹{x:.2f}")

    print(display_df.to_string(index=False))


# -------------------- MONTHLY REPORT --------------------

def monthly_report():
    df = load_expenses()

    print("\n========== MONTHLY REPORT ==========")

    if df.empty:
        print("No expenses available.")
        return

    try:
        month_input = input(
            "Enter month and year (MM-YYYY), e.g. 08-2026: "
        ).strip()

        month = datetime.strptime(month_input, "%m-%Y")

    except ValueError:
        print("Invalid format!")
        return

    monthly_df = df[
        (df["Date"].dt.month == month.month) &
        (df["Date"].dt.year == month.year)
    ]

    if monthly_df.empty:
        print("No expenses found for this month.")
        return

    total = monthly_df["Amount"].sum()

    print(f"\nMonth: {month.strftime('%B %Y')}")
    print(f"Total Expense: ₹{total:.2f}")

    print("\nCategory-wise Expenses:")
    category_total = monthly_df.groupby("Category")["Amount"].sum().sort_values(
        ascending=False
    )

    for category, amount in category_total.items():
        print(f"{category:<15} ₹{amount:.2f}")

    # Bar chart
    plt.figure(figsize=(9, 5))
    category_total.plot(kind="bar")
    plt.title(f"Monthly Expense by Category - {month.strftime('%B %Y')}")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # Pie chart
    plt.figure(figsize=(7, 7))
    category_total.plot(kind="pie", autopct="%1.1f%%")
    plt.title(f"Expense Distribution - {month.strftime('%B %Y')}")
    plt.ylabel("")
    plt.tight_layout()
    plt.show()


# -------------------- CATEGORY REPORT --------------------

def category_report():
    df = load_expenses()

    print("\n========== CATEGORY REPORT ==========")

    if df.empty:
        print("No expenses available.")
        return

    category_total = df.groupby("Category")["Amount"].sum().sort_values(
        ascending=False
    )

    print("\nTotal spending by category:")
    for category, amount in category_total.items():
        print(f"{category:<15} ₹{amount:.2f}")

    plt.figure(figsize=(9, 5))
    category_total.plot(kind="bar")
    plt.title("Total Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


# -------------------- DELETE EXPENSE --------------------

def delete_expense():
    df = load_expenses()

    print("\n========== DELETE EXPENSE ==========")

    if df.empty:
        print("No expenses available.")
        return

    print(df.to_string())

    try:
        index = int(input("\nEnter the index of expense to delete: "))

        if index not in df.index:
            print("Invalid index.")
            return

        df = df.drop(index)
        df.to_csv(FILE_NAME, index=False)

        print("Expense deleted successfully!")

    except ValueError:
        print("Please enter a valid index.")



def main():
    initialize_file()

    while True:
        print("\n")
        print("=" * 45)
        print("       PERSONAL EXPENSE TRACKER")
        print("=" * 45)
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Monthly Report")
        print("4. Category Report")
        print("5. Delete Expense")
        print("6. Exit")
        print("=" * 45)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_expense()

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            monthly_report()

        elif choice == "4":
            category_report()

        elif choice == "5":
            delete_expense()

        elif choice == "6":
            print("\nThank you for using Personal Expense Tracker!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
