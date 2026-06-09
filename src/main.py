import csv
from pathlib import Path


def load_products(csv_path):
    products = []

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row["商品名"]
            purchase_price = int(row["仕入価格"])
            selling_price = int(row["販売価格"])
            profit = selling_price - purchase_price
            profit_rate = profit / purchase_price * 100

            products.append(
                {
                    "商品名": name,
                    "仕入価格": purchase_price,
                    "販売価格": selling_price,
                    "利益": profit,
                    "利益率": profit_rate,
                }
            )

    return products


def print_products(products):
    headers = ["商品名", "仕入価格", "販売価格", "利益", "利益率"]
    rows = []
    for product in products:
        rows.append(
            [
                product["商品名"],
                str(product["仕入価格"]),
                str(product["販売価格"]),
                str(product["利益"]),
                f"{product['利益率']:.1f}",
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


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "products.csv"
    products = load_products(csv_path)
    filtered_products = [
        product for product in products if product["利益率"] >= 70
    ]
    sorted_products = sorted(
        filtered_products,
        key=lambda product: product["利益率"],
        reverse=True,
    )
    print_products(sorted_products)


if __name__ == "__main__":
    main()
