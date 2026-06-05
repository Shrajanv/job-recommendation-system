// Animate match bars on load
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".match-bar").forEach(bar => {
    const w = bar.style.width;
    bar.style.width = "0";
    setTimeout(() => { bar.style.width = w; }, 100);
  });
});
