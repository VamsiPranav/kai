import pandas as pd

def load_and_analyze_data(file_path):
    df = pd.read_csv(file_path)
    lowest_stock_wrt_demand = df.sort_values('Stock wrt Demand', ascending=True).head(5)
    highest_stock_wrt_demand = df.sort_values('Stock wrt Demand', ascending=False).head(5)

    return lowest_stock_wrt_demand, highest_stock_wrt_demand

def main():
    file_path = '../data/retrieval_table.csv'
    lowest_stock_wrt_demand, highest_stock_wrt_demand = load_and_analyze_data(file_path);
    lowest_stock_wrt_demand.to_csv("../data_that_matters/low_stock_wrt_demand.csv", index=False)
    highest_stock_wrt_demand.to_csv("../data_that_matters/high_stock_wrt_demand.csv", index=False)

if __name__ == "__main__":
    main()