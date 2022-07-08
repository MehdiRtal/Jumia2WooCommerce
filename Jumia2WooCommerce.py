import requests
from woocommerce import API
import json

wcapi = API(
    url="Your website url",
    consumer_key="Your consumer key",
    consumer_secret="Your consumer secret",
    timeout=50,
)

jumia_data = requests.get(r"Your jumia api").json()

def post_products():
    for product in jumia_data["SuccessResponse"]["Body"]["Products"]["Product"]:
        data = {}
        images = []
        if product["Status"] == "active":
            data["name"] = product["Name"]
            data["regular_price"] = product["Price"]
            data["sale_price"] = product["SalePrice"]
            if product["Quantity"] != "0":
                data["manage_stock"] = True
                data["stock_quantity"] = product["Quantity"]
            else:
                data["stock_status"] = "outofstock"
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
            data["attributes"] = [{"id": "2",
                                          "name": "Taille",
                                          "position": 0,
                                          "visible": True,
                                          "options": option}]
            print(json.dumps(data, indent=2))
            c = input("Add product ? (Y/N): ")
            if c in ["Y","y"]:
                wcapi.post("products", data=data)
            print("\033c")

post_products()
