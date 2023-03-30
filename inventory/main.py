from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-16434.c305.ap-south-1-1.ec2.cloud.redislabs.com",
    port=16434,
    password="BO8Z8iGbJgR4qrGuH66DVlDBZEwgMlbA",
    decode_responses=True
)

class Product(HashModel):
    name:str
    price:float
    quantity:int

    class Meta:
        database=redis


def productDetail(pk: str):
    product = Product.get(pk)
    id = product.pk
    name = product.name
    price = product.price
    quantity = product.quantity

    return {
        "id":id,
        "name":name,
        "price":price,
        "quantity":quantity
    }

@app.get("/products")
def getProducts():
    return [productDetail(pk) for pk in Product.all_pks()]

@app.get("/products/{pk}")
def getProducts(pk:str):
    product = Product.get(pk)
    return product

@app.post("/products")
def addProduct(product: Product):
    product.save()
    return product

@app.delete("/products/{pk}")
def deleteProduct(pk:str):
    Product.delete(pk)
    return "Deleted..."