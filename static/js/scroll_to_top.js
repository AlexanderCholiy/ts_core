document.addEventListener("DOMContentLoaded", () => {
    const scrollToTopButton = document.getElementById("scroll-to-top");

    scrollToTopButton.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
});