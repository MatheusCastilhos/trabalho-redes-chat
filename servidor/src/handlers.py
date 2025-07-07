import json
import os

from src.storage import (
    create_user, login_user, logout_user, get_user_by_token,
    get_all_logged_users, user_exists,
    store_message, get_messages_for_user, delete_message,
    get_all_news, store_news, delete_news,
    save_document, get_document, get_content_type, delete_document,
    list_all_documents
)

def send_cors_headers(self):
    """Envia os cabeçalhos CORS padrão."""
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type, X-Filename')


def send_json(self, obj, status=200):
    try:
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        send_cors_headers(self)
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))
    except ConnectionAbortedError:
        # Cliente desconectou antes do envio da resposta
        pass

def send_error_json(self, status, message):
    try:
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        send_cors_headers(self)
        self.end_headers()
        payload = {"error": message}
        self.wfile.write(json.dumps(payload).encode('utf-8'))
    except ConnectionAbortedError:
        pass

def send_204_no_content(self):
    try:
        self.send_response(204)
        send_cors_headers(self)
        self.end_headers()
    except ConnectionAbortedError:
        pass
    return None  # explícito

def handle_register(self, username):
    print(f"[DEBUG] handle_register chamado para username={username}")
    username = username.strip()
    if not username:
        return send_error_json(self, 400, "Nome inválido")
    if user_exists(username):
        return send_error_json(self, 409, "Usuário já existe")
    if create_user(username):
        return send_json(self, {"message": "Usuário criado"}, status=201)
    else:
        return send_error_json(self, 500, "Erro ao criar usuário")

def handle_login(self, username):
    username = username.strip()
    if not user_exists(username):
        return send_error_json(self, 404, "Usuário não existe")
    token = login_user(username)
    if not token:
        return send_error_json(self, 409, "Usuário já logado")
    return send_json(self, {"token": token})

def handle_logout(self, token):
    if not token or not get_user_by_token(token):
        return send_error_json(self, 403, "Usuário não autenticado")
    logout_user(token)
    return send_json(self, {"message": "Logout realizado"})

def handle_list_users(self, token):
    if not get_user_by_token(token):
        return send_error_json(self, 403, "Usuário não autenticado")
    users = list(get_all_logged_users())
    if not users:
        return send_204_no_content(self)
    return send_json(self, users)

def handle_get_messages(self, token):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    msgs = get_messages_for_user(user)
    if not msgs:
        return send_204_no_content(self)
    result = {
        msg["id"]: [msg["dir"], msg["user"], msg["text"], msg["time"]]
        for msg in msgs
    }
    return send_json(self, result)

def handle_send_message(self, token, to_user):
    from_user = get_user_by_token(token)
    if not from_user:
        return send_error_json(self, 403, "Usuário não autenticado")
    to_user = to_user.strip()
    if not user_exists(to_user):
        return send_error_json(self, 403, "Usuário de destino inválido")
    content_length = int(self.headers.get("Content-Length", 0))
    text = self.rfile.read(content_length).decode("utf-8").strip()
    if not text:
        return send_error_json(self, 400, "Mensagem vazia")
    store_message(from_user, to_user, text)
    return send_json(self, {"message": "Mensagem enviada"})

def handle_delete_message(self, token, msgid):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    if delete_message(user, msgid):
        try:
            self.send_response(204)
            send_cors_headers(self)
            self.end_headers()
        except ConnectionAbortedError:
            pass
        return None  # adicionado
    else:
        return send_error_json(self, 404, "Mensagem não encontrada")

def handle_get_news(self, token):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    data = get_all_news()
    if not data:
        return send_204_no_content(self)
    result = {
        nid: [n["user"], n["text"], n["time"]]
        for nid, n in data.items()
    }
    return send_json(self, result)

def handle_post_news(self, token):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    content_length = int(self.headers.get("Content-Length", 0))
    text = self.rfile.read(content_length).decode("utf-8").strip()
    if not text:
        return send_error_json(self, 400, "Notícia vazia")
    store_news(user, text)
    return send_json(self, {"message": "Notícia publicada"})

def handle_delete_news(self, token, newsid):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    if delete_news(user, newsid):
        try:
            self.send_response(204)
            send_cors_headers(self)
            self.end_headers()
        except ConnectionAbortedError:
            pass
        return None  # adicionado
    else:
        return send_error_json(self, 404, "Notícia não encontrada")

def handle_upload_doc(self, token):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    content_type = self.headers.get("Content-Type")
    filename = self.headers.get("X-Filename")
    if not filename or not content_type:
        return send_error_json(self, 400, "Cabeçalhos X-Filename e Content-Type são obrigatórios")
    content_length = int(self.headers.get("Content-Length", 0))
    file_content = self.rfile.read(content_length)
    success, msg = save_document(user, filename, content_type, file_content)
    status = 200 if success else 400
    if success:
        return send_json(self, {"message": msg}, status=status)
    else:
        return send_error_json(self, status, msg)

def handle_delete_doc(self, token, owner, docname):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    if user != owner:
        return send_error_json(self, 403, "Permissão negada para exclusão do documento")
    if delete_document(owner, docname):
        try:
            self.send_response(204)
            send_cors_headers(self)
            self.end_headers()
        except ConnectionAbortedError:
            pass
    else:
        return send_error_json(self, 404, "Documento não encontrado")

def handle_list_docs(self, token):
    user = get_user_by_token(token)
    if not user:
        return send_error_json(self, 403, "Usuário não autenticado")
    docs = list_all_documents()
    if not docs:
        return send_204_no_content(self)
    return send_json(self, docs)

def handle_get_doc_public(self, path):
    parts = path.split("/")
    if len(parts) < 6:
        return send_error_json(self, 400, "Formato da URL inválido")
    owner = parts[4]
    docname = "/".join(parts[5:])  # Suporta nomes com barras

    if not user_exists(owner):
        return send_error_json(self, 404, "Usuário não existe")
    filepath = get_document(owner, docname)
    if not filepath or not os.path.exists(filepath):
        return send_error_json(self, 404, "Documento não encontrado")
    mime_type = get_content_type(docname)
    try:
        with open(filepath, "rb") as f:
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(os.path.getsize(filepath)))
            send_cors_headers(self)
            self.end_headers()
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                self.wfile.write(chunk)
    except Exception as e:
        return send_error_json(self, 500, f"Erro ao ler arquivo: {e}")