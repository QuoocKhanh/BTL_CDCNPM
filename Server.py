import socket
import pymongo


DB_client = pymongo.MongoClient('mongodb://localhost:27017')
database = DB_client['Trading_Bot']
stock = database['Stock_4_Trade']
sell_orders = database['Sell_Order']
buy_orders = database['Buy_Order']
account = database['User']
success_trade = database['Successful_Trade']

lst_user = []
lst_Stock = []
for x in stock.find({}, {"_id": 0}):
    lst_Stock.append(x)

for user in account.find({}, {"_id": 0}):
    lst_user.append(user)



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

        client_sk.close()
        break
    sk.close()
    print('Connection from ' + str(client_addr) + ' closed !!!')
    return


def process_client_request(client_sk):
    process_login(client_sk)
    while True:
        req = recv_req(client_sk)
        print('Client request: {}'.format(req))

        if req == 'Exit':
            break

        menu(client_sk, req)
    return


def process_login(client_sk):
    req = recv_req(client_sk)
    username, password = req.split(' ')
    count = 0
    for x in lst_user:
        if x['name'] == username and x['password'] == password:
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

    # if req == '3':
    #     search_item(client_sk)
    #
    # if req == '4':
    #     buy_item(client_sk)
    #
    # if req == '5':
    #     sell_item(client_sk)
    #
    # if req == '6':
    #     transaction_history(client_sk)
    #
    # if req == '7':
    #     disconnect(client_sk)


def all_item(client_sk):
    buying = ''
    selling = ''
    for x in reversed(lst_Stock):
        if x['status'] == 'WTB':
            buying = str(x) + '$$' + buying

        if x['status'] == 'WTS':
            selling = str(x) + '$$' + selling

    all_stock = buying + '$!$' + selling
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


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    server_sk = create_socket(host, port)

    start_server(server_sk)

