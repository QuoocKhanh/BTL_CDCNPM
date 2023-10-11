import socket
import pymongo


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
    while True:
        req = input('Add request here: ')
        send_req(sk, req)
        if req == 'Exit':
            break
    return


if __name__ == '__main__':
    host = 'localhost'
    port = 8050

    client_sk = create_socket(host, port)

    start_client(client_sk)
