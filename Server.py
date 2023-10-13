import socket
import pymongo

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


def start_server(sk):
    while True:
        client_sk, client_addr = sk.accept()
        print('Client address ', client_addr)
        send_res(client_sk, 'Hello ' + str(client_addr))
        process_client_request(client_sk)

        # client_sk.close()
        print('Connection from ' + str(client_addr) + ' closed !!!')
        break
    sk.close()
    print('Server connection closed !!!')
    return


def process_client_request(client_sk):
    process_login(client_sk)
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


def top_server(client_sk):

    top_legit = ''
    top_spent = ''

    for a in account.find().sort('legit_point', -1).limit(3):
        top_legit = top_legit + '$$' + str([a['name'], a['legit_point']])

    for b in account.find().sort('money_spent', -1).limit(3):
        top_spent = top_spent + '$$' + str([b['name'], b['money_spent']])

    dash_board = top_legit + '$!$' + top_spent

    send_res(client_sk, dash_board)


def search_item(client_sk):
    lst_search = ''
    lst_Stock = []
    req = recv_req(client_sk)
    trader_name, name, money, quantity = req.split('@@')
    for a in stock.find({}, {"_id": 0}):
        lst_Stock.append(a)

    for x in reversed(lst_Stock):
        if x['user'] == trader_name or x['name'] == name or x['money'] == money or x['number'] == quantity:
            lst_search = str(x) + '@@' + lst_search
    print(lst_search)
    send_res(client_sk, lst_search)


def sub_search(client_sk, stock_id, name, money, quantity):

    for x in stock.find():
        if x['id'] == stock_id and x['name'] == name and x['money'] == money and int(x['number']) >= int(quantity):
            send_res(client_sk, 'found')
            return x
    send_res(client_sk, 'not found')


def buy_item(client_sk):
    trader_name = ''
    req = recv_req(client_sk)
    client_name, stock_id, name, money, quantity, time = req.split('$')
    total = int(money) * int(quantity) - int(money) * int(quantity) * 5 / 100
    profit = int(money) * int(quantity) * 5 / 100

    req = sub_search(client_sk, stock_id, name, money, quantity)
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

                myquery = {'user': client_name, 'state': 'BUY', 'id': stock_id, 'name': name, 'money': money, 'number': quantity, 'total': total, 'trader': trader_name,'time': time}
                buy_orders.insert_one(myquery)

                send_res(client_sk, 'success')
                break


def sell_item(client_sk):

    req = recv_req(client_sk)
    user, state, trader, id, name, money, number, time, confirm = req.split('#SELL#')
    count = 0
    c = 0

    if state == 'SELL' and confirm == 'YES' and trader == '':
        for x in stock.find():
            if x['user'] == user and x['status'] == 'WTS' and x['id'] == id and x['name'] == name:
                count += 1
                break
        if count == 0:
            order = dict(user=user, status='WTS', id=id, name=name, money=money, number=number)

            stock.insert_one(order)

            print('ORDER UPLOADED')
            return 'SUCCESSFUL'

        myquery = {'user': user, 'status': 'WTS', "id": id, 'name': name}
        newvalues = {"$set": {"money": money, "number": number}}

        stock.update_one(myquery, newvalues)
        print(user, 'WTS', id, name, money, number)
        print('ORDER UPDATED')
        return 'SUCCESSFUL'

    if state == 'SELL' and confirm == 'YES' and trader != '':
        for x in stock.find():
            if x['user'] != user and x['status'] == 'WTB' and x['id'] == id and x['name'] == name:
                number_remain = str(int(x['number']) - int(number))
                total_money = str(int(money) * int(number))

                print(user, 'WTS', id, name, money, number)
                print('ORDER CONFIRMED')
                count += 1
                break

        if count == 0:
            order = dict(user=user, status='WTS', id=id, name=name, money=money, number=number)

            stock.insert_one(order)
            print('ORDER UPLOADED')
            return 'SUCCESSFUL'

        myquery = {'user': trader, 'status': 'WTB', "id": id, 'name': name, 'money': money}
        newvalues = {"$set": {"number": number_remain}}
        sell_order = dict(user=user, id=id, name=name, money=money, number=number, total=total_money, trader=trader,
                          time=time)

        stock.update_one(myquery, newvalues)
        sell_orders.insert_one(sell_order)

        profit = int(total_money) * 5 / 100
        for a in account.find():
            if a['name'] == user:
                point = a['legit_point'] + int(number)
                cur_money = int(a['current_money']) + int(total_money) - profit
                break

        myquery = {'name': user}
        newvalues = {"$set": {"legit_point": point, "current_money": cur_money}}
        account.update_one(myquery, newvalues)

        transaction = dict(user=user, state=state, id=id, name=name, money=money, number=number, total=total_money,
                           profit=profit)
        success_trade.insert_one(transaction)

        total_money = ''
        number_remain = ''
        return 'SUCCESSFUL'


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


def disconnect(client_sk):
    client_sk.close()
    return


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    server_sk = create_socket(host, port)

    start_server(server_sk)
