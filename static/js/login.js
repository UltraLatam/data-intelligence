document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".login-form");
  form.addEventListener("submit", () => {
    const button = form.querySelector(".btn-login");
    button.textContent = "Verificando...";
    button.disabled = true;
  });
});
