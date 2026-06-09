import csv
import json
from pathlib import Path

from ebay_fetcher import check_ebay_api_settings, fetch_ebay_items, save_products_csv


def load_settings(settings_path):
    with settings_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_products(csv_path):
    products = []

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required_fields = {"商品名", "仕入価格", "販売価格"}
        if not required_fields.issubset(reader.fieldnames or []):
            return products

        for row in reader:
            name = row["商品名"]
            purchase_price = int(row["仕入価格"])
            selling_price = int(row["販売価格"])
            profit = selling_price - purchase_price
            profit_rate = profit / purchase_price * 100
            score = profit * profit_rate

            products.append(
                {
                    "商品名": name,
                    "仕入価格": purchase_price,
                    "販売価格": selling_price,
                    "利益": profit,
                    "利益率": profit_rate,
                    "スコア": score,
                }
            )

    return products


def print_products(products):
    headers = ["商品名", "仕入価格", "販売価格", "利益", "利益率", "スコア"]
    rows = []
    for product in products:
        rows.append(
            [
                product["商品名"],
                str(product["仕入価格"]),
                str(product["販売価格"]),
                str(product["利益"]),
                f"{product['利益率']:.1f}",
                f"{product['スコア']:.1f}",
            ]
        )

    if not rows:
        print("表示対象の商品はありません。")
        return

    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]

    header_line = " | ".join(
        header.ljust(widths[index]) for index, header in enumerate(headers)
    )
    separator = "-+-".join("-" * width for width in widths)

    print(header_line)
    print(separator)

    for row in rows:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))

    total_profit = sum(product["利益"] for product in products)
    print()
    print(f"合計利益: {total_profit}")


def save_report(products, report_path):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["商品名", "仕入価格", "販売価格", "利益", "利益率", "スコア"]

    with report_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for product in products:
            writer.writerow(
                {
                    "商品名": product["商品名"],
                    "仕入価格": product["仕入価格"],
                    "販売価格": product["販売価格"],
                    "利益": product["利益"],
                    "利益率": f"{product['利益率']:.1f}",
                    "スコア": f"{product['スコア']:.1f}",
                }
            )


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "products.csv"
    settings_path = project_root / "config" / "settings.json"
    report_path = project_root / "reports" / "report.csv"

    settings = load_settings(settings_path)

    if not csv_path.exists():
        if not check_ebay_api_settings(settings):
            return
        items = fetch_ebay_items(settings)
        save_products_csv(items, csv_path)

    products = load_products(csv_path)
    if not products:
        print("利益分析用CSV形式ではありません。data/products.csv を確認してください。")
        return

    filtered_products = [
        product
        for product in products
        if product["利益率"] >= settings["min_profit_rate"]
        and product["利益"] >= settings["min_profit"]
    ]
    sorted_products = sorted(
        filtered_products,
        key=lambda product: product["スコア"],
        reverse=True,
    )
    save_report(sorted_products, report_path)
    print_products(sorted_products)


if __name__ == "__main__":
    main()
