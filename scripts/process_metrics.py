import pandas as pd
from scripts.load_data import (
    load_publisher_traffic,
    load_google_ads_data,
    load_call_tracking_data,
    load_sales_data
)

def parse_call_source(source_str: str) -> tuple:
    """
    Parses a call source string to determine its type and identifier.

    Args:
        source_str (str): The source string from call tracking data.
                          Expected formats: 'publisher_campaignid' or 'google_campaignname'.

    Returns:
        tuple: (source_type, source_identifier)
               e.g., ('publisher', 'campaignid') or ('google', 'campaignname')
               Returns ('unknown', source_str) if format is not recognized.
    """
    if pd.isna(source_str):
        return 'unknown', None
    if source_str.startswith('publisher_'):
        return 'publisher', source_str.replace('publisher_', '', 1)
    elif source_str.startswith('google_'):
        return 'google', source_str.replace('google_', '', 1)
    else:
        return 'unknown', source_str

def generate_kpis(data_dfs: dict) -> dict:
    """
    Processes loaded dataframes to generate key performance indicators (KPIs).

    Args:
        data_dfs (dict): A dictionary of pandas DataFrames containing:
            'publisher': publisher_df,
            'google': google_df,
            'calls': calls_df,
            'sales': sales_df

    Returns:
        dict: A dictionary containing processed DataFrames and KPIs:
            'publisher_campaign_kpis': DataFrame with publisher campaign KPIs,
            'google_campaign_kpis': DataFrame with Google Ads campaign KPIs,
            'enriched_calls': DataFrame of calls merged with sales and parsed source,
            'overall_summary': Dictionary with overall performance metrics.
    """
    publisher_df = data_dfs['publisher'].copy()
    google_df = data_dfs['google'].copy()
    calls_df = data_dfs['calls'].copy()
    sales_df = data_dfs['sales'].copy()

    # --- Data Type Conversions & Cleaning ---
    print("Starting data type conversions and cleaning...")

    # Publisher data
    if not publisher_df.empty:
        publisher_df['date'] = pd.to_datetime(publisher_df['date'])
        publisher_df['impressions'] = pd.to_numeric(publisher_df['impressions'], errors='coerce').fillna(0).astype(int)
        publisher_df['clicks'] = pd.to_numeric(publisher_df['clicks'], errors='coerce').fillna(0).astype(int)
        publisher_df['cost'] = pd.to_numeric(publisher_df['cost'], errors='coerce').fillna(0).astype(float)
        publisher_df['conversions_to_call_intent'] = pd.to_numeric(publisher_df['conversions_to_call_intent'], errors='coerce').fillna(0).astype(int)
        print("Publisher data types converted.")

    # Google Ads data
    if not google_df.empty:
        google_df['date'] = pd.to_datetime(google_df['date'])
        google_df['impressions'] = pd.to_numeric(google_df['impressions'], errors='coerce').fillna(0).astype(int)
        google_df['clicks'] = pd.to_numeric(google_df['clicks'], errors='coerce').fillna(0).astype(int)
        google_df['cost'] = pd.to_numeric(google_df['cost'], errors='coerce').fillna(0).astype(float)
        google_df['calls_generated_directly'] = pd.to_numeric(google_df['calls_generated_directly'], errors='coerce').fillna(0).astype(int)
        print("Google Ads data types converted.")

    # Call tracking data
    if not calls_df.empty:
        calls_df['timestamp'] = pd.to_datetime(calls_df['timestamp'])
        calls_df['duration_seconds'] = pd.to_numeric(calls_df['duration_seconds'], errors='coerce').fillna(0)
        calls_df['lead_score'] = pd.to_numeric(calls_df['lead_score'], errors='coerce').fillna(0)
        print("Call tracking data types converted.")

    # Sales data
    if not sales_df.empty:
        sales_df['sale_timestamp'] = pd.to_datetime(sales_df['sale_timestamp'])
        sales_df['revenue_generated'] = pd.to_numeric(sales_df['revenue_generated'], errors='coerce').fillna(0).astype(float)
        print("Sales data types converted.")

    # --- Prepare Call Data for Merging ---
    if not calls_df.empty:
        parsed_sources = calls_df['source'].apply(parse_call_source)
        calls_df['source_type'] = parsed_sources.apply(lambda x: x[0])
        calls_df['source_campaign_id_or_name'] = parsed_sources.apply(lambda x: x[1])
        print("Call source parsed.")

    # --- Merge Call Data with Sales Data ---
    if not calls_df.empty and not sales_df.empty:
        calls_df = pd.merge(calls_df, sales_df, on='call_id', how='left')
        calls_df.rename(columns={'revenue_generated': 'sale_revenue', 'product_sold': 'sale_product'}, inplace=True)
        calls_df['sale_revenue'] = calls_df['sale_revenue'].fillna(0)
        print("Calls and Sales data merged.")
    elif not calls_df.empty:
        # If sales_df is empty, ensure these columns exist for consistency
        calls_df['sale_revenue'] = 0.0
        calls_df['sale_product'] = None
        print("Sales data is empty. Added placeholder columns to calls_df.")


    # --- Calculate Publisher-Specific KPIs ---
    publisher_campaign_kpis_df = pd.DataFrame()
    if not publisher_df.empty:
        publisher_summary = publisher_df.groupby('campaign_id').agg(
            total_cost=('cost', 'sum'),
            total_impressions=('impressions', 'sum'),
            total_clicks=('clicks', 'sum'),
            total_leads=('conversions_to_call_intent', 'sum')
        ).reset_index()
        publisher_summary['cpl'] = publisher_summary.apply(
            lambda row: row['total_cost'] / row['total_leads'] if row['total_leads'] > 0 else 0, axis=1
        )
        publisher_summary['ctr'] = publisher_summary.apply(
            lambda row: row['total_clicks'] / row['total_impressions'] if row['total_impressions'] > 0 else 0, axis=1
        )
        publisher_campaign_kpis_df = publisher_summary
        print("Publisher campaign KPIs calculated.")

    # --- Calculate Google Ads-Specific KPIs ---
    google_campaign_kpis_df = pd.DataFrame()
    if not google_df.empty:
        google_summary = google_df.groupby('campaign_name').agg(
            total_cost=('cost', 'sum'),
            total_impressions=('impressions', 'sum'),
            total_clicks=('clicks', 'sum'),
            total_leads=('calls_generated_directly', 'sum')
        ).reset_index()
        google_summary['cpl'] = google_summary.apply(
            lambda row: row['total_cost'] / row['total_leads'] if row['total_leads'] > 0 else 0, axis=1
        )
        google_summary['ctr'] = google_summary.apply(
            lambda row: row['total_clicks'] / row['total_impressions'] if row['total_impressions'] > 0 else 0, axis=1
        )
        google_campaign_kpis_df = google_summary
        print("Google Ads campaign KPIs calculated.")

    # --- Integrate Call Data with Ad Spend (Simplified Attribution) ---
    # This section is more for preparing 'enriched_calls_df' for potential future use.
    # The actual cost association for ROAS will use the campaign KPIs already calculated.
    enriched_calls_df = calls_df.copy() # Already includes sales data
    print("Enriched calls DataFrame prepared (includes sales data and parsed source).")

    # --- Calculate Overall/Aggregated KPIs ---
    total_calls = len(calls_df) if not calls_df.empty else 0
    total_sales = calls_df['sale_revenue'].gt(0).sum() if not calls_df.empty else 0
    total_revenue = calls_df['sale_revenue'].sum() if not calls_df.empty else 0

    sales_conversion_rate = total_sales / total_calls if total_calls > 0 else 0
    average_revenue_per_sale = total_revenue / total_sales if total_sales > 0 else 0

    total_publisher_cost = publisher_campaign_kpis_df['total_cost'].sum() if not publisher_campaign_kpis_df.empty else 0
    total_google_cost = google_campaign_kpis_df['total_cost'].sum() if not google_campaign_kpis_df.empty else 0
    total_ad_spend = total_publisher_cost + total_google_cost

    # ROAS calculation: (Total Revenue from Calls - Total Ad Spend) / Total Ad Spend
    # This simplified ROAS assumes all sales revenue can be attributed to the ad spend captured.
    # A more robust ROAS would require more granular attribution.
    overall_roas = (total_revenue - total_ad_spend) / total_ad_spend if total_ad_spend > 0 else 0
    
    # If total_revenue comes only from sales that are linked to calls, and calls are linked to campaigns,
    # then this ROAS is (total_revenue_from_tracked_calls - total_ad_spend) / total_ad_spend.
    # If revenue is less than ad_spend, ROAS will be negative.

    overall_summary_kpis = {
        'total_calls': total_calls,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'sales_conversion_rate': sales_conversion_rate,
        'average_revenue_per_sale': average_revenue_per_sale,
        'total_publisher_cost': total_publisher_cost,
        'total_google_cost': total_google_cost,
        'total_ad_spend': total_ad_spend,
        'overall_roas': overall_roas # (Revenue - Cost) / Cost
    }
    print("Overall summary KPIs calculated.")

    return {
        'publisher_campaign_kpis': publisher_campaign_kpis_df,
        'google_campaign_kpis': google_campaign_kpis_df,
        'enriched_calls': enriched_calls_df, # This is calls_df after merging with sales and parsing source
        'overall_summary': overall_summary_kpis
    }

