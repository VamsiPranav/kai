import pandas as pd
from datetime import datetime, timedelta


def gen_historic_sales():
    try:
        # Read the CSV files
        sales_df = pd.read_csv('data/historic_daily_sales.csv')
        retrieval_df = pd.read_csv('data/retrieval_table.csv')

        current_date = datetime(2024, 12, 31)

        def conv_string(x):
            date_string = x.strftime("%Y") + "-" + x.strftime("%m") + "-" + x.strftime("%d")
            return date_string

        start_date = current_date - timedelta(days=14)
        date_columns = [col for col in sales_df.columns if col != 'Barcode']

        barcodes = sales_df['Barcode']
        new_sales_df = sales_df.loc[:, conv_string(start_date):conv_string(current_date)]
        new_sales_df = new_sales_df.join(barcodes)

        new_sales_df = new_sales_df.set_index('Barcode').sum(axis=1).reset_index()
        new_sales_df.columns = ['Barcode', 'Total_Sales']

        merged_df = pd.merge(new_sales_df, retrieval_df[['Barcode', 'Product Name', 'Product Brand', 'MRP']],
                             on='Barcode', how='left')

        merged_df['Monetary_Value'] = merged_df['Total_Sales'] * merged_df['MRP']

        result_df = merged_df.sort_values('Monetary_Value', ascending=False)

        # print(result_df.to_string(index=False))

        value = result_df['Monetary_Value'].sum()
        # print(f"\nTotal Monetary Value for the last 15 days: ₹{value:.2f}")

        return value
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None