import pymongo
from flask import session

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
products_db = myclient["products"]
order_management_db = myclient["order_management"]

#PRODUCTS
def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code})

    return product


def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({}):
        product_list.append(p)

    return product_list

#BRANCHES
def get_branch(code):
    branches_coll = products_db["branches"]

    branches = branches_coll.find_one({"code":code})

    return branches

def get_branches():
    branches_list = []

    branches_coll = products_db["branches"]

    for b in branches_coll.find({}):
        branches_list.append(b)

    return branches_list

#AUTHENTICATION
def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

#CHECK-OUT
def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

#PAST ORDERS
def get_orders(username):
    order_list = []
    orders_coll = order_management_db['orders']

    for o in orders_coll.find({"username":username}):
        order_list.append(o)
    return order_list

def count_orders(username):
    orders_coll = order_management_db["orders"]
    numberoforders = []
    numberoforders = orders_coll.count({"username":username})
    return numberoforders
