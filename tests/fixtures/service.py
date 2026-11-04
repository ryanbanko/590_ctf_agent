"""Synthetic target only. Never copy this file or its environment into the solver."""

import json
import os
import socket
import threading


def serve(port):
    content = json.dumps({"flag": os.environ["FIXTURE_FLAG"]}).encode()
    response = (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                + f"Content-Length: {len(content)}\r\nConnection: close\r\n\r\n".encode()
                + content)
    with socket.create_server(("0.0.0.0", port)) as server:
        while True:
            connection, _ = server.accept()
            with connection:
                connection.settimeout(2)
                try:
                    connection.recv(4096)
                    connection.sendall(response)
                except OSError:
                    pass


if __name__ == "__main__":
    # A live second port proves the firewall blocks a service that exists.
    threading.Thread(target=serve, args=(8001,), daemon=True).start()
    serve(8000)
