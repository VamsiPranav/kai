from operator import index

import pandas as pd
from sympy import Product


def load_and_analyze_data(file_path):
    df = pd.read_csv(file_path)
    top_viability = df.sort_values('Viability Score', ascending=False).head(20)
    top_shelf = df.sort_values('Weighted Shelf Score', ascending=False).head(20)
    bottom_viability = df.sort_values('Viability Score', ascending=True).head(20)
    bottom_shelf = df.sort_values('Weighted Shelf Score', ascending=True).head(20)

    return top_viability, top_shelf, bottom_viability, bottom_shelf


def find_common_products(top_viability, top_shelf):
    common_products = pd.merge(top_viability, top_shelf, how='inner', on=['Barcode'])
    return common_products

def main():
    file_path = '../data/retrieval_table.csv'
    top_viability, top_shelf, bottom_viability, bottom_shelf = load_and_analyze_data(file_path)
    top_common_products = find_common_products(top_viability, top_shelf)
    top_common_products = top_common_products.sort_values('1-15 Days_x', ascending = False).head(5)
    top_common_products = top_common_products[['Product Brand_x', 'Product Name_x', 'Quantity Remaining_x', 'MRP_x', 'Weighted Cost Price_x', 'Minimum Price_x', 'Weighted Shelf Score_x', 'Viability Score_x', '1-15 Days_x', 'Together Bought With_x', 'Similar Products_x', 'Stock wrt Demand_x']]
    top_common_products.to_csv("../data_that_matters/top_products.csv", index=False)

    bottom_common_products = find_common_products(bottom_viability, bottom_shelf)
    bottom_common_products = bottom_common_products.sort_values('1-15 Days_x', ascending=True).head(5)
    bottom_common_products = bottom_common_products[
        ['Product Brand_x', 'Product Name_x', 'Quantity Remaining_x', 'MRP_x', 'Weighted Cost Price_x',
         'Minimum Price_x', 'Weighted Shelf Score_x', 'Viability Score_x', '1-15 Days_x', 'Together Bought With_x',
         'Similar Products_x', 'Stock wrt Demand_x']]
    bottom_common_products.to_csv("../data_that_matters/bottom_products.csv", index=False)

if __name__ == "__main__":
    main()