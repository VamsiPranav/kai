import pandas as pd

def averges_cal():
    df = pd.read_csv("data/retrieval_table.csv")
    avg_shelf_life_score = df['Weighted Shelf Score'].mean()
    avg_product_viability_score = df['Viability Score'].mean()

    df['15_day_demand_value'] = df['1-15 Days'] * df['MRP']
    total_15_day_demand_value = df['15_day_demand_value'].sum()

    print(f"Average Shelf Life Score: {avg_shelf_life_score:.4f}")
    print(f"Average Product Viability Score: {avg_product_viability_score:.4f}")
    print(f"Monetary Value of Demand for Next 15 Days: ₹{total_15_day_demand_value:.2f}")

    # print("\nTop 5 Products Contributing to 15-Day Demand Value:")
    # top_5_products = df.nlargest(5, '15_day_demand_value')[['Product Name', 'Product Brand', '15_day_demand_value']]
    # print(top_5_products.to_string(index=False))

    return avg_shelf_life_score, avg_product_viability_score, total_15_day_demand_value;