# eBay販売支援システム

目的：
eBayで売れているが出品数の少ない商品を抽出する。

将来的な機能：
- eBay API連携
- メルカリ価格調査
- ヤフオク価格調査
- 利益計算
- レポート出力

Gitで管理します。
Pythonで開発します。

## 実行方法

以下のコマンドで、`data/products.csv` を読み込み、利益計算の結果を表示します。

```bash
python3 src/main.py
```

## レポート出力

`src/main.py` を実行すると、条件に合った商品一覧を `reports/report.csv` に保存します。

出力列は以下です。

```text
商品名,仕入価格,販売価格,利益,利益率,スコア
```

## eBay API設定

将来的にeBay APIから商品データを取得するため、`config/settings.json` に以下の設定を用意しています。

```json
{
  "ebay_app_id": "",
  "ebay_environment": "sandbox",
  "search_keywords": [
    "KTM",
    "KTM PowerWear",
    "Dainese",
    "Alpinestars"
  ]
}
```

`ebay_app_id` にはeBay Developer Programで取得したApp IDを入力します。

`ebay_environment` は検証用の場合は `sandbox`、本番用の場合は `production` を指定します。

Client SecretはGitHubへ保存しないため、実行時に環境変数 `EBAY_CLIENT_SECRET` で指定します。

```bash
EBAY_CLIENT_SECRET="your_client_secret" python3 src/ebay_fetcher.py
```

`src/ebay_fetcher.py` は `search_keywords` の各キーワードでeBay Browse APIを検索し、キーワードごとに最大200件を取得します。

取得結果は `data/products_キーワード.csv` と、全キーワードをまとめた `data/products.csv` に保存します。

### eBay取得CSVからManus依頼CSVを作成

`src/ebay_fetcher.py` が作成した `data/products.csv` を、Manus調査に渡せる形式へ変換します。

```bash
python3 src/ebay_to_manus.py
```

出力ファイル:

```text
data/manus_requests/ebay_candidates_for_manus.csv
data/manus_requests/manus_request_from_ebay.csv
```

`ebay_candidates_for_manus.csv` の形式:

```text
title,ebay_price_jpy,ebay_url
```

`manus_request_from_ebay.csv` は、Manusへ国内調査を依頼するためのCSVです。

## キーワード別分析

以下のコマンドで、`data/products.csv` をキーワード別に分析します。

```bash
python3 src/analysis.py
```

分析結果は `reports/キーワード_report_summary.csv` と `reports/キーワード_top_sellers.csv` に保存します。

## Manus連携MVP

初号機では、eBay候補CSVをもとにManusへ国内調査を依頼するCSVを作成し、Manusの調査結果CSVを読み込んで利益計算とレポート出力を行います。

このMVPでは完全自動化は行わず、CSVベースで以下の流れを確認します。

```text
eBay候補CSV
↓
Manus依頼CSV
↓
Manus結果CSV
↓
利益計算
↓
利益ランキングCSV
↓
HTMLレポート
```

### 入力ファイル

eBay候補CSV:

```text
data/ebay_raw/ebay_candidates.csv
```

形式:

```text
title,ebay_price_jpy,ebay_url
```

Manus結果CSV:

```text
data/manus_results/manus_results.csv
```

形式:

```text
request_id,site,price_jpy,shipping_jpy,url
```

### 設定ファイル

利益計算の設定は以下で管理します。

```text
config/fees.json
```

管理項目:

```text
ebay_fee_rate
international_shipping_jpy
packing_cost_jpy
default_domestic_shipping_jpy
exchange_rate
minimum_profit_jpy
minimum_profit_rate
```

### 出力ファイル

Manus依頼CSV:

```text
data/manus_requests/manus_request.csv
```

利益ランキングCSV:

```text
data/processed/profit_ranking.csv
```

HTMLレポート:

```text
reports/daily_report.html
```

### 実行方法

ダミーデータでMVPの一連の処理を実行します。

```bash
python3 src/mvp_pipeline.py
```

個別に実行する場合は以下です。

```bash
python3 src/manus_request.py
python3 src/profit_calculator.py
python3 src/report_generator.py
```
