import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import warnings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)


def load_data():
    try:
        product_catalogue = pd.read_csv("../data/product_catalogue.csv")
        daily_sales = pd.read_csv("../data/historic_daily_sales.csv", index_col=0)
        return product_catalogue, daily_sales
    except FileNotFoundError as e:
        logging.error(f"Error loading data: {e}")
        raise


def prepare_data_for_prophet(daily_sales):
    melted_data = daily_sales.reset_index().melt(id_vars='Barcode', var_name='ds', value_name='y')
    melted_data['ds'] = pd.to_datetime(melted_data['ds'])
    melted_data['y'] = pd.to_numeric(melted_data['y'], errors='coerce')
    melted_data = melted_data.dropna()
    return melted_data


def train_model_and_forecast(data, product, forecast_windows):
    model_data = data[data['Barcode'] == product].sort_values('ds')

    if len(model_data) < 30:  # Require at least 30 data points for prediction
        return pd.Series([0] * len(forecast_windows), index=forecast_windows)

    model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True,
                    seasonality_mode='multiplicative', interval_width=0.95)
    model.fit(model_data)

    last_date = model_data['ds'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=75)
    future = pd.DataFrame({'ds': future_dates})
    forecast = model.predict(future)

    window_predictions = []
    for i, window in enumerate(forecast_windows):
        start_idx = i * 15
        end_idx = start_idx + 15
        window_sum = forecast['yhat'][start_idx:end_idx].sum()
        window_predictions.append(max(round(window_sum), 0))

    return pd.Series(window_predictions, index=forecast_windows)


def create_demand_prediction_table(product_catalogue, daily_sales):
    melted_data = prepare_data_for_prophet(daily_sales)

    forecast_windows = ['1-15 Days', '16-30 Days', '31-45 Days', '46-60 Days', '61-75 Days']

    predictions = []
    total_products = len(product_catalogue)

    for index, product in enumerate(product_catalogue['Barcode'], 1):
        try:
            product_predictions = train_model_and_forecast(melted_data, product, forecast_windows)
            predictions.append([product] + list(product_predictions))
            if index % 10 == 0:
                logging.info(f"Processed {index}/{total_products} products")
        except Exception as e:
            logging.warning(f"Error predicting for product {product}: {e}")
            predictions.append([product] + [0] * len(forecast_windows))

    columns = ['Barcode'] + forecast_windows
    prediction_df = pd.DataFrame(predictions, columns=columns)

    return prediction_df


def validate_predictions(prediction_df, daily_sales):
    historical_totals = daily_sales.sum(axis=1)
    predicted_totals = prediction_df.iloc[:, 1:].sum(axis=1)

    ratio = predicted_totals.mean() / historical_totals.mean()
    logging.info(f"Ratio of predicted to historical demand: {ratio:.2f}")

    if ratio < 0.5 or ratio > 2:
        logging.warning("Predicted demand seems significantly different from historical demand")

    return ratio


def main():
    try:
        product_catalogue, daily_sales = load_data()
        demand_prediction = create_demand_prediction_table(product_catalogue, daily_sales)

        validation_ratio = validate_predictions(demand_prediction, daily_sales)

        # Adjust predictions
        if validation_ratio < 0.5:
            logging.info("Adjusting predictions upward")
            demand_prediction.iloc[:, 1:] *= (1 / validation_ratio)
        elif validation_ratio > 2:
            logging.info("Adjusting predictions downward")
            demand_prediction.iloc[:, 1:] *= (2 / validation_ratio)

        demand_prediction.iloc[:, 1:] = demand_prediction.iloc[:, 1:].round().astype(int)

        demand_prediction.to_csv("../data/15_day_demand_prediction_windows.txt", index=False)

        # logging.info("Medium-term demand prediction table (15-day windows) has been created.")
        #
        # # Print some statistics
        # logging.info("\nSummary statistics of the predictions:")
        # logging.info(demand_prediction.describe())
        #
        # # Print sample rows
        # logging.info("\nSample rows from the prediction table:")
        # logging.info(demand_prediction.sample(5).to_string())
        #
        # # Print top 5 products by predicted demand for 61-75 days
        # logging.info("\nTop 5 products by predicted demand for 61-75 days:")
        # logging.info(demand_prediction.nlargest(5, '61-75 Days')[['Barcode', '61-75 Days']])

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()