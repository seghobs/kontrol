let notificationTimeout;
let pendingUsername = null;
let pendingButton = null;

const postLink = document.body.dataset.postLink || "";

function updateCount() {
    const listItems = document.getElementById("eksiklerListesi").getElementsByTagName("li");
    const visibleCount = Array.from(listItems).filter((item) => item.style.display !== "none").length;
    document.getElementById("elemanSayisi").innerText = `Eksik Sayisi: ${visibleCount}`;
}

function showNotification(message) {
    const notification = document.getElementById("notification");
    document.getElementById("notification-message").innerText = message;

    if (notification.classList.contains("visible")) {
        clearTimeout(notificationTimeout);
        notification.classList.remove("visible");
    }

    notification.style.display = "block";
    setTimeout(() => {
        notification.classList.add("visible");
    }, 10);

    notificationTimeout = setTimeout(() => {
        notification.classList.remove("visible");
    }, 3000);
}

function closeModal() {
    document.getElementById("confirmModal").classList.remove("show");
    pendingUsername = null;
    pendingButton = null;
}

function addExemption(username, button) {
    pendingUsername = username;
    pendingButton = button;
    document.getElementById("modalUsername").textContent = `@${username}`;
    document.getElementById("confirmModal").classList.add("show");
}

function confirmExemption() {
    if (!pendingUsername || !pendingButton) {
        return;
    }

    const username = pendingUsername;
    const button = pendingButton;
    closeModal();

    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Kaydediliyor...';

    fetch("/add_exemption", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_link: postLink, username }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                const listItem = button.closest("li");
                listItem.style.transition = "all 0.3s ease";
                listItem.style.opacity = "0";
                listItem.style.transform = "translateX(20px)";

                setTimeout(() => {
                    listItem.remove();
                    updateCount();
                    showNotification(`@${username} izinli listesine eklendi!`);
                }, 300);
                return;
            }

            showNotification(`Hata: ${data.message}`);
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check me-1"></i>Izinli Say';
        })
        .catch(() => {
            showNotification("Bir hata olustu!");
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check me-1"></i>Izinli Say';
        });
}

function fallbackCopyToClipboard(text, count) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-9999px";
    textArea.style.top = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand("copy");
        showNotification(successful ? `Liste kopyalandi! Toplam eksik sayisi: ${count}` : "Kopyalama basarisiz oldu!");
    } catch (_error) {
        showNotification("Kopyalama desteklenmiyor!");
    }

    document.body.removeChild(textArea);
}

function kopyalaListeyi() {
    const listItems = document.getElementById("eksiklerListesi").getElementsByTagName("li");
    let text = "";

    for (let i = 0; i < listItems.length; i += 1) {
        const username = listItems[i].getAttribute("data-username");
        if (username) {
            text += `@${username}`;
            if (i < listItems.length - 1) {
                text += "\n";
            }
        }
    }

    const count = listItems.length;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
            .then(() => showNotification(`Liste kopyalandi! Toplam eksik sayisi: ${count}`))
            .catch(() => fallbackCopyToClipboard(text, count));
        return;
    }

    fallbackCopyToClipboard(text, count);
}

function filterList() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const listItems = document.getElementById("eksiklerListesi").getElementsByTagName("li");

    for (let i = 0; i < listItems.length; i += 1) {
        const item = listItems[i];
        const textValue = item.innerText.toLowerCase();
        item.style.display = textValue.includes(input) ? "" : "none";
    }

    updateCount();
}

window.addExemption = addExemption;
window.closeModal = closeModal;
window.confirmExemption = confirmExemption;
window.kopyalaListeyi = kopyalaListeyi;
window.filterList = filterList;

window.onload = function onLoad() {
    updateCount();
};
