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
  "ebay_environment": "sandbox"
}
```

`ebay_app_id` にはeBay Developer Programで取得したApp IDを入力します。

`ebay_environment` は検証用の場合は `sandbox`、本番用の場合は `production` を指定します。

Client SecretはGitHubへ保存しないため、実行時に環境変数 `EBAY_CLIENT_SECRET` で指定します。

```bash
EBAY_CLIENT_SECRET="your_client_secret" python3 src/ebay_fetcher.py
```

`src/ebay_fetcher.py` はeBay Browse APIで `motorcycle` を検索し、最大50件を `data/products.csv` に保存します。
