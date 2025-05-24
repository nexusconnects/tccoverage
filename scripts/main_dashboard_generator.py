import os
import json
import pandas as pd
import numpy as np # Added for type checking

# Import data loading functions
from scripts.load_data import (
    load_publisher_traffic,
    load_google_ads_data,
    load_call_tracking_data,
    load_sales_data
)

# Import KPI generation function
from scripts.process_metrics import generate_kpis

def convert_numpy_types_in_dict(data_dict):
    """
    Recursively converts numpy numeric types in a dictionary to standard Python types.
    This is to ensure JSON serializability.
    """
    if not isinstance(data_dict, dict):
        return data_dict

    new_dict = {}
    for k, v in data_dict.items():
        if isinstance(v, dict):
            new_dict[k] = convert_numpy_types_in_dict(v)
        elif isinstance(v, np.integer): # Handles np.int64, np.int32, etc.
            new_dict[k] = int(v)
        elif isinstance(v, np.floating): # Handles np.float64, np.float32, etc.
            new_dict[k] = float(v)
        elif isinstance(v, np.bool_):
            new_dict[k] = bool(v)
        elif isinstance(v, list):
            new_dict[k] = [convert_numpy_types_in_dict(i) if isinstance(i, dict) else (int(i) if isinstance(i, np.integer) else (float(i) if isinstance(i, np.floating) else i)) for i in v]
        else:
            new_dict[k] = v
    return new_dict

def main():
    """
    Main function to orchestrate data loading, processing, and saving results.
    """
    print("--- Starting Main Dashboard Generation Script ---")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Ensured output directory exists: {output_dir}")

    # Load all data sources
    print("Loading data sources...")
    publisher_df = load_publisher_traffic()
    google_ads_df = load_google_ads_data()
    call_tracking_df = load_call_tracking_data()
    sales_df = load_sales_data()

    data_dfs = {
        'publisher': publisher_df,
        'google': google_ads_df,
        'calls': call_tracking_df,
        'sales': sales_df
    }
    print("Data loading complete.")

    # Basic Validation
    if call_tracking_df.empty:
        print("Error: Call tracking data is empty. This is critical for KPI generation.")
        print("Please check the source file: data/call_tracking.csv")
        print("Exiting script.")
        return # Exit if critical data is missing

    # Generate KPIs and processed data
    print("Generating KPIs and processing data...")
    try:
        processed_results = generate_kpis(data_dfs)
        print("KPI generation and data processing complete.")
    except Exception as e:
        print(f"Error during KPI generation: {e}")
        print("Exiting script.")
        return

    # Save the results
    print("Saving processed results...")
    for key, value in processed_results.items():
        if isinstance(value, pd.DataFrame):
            filename = f"{key}.csv"
            filepath = os.path.join(output_dir, filename)
            try:
                value.to_csv(filepath, index=False)
                print(f"Successfully saved DataFrame to {filepath}")
            except Exception as e:
                print(f"Error saving DataFrame {key} to {filepath}: {e}")
        elif isinstance(value, dict):
            filename = f"{key}.json"
            filepath = os.path.join(output_dir, filename)
            try:
                # Convert numpy types before saving to JSON
                value_to_save = convert_numpy_types_in_dict(value)
                with open(filepath, 'w') as f:
                    json.dump(value_to_save, f, indent=4)
                print(f"Successfully saved dictionary to {filepath}")
            except Exception as e:
                print(f"Error saving dictionary {key} to {filepath}: {e}")
        else:
            print(f"Warning: Result item '{key}' is not a DataFrame or dictionary. Skipping save.")

    print("All results saved.")
    print("--- Main Dashboard Generation Script Finished ---")

if __name__ == "__main__":
    main()
