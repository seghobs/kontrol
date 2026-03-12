function showAlert(message, type = "success") {
    const alertContainer = document.getElementById("alertContainer");
    const alert = document.createElement("div");
    alert.className = `alert alert-${type}`;

    const icon = type === "success" ? "check-circle" : type === "error" ? "exclamation-triangle" : "info-circle";
    alert.innerHTML = `<i class="fas fa-${icon}"></i><span>${message}</span>`;
    alertContainer.appendChild(alert);

    setTimeout(() => {
        alert.remove();
    }, 5000);
}

async function loadTokens() {
    const loading = document.getElementById("loading");
    const tokensList = document.getElementById("tokensList");

    loading.classList.add("show");
    tokensList.innerHTML = "";

    try {
        const response = await fetch("/admin/get_tokens");
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.message || "Token yuklenemedi");
        }

        loading.classList.remove("show");
        if (data.tokens.length === 0) {
            tokensList.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>Henuz eklenmis token yok.<br>Yukaridaki formu kullanarak token ekleyin.</p></div>';
            return;
        }

        data.tokens.forEach((token, index) => {
            const tokenCard = createTokenCard(token, index);
            tokensList.appendChild(tokenCard);
        });
    } catch (error) {
        loading.classList.remove("show");
        showAlert(error.message, "error");
    }
}

function createTokenCard(token) {
    const card = document.createElement("div");
    card.className = `token-card ${token.is_active ? "" : "inactive"}`;

    const safeTokenValue = typeof token.token === "string" ? token.token : "";
    const tokenPreview = safeTokenValue ? `${safeTokenValue.substring(0, 60)}...` : "Token yok";
    const safeAndroidId = token.android_id_yeni || "Yok";
    const safeDeviceId = token.device_id || "Yok";

    const statusText = token.is_active ? "Aktif" : "Pasif";
    const statusClass = token.is_active ? "active" : "inactive";
    const fullNameDisplay = token.full_name ? `<div style="color: rgba(255, 255, 255, 0.6); font-size: 14px; margin-top: 5px;">${token.full_name}</div>` : "";
    const logoutReasonDisplay = token.logout_reason
        ? `<div style="background: rgba(231, 76, 60, 0.15); border: 1px solid rgba(231, 76, 60, 0.3); border-radius: 8px; padding: 12px; margin: 10px 0;"><div style="color: #e74c3c; font-weight: 600; font-size: 13px; margin-bottom: 5px;"><i class="fas fa-exclamation-circle"></i> Cikis Yapildi</div><div style="color: rgba(255, 255, 255, 0.8); font-size: 12px;">${token.logout_reason}</div>${token.logout_time ? `<div style="color: rgba(255, 255, 255, 0.5); font-size: 11px; margin-top: 5px;">${new Date(token.logout_time).toLocaleString("tr-TR")}</div>` : ""}</div>`
        : "";

    card.innerHTML = `<div class="token-header"><div><span class="token-username"><i class="fab fa-instagram"></i> @${token.username}</span>${fullNameDisplay}</div><span class="token-status ${statusClass}">${statusText}</span></div>${logoutReasonDisplay}<div class="token-info"><strong>Token:</strong><div class="token-value">${tokenPreview}</div></div><div class="token-info"><strong>Android ID:</strong> <span class="token-value" style="display: inline-block;">${safeAndroidId}</span></div><div class="token-info"><strong>Device ID:</strong> <span class="token-value" style="display: inline-block;">${safeDeviceId}</span></div><div class="token-info"><strong>Eklenme Tarihi:</strong> ${token.added_at ? new Date(token.added_at).toLocaleString("tr-TR") : "Bilinmiyor"}</div><div class="token-actions"><button class="btn" onclick="editToken('${token.username}')"><i class="fas fa-edit"></i> Duzenle</button>${token.password ? `<button class="btn" style="background: rgba(52, 152, 219, 0.2); border-color: rgba(52, 152, 219, 0.4);" onclick="reloginToken('${token.username}')"><i class="fas fa-sync-alt"></i> Tekrar Giris Yap</button>` : ""}<button class="btn btn-warning" onclick="toggleToken('${token.username}')"><i class="fas fa-toggle-${token.is_active ? "off" : "on"}"></i> ${token.is_active ? "Pasif Yap" : "Aktif Yap"}</button><button class="btn btn-success" onclick="validateToken('${token.username}')"><i class="fas fa-check-circle"></i> Dogrula</button><button class="btn btn-danger" onclick="deleteToken('${token.username}')"><i class="fas fa-trash"></i> Sil</button></div>`;

    return card;
}

async function toggleToken(username) {
    try {
        const response = await fetch("/admin/toggle_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username }),
        });

        const data = await response.json();
        if (data.success) {
            showAlert(data.message, "success");
            loadTokens();
            return;
        }
        showAlert(data.message, "error");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
}

