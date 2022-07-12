import requests
from woocommerce import API
import json
import urllib.parse
from hashlib import sha256
from hmac import HMAC
import datetime

userid = input("Enter Jumia User ID: ")
key = input("Enter Jumia API Key: ")
products_filter = input("Enter Jumia Products Filter (all, live, inactive, deleted, image-missing, pending, rejected, sold-out): ")
url = input("Enter WooCommerce store URL: ")
consumer_key = input("Enter WooCommerce Consumer Key: ")
consumer_secret = input("Enter WooCommerce Consumer Secret: ")

def get_products(arg):
    parameters = {
                'UserID': userid,
                'Version': '1.0',
                'Action': 'GetProducts',
                'Format':'JSON',
                'Filter': products_filter,
                'Timestamp': datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    }
    api_key = key.encode(encoding='utf-8')
    concatenated = urllib.parse.urlencode(sorted(parameters.items())).encode(encoding='utf-8')
    data = requests.get(f"https://sellercenter-api.jumia.ma?{concatenated.decode()}&Signature={HMAC(api_key, concatenated, sha256).hexdigest()}").json()
    products = data["SuccessResponse"]["Body"]["Products"]["Product"]
    if arg == "all":
        return products
    else:
        seen = []
        duplicates = []
        clean = []
        counter = 0
        for product in products:
            if product["Name"] in seen:
                duplicates.append(product)
            if product["Name"] not in seen:
                if counter == 1:
                    clean.append(product)
                counter = 1
            seen.append(product["Name"])
        if arg == "duplicates":
            return duplicates
        if arg == "clean":
            return clean

def post_products():
    wcapi = API(
                url=url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                timeout=5,
    )
    for product in get_products("clean"):
        data = {}
        images = []
        if product["Status"] == "active" and product["Quantity"] != "0":
            data["name"] = product["Name"]
            data["regular_price"] = product["Price"]
            data["sale_price"] = product["SalePrice"]
            data["manage_stock"] = True
            data["stock_quantity"] = product["Quantity"]
            data["weight"] = product["ProductData"]["ProductWeight"]
            try:
                for image in product["Images"]["Image"]:
                    images.append({"src": image})
            except: pass
            data["images"] = images
            if product["Variation"] == "S":
                option = "S"
            elif product["Variation"] == "M":
                option = "M"
            elif product["Variation"] == "L":
                option = "L"
            elif product["Variation"] == "XL":
                option = "XL"
            else:
                option = "Standard"
            data["attributes"] = [{
                                "id": "2",
                                "name": "Taille",
                                "position": 0,
                                "visible": True,
                                "options": option
            }]
            print(json.dumps(data, indent=2))
            c = input("Add product ? (Y/N): ")
            if c in ["Y","y"]:
                wcapi.post("products", data=data)
            print("\033c")

post_products()
