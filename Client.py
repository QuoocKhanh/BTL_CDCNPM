import socket
import time
from colorama import Fore


def create_socket(h, p):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket created")
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
        make_request(sk)

        break
    sk.close()
    print('Connection close !!!')
    return


def make_request(sk):
    login(sk)
    while True:
        print(Fore.CYAN + '(All(1) Board(2) Search(3) Sell(4) Buy(5) History(6) Exit(7)' + Fore.RESET)
        req = input('Add request here: ')
        menu(sk, req)
        # send_req(sk, req)
        if req == 'Exit':
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
    if req == '1':
        all_item(sk)

    if req == '2':
        top_server(sk)

    # if req == '3':
    #     search_item(sk)
    #
    # if req == '4':
    #     buy_item(sk)
    #
    # if req == '5':
    #     sell_item(sk)
    #
    # if req == '6':
    #     transaction_history(sk)
    #
    # if req == '7':
    #     disconnect(sk)


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
    return


def top_server(sk):
    print(Fore.CYAN + 'TOP SERVER' + Fore.RESET)
    send_req(sk, '2')
    res = recv_res(sk)
    top_legit, top_spent = res.split('$!$')

    top_legit = top_legit.split('$$')
    top_spent = top_spent.split('$$')

    print(Fore.GREEN + 'Top transaction trader' + Fore.RESET)
    for a in reversed(top_legit):
        print(a)

    print(Fore.GREEN + 'Top spent trader' + Fore.RESET)
    for b in reversed(top_spent):
        print(b)

    top_legit.clear()
    top_spent.clear()
    return


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    client_sk = create_socket(host, port)

    start_client(client_sk)
