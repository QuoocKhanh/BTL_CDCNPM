import socket
import time
from datetime import datetime

from tabulate import tabulate
from colorama import Fore


def create_socket(h, p):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")
    sk.connect((h, p))
    print("Socket connected to %s on port %s" % (host, port))
    return sk


def send_req(sk, req):
    req = req.encode('utf-8')
    sk.send(req)


def recv_res(sk):
    data = ''
    res = ''
    while not data:
        data = sk.recv(4096)
        if not data:
            raise ConnectionError()
        res = data.decode('utf-8')
    return res


def start_client(sk):
    while True:
        data = recv_res(sk)
        if not data:
            break
        print(data)
        client_name = login(sk)
        client_name = str(client_name)
        make_request(sk, client_name)
        break
    print(Fore.YELLOW + 'Connection to server closed !!!' + Fore.RESET)
    return


def make_request(sk, client_name):
    while True:
        print(Fore.CYAN + 'All(1) Board(2) Search(3) Buy(4) Sell(5) Account_Infor(6) Exit(7)' + Fore.RESET)
        req = input('Add request here: ')
        menu(sk, req, client_name)
        break
    return


def login(sk):
    username = input('Username: ')
    password = input('Password: ')
    client_acc = username + ' ' + password
    send_req(sk, client_acc)

    res = recv_res(sk)
    if res == 'success':
        return username
    if res == 'fail':
        print(Fore.RED + 'Username or Password incorrect !!!' + Fore.RESET)
        login(sk)


def menu(sk, req, client_name):
    if not req.isdigit():
        make_request(sk, client_name)

    if 1 > int(req) or int(req) > 7:
        make_request(sk, client_name)

    send_req(sk, req)

    if req == '1':
        all_item(sk, client_name)

    if req == '2':
        top_server(sk, client_name)

    if req == '3':
        search_item(sk, client_name)

    if req == '4':
        buy_item(sk, client_name)

    if req == '5':
        sell_item(sk, client_name)

    if req == '6':
        acc_info(sk, client_name)

    if req == '7':
        disconnect(sk)


def all_item(sk, client_name):

    print(Fore.CYAN + 'ALL STOCKS AVAILABLE: ' + Fore.RESET)
    res = recv_res(sk)

    all_stock = res.split('$$')
    for x in all_stock:
        print(x)

    make_request(sk, client_name)


def top_server(sk, client_name):

    print(Fore.CYAN + 'TOP SERVER' + Fore.RESET)
    res = recv_res(sk)
    top_legit, top_spent = res.split('$!$')

    top_legit = top_legit.split('$$')
    top_spent = top_spent.split('$$')

    print(Fore.GREEN + 'Top transaction trader' + Fore.RESET)
    for a in top_legit:
        print(a)

    print(Fore.GREEN + 'Top spent trader' + Fore.RESET)
    for b in top_spent:
        print(b)

    top_legit.clear()
    top_spent.clear()

    make_request(sk, client_name)


def search_item(sk, client_name):
    print(Fore.CYAN + 'SEARCH' + Fore.RESET)
    trader_name = input('Trader name: ')
    name = input('Stock name: ')
    money = input('Money per stock: ')
    quantity = input('Quantity: ')

    req = trader_name + '@@' + name + '@@' + money + '@@' + quantity
    send_req(sk, req)

    if trader_name == 'exit' or name == 'exit' or money == 'exit' or quantity == 'exit':
        make_request(sk, client_name)

    res = recv_res(sk)
    print(Fore.CYAN + 'FOUND THESE STOCKS: ' + Fore.RESET)
    lst_stock = res.split('@@')
    for i in lst_stock:
        print(i)
    lst_stock.clear()

    make_request(sk, client_name)


