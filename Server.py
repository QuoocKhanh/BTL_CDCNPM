import socket
import pymongo
import threading

DB_client = pymongo.MongoClient('mongodb://localhost:27017')
database = DB_client['Trading_Bot']
stock = database['Stock_4_Trade']
user_stock = database['User_Stock']
sell_orders = database['Sell_Order']
buy_orders = database['Buy_Order']
account = database['User']
success_trade = database['Successful_Trade']

# lst_user = []
# lst_Stock = []
# for x in stock.find({}, {"_id": 0}):
#     lst_Stock.append(x)
# #
# # for user in account.find({}, {"_id": 0}):
# #     lst_user.append(user)


def create_socket(h, p):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    sk.bind((h, p))
    sk.listen(5)
    return sk


def send_res(sk, res):
    res = res.encode('utf-8')
    sk.send(res)


def recv_req(client_sk):
    data = ''
    req = ''
    while not data:
        data = client_sk.recv(4096)
        if not data:
            raise ConnectionError()
        req = data.decode('utf-8')
    return req


def start_server():
    server_sk = create_socket(host, port)

    client_sk, client_addr = server_sk.accept()
    print('Client address ', client_addr)
    send_res(client_sk, 'Hello ' + str(client_addr))
    process_login(client_sk)
    process_client_request(client_sk)

    print('Connection from ' + str(client_addr) + ' closed !!!')

    server_sk.close()
    print('Server connection closed !!!')
    return


def process_client_request(client_sk):
    while True:
        req = recv_req(client_sk)
        print('Client request: {}'.format(req))

        menu(client_sk, req)
        break
    return


def process_login(client_sk):
    req = recv_req(client_sk)
    username, password = req.split(' ')
    count = 0
    for user in account.find({}, {"_id": 0}):
        if user['name'] == username and user['password'] == password:
            count += 1
    if count > 0:
        send_res(client_sk, 'success')
        print('Login successful !')
        return
    send_res(client_sk, 'fail')
    print('Login fail !')
    return


def menu(client_sk, req):

    if req == '1':
        all_item(client_sk)

    if req == '2':
        top_server(client_sk)

    if req == '3':
        search_item(client_sk)

    if req == '4':
        buy_item(client_sk)

    if req == '5':
        sell_item(client_sk)

    if req == '6':
        acc_info(client_sk)

    if req == '7':
        disconnect(client_sk)


def all_item(client_sk):

    all_stock = ''
    lst_Stock = []
    for a in stock.find({}, {"_id": 0}):
        lst_Stock.append(a)
    for x in reversed(lst_Stock):
        all_stock = str(x) + '$$' + all_stock

    send_res(client_sk, all_stock)
    process_client_request(client_sk)


def top_server(client_sk):

    top_legit = ''
    top_spent = ''

    for a in account.find().sort('legit_point', -1).limit(3):
        top_legit = top_legit + '$$' + str([a['name'], a['legit_point']])

    for b in account.find().sort('money_spent', -1).limit(3):
        top_spent = top_spent + '$$' + str([b['name'], b['money_spent']])

    dash_board = top_legit + '$!$' + top_spent

    send_res(client_sk, dash_board)
    process_client_request(client_sk)


def search_item(client_sk):
    lst_search = ''
    lst_Stock = []
    req = recv_req(client_sk)
    trader_name, name, money, quantity = req.split('@@')

    if trader_name == 'exit' or name == 'exit' or money == 'exit' or quantity == 'exit':
        process_client_request(client_sk)

    for a in stock.find({}, {"_id": 0}):
        lst_Stock.append(a)

    for x in reversed(lst_Stock):
        if x['user'] == trader_name or x['name'] == name or x['money'] == money or x['number'] == quantity:
            lst_search = str(x) + '@@' + lst_search
    print(lst_search)
    send_res(client_sk, lst_search)
    process_client_request(client_sk)


def sub_buy_search(client_sk, stock_id, name, money, quantity):

    for x in stock.find():
        if x['id'] == stock_id and x['name'] == name and x['money'] == money and int(x['number']) >= int(quantity):
            send_res(client_sk, 'found')
            return x
    send_res(client_sk, 'not found')


