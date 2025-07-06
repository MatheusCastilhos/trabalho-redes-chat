const API_URL = "http://localhost:7447/webtalk";

document.getElementById("loginBtn").addEventListener("click", login);
document.getElementById("registerBtn").addEventListener("click", register);
document.getElementById("usernameInput").addEventListener("input", clearError);

function login() {
  const username = getUsername();
  if (!username) return;

  fetch(`${API_URL}/login/${encodeURIComponent(username)}`, { method: "POST" })
    .then(res => {
      if (res.status === 200) return res.json();
      if (res.status === 404) throw new Error("Usuário não existe. Cadastre-se primeiro.");
      if (res.status === 409) throw new Error("Usuário já está logado.");
      throw new Error("Erro ao fazer login.");
    })
    .then(data => {
      localStorage.setItem("username", username);
      localStorage.setItem("token", data.token);
      window.location.href = "main.html";
    })
    .catch(err => showError(err.message));
}

function register() {
  const username = getUsername();
  if (!username) return;

  fetch(`${API_URL}/register/${encodeURIComponent(username)}`, { method: "POST" })
    .then(res => {
      if (res.status === 201) {
        alert("Usuário cadastrado com sucesso! Agora é só fazer login.");
      } else if (res.status === 409) {
        showError("Este nome de usuário já está cadastrado.");
      } else {
        showError("Erro ao cadastrar usuário.");
      }
    })
    .catch(() => showError("Erro ao conectar com o servidor."));
}

function getUsername() {
  const input = document.getElementById("usernameInput");
  const username = input.value.trim();

  if (!username) {
    showError("Digite um nome válido!");
    return null;
  }

  return username;
}

function showError(msg) {
  const errorMsg = document.getElementById("errorMsg");
  errorMsg.innerText = msg;
}

function clearError() {
  showError("");
}