import pymongo


myclient = pymongo.MongoClient('mongodb://localhost:27017')

mydb = myclient['Trading_Bot']
stock = mydb['Stock_4_Trade']
user_stock = mydb['User_Stock']

buy_orders = mydb['Buy_Order']
sell_orders = mydb['Sell_Order']
successful_trade = mydb['Successful_Trade']
account = mydb['User']

my_stock_list = [
    {'user': 'A', "id": 'FB', "name": "Facebook", 'money': "300", 'number': '50'},
    {'user': 'A', "id": 'MS', "name": "Microsoft", 'money': "310", 'number': '50'},
    {'user': 'B', "id": 'YT', "name": "Youtube", 'money': "300", 'number': '50'},
    {'user': 'B', "id": 'TW', "name": "Twitter", 'money': "280", 'number': '50'},
    {'user': 'Client 2', "id": 'SPX', "name": "SpaceX", 'money': "330", 'number': '50'},
    {'user': 'Client 1', "id": 'GG', "name": "Google", 'money': "320", 'number': '50'},
    {'user': 'C', "id": 'BL', "name": "Bentley", 'money': "320", 'number': '50'},
    {'user': 'C', "id": 'RR', "name": "RollRoyce", 'money': "310", 'number': '50'},
    {'user': 'D', "id": 'NIS', "name": "Nissan", 'money': "290", 'number': '50'}
]

user_stock_list = [
    {'user': 'A', "id": 'FB', "name": "Facebook", 'number': '20'},
    {'user': 'A', "id": 'MS', "name": "Microsoft", 'number': '10'},
    {'user': 'A', "id": 'YT', "name": "Youtube", 'number': '30'},
    {'user': 'A', "id": 'TW', "name": "Twitter", 'number': '10'},
    {'user': 'Client 2', "id": 'SPX', "name": "SpaceX", 'number': '10'},
    {'user': 'Client 1', "id": 'GG', "name": "Google", 'number': '10'},
    {'user': 'B', "id": 'BL', "name": "Bentley", 'number': '30'},
    {'user': 'C', "id": 'RR', "name": "RollRoyce", 'number': '50'},
    {'user': 'D', "id": 'NIS', "name": "Nissan", 'number': '50'}
]

my_user_list = [
    {'name': 'Fap su co dai', 'password': '1', 'legit_point': 1000, 'money_spent': 100000000, 'current_money': 100000},
    {'name': 'Client 1', 'password': '1', 'legit_point': 400, 'money_spent': 8000, 'current_money': 1500},
    {'name': 'Client 2', 'password': '1', 'legit_point': 300, 'money_spent': 11000, 'current_money': 1200},
    {'name': 'Client 3', 'password': '1', 'legit_point': 200, 'money_spent': 10000, 'current_money': 3000},
    {'name': 'Client 4', 'password': '1', 'legit_point': 100, 'money_spent': 10000, 'current_money': 2500},
    {'name': 'A', 'password': '1', 'legit_point': 40, 'money_spent': 8000, 'current_money': 750},
    {'name': 'B', 'password': '1', 'legit_point': 30, 'money_spent': 7000, 'current_money': 1500},
    {'name': 'C', 'password': '1', 'legit_point': 20, 'money_spent': 6000, 'current_money': 900},
    {'name': 'D', 'password': '1', 'legit_point': 10, 'money_spent': 5000, 'current_money': 800},
]

my_successful_trade = [
    {'user': 'A', 'state': 'SELL', 'id': 'T1', 'name': 'Test1', 'money': '110', 'number': '40', 'total': '4400', 'profit': '220'},
    {'user': 'B', 'state': 'BUY', 'id': 'T', 'name': 'Test', 'money': '100', 'number': '23', 'total': '2300', 'profit': '115'}
]

dif1 = {'user': 'A', 'status': 'WTS', 'id': 'T1', 'name': 'Test1', 'money': '110', 'number': '40'}
dif = {'user': 'B', 'status': 'WTB', 'id': 'T', 'name': 'Test', 'money': '100', 'number': '23'}

a = {'user': 'A', "id": 'FB', "name": "Facebook", 'money': "290", 'number': '50'}
# stock.insert_many(my_stock_list)
# user_stock.insert_many(user_stock_list)
# stock.insert_one(dif)
# stock.insert_one(a)
# account.insert_many(my_user_list)
# successful_trade.insert_many(my_successful_trade)
