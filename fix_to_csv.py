import argparse
import csv


def parse_fix_message(line):
    """Convert one FIX log line to a dictionary of tags."""
    fix_part = line.split(" : ", 1)[-1]
    message = {}
    for field in fix_part.strip().split("\x01"):
        if "=" in field:
            tag, value = field.split("=", 1)
            message[tag] = value
    return message


def fix_to_csv(input_fix_file, output_csv_file):
    """Write one CSV row for each matched full fill."""
    orders = {}
    fills = []
    with open(input_fix_file, "r", encoding="utf-8") as file:
        for line in file:
            message = parse_fix_message(line)
            if message.get("35") == "D" and message.get("40") == "2":
                order_id = message.get("11")
                if order_id:
                    orders[order_id] = message
            elif (message.get("35") == "8"
                  and message.get("150") == "2"
                  and message.get("39") == "2"
                  and message.get("40") == "2"):
                fills.append(message)

    columns = ["OrderID", "OrderTransactTime", "ExecutionTransactTime",
               "Symbol", "Side", "OrderQty", "LimitPrice", "AvgPx", "LastMkt"]
    with open(output_csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for fill in fills:
            order_id = fill.get("11")
            if order_id not in orders:
                continue
            order = orders[order_id]
            writer.writerow({
                "OrderID": order_id,
                "OrderTransactTime": order.get("60", ""),
                "ExecutionTransactTime": fill.get("60", ""),
                "Symbol": order.get("55", ""),
                "Side": order.get("54", ""),
                "OrderQty": order.get("38", ""),
                "LimitPrice": order.get("44", ""),
                "AvgPx": fill.get("6", ""),
                "LastMkt": fill.get("30", ""),
            })


def main():
    """Read arguments and convert the FIX file."""
    parser = argparse.ArgumentParser(description="Convert FIX fills to CSV")
    parser.add_argument("--input_fix_file", required=True)
    parser.add_argument("--output_csv_file", required=True)
    args = parser.parse_args()
    fix_to_csv(args.input_fix_file, args.output_csv_file)


if __name__ == "__main__":
    main()
