import base64
import csv
import json
import os
from pathlib import Path
from urllib import parse, request


SEARCH_KEYWORD = "motorcycle"
SEARCH_LIMIT = 200


def load_settings(settings_path):
    with settings_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_api_base_url(environment):
    if environment == "production":
        return "https://api.ebay.com"
    return "https://api.sandbox.ebay.com"


def check_ebay_api_settings(settings):
    ebay_app_id = settings["ebay_app_id"]
    ebay_environment = settings["ebay_environment"]
    ebay_client_secret = os.environ.get("EBAY_CLIENT_SECRET")

    if not ebay_app_id:
        print("eBay App ID が未設定です。settings.json に入力してください")
        return False

    if not ebay_client_secret:
        print("eBay Client Secret が未設定です。環境変数 EBAY_CLIENT_SECRET に入力してください")
        return False

    print(f"eBay API設定: {ebay_environment}")
    return True


def get_access_token(settings):
    ebay_app_id = settings["ebay_app_id"]
    ebay_environment = settings["ebay_environment"]
    ebay_client_secret = os.environ["EBAY_CLIENT_SECRET"]
    credentials = f"{ebay_app_id}:{ebay_client_secret}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("utf-8")
    token_url = f"{get_api_base_url(ebay_environment)}/identity/v1/oauth2/token"
    data = parse.urlencode(
        {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        }
    ).encode("utf-8")
    token_request = request.Request(
        token_url,
        data=data,
        headers={
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    with request.urlopen(token_request, timeout=30) as response:
        token_response = json.load(response)

    return token_response["access_token"]


def fetch_ebay_items(settings):
    ebay_environment = settings["ebay_environment"]
    access_token = get_access_token(settings)
    query = parse.urlencode({"q": SEARCH_KEYWORD, "limit": SEARCH_LIMIT})
    search_url = (
        f"{get_api_base_url(ebay_environment)}"
        f"/buy/browse/v1/item_summary/search?{query}"
    )
    search_request = request.Request(
        search_url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        },
        method="GET",
    )

    with request.urlopen(search_request, timeout=30) as response:
        search_response = json.load(response)

    return search_response.get("itemSummaries", [])


def format_item_location(item_location):
    if not item_location:
        return ""

    location_parts = [
        item_location.get("city", ""),
        item_location.get("stateOrProvince", ""),
        item_location.get("postalCode", ""),
        item_location.get("country", ""),
    ]
    return ", ".join(part for part in location_parts if part)


def format_category_path(categories):
    if not categories:
        return ""

    return " > ".join(category.get("categoryName", "") for category in categories)


def save_products_csv(items, csv_path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "title",
            "price",
            "itemWebUrl",
            "sellerUsername",
            "condition",
            "itemLocation",
            "categoryPath",
            "buyingOptions",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for item in items:
            price = item.get("price", {})
            seller = item.get("seller", {})
            writer.writerow(
                {
                    "title": item.get("title", ""),
                    "price": price.get("value", ""),
                    "itemWebUrl": item.get("itemWebUrl", ""),
                    "sellerUsername": seller.get("username", ""),
                    "condition": item.get("condition", ""),
                    "itemLocation": format_item_location(item.get("itemLocation", {})),
                    "categoryPath": format_category_path(item.get("categories", [])),
                    "buyingOptions": ",".join(item.get("buyingOptions", [])),
                }
            )


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "products.csv"
    settings_path = project_root / "config" / "settings.json"
    settings = load_settings(settings_path)

    if not check_ebay_api_settings(settings):
        return

    items = fetch_ebay_items(settings)
    save_products_csv(items, csv_path)
    print(f"{len(items)}件の商品データを保存しました: {csv_path}")


if __name__ == "__main__":
    main()
