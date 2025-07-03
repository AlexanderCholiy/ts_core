document.addEventListener("DOMContentLoaded", () => {
    const spinnerOverlay = document.getElementById("spinner-overlay");

    setTimeout(() => {
        spinnerOverlay.classList.add("hidden");
    }, 500);
});