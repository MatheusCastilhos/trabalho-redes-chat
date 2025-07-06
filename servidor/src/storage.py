from datetime import datetime
import uuid

# Armazenamento em memória
users = {}           # username: login_time
messages = {}        # username: [mensagens]
message_id_counter = [0]

news = {}            # news_id: dict
news_id_counter = [0]

sessions = {}        # token: username


# --------- AUTENTICAÇÃO E SESSÃO ---------

def create_user(username):
    if username in users:
        return False
    users[username] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return True

def login_user(username):
    if username not in users:
        return None
    # já está logado?
    for token, user in sessions.items():
        if user == username:
            return None
    token = str(uuid.uuid4())
    sessions[token] = username
    return token

def logout_user(token):
    if token in sessions:
        del sessions[token]

def get_user_by_token(token):
    return sessions.get(token)

def get_all_logged_users():
    return sessions.values()

def user_exists(username):
    return username in users


# --------- MENSAGENS ---------

def get_next_message_id():
    message_id_counter[0] += 1
    return str(message_id_counter[0])

def store_message(from_user, to_user, text):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg_id = get_next_message_id()

    msg_from = {
        "id": msg_id,
        "dir": "para",
        "user": to_user,
        "text": text,
        "time": timestamp
    }

    msg_to = {
        "id": msg_id,
        "dir": "de",
        "user": from_user,
        "text": text,
        "time": timestamp
    }

    for user, msg in [(from_user, msg_from), (to_user, msg_to)]:
        if user not in messages:
            messages[user] = []
        messages[user].append(msg)

def get_messages_for_user(username):
    return messages.get(username, [])


# --------- NOTÍCIAS ---------

def get_next_news_id():
    news_id_counter[0] += 1
    return str(news_id_counter[0])

def store_news(username, text):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    news_id = get_next_news_id()

    news[news_id] = {
        "dir": "de",
        "user": username,
        "text": text,
        "time": timestamp
    }

def get_all_news():
    return news

def delete_news(username, newsid):
    if newsid not in news:
        return False
    if news[newsid]["user"] != username:
        return False
    del news[newsid]
    return True


# --------- EXCLUSÃO DE MENSAGENS ---------

def delete_message(username, msgid):
    if username not in messages:
        return False

    # Verifica se a mensagem com esse ID foi enviada por esse usuário
    target_msg = next(
        (msg for msg in messages[username] if msg["id"] == msgid and msg["dir"] == "para"), None
    )
    if not target_msg:
        return False

    # Remove da lista do próprio usuário
    messages[username] = [msg for msg in messages[username] if msg["id"] != msgid]

    # Remove das listas dos outros usuários (caso exista o mesmo ID)
    for user, msg_list in messages.items():
        messages[user] = [msg for msg in msg_list if msg["id"] != msgid]

    return True
