from flask import Blueprint, request, Response, jsonify, send_file
from src.storage import (
    create_user, login_user, logout_user, get_user_by_token,
    get_all_logged_users, user_exists,
    store_message, get_messages_for_user, delete_message,
    get_all_news, store_news, delete_news,
    save_document, get_document, get_content_type, delete_document,
    list_all_documents
)

webtalk = Blueprint("webtalk", __name__)

# ========== HELPERS ==========

def require_auth():
    token = request.headers.get("Authorization")
    user = get_user_by_token(token)
    if not user:
        return None, Response("Usuário não autenticado", status=403)
    return user, None

# ========== AUTENTICAÇÃO ==========

@webtalk.route("/register/<username>", methods=["POST"])
def register(username):
    username = username.strip()
    if not username:
        return Response("Nome inválido", status=400)
    if user_exists(username):
        return Response("Usuário já existe", status=409)
    return Response("Usuário criado", status=201) if create_user(username) else Response("Erro ao criar", status=500)

@webtalk.route("/login/<username>", methods=["POST"])
def login(username):
    username = username.strip()
    if not user_exists(username):
        return Response("Usuário não existe", status=404)
    token = login_user(username)
    return (jsonify({"token": token}), 200) if token else Response("Usuário já logado", status=409)

@webtalk.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization")
    if not token or not get_user_by_token(token):
        return Response("Usuário não autenticado", status=403)
    logout_user(token)
    return Response("Logout realizado", status=200)

# ========== USUÁRIOS ONLINE ==========

@webtalk.route("/users", methods=["GET"])
def list_users():
    _, error = require_auth()
    if error:
        return error
    users = list(get_all_logged_users())
    if not users:
        return Response(status=204)
    return jsonify(users), 200

# ========== MENSAGENS ==========

@webtalk.route("/messages", methods=["GET"])
def get_messages():
    user, error = require_auth()
    if error:
        return error
    msgs = get_messages_for_user(user)
    if not msgs:
        return Response(status=204)
    return jsonify({
        msg["id"]: [msg["dir"], msg["user"], msg["text"], msg["time"]]
        for msg in msgs
    }), 200

@webtalk.route("/messages/<to_user>", methods=["POST"])
def send_message(to_user):
    from_user, error = require_auth()
    if error:
        return error
    if not user_exists(to_user.strip()):
        return Response("Usuário de destino inválido", status=403)
    text = request.get_data(as_text=True).strip()
    if not text:
        return Response("Mensagem vazia", status=400)
    store_message(from_user, to_user.strip(), text)
    return Response("Mensagem enviada", status=200)

@webtalk.route("/messages/<msgid>", methods=["DELETE"])
def delete_msg(msgid):
    user, error = require_auth()
    if error:
        return error
    return Response(status=204) if delete_message(user, msgid) else Response("Mensagem não encontrada", status=404)

# ========== NOTÍCIAS ==========

@webtalk.route("/news", methods=["GET", "POST"])
def news():
    user, error = require_auth()
    if error:
        return error
    if request.method == "GET":
        data = get_all_news()

        if not data:
            return Response(status=204)

        return jsonify({
            nid: [n["user"], n["text"], n["time"]]
            for nid, n in data.items()
        }), 200
    else:
        text = request.get_data(as_text=True).strip()
        if not text:
            return Response("Notícia vazia", status=400)
        store_news(user, text)
        return Response("Notícia publicada", status=200)

@webtalk.route("/news/<newsid>", methods=["DELETE"])
def delete_news_route(newsid):
    user, error = require_auth()
    if error:
        return error
    return Response(status=204) if delete_news(user, newsid) else Response("Notícia não encontrada", status=404)

# ========== DOCUMENTOS ==========

@webtalk.route("/doc", methods=["PUT"])
def upload_doc():
    user, error = require_auth()
    if error:
        return error
    file = request.files.get("file")
    if not file or file.filename == '':
        return Response("Arquivo inválido", status=400)
    success, message = save_document(user, file.filename, file.content_type, file.read())
    return Response(message, status=200 if success else 400)

@webtalk.route("/doc/<docname>", methods=["DELETE"])
def delete_doc(docname):
    user, error = require_auth()
    if error:
        return error
    return Response(status=204) if delete_document(user, docname) else Response("Documento não encontrado", status=404)

@webtalk.route("/doc/list", methods=["GET"])
def list_docs():
    user, error = require_auth()
    if error:
        return error
    docs = list_all_documents()  # ← sem passar o usuário
    if not docs:
        return Response(status=204)
    return jsonify(docs), 200

# ========== DOCUMENTOS PÚBLICOS (sem token) ==========

@webtalk.route("/doc/public/<username>/<docname>", methods=["GET"])
def get_doc_public(username, docname):
    if not user_exists(username):
        return Response("Usuário não existe", status=404)
    file_path = get_document(username, docname)
    if not file_path:
        return Response("Documento não encontrado", status=404)
    return send_file(file_path, mimetype=get_content_type(docname))