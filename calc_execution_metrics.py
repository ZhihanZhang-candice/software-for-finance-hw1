import argparse
import pandas as pd


def calc_execution_metrics(input_csv_file, output_metrics_file):
    """Calculate average execution metrics for each exchange."""

    # Read CSV file
    df = pd.read_csv(input_csv_file)

    # Calculate execution speed in seconds
    order_time = pd.to_datetime(df["OrderTransactTime"], format="%Y%m%d-%H:%M:%S.%f")
    execution_time = pd.to_datetime(df["ExecutionTransactTime"], format="%Y%m%d-%H:%M:%S.%f")

    df["ExecSpeedSecs"] = (execution_time - order_time).dt.total_seconds()

    # Calculate price improvement
    df["PriceImprovement"] = 0.0

    buy = df["Side"] == 1
    sell = df["Side"].isin([2, 5])

    df.loc[buy, "PriceImprovement"] = (
        df.loc[buy, "LimitPrice"] - df.loc[buy, "AvgPx"]
    )

    df.loc[sell, "PriceImprovement"] = (
        df.loc[sell, "AvgPx"] - df.loc[sell, "LimitPrice"]
    )

    # Calculate average metrics for each exchange
    result = df.groupby("LastMkt", as_index=False).agg(
        AvgPriceImprovement=("PriceImprovement", "mean"),
        AvgExecSpeedSecs=("ExecSpeedSecs", "mean")
    )

    # Save results
    result.to_csv(output_metrics_file, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate execution metrics by exchange"
    )

    parser.add_argument("--input_csv_file", required=True)
    parser.add_argument("--output_metrics_file", required=True)

    args = parser.parse_args()

    calc_execution_metrics(args.input_csv_file, args.output_metrics_file)


if __name__ == "__main__":
    main()