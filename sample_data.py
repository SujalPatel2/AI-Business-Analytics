import pandas as pd
import numpy as np

def get_sales_data():
    np.random.seed(42)
    months = pd.date_range("2023-01-01", periods=24, freq="MS")
    products = ["Laptop", "Phone", "Tablet", "Watch", "Earbuds"]
    regions = ["North", "South", "East", "West"]
    rows = []
    for month in months:
        for product in products:
            for region in regions:
                base = {"Laptop": 80000, "Phone": 50000, "Tablet": 30000,
                        "Watch": 20000, "Earbuds": 15000}[product]
                region_factor = {"North": 1.2, "South": 0.9, "East": 1.1, "West": 0.95}[region]
                trend = 1 + (months.get_loc(month) * 0.015)
                seasonal = 1 + 0.2 * np.sin(2 * np.pi * month.month / 12)
                noise = np.random.normal(1, 0.1)
                # March dip
                if month.month == 3:
                    seasonal *= 0.75
                sales = max(0, int(base * region_factor * trend * seasonal * noise))
                units = max(1, int(sales / (base / 100) * noise))
                rows.append({
                    "Date": month,
                    "Month": month.strftime("%b %Y"),
                    "Product": product,
                    "Region": region,
                    "Sales": sales,
                    "Units": units,
                    "Cost": int(sales * np.random.uniform(0.55, 0.70)),
                    "Returns": max(0, int(units * np.random.uniform(0, 0.05))),
                    "Customer_Rating": round(np.random.uniform(3.5, 5.0), 1),
                    "Marketing_Spend": int(sales * np.random.uniform(0.08, 0.15)),
                })
    df = pd.DataFrame(rows)
    df["Profit"] = df["Sales"] - df["Cost"]
    df["Profit_Margin"] = ((df["Profit"] / df["Sales"]) * 100).round(2)
    return df

def get_hr_data():
    np.random.seed(7)
    n = 200
    departments = ["Engineering", "Sales", "Marketing", "Finance", "HR", "Operations"]
    df = pd.DataFrame({
        "Employee_ID": [f"EMP{str(i).zfill(4)}" for i in range(1, n+1)],
        "Department": np.random.choice(departments, n),
        "Age": np.random.randint(22, 60, n),
        "Salary": np.random.randint(35000, 150000, n),
        "Years_Experience": np.random.randint(0, 30, n),
        "Performance_Score": np.random.randint(1, 6, n),
        "Satisfaction": np.random.uniform(1, 5, n).round(1),
        "Attrition": np.random.choice(["Yes", "No"], n, p=[0.16, 0.84]),
        "Work_Mode": np.random.choice(["Remote", "Hybrid", "On-site"], n, p=[0.3, 0.4, 0.3]),
        "Training_Hours": np.random.randint(0, 80, n),
        "Overtime": np.random.choice(["Yes", "No"], n, p=[0.35, 0.65]),
    })
    df["Salary"] = df["Salary"].clip(35000, 150000)
    return df

def get_ecommerce_data():
    np.random.seed(99)
    n = 500
    categories = ["Electronics", "Clothing", "Home", "Books", "Sports", "Beauty"]
    df = pd.DataFrame({
        "Order_ID": [f"ORD{str(i).zfill(5)}" for i in range(1, n+1)],
        "Date": pd.date_range("2023-01-01", periods=n, freq="D")[:n],
        "Category": np.random.choice(categories, n),
        "Revenue": np.random.randint(200, 15000, n),
        "Orders": np.random.randint(1, 50, n),
        "Visitors": np.random.randint(100, 5000, n),
        "Conversion_Rate": np.random.uniform(1, 8, n).round(2),
        "Avg_Order_Value": np.random.randint(150, 800, n),
        "Cart_Abandonment": np.random.uniform(50, 85, n).round(1),
        "New_Customers": np.random.randint(10, 200, n),
        "Returning_Customers": np.random.randint(5, 150, n),
        "Ad_Spend": np.random.randint(500, 8000, n),
    })
    df["ROAS"] = (df["Revenue"] / df["Ad_Spend"]).round(2)
    return df

SAMPLE_DATASETS = {
    "📊 Sales Dataset (Multi-Product, 2 Years)": get_sales_data,
    "👥 HR Analytics Dataset (200 Employees)": get_hr_data,
    "🛒 E-Commerce Dataset (500 Orders)": get_ecommerce_data,
}
