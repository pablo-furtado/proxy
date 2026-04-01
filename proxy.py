from dotenv import load_dotenv
load_dotenv()
import os
import socket
import threading
import datetime
import time

LISTEN_ADDR = "0.0.0.0"
LISTEN_PORT = int(os.getenv("LISTEN_PORT", 1080))
ALLOWED_IP = os.getenv("ALLOWED_IP", ")/*IP_ADDRESS*/")

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")


def keep_alive(sock):
    while True:
        try:
            sock.send(b"\x00")  # byte mínimo
        except:
            break
        time.sleep(30)

def handle_client(client_socket, client_ip):
    try:

        log(f"Nova conexão de {client_ip}")

        # handshake SOCKS5

        client_socket.recv(262)

        client_socket.sendall(b"\x05\x00")

        # request

        request = client_socket.recv(4)

        addr_type = request[3]

        if addr_type == 1:  # IPv4

            addr = socket.inet_ntoa(client_socket.recv(4))

        elif addr_type == 3:  # Domain

            domain_length = client_socket.recv(1)[0]

            addr = client_socket.recv(domain_length).decode()

        else:

            log(f"Tipo de endereço não suportado: {addr_type}")

            client_socket.close()

            return

        port = int.from_bytes(client_socket.recv(2), 'big')

        log(f"{client_ip} -> {addr}:{port}")

        # connect to target

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        remote.settimeout(300)
        
        remote.connect((addr, port))

        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        client_socket.settimeout(300)
        threading.Thread(target=keep_alive, args=(remote,), daemon=True).start()
        threading.Thread(target=keep_alive, args=(client_socket,), daemon=True).start()
        client_socket.sendall(b"\x05\x00\x00\x01")

        client_socket.sendall(socket.inet_aton("0.0.0.0") + (0).to_bytes(2, 'big'))

        def forward(source, destination, direction):

            try:

                while True:

                    data = source.recv(65536)

                    if not data:

                        break

                    destination.sendall(data)

            except Exception as e:
                log(f"Erro forward: {e}")
            finally:
                source.close()
                destination.close()
                log(f"Conexão encerrada ({direction}) {client_ip} -> {addr}:{port}")

        t1 = threading.Thread(target=forward, args=(client_socket, remote, "C→R"))

        t2 = threading.Thread(target=forward, args=(remote, client_socket, "R→C"))

        t1.start()

        t2.start()

    except Exception as e:
        log(f"Erro: {e}")
        client_socket.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((LISTEN_ADDR, LISTEN_PORT))

    server.listen(20)

    log(f"Proxy SOCKS5 rodando em {LISTEN_PORT}")

    while True:

        client_socket, addr = server.accept()

        client_ip = addr[0]

        if client_ip != ALLOWED_IP:

            log(f"Conexão BLOQUEADA de {client_ip}")

            client_socket.close()

            continue

        threading.Thread(target=handle_client, args=(client_socket, client_ip), daemon=True).start()

if __name__ == "__main__":
    start()

