import csv
import json
from pathlib import Path


def load_json(json_path):
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_csv(csv_path):
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_int(value, default=0):
    if value in (None, ""):
        return default
    return int(float(value))


def index_requests_by_id(requests):
    return {row["request_id"]: row for row in requests}


def calculate_profit(request, result, fees):
    ebay_price_jpy = parse_int(request["ebay_price_jpy"])
    domestic_price_jpy = parse_int(result["price_jpy"])
    domestic_shipping_jpy = parse_int(
        result.get("shipping_jpy"),
        parse_int(fees["default_domestic_shipping_jpy"]),
    )
    ebay_fee_jpy = ebay_price_jpy * float(fees["ebay_fee_rate"])
    international_shipping_jpy = parse_int(fees["international_shipping_jpy"])
    packing_cost_jpy = parse_int(fees["packing_cost_jpy"])

    profit_jpy = (
        ebay_price_jpy
        - ebay_fee_jpy
        - international_shipping_jpy
        - packing_cost_jpy
        - domestic_price_jpy
        - domestic_shipping_jpy
    )
    profit_rate = profit_jpy / domestic_price_jpy * 100 if domestic_price_jpy else 0

    return {
        "title": request["title"],
        "site": result["site"],
        "domestic_price_jpy": domestic_price_jpy,
        "domestic_shipping_jpy": domestic_shipping_jpy,
        "ebay_price_jpy": ebay_price_jpy,
        "profit_jpy": round(profit_jpy),
        "profit_rate": round(profit_rate, 1),
        "ebay_url": request["ebay_url"],
        "domestic_url": result["url"],
    }


def calculate_profit_ranking(requests, results, fees):
    request_index = index_requests_by_id(requests)
    rows = []

    for result in results:
        request = request_index.get(result["request_id"])
        if not request:
            continue

        row = calculate_profit(request, result, fees)
        if (
            row["profit_jpy"] >= parse_int(fees["minimum_profit_jpy"])
            and row["profit_rate"] >= float(fees["minimum_profit_rate"])
        ):
            rows.append(row)

    rows.sort(key=lambda row: row["profit_jpy"], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank

    return rows


def save_profit_ranking(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank",
        "title",
        "site",
        "domestic_price_jpy",
        "domestic_shipping_jpy",
        "ebay_price_jpy",
        "profit_jpy",
        "profit_rate",
        "ebay_url",
        "domestic_url",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def create_profit_ranking(request_path, result_path, fees_path, output_path):
    requests = load_csv(request_path)
    results = load_csv(result_path)
    fees = load_json(fees_path)
    ranking = calculate_profit_ranking(requests, results, fees)
    save_profit_ranking(ranking, output_path)
    return ranking


def main():
    project_root = Path(__file__).resolve().parent.parent
    ranking = create_profit_ranking(
        project_root / "data" / "manus_requests" / "manus_request.csv",
        project_root / "data" / "manus_results" / "manus_results.csv",
        project_root / "config" / "fees.json",
        project_root / "data" / "processed" / "profit_ranking.csv",
    )
    print(f"利益ランキングCSVを作成しました: {len(ranking)}件")


if __name__ == "__main__":
    main()
