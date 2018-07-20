// README.txt 
Student ID: z5137895
Name: Zhuowen Deng
Installation Guide 
- unzip the service.zip
- Open PyCharm firstly, then click “open”, next select file folder and click open
- Strongly recommend the users to open the Chrome browser and open the Restlet Client.

Running the python program

1, Order Operation:
Create order: http://127.0.0.1:5000/order?drink={}&cost={}&additions={}
Attention: the ID will be created automatically which is based on current time. Users can choose one extra ingredient from 4 additions(sugar, chocolate, milk and shot).

Get an Order info: http://127.0.0.1:5000/order/{id}
Attention:You just needs to copy the ID and paste it into “id” section

Get Order List: http://127.0.0.1:5000/order

Update Order: http://127.0.0.1:5000/order/{id}?drink={}&cost={}&additions={} or http://127.0.0.1:5000/order/{id}?additions={}
Attentions: Users can choose one extra ingredient from 4 additions(sugar, chocolate, milk and shot).

Delete Order: http://127.0.0.1:5000/order/{id}

Get the OpenOrder (barista only): http://127.0.0.1:5000/order/barista

Check the order whether is paid (barista only): http://127.0.0.1:5000/checkpaid/barista/{id}

Change the status (barista only): http://127.0.0.1:5000/order/{id}?status={}
Attention: the initial value of status is “open”, you can change it into “preparing” and “released”

2, Payment Operation:
Create a payment: 
(if pay by card)http://127.0.0.1:5000/payment/order/{id}?cardID={}&name={}&number={}&expiry={}
(If pay by cash)http://127.0.0.1:5000/payment/order/{id}?name={}&number={}
Attention: the final price will be calculated by the program, what is more, the payment type is judged automatically as well, "number" is the number of coffee in one order.

Get the detail of an payment:http://127.0.0.1:5000/payment/order/{id}


         
    