def buy_item(client_sk):

    req = recv_req(client_sk)
    client_name, stock_id, name, money, quantity, time = req.split('$')

    if stock_id == 'exit' or name == 'exit' or money == 'exit' or quantity == 'exit':
        process_client_request(client_sk)

    total = int(money) * int(quantity) - int(money) * int(quantity) * 5 / 100
    profit = int(money) * int(quantity) * 5 / 100

    req = sub_buy_search(client_sk, stock_id, name, money, quantity)
    trader_name = req['user']

    data = recv_req(client_sk)
    if data == 'YES':
        stock_query = {'user': client_name, 'id': stock_id, 'name': name, 'number': quantity}

        for x in account.find():
            if client_name == x['name'] and int(x['current_money']) >= total:
                money_pay = int(x['current_money']) - total
                money_get = int(x['current_money']) + total
                point_get = int(x['legit_point']) + int(quantity)
                number_remain = str(int(req['number']) - int(quantity))
                for a in user_stock.find():
                    if a['user'] == client_name and a['id'] == stock_id and a['name'] == name:
                        myquery = {'user': client_name, 'id': stock_id, 'name': name}
                        b = int(a['number']) + int(quantity)
                        new_user_value = {'$set': {'number': b}}
                        user_stock.update_one(myquery, new_user_value)
                        break
                    else:
                        user_stock.insert_one(stock_query)

                # Update money for buyer
                myquery = {'name': client_name}
                new_user_value = {'$set': {'current_money': money_pay, 'legit_point': point_get, 'money_spent': total}}
                account.update_one(myquery, new_user_value)

                # Update money for trader bought by buyer
                myquery = {'name': trader_name}
                new_user_value = {'$set': {'current_money': money_get, 'legit_point': point_get}}
                account.update_one(myquery, new_user_value)

                new_stock_value = {'$set': {'number': number_remain}}
                stock.update_one(req, new_stock_value)

                myquery = {'user': client_name, 'state': 'BUY', 'id': stock_id, 'name': name, 'money': money, 'number': quantity, 'total': total, 'profit': profit}
                success_trade.insert_one(myquery)

                myquery = {'user': client_name, 'state': 'BUY', 'id': stock_id, 'name': name, 'money': money, 'number': quantity, 'total': total, 'trader': trader_name, 'time': time}
                buy_orders.insert_one(myquery)

                myquery = {'user': trader_name, 'state': 'SELL', 'id': stock_id, 'name': name, 'money': money, 'number': quantity, 'total': total, 'trader': client_name, 'time': time}
                sell_orders.insert_one(myquery)

                send_res(client_sk, 'success')
                break
    process_client_request(client_sk)


def sub_sell_search(client_sk, stock_id, name, money, quantity):
    for x in stock.find():
        if x['id'] == stock_id and x['name'] == name and x['money'] == money and int(x['number']) >= 0:
            send_res(client_sk, 'found')
            return x
    send_res(client_sk, 'available')
    return ''


def sell_item(client_sk):
    req = recv_req(client_sk)
    client_name, stock_id, name, money, quantity, time = req.split('$')

    if stock_id == 'exit' or name == 'exit' or money == 'exit' or quantity == 'exit':
        process_client_request(client_sk)

    req = sub_sell_search(client_sk, stock_id, name, money, quantity)

    data = recv_req(client_sk)

    if req != '':
        if data == 'YES':
            stock_query = {'user': client_name, 'id': stock_id, 'name': name, 'number': quantity}

            for x in user_stock.find():
                if client_name == x['name'] and x['id'] == stock_id and int(x['number']) >= quantity:
                    myquery = {'user': client_name, 'id': stock_id}
                    number_remain = str(int(x['number']) - int(quantity))
                    new_stock_value = {'$set': {'number': number_remain}}
                    user_stock.update_one(myquery, new_stock_value)

                    myquery = req
                    number_remain = str(int(x['number']) + int(quantity))
                    new_stock_value = {'$set': {'number': number_remain}}
                    stock.update_one(myquery, new_stock_value)

                send_res(client_sk, 'success')
                break
    else:
        if data == 'YES':
            for x in user_stock.find():
                if client_name == x['name'] and x['id'] == stock_id and int(x['number']) >= quantity:
                    myquery = {'user': client_name, 'id': stock_id}
                    number_remain = str(int(x['number']) - int(quantity))
                    new_stock_value = {'$set': {'number': number_remain}}
                    user_stock.update_one(myquery, new_stock_value)

                    myquery = req
                    stock.insert_one(myquery)

                send_res(client_sk, 'success')
                break

    process_client_request(client_sk)


def acc_info(client_sk):
    buy_order = ''
    sell_order = ''
    curr_stock = ''
    point = ''
    spent = ''
    curr_money = ''

    req = recv_req(client_sk)
    client_name = req.strip('!!')

    for a in account.find({}, {"_id": 0}):
        if a['name'] == client_name:
            point = a['legit_point']
            spent = a['money_spent']
            curr_money = a['current_money']

    for x in sell_orders.find({}, {"_id": 0}):
        if x['user'] == client_name:
            sell_order = str(x) + '...' + sell_order
    for y in buy_orders.find({}, {"_id": 0}):
        if y['user'] == client_name:
            buy_order = str(y) + '...' + buy_order
    for z in user_stock.find({}, {"_id": 0}):
        if z['user'] == client_name:
            curr_stock = str(z) + '...' + curr_stock

    client_stock = client_name + '!!' + str(point) + '!!' + str(spent) + '!!' + str(
        curr_money) + '!!' + curr_stock + '!!' + buy_order + '!!' + sell_order

    send_res(client_sk, client_stock)

    process_client_request(client_sk)


def disconnect(client_sk):
    client_sk.close()
    return


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    start_server()
