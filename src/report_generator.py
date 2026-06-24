import csv
import html
from pathlib import Path


def load_csv(csv_path):
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def money(value):
    return f"{int(float(value)):,}円"


def percent(value):
    return f"{float(value):.1f}%"


def build_ranking_rows(ranking):
    rows = []

    for row in ranking:
        rows.append(
            "<tr>"
            f"<td>{html.escape(row['rank'])}</td>"
            f"<td>{html.escape(row['title'])}</td>"
            f"<td>{html.escape(row['site'])}</td>"
            f"<td>{money(row['ebay_price_jpy'])}</td>"
            f"<td>{money(row['domestic_price_jpy'])}</td>"
            f"<td>{money(row['domestic_shipping_jpy'])}</td>"
            f"<td>{money(row['profit_jpy'])}</td>"
            f"<td>{percent(row['profit_rate'])}</td>"
            f"<td><a href=\"{html.escape(row['ebay_url'])}\">eBay</a></td>"
            f"<td><a href=\"{html.escape(row['domestic_url'])}\">国内仕入</a></td>"
            "</tr>"
        )

    return "\n".join(rows)


def build_html_report(candidate_count, ranking):
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>eBay利益発掘レポート</title>
  <style>
    body {{ font-family: sans-serif; margin: 32px; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .summary {{ margin-bottom: 24px; }}
  </style>
</head>
<body>
  <h1>eBay利益発掘レポート</h1>
  <div class="summary">
    <p>候補件数: {candidate_count}件</p>
    <p>利益商品件数: {len(ranking)}件</p>
  </div>
  <h2>利益ランキング</h2>
  <table>
    <thead>
      <tr>
        <th>順位</th>
        <th>商品名</th>
        <th>仕入先</th>
        <th>eBay売価</th>
        <th>国内仕入価格</th>
        <th>国内送料</th>
        <th>利益額</th>
        <th>利益率</th>
        <th>eBay URL</th>
        <th>国内仕入URL</th>
      </tr>
    </thead>
    <tbody>
      {build_ranking_rows(ranking)}
    </tbody>
  </table>
</body>
</html>
"""


def save_html_report(candidate_path, ranking_path, output_path):
    candidates = load_csv(candidate_path)
    ranking = load_csv(ranking_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_html_report(len(candidates), ranking),
        encoding="utf-8",
    )
    return len(candidates), len(ranking)


def main():
    project_root = Path(__file__).resolve().parent.parent
    candidate_count, ranking_count = save_html_report(
        project_root / "data" / "ebay_raw" / "ebay_candidates.csv",
        project_root / "data" / "processed" / "profit_ranking.csv",
        project_root / "reports" / "daily_report.html",
    )
    print(f"HTMLレポートを作成しました: 候補{candidate_count}件 / 利益商品{ranking_count}件")


if __name__ == "__main__":
    main()
