const API_URL = "http://localhost:7447/webtalk";

document.addEventListener("DOMContentLoaded", () => {
  const username = localStorage.getItem("username");
  const token = localStorage.getItem("token");

  if (!username || !token) {
    alert("Usuário não autenticado. Redirecionando para o login.");
    window.location.href = "index.html";
    return;
  }

  document.getElementById("userLabel").innerText = username;

  // Eventos de formulários
  document.getElementById("logoutBtn").addEventListener("click", logout);
  document.getElementById("messageForm").addEventListener("submit", sendMessage);
  document.getElementById("newsForm").addEventListener("submit", sendNews);
  document.getElementById("docForm").addEventListener("submit", uploadDoc);

  // Carregamento inicial
  loadUsers();
  loadMessages();
  loadNews();
  loadDocs();

  // Atualiza as listas automaticamente a cada 5 segundos
  setInterval(() => {
    loadUsers();
    loadMessages();
    loadNews();
    loadDocs();
  }, 5000); // 5000 ms = 5 segundos
});

function authHeaders() {
  return {
    headers: { Authorization: localStorage.getItem("token") }
  };
}

function loadUsers() {
  fetch(`${API_URL}/users`, authHeaders())
    .then(res => res.status === 204 ? [] : res.json())
    .then(data => {
      const list = document.getElementById("userList");
      list.innerHTML = "";
      data.forEach(user => {
        const li = document.createElement("li");
        li.innerText = user;
        list.appendChild(li);
      });
    })
    .catch(() => console.warn("Erro ao carregar usuários."));
}

function loadMessages() {
  fetch(`${API_URL}/messages`, authHeaders())
    .then(res => res.status === 204 ? [] : res.json())
    .then(data => {
      const list = document.getElementById("messageList");
      list.innerHTML = "";
      for (let id in data) {
        const [dir, user, text, time] = data[id];
        const li = document.createElement("li");
        li.innerText = `${dir} ${user} (${time}): ${text}`;

        if (dir === "para") {
          const del = createDeleteButton(() => deleteMessage(id));
          li.appendChild(del);
        }

        list.appendChild(li);
      }
    })
    .catch(() => console.warn("Erro ao carregar mensagens."));
}

function sendMessage(event) {
  event.preventDefault();

  const to = document.getElementById("toUser").value.trim();
  const text = document.getElementById("messageText").value.trim();

  if (!to || !text) return alert("Preencha os campos para enviar.");

  fetch(`${API_URL}/messages/${encodeURIComponent(to)}`, {
    method: "POST",
    headers: { Authorization: localStorage.getItem("token") },
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

function deleteMessage(id) {
  fetch(`${API_URL}/messages/${id}`, {
    method: "DELETE",
    headers: { Authorization: localStorage.getItem("token") }
  })
    .then(res => {
      if (res.status === 204) loadMessages();
      else alert("Erro ao excluir mensagem.");
    })
    .catch(() => alert("Erro de conexão."));
}

function loadNews() {
  fetch(`${API_URL}/news`, authHeaders())
    .then(res => res.status === 204 ? [] : res.json())
    .then(data => {
      const list = document.getElementById("newsList");
      const currentUser = localStorage.getItem("username");
      list.innerHTML = "";

      for (let id in data) {
        const [author, text, time] = data[id];
        const li = document.createElement("li");
        li.innerText = `${author} (${time}): ${text}`;

        if (author === currentUser) {
          const del = createDeleteButton(() => deleteNews(id));
          li.appendChild(del);
        }

        list.appendChild(li);
      }
    })
    .catch(() => console.warn("Erro ao carregar notícias."));
}

function sendNews(event) {
  event.preventDefault();

  const text = document.getElementById("newsText").value.trim();
  if (!text) return alert("Digite uma notícia.");

  fetch(`${API_URL}/news`, {
    method: "POST",
    headers: { Authorization: localStorage.getItem("token") },
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

function deleteNews(id) {
  fetch(`${API_URL}/news/${id}`, {
    method: "DELETE",
    headers: { Authorization: localStorage.getItem("token") }
  })
    .then(res => {
      if (res.status === 204) loadNews();
      else alert("Erro ao excluir notícia.");
    })
    .catch(() => alert("Erro de conexão."));
}

function uploadDoc(event) {
  event.preventDefault();

  const input = document.getElementById("docFile");
  const file = input.files[0];
  if (!file) return alert("Selecione um arquivo.");

  fetch(`${API_URL}/doc`, {
    method: "PUT",
    headers: {
      Authorization: localStorage.getItem("token"),
      "Content-Type": file.type,
      "X-Filename": file.name
    },
    body: file
  })
    .then(res => {
      if (res.status === 200) {
        loadDocs();
        input.value = "";
      } else {
        res.text().then(msg => alert("Erro: " + msg));
      }
    })
    .catch(() => alert("Erro de conexão."));
}

function loadDocs() {
  const username = localStorage.getItem("username");
  const list = document.getElementById("docList");

  fetch(`${API_URL}/doc/list`, authHeaders())
    .then(res => (res.status === 200 ? res.json() : []))
    .then(files => {
      const existingItems = Array.from(list.children);
      const existingDocs = existingItems.map(li => li.getAttribute('data-doc-name'));

      // Cria um Set dos documentos recebidos para rápida checagem
      const incomingDocs = new Set(files.map(doc => doc.name));

      // Remove os elementos da lista que não existem mais no servidor
      existingItems.forEach(li => {
        const docName = li.getAttribute('data-doc-name');
        if (!incomingDocs.has(docName)) {
          list.removeChild(li);
        }
      });

      // Adiciona os documentos novos que ainda não estão na lista
      files.forEach(doc => {
        if (!existingDocs.includes(doc.name)) {
          const li = document.createElement("li");
          li.setAttribute('data-doc-name', doc.name);

          const link = document.createElement("a");
          link.href = `http://localhost:7447/webtalk/doc/public/${doc.owner}/${encodeURIComponent(doc.name)}`;
          link.target = "_blank";
          link.innerText = `${doc.name} (de ${doc.owner})`;

          li.appendChild(link);

          if (doc.owner === username) {
            const del = createDeleteButton(() => deleteDoc(doc.name, doc.owner));
            li.appendChild(del);
          }

          list.appendChild(li);
        }
      });
    })
    .catch(() => console.warn("Erro ao carregar documentos."));
}

function deleteDoc(name, owner) {
  fetch(`${API_URL}/doc/${encodeURIComponent(owner)}/${encodeURIComponent(name)}`, {
    method: "DELETE",
    headers: { Authorization: localStorage.getItem("token") }
  })
  .then(res => {
    if (res.status === 204) loadDocs();
    else alert("Erro ao excluir documento.");
  })
  .catch(() => alert("Erro de conexão."));
}


function logout() {
  fetch(`${API_URL}/logout`, {
    method: "POST",
    headers: { Authorization: localStorage.getItem("token") }
  })
    .finally(() => {
      localStorage.removeItem("username");
      localStorage.removeItem("token");
      window.location.href = "index.html";
    });
}

// Utilitário comum para botão de exclusão
function createDeleteButton(onClick) {
  const btn = document.createElement("button");
  btn.innerText = "🗑";
  btn.style.marginLeft = "10px";
  btn.addEventListener("click", onClick);
  return btn;
}