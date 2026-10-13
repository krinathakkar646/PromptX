fetch("http://127.0.0.1:5000/api/history")
  .then((response) => {
    document.getElementById("status").textContent = response.ok ? "connected" : "unavailable";
  })
  .catch(() => {
    document.getElementById("status").textContent = "unavailable";
  });