async function validateToken(username) {
    showAlert("Token dogrulaniyor...", "info");

    try {
        const response = await fetch("/admin/validate_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username }),
        });

        const data = await response.json();
        if (data.success) {
            if (data.is_valid) {
                showAlert(`✓ ${username} icin token gecerli!`, "success");
            } else {
                showAlert(`✗ ${username} icin token gecersiz!`, "error");
                loadTokens();
            }
            return;
        }
        showAlert(data.message, "error");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
}

async function deleteToken(username) {
    if (!confirm(`⚠️ ${username} icin tokeni silmek istediginizden emin misiniz?`)) {
        return;
    }

    try {
        const response = await fetch("/admin/delete_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username }),
        });

        const data = await response.json();
        if (data.success) {
            showAlert(data.message, "success");
            loadTokens();
            return;
        }
        showAlert(data.message, "error");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
}

async function reloginToken(username) {
    if (!confirm(`@${username} icin tekrar giris yapilacak ve token yenilenecek. Devam edilsin mi?`)) {
        return;
    }

    showAlert("Tekrar giris yapiliyor...", "info");

    try {
        const response = await fetch("/admin/relogin_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username }),
        });

        const data = await response.json();
        if (data.success) {
            showAlert(data.message, "success");
            loadTokens();
            return;
        }
        showAlert(data.message, "error");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
}

async function editToken(username) {
    try {
        const response = await fetch("/admin/get_tokens");
        const data = await response.json();
        if (!data.success) {
            showAlert("Tokenler yuklenemedi", "error");
            return;
        }

        const token = data.tokens.find((item) => item.username === username);
        if (!token) {
            showAlert("Token bulunamadi", "error");
            return;
        }

        document.getElementById("edit_username").value = token.username;
        document.getElementById("edit_username_display").value = `@${token.username}${token.full_name ? ` (${token.full_name})` : ""}`;
        document.getElementById("edit_token").value = token.token;
        document.getElementById("edit_android_id").value = token.android_id_yeni;
        document.getElementById("edit_device_id").value = token.device_id || "";
        document.getElementById("edit_password").value = token.password || "";
        document.getElementById("edit_user_agent").value = token.user_agent;
        document.getElementById("editModal").classList.add("show");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
}

function closeEditModal() {
    document.getElementById("editModal").classList.remove("show");
}

document.getElementById("addTokenForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = {
        token: document.getElementById("token").value.trim(),
        android_id: document.getElementById("android_id").value.trim(),
        device_id: document.getElementById("device_id").value.trim(),
        user_agent: document.getElementById("user_agent").value.trim(),
        password: document.getElementById("password").value.trim(),
        is_active: true,
        added_at: new Date().toISOString(),
    };

    if (!formData.token || !formData.android_id || !formData.device_id || !formData.user_agent || !formData.password) {
        showAlert("Lutfen tum alanlari doldurun!", "error");
        return;
    }

    showAlert("Token dogrulaniyor ve kullanici adi aliniyor...", "info");

    try {
        const response = await fetch("/admin/add_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        if (data.success) {
            const successMsg = data.username && data.full_name ? `✓ Token basariyla eklendi: @${data.username} (${data.full_name})` : data.message;
            showAlert(successMsg, "success");
            document.getElementById("addTokenForm").reset();
            loadTokens();
            return;
        }
        showAlert(data.message, "error");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
});

document.getElementById("editModal").addEventListener("click", (event) => {
    if (event.target.id === "editModal") {
        closeEditModal();
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeEditModal();
    }
});

document.getElementById("editTokenForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("edit_username").value;
    const formData = {
        username,
        token: document.getElementById("edit_token").value.trim(),
        android_id: document.getElementById("edit_android_id").value.trim(),
        device_id: document.getElementById("edit_device_id").value.trim(),
        password: document.getElementById("edit_password").value.trim(),
        user_agent: document.getElementById("edit_user_agent").value.trim(),
    };

    if (!formData.token || !formData.android_id || !formData.device_id || !formData.user_agent || !formData.password) {
        showAlert("Lutfen tum alanlari doldurun!", "error");
        return;
    }

    showAlert("Token guncelleniyor...", "info");

    try {
        const response = await fetch("/admin/update_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        });
        const data = await response.json();
        if (data.success) {
            showAlert(data.message, "success");
            closeEditModal();
            loadTokens();
            return;
        }
        showAlert(data.message, "error");
    } catch (error) {
        showAlert(`Bir hata olustu: ${error.message}`, "error");
    }
});

window.toggleToken = toggleToken;
window.validateToken = validateToken;
window.deleteToken = deleteToken;
window.reloginToken = reloginToken;
window.editToken = editToken;
window.closeEditModal = closeEditModal;

loadTokens();
setInterval(loadTokens, 30000);
