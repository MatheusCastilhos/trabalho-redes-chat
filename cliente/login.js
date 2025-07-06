const API_URL = "http://localhost:7447/webtalk";

function login() {
  const username = document.getElementById("usernameInput").value.trim();

  if (!username) {
    showError("Digite um nome válido!");
    return;
  }

  fetch(`${API_URL}/login/${encodeURIComponent(username)}`, {
    method: "POST"
  })
    .then(res => {
      if (res.status === 200) {
        return res.json();
      } else if (res.status === 404) {
        throw new Error("Usuário não existe. Cadastre-se primeiro.");
      } else if (res.status === 409) {
        throw new Error("Usuário já está logado.");
      } else {
        throw new Error("Erro ao fazer login.");
      }
    })
    .then(data => {
      localStorage.setItem("username", username);
      localStorage.setItem("token", data.token);  // armazenando token
      window.location.href = "main.html";
    })
    .catch(err => {
      showError(err.message);
    });
}


function register() {
  const username = document.getElementById("usernameInput").value.trim();

  if (!username) {
    showError("Digite um nome válido!");
    return;
  }

  fetch(`${API_URL}/register/${encodeURIComponent(username)}`, {
    method: "POST"
  })
    .then(res => {
      if (res.status === 201) {
        alert("Usuário cadastrado com sucesso! Agora é só fazer login.");
      } else if (res.status === 409) {
        showError("Este nome de usuário já está cadastrado.");
      } else {
        showError("Erro ao cadastrar usuário.");
      }
    })
    .catch(() => {
      showError("Erro ao conectar com o servidor.");
    });
}

function showError(msg) {
  document.getElementById("errorMsg").innerText = msg;
  document.getElementById("usernameInput").addEventListener("input", () => {
    showError(""); // limpa mensagem ao digitar
    });
}