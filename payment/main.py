from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests
import time

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

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis

def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    

@app.get('/orders/{pk}')
def getOrder(pk:str):
    order = Order.get(pk)
    return order

@app.post('/orders')
async def createOrder(request: Request, background_tasks:BackgroundTasks):
    body = await request.json()
    req = requests.get("http://localhost:8000/products/{}".format(body['id']))
    product =  req.json()

    order = Order(
        product_id=product['pk'],
        price=product['price'],
        fee = 0.2*product['price'],
        total = 1.2*product['price'],
        quantity = body['quantity'],
        status = "pending"
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order