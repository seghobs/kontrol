function showTokenErrorModal(message) {
    const modal = document.getElementById("tokenErrorModal");
    document.getElementById("tokenErrorText").textContent = message;
    modal.classList.add("show");
}

function updateUserCount() {
    const textarea = document.getElementById("grup_uye");
    const userCountDisplay = document.getElementById("user_count");
    const users = textarea.value.split("\n").filter((user) => user.trim() !== "");
    userCountDisplay.textContent = `${users.length} Adet kullanici eklendi.`;
}

window.updateUserCount = updateUserCount;

document.addEventListener("DOMContentLoaded", () => {
    const tokenErrorMessage = document.body.dataset.tokenErrorMessage;

    document.getElementById("closeTokenModalBtn").addEventListener("click", () => {
        document.getElementById("tokenErrorModal").classList.remove("show");
    });

    document.getElementById("tokenErrorModal").addEventListener("click", (event) => {
        if (event.target.id === "tokenErrorModal") {
            event.currentTarget.classList.remove("show");
        }
    });

    if (tokenErrorMessage) {
        showTokenErrorModal(tokenErrorMessage);
    }
});
