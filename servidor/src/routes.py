from flask import Blueprint, request, Response, jsonify
from src.storage import users, is_logged_in, log_user_in, log_user_out, get_messages_for_user, store_message, get_all_news, store_news, delete_message, delete_news

webtalk_blueprint = Blueprint('webtalk', __name__)

@webtalk_blueprint.route("/login/<username>", methods=["POST"])
def login(username):
    username = username.strip()
    if not username:
        return Response("Bad Request", status=400)

    if is_logged_in(username):
        return Response("Usuário já logado", status=409)

    log_user_in(username)
    return Response("OK", status=200)

@webtalk_blueprint.route("/logout/<username>", methods=["POST"])
def logout(username):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=404)

    log_user_out(username)
    return Response("OK", status=200)

@webtalk_blueprint.route("/users/<username>", methods=["GET"])
def get_users(username):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=403)

    if not users:
        return Response(status=204)

    # Modo JSON
    user_list = {u: [t] for u, t in users.items()}
    return jsonify(user_list), 200

@webtalk_blueprint.route("/msgs/<username>", methods=["GET"])
def get_messages(username):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=403)

    user_msgs = get_messages_for_user(username)
    if not user_msgs:
        return Response(status=204)

    result = {}
    for msg in user_msgs:
        result[msg["id"]] = [
            msg["dir"],
            msg["user"],
            msg["text"],
            msg["time"]
        ]

    return jsonify(result), 200

@webtalk_blueprint.route("/msg/<from_user>/<to_user>", methods=["POST"])
def send_message(from_user, to_user):
    from_user = from_user.strip()
    to_user = to_user.strip()
    if not (is_logged_in(from_user) and is_logged_in(to_user)):
        return Response("Usuário(s) não logado(s)", status=403)

    text = request.get_data(as_text=True)
    if not text.strip():
        return Response("Mensagem vazia", status=400)

    store_message(from_user, to_user, text)
    return Response("OK", status=200)

@webtalk_blueprint.route("/news/<username>", methods=["GET"])
def get_news(username):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=403)

    all_news = get_all_news()
    if not all_news:
        return Response(status=204)

    result = {}
    for news_id, n in all_news.items():
        result[news_id] = [
            n["dir"],
            n["user"],
            n["text"],
            n["time"]
        ]

    return jsonify(result), 200

@webtalk_blueprint.route("/news/<username>", methods=["POST"])
def publish_news(username):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=403)

    text = request.get_data(as_text=True)
    if not text.strip():
        return Response("Notícia vazia", status=400)

    store_news(username, text)
    return Response("OK", status=200)

@webtalk_blueprint.route("/msg/<username>/<msgid>", methods=["DELETE"])
def delete_msg(username, msgid):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=403)

    success = delete_message(username, msgid)
    if success:
        return Response(status=204)
    else:
        return Response("Mensagem não encontrada ou sem permissão", status=404)

@webtalk_blueprint.route("/news/<username>/<newsid>", methods=["DELETE"])
def delete_news_route(username, newsid):
    username = username.strip()
    if not is_logged_in(username):
        return Response("Usuário não está logado", status=403)

    success = delete_news(username, newsid)
    if success:
        return Response(status=204)
    else:
        return Response("Notícia não encontrada ou sem permissão", status=404)

