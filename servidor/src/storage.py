from datetime import datetime
import shutil
import atexit
import uuid
import stat
import os

# ========== CONSTANTES E ESTRUTURAS ==========

BASEDIR = os.path.dirname(__file__)
DOCS_FOLDER = os.path.join(BASEDIR, "docs")
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf"]

users = {}               # username: login_time
sessions = {}            # token: username
messages = {}            # username: list of messages
news = {}                # news_id: dict with news data
message_id_counter = [0]
news_id_counter = [0]

# ========== USUÁRIOS E AUTENTICAÇÃO ==========

def create_user(username):
    if username in users:
        return False
    users[username] = timestamp()
    return True

def login_user(username):
    if username not in users:
        return None
    if username in sessions.values():
        return None
    token = str(uuid.uuid4())
    sessions[token] = username
    return token

def logout_user(token):
    sessions.pop(token, None)

def get_user_by_token(token):
    return sessions.get(token)

def get_all_logged_users():
    return list(sessions.values())

def user_exists(username):
    return username in users

# ========== MENSAGENS ==========

def store_message(from_user, to_user, text):
    msg_id = get_next_message_id()
    time = timestamp()

    msg_from = {
        "id": msg_id, "dir": "para", "user": to_user,
        "text": text, "time": time
    }
    msg_to = {
        "id": msg_id, "dir": "de", "user": from_user,
        "text": text, "time": time
    }

    for user, msg in [(from_user, msg_from), (to_user, msg_to)]:
        messages.setdefault(user, []).append(msg)

def get_messages_for_user(username):
    return messages.get(username, [])

def delete_message(username, msgid):
    if username not in messages:
        return False

    msgs = messages[username]
    # Só pode deletar mensagem 'para' do usuário
    if not any(msg for msg in msgs if msg["id"] == msgid and msg["dir"] == "para"):
        return False

    # Remove a mensagem de todas as caixas
    for user in messages:
        messages[user] = [msg for msg in messages[user] if msg["id"] != msgid]

    return True

# ========== NOTÍCIAS ==========

def store_news(username, text):
    news_id = get_next_news_id()
    news[news_id] = {
        "user": username,
        "text": text,
        "time": timestamp()
    }

def get_all_news():
    return news

def delete_news(username, newsid):
    if newsid not in news or news[newsid]["user"] != username:
        return False
    del news[newsid]
    return True

# ========== DOCUMENTOS ==========

def save_document(username, docname, content_type, file_data):
    if content_type not in ALLOWED_MIME_TYPES:
        return False, "Tipo de arquivo não suportado."

    user_folder = os.path.join(DOCS_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)

    try:
        with open(os.path.join(user_folder, docname), "wb") as f:
            f.write(file_data)
        return True, "Arquivo salvo com sucesso."
    except Exception as e:
        return False, f"Erro ao salvar arquivo: {e}"

def get_document(username, docname):
    path = os.path.join(DOCS_FOLDER, username, docname)
    if not os.path.exists(path):
        return None
    # DEBUG opcional: pode remover depois
    print(f"[DEBUG] Buscando documento em: {path}")
    return path

def delete_document(username, docname):
    path = os.path.join(DOCS_FOLDER, username, docname)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def list_all_documents(_=None):
    if not os.path.exists(DOCS_FOLDER):
        return []

    result = []
    for user_folder in os.listdir(DOCS_FOLDER):
        user_path = os.path.join(DOCS_FOLDER, user_folder)
        if os.path.isdir(user_path):
            for fname in os.listdir(user_path):
                result.append({"owner": user_folder, "name": fname})
    return result

def get_content_type(filename):
    ext = filename.lower().split('.')[-1]
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "pdf": "application/pdf"
    }.get(ext, "application/octet-stream")

# ========== UTILITÁRIOS ==========

def timestamp():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_next_message_id():
    message_id_counter[0] += 1
    return str(message_id_counter[0])

def get_next_news_id():
    news_id_counter[0] += 1
    return str(news_id_counter[0])

def handle_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def limpar_documentos():
    if os.path.exists(DOCS_FOLDER):
        shutil.rmtree(DOCS_FOLDER, onerror=handle_remove_readonly)

atexit.register(limpar_documentos)