if __name__ == "__main__":
    print("--- Starting Metric Processing Script ---")

    # Load data
    print("Loading data using functions from load_data.py...")
    publisher_df = load_publisher_traffic()
    google_df = load_google_ads_data()
    calls_df = load_call_tracking_data()
    sales_df = load_sales_data()

    if publisher_df.empty and google_df.empty and calls_df.empty and sales_df.empty:
        print("All dataframes are empty. Exiting script.")
    else:
        data_dfs = {
            'publisher': publisher_df,
            'google': google_df,
            'calls': calls_df,
            'sales': sales_df
        }

        print("\n--- Generating KPIs ---")
        kpi_results = generate_kpis(data_dfs)

        print("\n--- KPI Generation Complete ---")
        print("\nResults Overview:")

        print("\nPublisher Campaign KPIs:")
        if not kpi_results['publisher_campaign_kpis'].empty:
            print(kpi_results['publisher_campaign_kpis'].head())
            print(f"Shape: {kpi_results['publisher_campaign_kpis'].shape}")
        else:
            print("No publisher campaign KPIs generated (input might be empty).")

        print("\nGoogle Ads Campaign KPIs:")
        if not kpi_results['google_campaign_kpis'].empty:
            print(kpi_results['google_campaign_kpis'].head())
            print(f"Shape: {kpi_results['google_campaign_kpis'].shape}")
        else:
            print("No Google Ads campaign KPIs generated (input might be empty).")

        print("\nEnriched Calls Data (first 5 rows):")
        if not kpi_results['enriched_calls'].empty:
            print(kpi_results['enriched_calls'].head())
            print(f"Shape: {kpi_results['enriched_calls'].shape}")
        else:
            print("No enriched calls data generated (input might be empty).")

        print("\nOverall Summary KPIs:")
        for key, value in kpi_results['overall_summary'].items():
            print(f"  {key}: {value}")

    print("\n--- Metric Processing Script Finished ---")