def buy_item(sk, client_name):
    state = 'BUY'
    utc_time = datetime.utcnow()
    curr_time = time.localtime()
    local_time = time.strftime("%H:%M:%S", curr_time)

    print(Fore.CYAN + 'BUYING...' + Fore.RESET)
    stock_id = input('Stock id: ')
    name = input('Stock name: ')
    money = input('Money per stock: ')
    quantity = input('Quantity: ')

    if stock_id == '' or name == '' or money == '' or quantity == '' or not money.isnumeric() or not quantity.isnumeric():
        print(Fore.RED + 'Do you miss any fields ?' + Fore.RESET)
        buy_item(sk, client_name)

    if stock_id == 'exit' or name == 'exit' or money == 'exit' or quantity == 'exit':
        make_request(sk, client_name)

    req = client_name + '$' + stock_id + '$' + name + '$' + money + '$' + quantity + '$' + str(utc_time)
    send_req(sk, req)
    res = recv_res(sk)
    if res == 'found':
        print('Found')
        confirm_action(sk, state, client_name)

    if res == 'Not enough money !!!':
        print(Fore.RED + res + Fore.RESET)
        make_request(sk, client_name)

    res = recv_res(sk)

    if res == 'success':
        data = str(dict(id=stock_id, name=name, money=money, quantity=quantity))
        print(Fore.GREEN + client_name + ' ' + state + ' ' + data + ' SUCCESSFUL !!!' + Fore.RESET)
        print('Local time: ', local_time)
        print('UTC time: ', utc_time)
        print(' ')

        make_request(sk, client_name)

    if res == 'fail':
        data = str(dict(id=stock_id, name=name, money=money, quantity=quantity))
        print(Fore.GREEN + client_name + ' ' + state + ' ' + data + ' FAIL !!!' + Fore.RESET)
        print('Local time: ', local_time)
        print('UTC time: ', utc_time)
        print(' ')

        make_request(sk, client_name)


def sell_item(sk, client_name):
    utc_time = datetime.utcnow()
    curr_time = time.localtime()
    local_time = time.strftime("%H:%M:%S", curr_time)
    print(Fore.CYAN + 'SELLING...' + Fore.RESET)

    stock_id = input('Stock id: ')
    name = input('Stock name: ')
    money = input('Money per stock: ')
    quantity = input('Quantity: ')

    if stock_id == '' or name == '' or money == '' or quantity == '' or not money.isnumeric() or not quantity.isnumeric():
        print(Fore.RED + 'Do you miss any fields ?' + Fore.RESET)
        buy_item(sk, client_name)

    if stock_id == 'exit' or name == 'exit' or money == 'exit' or quantity == 'exit':
        make_request(sk, client_name)

    req = client_name + '$' + stock_id + '$' + name + '$' + money + '$' + quantity + '$' + str(utc_time)
    send_req(sk, req)
    print(req)
    res = recv_res(sk)
    if res == 'found':
        print('Found')
        state = 'UPDATE'
        confirm_action(sk, state, client_name)

    if res == 'available':
        print('Available')
        state = 'SELL'
        confirm_action(sk, state, client_name)

    res = recv_res(sk)
    print(res)

    if res == 'success':
        data = str(dict(id=stock_id, name=name, money=money, quantity=quantity))
        print(Fore.GREEN + 'Your order ' + data + ' upload SUCCESSFUL !!!' + Fore.RESET)
        print('Local time: ', local_time)
        print('UTC time: ', utc_time)
        print(' ')

        make_request(sk, client_name)

    if res == 'fail':
        data = str(dict(id=id, name=name, money=money, quantity=quantity))
        print(Fore.GREEN + 'Your order ' + data + ' upload FAIL !!!' + Fore.RESET)
        print('Local time: ', local_time)
        print('UTC time: ', utc_time)
        print(' ')

        make_request(sk, client_name)


def confirm_action(sk, state, client_name):
    print(Fore.RED + "SERVER WILL TAKE 5% FROM THE TRANSACTION !!!" + Fore.RESET)
    confirm = input('Do you want to {} this (YES/NO) '.format(state))
    if confirm == 'YES':
        send_req(sk, 'YES')
        return
    if confirm == 'NO':
        make_request(sk, client_name)

    confirm_action(sk, state, client_name)


def acc_info(sk, client_name):
    client_name = client_name + '!!'
    send_req(sk, client_name)
    msg = recv_res(sk)
    name, point, spent, curr_money, curr_stock, buy_order, sell_order = msg.split('!!')

    a = [[Fore.CYAN + 'Username:', Fore.GREEN + name, Fore.CYAN + 'Current money:', Fore.GREEN + curr_money],
         [Fore.CYAN + 'Trading point:', Fore.RED + point, Fore.CYAN + 'Total spent:', Fore.RED + spent + Fore.RESET]]
    print(tabulate(a))

    print(Fore.CYAN + 'Current Stock: ' + Fore.RESET)
    curr_stock = curr_stock.split('...')
    for x in curr_stock:
        print(x)

    print(Fore.CYAN + 'Buy order: ' + Fore.RESET)
    buy_order = buy_order.split('...')
    for y in buy_order:
        print(y)

    print(Fore.CYAN + 'Sell order: ' + Fore.RESET)
    sell_order = sell_order.split('...')
    for z in sell_order:
        print(z)

    make_request(sk, client_name)


def disconnect(sk):
    sk.close()
    return


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    client_sk = create_socket(host, port)

    start_client(client_sk)
