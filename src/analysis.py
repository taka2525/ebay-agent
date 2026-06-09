import csv
from collections import Counter
from pathlib import Path


def load_products(csv_path):
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def parse_price(value):
    if not value:
        return None
    return float(value)


def get_category(category_path):
    if not category_path:
        return "未分類"
    return category_path.split(" > ")[0]


def get_country(item_location):
    if not item_location:
        return "不明"
    return item_location.split(",")[-1].strip() or "不明"


def is_new_condition(condition):
    return condition.strip().lower().startswith("new")


def is_used_condition(condition):
    return condition.strip().lower().startswith("used")


def write_report_summary(products, report_path):
    report_path.parent.mkdir(parents=True, exist_ok=True)

    category_counts = Counter(get_category(row["categoryPath"]) for row in products)
    country_counts = Counter(get_country(row["itemLocation"]) for row in products)
    prices = [
        price
        for price in (parse_price(row["price"]) for row in products)
        if price is not None
    ]
    total_count = len(products)
    new_count = sum(1 for row in products if is_new_condition(row["condition"]))
    used_count = sum(1 for row in products if is_used_condition(row["condition"]))
    new_rate = new_count / total_count * 100 if total_count else 0
    used_rate = used_count / total_count * 100 if total_count else 0
    average_price = sum(prices) / len(prices) if prices else 0
    max_price = max(prices) if prices else 0
    min_price = min(prices) if prices else 0

    with report_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["集計種別", "項目", "値"])

        for category, count in category_counts.most_common():
            writer.writerow(["カテゴリ別件数", category, count])

        for country, count in country_counts.most_common():
            writer.writerow(["国別件数", country, count])

        writer.writerow(["新品割合", "全体", f"{new_rate:.1f}%"])
        writer.writerow(["中古割合", "全体", f"{used_rate:.1f}%"])
        writer.writerow(["平均価格", "全体", f"{average_price:.2f}"])
        writer.writerow(["最高価格", "全体", f"{max_price:.2f}"])
        writer.writerow(["最低価格", "全体", f"{min_price:.2f}"])


def write_top_sellers(products, top_sellers_path):
    top_sellers_path.parent.mkdir(parents=True, exist_ok=True)
    seller_counts = Counter(
        row["sellerUsername"] or "不明"
        for row in products
    )

    with top_sellers_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["sellerUsername", "出品数"])
        for seller, count in seller_counts.most_common(20):
            writer.writerow([seller, count])


def main():
    project_root = Path(__file__).resolve().parent.parent
    products_path = project_root / "data" / "products.csv"
    report_summary_path = project_root / "reports" / "report_summary.csv"
    top_sellers_path = project_root / "reports" / "top_sellers.csv"

    products = load_products(products_path)
    write_report_summary(products, report_summary_path)
    write_top_sellers(products, top_sellers_path)

    print(f"分析サマリーを保存しました: {report_summary_path}")
    print(f"上位セラー一覧を保存しました: {top_sellers_path}")


if __name__ == "__main__":
    main()
