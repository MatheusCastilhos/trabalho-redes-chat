from flask import Blueprint, request, Response, jsonify
from src.storage import (
    create_user, login_user, logout_user, get_user_by_token,
    get_all_logged_users, user_exists,
    store_message, get_messages_for_user, 
    get_all_news, store_news,
    delete_message, delete_news
)

webtalk_blueprint = Blueprint('webtalk', __name__)


# ---------- AUTENTICAÇÃO ----------

@webtalk_blueprint.route("/register/<username>", methods=["POST"])
def register(username):
    username = username.strip()
    if not username:
        return Response("Nome inválido", status=400)

    if user_exists(username):
        return Response("Usuário já existe", status=409)

    success = create_user(username)
    if success:
        return Response("Usuário criado", status=201)
    else:
        return Response("Erro ao criar usuário", status=500)


@webtalk_blueprint.route("/login/<username>", methods=["POST"])
def login(username):
    username = username.strip()
    if not user_exists(username):
        return Response("Usuário não existe", status=404)

    token = login_user(username)
    if not token:
        return Response("Usuário já logado", status=409)

    return jsonify({"token": token}), 200


@webtalk_blueprint.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization")
    if not token or not get_user_by_token(token):
        return Response("Usuário não autenticado", status=403)

    logout_user(token)
    return Response("Logout realizado", status=200)


# ---------- USUÁRIOS ONLINE ----------

@webtalk_blueprint.route("/users", methods=["GET"])
def list_users():
    token = request.headers.get("Authorization")
    user = get_user_by_token(token)
    if not user:
        return Response("Usuário não autenticado", status=403)

    all_users = list(get_all_logged_users())
    return jsonify(all_users), 200 if all_users else Response(status=204)


# ---------- MENSAGENS ----------

@webtalk_blueprint.route("/messages", methods=["GET"])
def get_messages():
    token = request.headers.get("Authorization")
    username = get_user_by_token(token)
    if not username:
        return Response("Usuário não autenticado", status=403)

    msgs = get_messages_for_user(username)
    if not msgs:
        return Response(status=204)

    result = {
        msg["id"]: [msg["dir"], msg["user"], msg["text"], msg["time"]]
        for msg in msgs
    }
    return jsonify(result), 200


@webtalk_blueprint.route("/messages/<to_user>", methods=["POST"])
def send_message(to_user):
    token = request.headers.get("Authorization")
    from_user = get_user_by_token(token)
    to_user = to_user.strip()

    if not from_user or not user_exists(to_user):
        return Response("Usuário inválido", status=403)

    text = request.get_data(as_text=True)
    if not text.strip():
        return Response("Mensagem vazia", status=400)

    store_message(from_user, to_user, text)
    return Response("Mensagem enviada", status=200)


@webtalk_blueprint.route("/messages/<msgid>", methods=["DELETE"])
def delete_msg(msgid):
    token = request.headers.get("Authorization")
    username = get_user_by_token(token)
    if not username:
        return Response("Usuário não autenticado", status=403)

    success = delete_message(username, msgid)
    return Response(status=204) if success else Response("Mensagem não encontrada", status=404)


# ---------- NOTÍCIAS ----------

@webtalk_blueprint.route("/news", methods=["GET"])
def get_news():
    token = request.headers.get("Authorization")
    username = get_user_by_token(token)
    if not username:
        return Response("Usuário não autenticado", status=403)

    all_news = get_all_news()
    if not all_news:
        return Response(status=204)

    result = {
        news_id: [n["user"], n["text"], n["time"]]
        for news_id, n in all_news.items()
    }
    return jsonify(result), 200


@webtalk_blueprint.route("/news", methods=["POST"])
def publish_news():
    token = request.headers.get("Authorization")
    username = get_user_by_token(token)
    if not username:
        return Response("Usuário não autenticado", status=403)

    text = request.get_data(as_text=True)
    if not text.strip():
        return Response("Notícia vazia", status=400)

    store_news(username, text)
    return Response("Notícia publicada", status=200)


@webtalk_blueprint.route("/news/<newsid>", methods=["DELETE"])
def delete_news_route(newsid):
    token = request.headers.get("Authorization")
    username = get_user_by_token(token)
    if not username:
        return Response("Usuário não autenticado", status=403)

    success = delete_news(username, newsid)
    return Response(status=204) if success else Response("Notícia não encontrada", status=404)