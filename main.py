# SSLv3Trap
# v1.1 - 09.09.2024

import socket
import socketserver
import argparse
import selectors
import ssl

NAME = "SSLv3 Trap"
VERSION = "1.0"

parser = argparse.ArgumentParser(description='Proxy server - {0} v{1}'.format(NAME, VERSION))
parser.add_argument(
    '--target_server_address',
    type=str,
    default="127.0.0.1",
    help='Address of the target server (default: "127.0.0.1")'
)
parser.add_argument(
    '--target_server_port',
    type=int,
    default=19120,
    help='Port of the target server (default: 19120)'
)
parser.add_argument(
    '--proxy_server_address',
    type=str,
    default="127.0.0.1",
    help='Address of the proxy server (default: "127.0.0.1")'
)
parser.add_argument(
    '--proxy_server_port',
    type=int,
    default=19100,
    help='Port of the proxy server (default: 19100)'
)
parser.add_argument(
    '--has_debug',
    type=bool,
    default=False,
    help='For the developer (default: false)'
)
parser.add_argument(
    '--path_cert',
    type=str,
    help='Path to the certificate',
    required=True
)
parser.add_argument(
    '--path_key',
    type=str,
    help='Path to the private key',
    required=True
)

args = parser.parse_args()

class Logger:

    @staticmethod
    def info(value: str, *options):
        print(value.format(*options))

    @staticmethod
    def debug(value: str, *options):
        if not args.has_debug: return
        print(value.format(*options))

    @staticmethod
    def error(value: str, *options):
        if not args.has_debug: return
        print(value.format(*options))

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def setup(self):

        Logger.debug("Connected {0}:{1}", *self.client_address)

        try:
            self.request = self.server.sslContext.wrap_socket(self.request, server_side=True)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((args.target_server_address, args.target_server_port))
            self.client_socket.setblocking(False)
            self.client_socket.send(bytes("C %s:%s" % self.client_address, "ascii"))
        except Exception as error:
            Logger.error("ERROR: {1}:{2}: {0}", error, *self.client_address)
            self.request.close()
            return

        self.request.setblocking(False)

        self.selector = selectors.DefaultSelector()

        self.selector.register(self.client_socket, selectors.EVENT_READ, self.handle_client)
        self.selector.register(self.request, selectors.EVENT_READ, self.handle_proxy)

    def handle_client(self):
        data = self.client_socket.recv(1024)
        if not data: raise Exception("Target server disconnected")
        #data = str(data, args.encoding)
        Logger.debug("FORWARDING: {1}:{2} << {0}",  data, *self.client_address)
        self.request.send(data)

    def handle_proxy(self):
        data = self.request.recv(1024)
        if not data: raise Exception("Client proxy disconnected")
        #data = str(data, args.encoding) bytes(data, args.encoding)
        Logger.debug("FORWARDING: {1}:{2} >> {0}",  data, *self.client_address)
        self.client_socket.send(data)

    def handle(self):
        while True:
            try:
                events = self.selector.select()
                for key, _ in events:
                    callback = key.data
                    callback()
            except Exception as error:
                Logger.error("ERROR: {1}:{2}: {0}", error, *self.client_address)
                break

        self.client_socket.close()
        self.request.close()

    def finish(self):
        Logger.debug("Disconnected {0}:{1}", *self.client_address)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = False
    daemon_threads = False

    def __init__(self, *_args, **kwargs):
        super().__init__(*_args, **kwargs)

        self.sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
        self.sslContext.load_cert_chain(certfile=args.path_cert, keyfile=args.path_key)
        self.sslContext.set_ciphers("SSLv3")
        self.sslContext.verify_mode = ssl.CERT_NONE

if __name__ == "__main__":

    try:
        server = ThreadedTCPServer((args.proxy_server_address, args.proxy_server_port), ThreadedTCPRequestHandler)
        ip, port = server.server_address

        Logger.info("Proxy Server {0} v{1} started on {2}:{3}", NAME, VERSION, ip, port)
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
    except socket.error as error:
        Logger.error("ERROR: {0}", error)
    finally:
        Logger.info("Stopped")