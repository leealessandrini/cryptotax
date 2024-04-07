import argparse
import pandas as pd


def aggregate_transactions(tx_df):
    """
    Aggregates and summarizes transactions by token, including net sales and
    PNL.

    Args:
        tx_df (pandas.DataFrame): DataFrame containing transaction data.

    Returns:
        pandas.DataFrame:
            Summarized data by token, with calculated net sales and PNL.
    """
    # Cast buy and sell dates to datetime
    tx_df["buy_date"] = pd.to_datetime(tx_df["buy_date"])
    tx_df["sale_date"] = pd.to_datetime(tx_df["sale_date"])
    # Calculate net sale (sale price minus fees)
    tx_df["net_sale"] = tx_df["sale_price"] * ((100 - tx_df["fee_percentage"]) / 100)
    # Calculate profit and loss (PNL)
    tx_df["pnl"] = tx_df["net_sale"] - tx_df["buy_price"]
    cols = [
        "token", "quantity", "date_acquired", "date_sold",
        "total_sale_proceeds", "total_cost_basis", "pnl"]
    aggregated_df = pd.DataFrame(columns=cols)
    aggregated_df["token"] = tx_df["token"].unique()
    # Iterate over each unique token and aggregate the transactions
    for token, group in tx_df.groupby("token"):
        # Get date acquired and sold
        # TODO: Add logic to separate short term and long term transactions
        if group["buy_date"].nunique() > 1:
            date_acquired = "Various"
        else:
            date_acquired = group["buy_date"].values[0]
        if group["sale_date"].nunique() > 1:
            date_sold = "Various"
        else:
            date_sold = group["sale_date"].values[0]
        # Add the result to the aggregate DataFrame
        aggregated_df.loc[
            aggregated_df["token"] == token, cols[1:]
        ] = [
            len(group),
            date_acquired,
            date_sold,
            round(group["net_sale"].sum()),
            round(group["buy_price"].sum()),
            round(group["pnl"].sum())]

    return aggregated_df


def parse_arguments():
    """
    Parse input arguments and return result.
    """
    parser = argparse.ArgumentParser(description="Process the path to transactions.")
    parser.add_argument(
        "-t", "--transactions", type=str, required=True,
        help="Path to the transactions file", dest="tx_filepath")
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help="Path to the output filepath", dest="output_filepath")

    return parser.parse_args()


def main():
    # Parse the arguments
    args = parse_arguments()
    # Access the "transactions" argument and load as DataFrame
    tx_df = pd.read_csv(args.tx_filepath)
    # Aggregate the transactions
    aggregate_df = aggregate_transactions(tx_df)
    # Write to file
    aggregate_df.to_csv(args.output_filepath, index=False)


if __name__ == "__main__":
    main()
