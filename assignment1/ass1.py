from flask import Flask, jsonify
from flask_restful import reqparse
import time

app = Flask(__name__)
database = []
database2 = []
dictionary = {"sugar":1,"milk":0.2,"chocolate":0.5,"shot":1}

class Order:
    def __init__(self, ID, drink, cost,  additions, status):
        self.ID = ID
        self.drink = drink
        self.cost = cost
        self.additions = additions
        self.status = status
        # type of coffee, cost, additions (e.g., skim milk, extra shot)

class Payment:
    def __init__(self, ID, PaymentType, cardID, name, number, amount,expiry):
        self.ID =ID
        self.PaymentType = PaymentType
        self.cardID = cardID
        self.name = name
        self.number = number
        self.amount = amount
        self.expiry = expiry

@app.route("/order", methods=['POST'])
def create_order():
    parser = reqparse.RequestParser()
    parser.add_argument('ID', type=int)
    parser.add_argument('drink', type=str)
    parser.add_argument('cost', type=float)
    parser.add_argument('additions', type=str)
    parser.add_argument('status', type=str)
    args = parser.parse_args()
    ID = int(time.time())
    drink = args.get("drink")
    cost = args.get("cost")
    additions = args.get("additions")
    status = "open"
    database.append(Order(ID, drink, cost, additions, status))
    return jsonify(ID = ID, coffeeName=drink, cost=cost), 200

@app.route("/order", methods = ['Get'])
def get_orderinfo():
    return jsonify([st.__dict__ for st in database]), 200

@app.route("/checkpaid/barista/<int:ID>", methods = ['Get'])
def get_paidorder(ID):
    # OpenOrderID = []
    # Opendata = []
    for st in database2:
        if st.ID == ID:
            return jsonify(ID = ID, PaidResult=True), 200
    return jsonify(ID = ID, PaidResult=False), 200
        # OpenOrderID.append(st.ID)
    # for id in OpenOrderID:
    #     for order in database:
    #         if id == order.ID:
    #             Opendata.append(order)
    #return jsonify([st.__dict__ for st in Opendata])

@app.route("/order/<int:ID>", methods=['GET'])
def get_coffee_detail(ID):
    for st in database:
        if st.ID == ID:
            return jsonify(st.__dict__), 200
    return jsonify(ID=ID, Getinfo = "Not found"), 404

@app.route("/order/<int:ID>", methods=['DELETE'])
def delete_coffee(ID):
    for st in database2:
        if st.ID == ID:
            return jsonify(cardID=False), 401
    for st in database:
        if st.ID == ID:
            database.remove(st)
            return jsonify(ID=ID), 200
    return jsonify(ID=ID, DeleteResult = "Not found"), 404

@app.route("/order/<int:ID>", methods=['PUT'])
def update_coffee(ID):
    for st in database2:
        if st.ID == ID:
            return jsonify(cardID=False), 401
    for st in database:
        if st.ID == ID:
            parser = reqparse.RequestParser()
            parser.add_argument('drink', type=str)
            parser.add_argument('cost', type=float)
            parser.add_argument('additions', type=str)

            args = parser.parse_args()
            newdrink = args.get("drink")
            newcost = args.get("cost")
            newadditions = args.get("additions")
            # if st.status == "":
            #     return jsonify(cardID=False), 401
            if newdrink == st.drink or not newdrink:
                st.additions = newadditions
            else:
                st.drink = newdrink
                st.cost = newcost
                st.additions = newadditions
            return jsonify(ID=ID, coffeeName=st.drink, additions=st.additions, cost=st.cost), 201

    return jsonify(ID = ID, updateresult="Not found"), 404

@app.route("/order/barista", methods=['GET'])
def get_OpenOrder():
    result = []
    for st in database:
        if st.status != "released":
            result.append(st)
    return jsonify([st.__dict__ for st in result]), 200


@app.route("/order/barista/<int:ID>", methods=['PATCH'])
def change_status(ID):
    for st in database:
        if st.ID == ID:
            parser = reqparse.RequestParser()
            parser.add_argument('status', type=str)
            args = parser.parse_args()
            st.status = args.get("status")
            return jsonify(ID=ID,status=st.status), 201
    return jsonify(ID=ID, ChangeStatus="Not found"), 404

@app.route("/payment/order/<int:ID>", methods=['POST'])
def create_payment(ID):
    for st in database2:
        if st.ID == ID:
            return jsonify(cardID=False), 401
    parser = reqparse.RequestParser()
    parser.add_argument('OrderID', type=int)
    parser.add_argument('PaymentType', type=str)
    parser.add_argument('cardID', type=int)
    parser.add_argument('name', type=str)
    parser.add_argument('number', type=int)
    parser.add_argument('amount', type=float)
    parser.add_argument('expiry', type=str)
    args = parser.parse_args()
    OrderID = ID
  #  PaymentType = args.get("PaymentType")
    cardID = args.get("cardID")
    check = str(cardID)
    name = args.get("name")
    number = args.get("number")
    if  len(check)==16 and check.isdigit():
        amount = 0.0
        PaymentType = "card"
        for st in database:
            if st.ID == ID and st.cost:
                amount = (st.cost)*number
                if st.additions in dictionary:
                    amount += dictionary[st.additions]
        expiry = args.get("expiry")
        database2.append(Payment(OrderID, PaymentType, cardID, name, number, amount, expiry))
        return jsonify(IDNumber=ID, name = name, Paymethod= cardID, Amount=amount), 201
    elif not cardID:
        expiry = ''
        amount = 0.0
        PaymentType = "cash"
        for st in database:
            if st.ID == ID and st.cost:
                amount = (st.cost) * number
                if st.additions in dictionary:
                    amount += dictionary[st.additions]
        database2.append(Payment(OrderID, PaymentType, cardID, name, number, amount, expiry))
        return jsonify(IDNumber=ID, name=name, Paymethod=cardID, Amount=amount), 201
    return jsonify(orderID = ID, createPayment=False), 401

@app.route("/payment/order/<int:ID>。", methods=['GET'])
def get_payment_detail(ID):
    for st in database2:
        if st.ID == ID:
            return jsonify(st.__dict__), 200
    return jsonify(ID=ID, Getinfo="Not found"), 404
   # return jsonify([st.__dict__ for st in database2]), 200


if __name__ == "__main__":
    app.run()
