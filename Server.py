import socket
import pymongo


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
    while True:
        req = recv_req(client_sk)
        print('Client request: {}'.format(req))
        if req == 'Exit':
            break
    return


def menu(req):
    match req:
        case 1:
            all_item()
        case 2:
            top_server()
        case 3:
            buy_item()


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    server_sk = create_socket(host, port)

    start_server(server_sk)

