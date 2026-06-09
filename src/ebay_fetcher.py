import csv
from pathlib import Path


SAMPLE_PRODUCTS = [
    {"商品名": "ゲームソフト", "仕入価格": 1200, "販売価格": 2500},
    {"商品名": "フィギュア", "仕入価格": 3000, "販売価格": 5200},
    {"商品名": "腕時計", "仕入価格": 4500, "販売価格": 7800},
]


def generate_products_csv(csv_path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        fieldnames = ["商品名", "仕入価格", "販売価格"]
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(SAMPLE_PRODUCTS)


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "products.csv"
    generate_products_csv(csv_path)
    print(f"CSVを生成しました: {csv_path}")


if __name__ == "__main__":
    main()
