document.addEventListener("DOMContentLoaded", function () {
const toggleButton = document.getElementById("auth-toggle");
const authMenu = document.querySelector(".auth");

if (toggleButton && authMenu) {
    toggleButton.addEventListener("click", function (e) {
    e.stopPropagation();
    authMenu.classList.toggle("show");
    });

    document.addEventListener("click", function (e) {
    if (!authMenu.contains(e.target) && !toggleButton.contains(e.target)) {
        authMenu.classList.remove("show");
    }
    });
}
});