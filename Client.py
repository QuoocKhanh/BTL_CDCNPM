import socket
import time
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
        login(sk)
        make_request(sk)
        break
    print('Connection to server closed !!!')
    return


def make_request(sk):
    while True:
        print(Fore.CYAN + 'All(1) Board(2) Search(3) Sell(4) Buy(5) History(6) Exit(7)' + Fore.RESET)
        req = input('Add request here: ')
        menu(sk, req)
        break
    return


# def process_server_response(sk):
#     res = recv_res(sk)
#     if res == 'success':
#         return ''
#     if res == '0':
#         return 'fail'


def login(sk):
    username = input('Username: ')
    password = input('Password: ')
    client_name = username + ' ' + password
    send_req(sk, client_name)

    res = recv_res(sk)
    if res == 'success':
        return
    if res == 'fail':
        print('Username or Password incorrect !!!')
        login(sk)


def menu(sk, req):
    if not req.isdigit():
        make_request(sk)

    if 1 > int(req) or int(req) > 7:
        make_request(sk)

    if req == '1':
        all_item(sk)

    if req == '2':
        top_server(sk)

    if req == '3':
        search_item(sk)

    if req == '4':
        buy_item(sk)

    if req == '5':
        sell_item(sk)

    if req == '6':
        transaction_history(sk)

    if req == '7':
        disconnect(sk)


def all_item(sk):
    print(Fore.CYAN + 'ALL STOCKS AVAILABLE: ' + Fore.RESET)
    send_req(sk, '1')
    res = recv_res(sk)
    buying_stock, selling_stock = res.split('$!$')

    buying_stock = buying_stock.split('$$')
    selling_stock = selling_stock.split('$$')

    print(Fore.GREEN + 'BUYING:' + Fore.RESET)
    for x in buying_stock:
        print(x)

    print(Fore.GREEN + 'SELLING:' + Fore.RESET)
    for y in selling_stock:
        print(y)

    buying_stock.clear()
    selling_stock.clear()

    make_request(sk)


def top_server(sk):
    print(Fore.CYAN + 'TOP SERVER' + Fore.RESET)
    send_req(sk, '2')
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

    make_request(sk)


def search_item(sk):
    send_req(sk, '3')
    print('SEARCH')
    trader_name = input('Nhap ten trader: ')
    name = input('Nhap ten: ')

    req = trader_name + '@@' + name
    send_req(sk, req)
    res = recv_res(sk)
    print(Fore.CYAN + 'FOUND THESE STOCKS: ' + Fore.RESET)
    lst_stock = res.split('@@')
    for i in lst_stock:
        print(i)
    lst_stock.clear()

    make_request(sk)


def buy_item(sk):
    a = 'nothing here'


def sell_item(sk):
    a = 'nothing here'


def transaction_history(sk):
    a = 'nothing here'


def disconnect(sk):
    send_req(sk, '7')
    sk.close()
    return


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    client_sk = create_socket(host, port)

    start_client(client_sk)
