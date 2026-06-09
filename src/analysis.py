import csv
from collections import Counter
from pathlib import Path
import re


ITEM_TYPE_PATTERNS = {
    "T-Shirt": r"\bt[-\s]?shirts?\b",
    "Cap": r"\bcaps?\b",
    "Hat": r"\bhats?\b",
    "Hoodie": r"\bhoodies?\b",
    "Jacket": r"\bjackets?\b",
    "Gloves": r"\bgloves?\b",
    "Boots": r"\bboots?\b",
    "Pants": r"\bpants?\b",
}


def load_products(csv_path):
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def load_settings(settings_path):
    import json

    with settings_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def slugify_keyword(keyword):
    slug = re.sub(r"[^A-Za-z0-9]+", "_", keyword).strip("_")
    return slug or "keyword"


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


def get_brand(product, search_keywords):
    search_keyword = product.get("searchKeyword", "")
    if search_keyword:
        return search_keyword

    title = product.get("title", "").lower()
    for keyword in search_keywords:
        if keyword.lower() in title:
            return keyword

    return "不明"


def get_price_band(price):
    if price is None:
        return "価格不明"
    if price < 20:
        return "0-20ドル"
    if price < 50:
        return "20-50ドル"
    if price < 100:
        return "50-100ドル"
    return "100ドル以上"


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


def write_market_report(products, report_path, search_keywords):
    report_path.parent.mkdir(parents=True, exist_ok=True)

    category_counts = Counter(get_category(row["categoryPath"]) for row in products)
    brand_counts = Counter(get_brand(row, search_keywords) for row in products)
    price_band_counts = Counter(
        get_price_band(parse_price(row["price"]))
        for row in products
    )
    seller_count = len(
        {
            row["sellerUsername"]
            for row in products
            if row.get("sellerUsername")
        }
    )
    title_counts = Counter(row["title"] for row in products if row.get("title"))
    low_listing_titles = [
        (title, count)
        for title, count in title_counts.most_common()
        if count <= 3
    ]

    with report_path.open("w", encoding="utf-8") as file:
        file.write("# Market Report\n\n")
        file.write(f"分析対象件数: {len(products)}件\n\n")

        file.write("## 1. カテゴリ別件数\n\n")
        for category, count in category_counts.most_common():
            file.write(f"- {category}: {count}件\n")

        file.write("\n## 2. ブランド別件数\n\n")
        for brand, count in brand_counts.most_common():
            file.write(f"- {brand}: {count}件\n")

        file.write("\n## 3. 価格帯別件数\n\n")
        for price_band in ["0-20ドル", "20-50ドル", "50-100ドル", "100ドル以上", "価格不明"]:
            file.write(f"- {price_band}: {price_band_counts[price_band]}件\n")

        file.write("\n## 4. 出品者数\n\n")
        file.write(f"{seller_count}セラー\n")

        file.write("\n## 5. 出品数が3件以下の商品タイトル一覧\n\n")
        for title, count in low_listing_titles:
            file.write(f"- {title}: {count}件\n")

        file.write("\n## 6. 商品タイトル出現回数ランキング\n\n")
        for rank, (title, count) in enumerate(title_counts.most_common(), start=1):
            file.write(f"{rank}. {title}: {count}件\n")


def write_item_type_report(products, report_path):
    report_path.parent.mkdir(parents=True, exist_ok=True)
    item_type_prices = {item_type: [] for item_type in ITEM_TYPE_PATTERNS}

    for product in products:
        title = product.get("title", "")
        price = parse_price(product.get("price", ""))
        for item_type, pattern in ITEM_TYPE_PATTERNS.items():
            if re.search(pattern, title, re.IGNORECASE):
                item_type_prices[item_type].append(price)

    with report_path.open("w", encoding="utf-8") as file:
        file.write("# Item Type Report\n\n")
        file.write(f"分析対象件数: {len(products)}件\n\n")
        for item_type in ITEM_TYPE_PATTERNS:
            prices = [
                price
                for price in item_type_prices[item_type]
                if price is not None
            ]
            average_price = sum(prices) / len(prices) if prices else 0
            max_price = max(prices) if prices else 0
            min_price = min(prices) if prices else 0

            file.write(f"## {item_type}\n\n")
            file.write(f"件数: {len(item_type_prices[item_type])}\n")
            file.write(f"平均価格: {average_price:.2f}ドル\n")
            file.write(f"最高価格: {max_price:.2f}ドル\n")
            file.write(f"最低価格: {min_price:.2f}ドル\n\n")


def group_products_by_keyword(products):
    grouped_products = {}
    for product in products:
        keyword = product.get("searchKeyword") or "all"
        grouped_products.setdefault(keyword, []).append(product)
    return grouped_products


def main():
    project_root = Path(__file__).resolve().parent.parent
    products_path = project_root / "data" / "products.csv"
    settings_path = project_root / "config" / "settings.json"
    market_report_path = project_root / "reports" / "market_report.txt"
    item_type_report_path = project_root / "reports" / "item_type_report.txt"

    products = load_products(products_path)
    settings = load_settings(settings_path)
    search_keywords = settings.get("search_keywords", [])
    grouped_products = group_products_by_keyword(products)
    write_market_report(products, market_report_path, search_keywords)
    write_item_type_report(products, item_type_report_path)

    for keyword, keyword_products in grouped_products.items():
        keyword_slug = slugify_keyword(keyword)
        report_summary_path = (
            project_root / "reports" / f"{keyword_slug}_report_summary.csv"
        )
        top_sellers_path = project_root / "reports" / f"{keyword_slug}_top_sellers.csv"

        write_report_summary(keyword_products, report_summary_path)
        write_top_sellers(keyword_products, top_sellers_path)

        print(f"{keyword}: 分析サマリーを保存しました: {report_summary_path}")
        print(f"{keyword}: 上位セラー一覧を保存しました: {top_sellers_path}")

    print(f"市場レポートを保存しました: {market_report_path}")
    print(f"アイテム種別レポートを保存しました: {item_type_report_path}")


if __name__ == "__main__":
    main()
