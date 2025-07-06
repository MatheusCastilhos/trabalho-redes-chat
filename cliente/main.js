const API_URL = "http://localhost:7447/webtalk";

window.addEventListener("DOMContentLoaded", () => {
  const username = localStorage.getItem("username");
  const token = localStorage.getItem("token");

  if (!username || !token) {
    alert("Usuário não autenticado. Voltando para o login.");
    window.location.href = "index.html";
    return;
  }

  document.getElementById("userLabel").innerText = username;
  loadUsers();
  loadMessages();
  loadNews();
});

function authHeaders() {
  return {
    headers: {
      "Authorization": localStorage.getItem("token")
    }
  };
}

function loadUsers() {
  fetch(`${API_URL}/users`, authHeaders())
    .then(res => res.status === 204 ? [] : res.json())
    .then(data => {
      const userList = document.getElementById("userList");
      userList.innerHTML = "";

      for (let user of data) {
        const li = document.createElement("li");
        li.innerText = user;
        userList.appendChild(li);
      }
    })
    .catch(() => console.log("Erro ao carregar usuários."));
}

function loadMessages() {
  fetch(`${API_URL}/messages`, authHeaders())
    .then(res => res.status === 204 ? [] : res.json())
    .then(data => {
      const messageList = document.getElementById("messageList");
      messageList.innerHTML = "";

      for (let id in data) {
        const [dir, user, text, time] = data[id];
        const li = document.createElement("li");
        li.innerText = `${dir} ${user} (${time}): ${text}`;

        if (dir === "para") {
          const btn = document.createElement("button");
          btn.innerText = "🗑";
          btn.style.marginLeft = "10px";
          btn.onclick = () => deleteMessage(id);
          li.appendChild(btn);
        }

        messageList.appendChild(li);
      }
    })
    .catch(() => console.log("Erro ao carregar mensagens."));
}

function loadNews() {
  fetch(`${API_URL}/news`, authHeaders())
    .then(res => res.status === 204 ? [] : res.json())
    .then(data => {
      const newsList = document.getElementById("newsList");
      newsList.innerHTML = "";
      const username = localStorage.getItem("username");

      for (let id in data) {
        const [author, text, time] = data[id];
        const li = document.createElement("li");
        li.innerText = `${author} (${time}): ${text}`;

        if (author === username) {
          const btn = document.createElement("button");
          btn.innerText = "🗑";
          btn.style.marginLeft = "10px";
          btn.onclick = () => deleteNews(id);
          li.appendChild(btn);
        }

        newsList.appendChild(li);
      }
    })
    .catch(() => console.log("Erro ao carregar notícias."));
}

function sendMessage() {
  const to = document.getElementById("toUser").value.trim();
  const text = document.getElementById("messageText").value.trim();

  if (!to || !text) {
    alert("Preencha os campos para enviar a mensagem.");
    return;
  }

  fetch(`${API_URL}/messages/${encodeURIComponent(to)}`, {
    method: "POST",
    headers: {
      "Authorization": localStorage.getItem("token")
    },
    body: text
  })
    .then(res => {
      if (res.status === 200) {
        loadMessages();
        document.getElementById("messageText").value = "";
      } else {
        alert("Erro ao enviar mensagem.");
      }
    })
    .catch(() => alert("Erro de conexão."));
}

function sendNews() {
  const text = document.getElementById("newsText").value.trim();

  if (!text) {
    alert("Digite uma notícia.");
    return;
  }

  fetch(`${API_URL}/news`, {
    method: "POST",
    headers: {
      "Authorization": localStorage.getItem("token")
    },
    body: text
  })
    .then(res => {
      if (res.status === 200) {
        loadNews();
        document.getElementById("newsText").value = "";
      } else {
        alert("Erro ao publicar notícia.");
      }
    })
    .catch(() => alert("Erro de conexão."));
}

function deleteMessage(msgId) {
  fetch(`${API_URL}/messages/${msgId}`, {
    method: "DELETE",
    headers: {
      "Authorization": localStorage.getItem("token")
    }
  })
    .then(res => {
      if (res.status === 204) {
        loadMessages();
      } else {
        alert("Erro ao excluir mensagem.");
      }
    })
    .catch(() => alert("Erro de conexão."));
}

function deleteNews(newsId) {
  fetch(`${API_URL}/news/${newsId}`, {
    method: "DELETE",
    headers: {
      "Authorization": localStorage.getItem("token")
    }
  })
    .then(res => {
      if (res.status === 204) {
        loadNews();
      } else {
        alert("Erro ao excluir notícia.");
      }
    })
    .catch(() => alert("Erro de conexão."));
}

function logout() {
  fetch(`${API_URL}/logout`, {
    method: "POST",
    headers: {
      "Authorization": localStorage.getItem("token")
    }
  })
    .then(() => {
      localStorage.removeItem("username");
      localStorage.removeItem("token");
      window.location.href = "index.html";
    })
    .catch(() => alert("Erro ao sair."));
}