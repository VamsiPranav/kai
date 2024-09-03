import pandas as pd
import numpy as np


def load_data():
    product_catalogue = pd.read_csv("../data/product_catalogue.csv")
    transactions = pd.read_csv("../data/customer_transaction_data.csv")
    return product_catalogue, transactions


def create_daily_sales_pivot(transactions, product_catalogue):

    transactions['Date'] = pd.to_datetime(transactions['TimeStamp']).dt.date
    daily_sales = transactions.groupby(['Date', 'Barcode']).size().reset_index(name='Quantity')

    pivot_table = daily_sales.pivot(index='Barcode', columns='Date', values='Quantity').fillna(0)

    all_products = pd.DataFrame(index=product_catalogue['Barcode'])
    pivot_table = all_products.join(pivot_table, how='left').fillna(0)

    pivot_table = pivot_table.astype(int)

    return pivot_table


def main():
    product_catalogue, transactions = load_data()
    daily_sales_pivot = create_daily_sales_pivot(transactions, product_catalogue)

    daily_sales_pivot.to_csv("../data/historic_daily_sales.csv")

    # print("Product daily sales pivot table has been created.")
    # # Print some statistics
    # print(f"\nTotal number of products: {len(daily_sales_pivot)}")
    # print(f"Date range: from {daily_sales_pivot.columns.min()} to {daily_sales_pivot.columns.max()}")
    #
    # # Print total sales for each product
    # total_sales = daily_sales_pivot.sum(axis=1).sort_values(ascending=False)
    # print("\nTop 5 products by total sales:")
    # print(total_sales.head())
    #
    # print("\nBottom 5 products by total sales:")
    # print(total_sales.tail())
    #
    # # Print sample of the pivot table
    # print("\nSample of the pivot table (first 5 products, first 5 dates):")
    # print(daily_sales_pivot.iloc[:5, :5])


if __name__ == "__main__":
    main()