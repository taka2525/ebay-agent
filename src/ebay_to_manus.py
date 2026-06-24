import csv
import json
from pathlib import Path

from manus_request import generate_manus_request_file


def load_json(json_path):
    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_ebay_products(input_path):
    with input_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_price(value):
    if value in (None, ""):
        return 0
    return float(value)


def convert_to_candidate_rows(products, exchange_rate):
    candidates = []

    for product in products:
        price_usd = parse_price(product.get("price"))
        candidates.append(
            {
                "title": product.get("title", ""),
                "ebay_price_jpy": round(price_usd * exchange_rate),
                "ebay_url": product.get("itemWebUrl", ""),
            }
        )

    return candidates


def save_candidates(candidates, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["title", "ebay_price_jpy", "ebay_url"]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidates)


def convert_ebay_products_for_manus(input_path, fees_path, candidate_output_path):
    products = load_ebay_products(input_path)
    fees = load_json(fees_path)
    exchange_rate = float(fees["exchange_rate"])
    candidates = convert_to_candidate_rows(products, exchange_rate)
    save_candidates(candidates, candidate_output_path)
    return candidates


def main():
    project_root = Path(__file__).resolve().parent.parent
    ebay_products_path = project_root / "data" / "products.csv"
    fees_path = project_root / "config" / "fees.json"
    candidate_output_path = (
        project_root / "data" / "manus_requests" / "ebay_candidates_for_manus.csv"
    )
    manus_request_output_path = (
        project_root / "data" / "manus_requests" / "manus_request_from_ebay.csv"
    )

    candidates = convert_ebay_products_for_manus(
        ebay_products_path,
        fees_path,
        candidate_output_path,
    )
    requests = generate_manus_request_file(
        candidate_output_path,
        manus_request_output_path,
    )

    print(f"eBay候補CSVをManus用形式へ変換しました: {candidate_output_path}")
    print(f"Manus依頼CSVを作成しました: {manus_request_output_path}")
    print(f"候補件数: {len(candidates)}件")
    print(f"依頼件数: {len(requests)}件")


if __name__ == "__main__":
    main()
