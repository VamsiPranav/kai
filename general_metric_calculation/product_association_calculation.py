import pandas as pd
from collections import Counter


def load_data():
    product_catalogue = pd.read_csv("../data/product_catalogue.csv")
    transactions = pd.read_csv("../data/customer_transaction_data.csv")
    return product_catalogue, transactions


def find_products_bought_together(transactions, n=3):
    grouped_transactions = transactions.groupby('Txn ID')['Barcode'].apply(list).reset_index()

    bought_together = {}

    for _, row in grouped_transactions.iterrows():
        products = row['Barcode']
        for product in products:
            if product not in bought_together:
                bought_together[product] = Counter()
            bought_together[product].update(set(products) - {product})

    # Get top n products bought together for each product
    for product in bought_together:
        bought_together[product] = [item for item, _ in bought_together[product].most_common(n)]

    return bought_together


def find_similar_products(product_catalogue, n=3):
    similar_products = {}

    for _, row in product_catalogue.iterrows():
        barcode = row['Barcode']
        product_name = row['Product Name']
        brand = row['Product Brand']

        similar = product_catalogue[
            (product_catalogue['Product Name'] == product_name) &
            (product_catalogue['Product Brand'] != brand)
            ]['Barcode'].tolist()

        similar_products[barcode] = similar[:n]  # Limit to n similar products

    return similar_products


def create_association_table(product_catalogue, bought_together, similar_products):
    association_table = pd.DataFrame({
        'Barcode': product_catalogue['Barcode'],
        'Together Bought With': [
            ', '.join(map(str, bought_together.get(barcode, [])))
            for barcode in product_catalogue['Barcode']
        ],
        'Similar Products': [
            ', '.join(map(str, similar_products.get(barcode, [])))
            for barcode in product_catalogue['Barcode']
        ]
    })

    return association_table


def main():
    product_catalogue, transactions = load_data()
    bought_together = find_products_bought_together(transactions)
    similar_products = find_similar_products(product_catalogue)
    association_table = create_association_table(product_catalogue, bought_together, similar_products)
    association_table.to_csv("../data/product_associations.csv", index=False)

    # print("Product associations and similarities table has been created.")
    # # Print some statistics and sample rows
    # print(f"\nTotal number of products: {len(association_table)}")
    # print(f"Products with associated items: {association_table['Together Bought With'].str.len().gt(0).sum()}")
    # print(f"Products with similar items: {association_table['Similar Products'].str.len().gt(0).sum()}")
    #
    # print("\nSample rows from the association table:")
    # print(association_table.sample(5).to_string())
    #

if __name__ == "__main__":
    main()