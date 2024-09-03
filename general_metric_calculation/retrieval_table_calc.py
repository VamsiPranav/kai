import pandas as pd
import ast
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_and_prepare_data():
    computation_df = pd.read_csv('../data/computation_table.csv')
    demand_df = pd.read_csv('../data/15_day_demand_prediction_windows.csv')
    associations_df = pd.read_csv('../data/product_associations.csv')

    logging.info(f"Loaded computation_df with {len(computation_df)} rows")
    logging.info(f"Loaded demand_df with {len(demand_df)} rows")
    logging.info(f"Loaded associations_df with {len(associations_df)} rows")

    product_lookup = dict(zip(computation_df['Barcode'].astype(str),
                              computation_df['Product Brand'] + ' ' + computation_df['Product Name']))
    logging.info(f"Created product_lookup with {len(product_lookup)} items")

    def replace_barcodes(barcodes_str):
        try:
            barcodes = ast.literal_eval(barcodes_str)
        except ValueError:
            barcodes = [b.strip() for b in barcodes_str.split(',')]

        replaced = [product_lookup.get(str(barcode).strip(), str(barcode)) for barcode in barcodes]
        logging.debug(f"Replaced barcodes: {barcodes} with: {replaced}")
        return ', '.join(replaced)

    associations_df['Together Bought With'] = associations_df['Together Bought With'].apply(replace_barcodes)
    associations_df['Similar Products'] = associations_df['Similar Products'].apply(replace_barcodes)

    logging.info("Applied barcode replacement to 'Together Bought With' and 'Similar Products' columns")

    merged_df = computation_df.merge(demand_df, on='Barcode', how='left')
    merged_df = merged_df.merge(associations_df, on='Barcode', how='left')
    merged_df['Quantity Remaining'] = np.round(merged_df['Quantity Remaining'] / 100).astype(int)
    merged_df['1-15 Days'] = np.round(merged_df['1-15 Days'] / 6).astype(int)
    merged_df['Stock wrt Demand'] = merged_df['Quantity Remaining'] / merged_df['1-15 Days']
    logging.info(f"Merged dataframe created with {len(merged_df)} rows")

    return merged_df


def main():
    merged_data = load_and_prepare_data()

    merged_data = merged_data.drop(columns =['16-30 Days', '31-45 Days', '46-60 Days', '61-75 Days'])
    output_file = '../data/retrieval_table.csv'
    merged_data.to_csv(output_file, index=False)
    logging.info(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    main()