import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def load_data():
    product_catalogue = pd.read_csv("../data/product_catalogue.csv")
    transactions = pd.read_csv("../data/customer_transaction_data.csv")
    working_table = pd.read_csv("../data/working_table.csv")
    return product_catalogue, transactions, working_table


def preprocess_data(transactions, working_table):
    # Calculate total quantity sold and revenue for each product
    sales_data = transactions.groupby('Barcode').agg({
        'Selling Price': 'sum',
        'Quantity': 'sum'
    }).rename(columns={'Quantity': 'Quantity Sold', 'Selling Price': 'Total Revenue'})

    # Calculate average inventory and aggregate quantity remaining for each product
    inventory_data = working_table.groupby('Barcode').agg({
        'Quantity Remaining': ['mean', 'sum']
    })
    inventory_data.columns = ['Average Inventory', 'Quantity Remaining']

    # Merge sales and inventory data
    product_data = sales_data.join(inventory_data)

    # Calculate total cost and weighted shelf score
    cost_and_shelf_data = working_table.groupby('Barcode').apply(lambda x: pd.Series({
        'Total Cost': (x['Cost Price'] * x['Quantity Remaining']).sum(),
        'Weighted Shelf Score': (x['Shelf Score'] * x['Quantity Remaining']).sum() / x['Quantity Remaining'].sum()
    }))

    product_data = product_data.join(cost_and_shelf_data)

    return product_data


def calculate_sales_trend(transactions):
    transactions['Date'] = pd.to_datetime(transactions['TimeStamp']).dt.date
    daily_sales = transactions.groupby(['Date', 'Barcode'])['Quantity'].sum().reset_index()

    trends = {}
    for barcode, group in daily_sales.groupby('Barcode'):
        if len(group) < 2:  # Need at least 2 points for a trend
            trends[barcode] = 0
        else:
            X = np.array(range(len(group))).reshape(-1, 1)
            y = group['Quantity'].values
            model = LinearRegression()
            model.fit(X, y)
            trends[barcode] = model.coef_[0]  # Slope of the trend line

    # Normalize trends
    trend_series = pd.Series(trends)
    min_trend, max_trend = trend_series.min(), trend_series.max()
    if min_trend != max_trend:
        normalized_trends = (trend_series - min_trend) / (max_trend - min_trend)
    else:
        normalized_trends = pd.Series(0.5, index=trend_series.index)  # If all trends are the same, set to 0.5

    return normalized_trends


def calculate_viability_score(product_data, sales_trends):
    # No divide by zero
    product_data['Average Inventory'] = product_data['Average Inventory'].replace(0, 0.01)
    product_data['Total Revenue'] = product_data['Total Revenue'].replace(0, 0.01)

    product_data['Profit Margin Ratio'] = (product_data['Total Revenue'] - product_data['Total Cost']) / product_data[
        'Total Revenue']
    product_data['Turnover Ratio'] = product_data['Quantity Sold'] / product_data['Average Inventory']

    # Normalize turnover ratio
    max_turnover = product_data['Turnover Ratio'].max()
    product_data['Normalized Turnover'] = product_data['Turnover Ratio'] / max_turnover if max_turnover > 0 else 0

    product_data['Sales Trend'] = product_data.index.map(sales_trends)

    product_data['Viability Score'] = (
            product_data['Profit Margin Ratio'].clip(0, 1) * 0.4 +
            product_data['Normalized Turnover'] * 0.3 +
            product_data['Sales Trend'].fillna(0) * 0.3
    )

    product_data['Viability Score'] = product_data['Viability Score'].clip(0, 1)

    return product_data['Viability Score']


def create_computation_table(product_catalogue, product_data):
    computation_table = product_catalogue[['Barcode', 'Product Name', 'Product Brand', 'MRP']].copy()

    computation_table = computation_table.merge(
        product_data[['Quantity Remaining', 'Weighted Shelf Score', 'Viability Score']],
        on='Barcode', how='left')


    total_cost = product_data['Total Cost']
    total_quantity = product_data['Quantity Remaining']
    weighted_cost_price = (total_cost / total_quantity).fillna(0)
    computation_table['Weighted Cost Price'] = computation_table['Barcode'].map(weighted_cost_price)
    computation_table['Minimum Price'] = computation_table['Weighted Cost Price'] * 1.05

    computation_table = computation_table.fillna(0)

    column_order = ['Barcode', 'Product Name', 'Product Brand', 'Quantity Remaining', 'MRP',
                    'Weighted Cost Price', 'Minimum Price', 'Weighted Shelf Score', 'Viability Score']
    computation_table = computation_table[column_order]

    return computation_table


def main():
    try:
        product_catalogue, transactions, working_table = load_data()
        product_data = preprocess_data(transactions, working_table)
        sales_trends = calculate_sales_trend(transactions)

        product_data['Viability Score'] = calculate_viability_score(product_data, sales_trends)

        computation_table = create_computation_table(product_catalogue, product_data)

        computation_table.to_csv("../data/computation_table.csv", index=False)

        # print("Computation table has been created and saved as 'computation_table.txt'")
        # print("\nSample rows from the computation table:")
        # print(computation_table.head())
        #
        # # Print some statistics
        # print("\nComputation Table Statistics:")
        # print(computation_table.describe())

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print("Error details:")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()