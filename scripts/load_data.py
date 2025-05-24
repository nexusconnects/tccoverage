import pandas as pd

def load_csv_data(file_path: str, required_columns: list = None) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame with error handling and column validation.

    Args:
        file_path (str): The path to the CSV file.
        required_columns (list, optional): A list of column names that must be present
                                           in the CSV. Defaults to None.

    Returns:
        pd.DataFrame: The loaded DataFrame, or an empty DataFrame if loading fails
                      or required columns are missing.
    """
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            print(f"Warning: Loaded file {file_path} is empty.")
            return df

        if required_columns:
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"Error: File {file_path} is missing required columns: {missing_columns}")
                return pd.DataFrame()  # Return empty DataFrame

        print(f"Successfully loaded {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()  # Return empty DataFrame
    except Exception as e:
        print(f"An unexpected error occurred while loading {file_path}: {e}")
        return pd.DataFrame()  # Return empty DataFrame

def load_publisher_traffic(file_path: str = "data/publisher_traffic.csv") -> pd.DataFrame:
    """
    Loads publisher traffic data from a CSV file.

    Args:
        file_path (str, optional): Path to the publisher traffic CSV.
                                   Defaults to "data/publisher_traffic.csv".

    Returns:
        pd.DataFrame: Loaded DataFrame or empty DataFrame on error.
    """
    required_columns = [
        'date', 'publisher_id', 'publisher_name', 'campaign_id',
        'impressions', 'clicks', 'cost', 'conversions_to_call_intent'
    ]
    return load_csv_data(file_path, required_columns)

def load_google_ads_data(file_path: str = "data/google_ads.csv") -> pd.DataFrame:
    """
    Loads Google Ads data from a CSV file.

    Args:
        file_path (str, optional): Path to the Google Ads CSV.
                                   Defaults to "data/google_ads.csv".

    Returns:
        pd.DataFrame: Loaded DataFrame or empty DataFrame on error.
    """
    required_columns = [
        'date', 'campaign_name', 'ad_group_name', 'keyword',
        'impressions', 'clicks', 'cost', 'calls_generated_directly'
    ]
    return load_csv_data(file_path, required_columns)

def load_call_tracking_data(file_path: str = "data/call_tracking.csv") -> pd.DataFrame:
    """
    Loads call tracking data from a CSV file.

    Args:
        file_path (str, optional): Path to the call tracking CSV.
                                   Defaults to "data/call_tracking.csv".

    Returns:
        pd.DataFrame: Loaded DataFrame or empty DataFrame on error.
    """
    required_columns = [
        'call_id', 'timestamp', 'source', 'duration_seconds',
        'lead_score', 'contact_phone_number'
    ]
    return load_csv_data(file_path, required_columns)

def load_sales_data(file_path: str = "data/sales_data.csv") -> pd.DataFrame:
    """
    Loads sales data from a CSV file.

    Args:
        file_path (str, optional): Path to the sales data CSV.
                                   Defaults to "data/sales_data.csv".

    Returns:
        pd.DataFrame: Loaded DataFrame or empty DataFrame on error.
    """
    required_columns = [
        'call_id', 'sale_timestamp', 'revenue_generated', 'product_sold'
    ]
    return load_csv_data(file_path, required_columns)

if __name__ == "__main__":
    print("--- Loading Data ---")

    publisher_df = load_publisher_traffic()
    if not publisher_df.empty:
        print(f"Publisher traffic data shape: {publisher_df.shape}")

    google_ads_df = load_google_ads_data()
    if not google_ads_df.empty:
        print(f"Google Ads data shape: {google_ads_df.shape}")

    call_tracking_df = load_call_tracking_data()
    if not call_tracking_df.empty:
        print(f"Call tracking data shape: {call_tracking_df.shape}")

    sales_df = load_sales_data()
    if not sales_df.empty:
        print(f"Sales data shape: {sales_df.shape}")

    print("--- Data Loading Complete ---")
