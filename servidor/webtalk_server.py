from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from src import handlers

class WebTalkHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Filename')

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        auth = self.headers.get('Authorization')

        if path == "/webtalk/users":
            handlers.handle_list_users(self, auth)
        elif path == "/webtalk/messages":
            handlers.handle_get_messages(self, auth)
        elif path == "/webtalk/news":
            handlers.handle_get_news(self, auth)
        elif path.startswith("/webtalk/doc/list"):
            handlers.handle_list_docs(self, auth)
        elif path.startswith("/webtalk/doc/public/"):
            handlers.handle_get_doc_public(self, path)
        else:
            self.send_error(404, "Rota GET não encontrada")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        auth = self.headers.get('Authorization')

        if path.startswith("/webtalk/register/"):
            username = path.split("/")[-1]
            handlers.handle_register(self, username)
        elif path.startswith("/webtalk/login/"):
            username = path.split("/")[-1]
            handlers.handle_login(self, username)
        elif path == "/webtalk/logout":
            handlers.handle_logout(self, auth)
        elif path.startswith("/webtalk/messages/"):
            to_user = path.split("/")[-1]
            handlers.handle_send_message(self, auth, to_user)
        elif path == "/webtalk/news":
            handlers.handle_post_news(self, auth)
        else:
            self.send_error(404, "Rota POST não encontrada")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        auth = self.headers.get('Authorization')

        if path.startswith("/webtalk/messages/"):
            msgid = path.split("/")[-1]
            handlers.handle_delete_message(self, auth, msgid)
        elif path.startswith("/webtalk/news/"):
            newsid = path.split("/")[-1]
            handlers.handle_delete_news(self, auth, newsid)
        elif path.startswith("/webtalk/doc/"):
            parts = path.split("/")
            if len(parts) >= 5:
                owner = parts[3]
                docname = "/".join(parts[4:])  # Suporta nomes com barras
                handlers.handle_delete_doc(self, auth, owner, docname)
            else:
                self.send_error(404, "Rota DELETE de documento inválida")
        else:
            self.send_error(404, "Rota DELETE não encontrada")

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        auth = self.headers.get('Authorization')

        if path == "/webtalk/doc":
            handlers.handle_upload_doc(self, auth)
        else:
            self.send_error(404, "Rota PUT não encontrada")

def run_server():
    server_address = ("0.0.0.0", 7447)
    httpd = ThreadingHTTPServer(server_address, WebTalkHandler)
    print("Servidor WebTalk rodando em http://0.0.0.0:7447/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor interrompido pelo usuário")
    finally:
        httpd.server_close()
        print("Servidor finalizado")

if __name__ == "__main__":
    run_server()