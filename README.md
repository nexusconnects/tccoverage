# Sales & Marketing KPI Dashboard Data Generator

## Overview

This project processes various marketing and sales data from CSV files to generate Key Performance Indicator (KPI) reports. It takes input data related to publisher traffic, Google Ads performance, call tracking, and sales conversions, then outputs aggregated campaign-level metrics and an overall performance summary.

## Project Structure

The repository is organized as follows:

*   `data/`: This directory contains the input CSV files required for processing.
    *   `publisher_traffic.csv`: Data from various publishers.
    *   `google_ads.csv`: Performance data from Google Ads campaigns.
    *   `call_tracking.csv`: Logs of calls received, including source and lead scores.
    *   `sales_data.csv`: Information on sales resulting from calls.
*   `scripts/`: This directory houses the Python scripts responsible for data loading, processing, and KPI generation.
    *   `load_data.py`: Contains functions to load and validate the input CSV files.
    *   `process_metrics.py`: Includes functions for data cleaning, transformation, merging, and KPI calculation.
    *   `main_dashboard_generator.py`: The main script that orchestrates the entire workflow from data loading to saving the final reports.
*   `output/`: This directory stores the generated reports, which include processed data in CSV format and summary KPIs in JSON format.

## Input Data File Schemas

The following are the expected column headers for each input CSV file:

*   **`publisher_traffic.csv`**:
    `date,publisher_id,publisher_name,campaign_id,impressions,clicks,cost,conversions_to_call_intent`

*   **`google_ads.csv`**:
    `date,campaign_name,ad_group_name,keyword,impressions,clicks,cost,calls_generated_directly`

*   **`call_tracking.csv`**:
    `call_id,timestamp,source,duration_seconds,lead_score,contact_phone_number`

*   **`sales_data.csv`**:
    `call_id,sale_timestamp,revenue_generated,product_sold`

## Setup & Dependencies

The primary dependency for this project is the `pandas` library for data manipulation.

To install the necessary dependencies, run:
```bash
pip install pandas
```

Ensure you have Python 3 installed.

## How to Run

1.  **Prepare Input Data:**
    Place your input CSV files (e.g., `publisher_traffic.csv`, `google_ads.csv`, `call_tracking.csv`, `sales_data.csv`) into the `data/` directory. Ensure they conform to the schemas defined above. Sample data is provided in the repository.

2.  **Execute the Main Script:**
    Navigate to the root directory of the project in your terminal and run the main generator script using the following command:

    ```bash
    python -m scripts.main_dashboard_generator
    ```

    This command ensures that the Python interpreter correctly handles module imports within the `scripts` package.

## Output Files

The processed reports will be saved in the `output/` directory:

*   **`output/publisher_campaign_kpis.csv`**: Contains campaign-level key performance indicators derived from publisher traffic data, including cost, impressions, clicks, leads, CPL, and CTR.
*   **`output/google_campaign_kpis.csv`**: Provides campaign-level key performance indicators for Google Ads campaigns, including similar metrics as the publisher report.
*   **`output/enriched_calls.csv`**: A detailed log of all calls, enriched with parsed source attribution (publisher or Google campaign) and merged with corresponding sales data (revenue, product sold).
*   **`output/overall_summary.json`**: A JSON file summarizing overall performance metrics, including total calls, total sales, total revenue generated, sales conversion rate, average revenue per sale, total ad spend (from publishers and Google), and the overall Return On Ad Spend (ROAS).

## Key KPIs Calculated (Examples)

The system calculates various KPIs to help assess marketing and sales performance. Some examples include:

*   **Cost Per Lead (CPL)**: The average cost to acquire a lead from a campaign.
*   **Click-Through Rate (CTR)**: The percentage of impressions that resulted in a click.
*   **Sales Conversion Rate**: The percentage of calls that resulted in a sale.
*   **Average Revenue Per Sale**: The average revenue generated from each successful sale.
*   **Return On Ad Spend (ROAS)**: The total revenue generated for every dollar spent on advertising, calculated as `(Total Revenue - Total Ad Spend) / Total Ad Spend`.

---
This README provides a comprehensive guide to understanding, setting up, and running the Sales & Marketing KPI Dashboard Data Generator.
