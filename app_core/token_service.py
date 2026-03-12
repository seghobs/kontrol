from datetime import datetime

from log_in import giris_yap

from app_core.instagram_api import fetch_comment_usernames, fetch_current_user, validate_token
from app_core.storage import load_tokens, save_tokens


def deactivate_token(tokens, username, reason):
    for token in tokens:
        if token.get("username") == username:
            token["is_active"] = False
            token["logout_reason"] = reason
            token["logout_time"] = str(datetime.now())
            return True
    return False


def clear_logout_state(token):
    token.pop("logout_reason", None)
    token.pop("logout_time", None)


def get_working_active_token(excluded_usernames=None):
    if excluded_usernames is None:
        excluded_usernames = set()

    tokens = load_tokens()
    changed = False

    for token_record in tokens:
        if not token_record.get("is_active", False):
            continue

        username = token_record.get("username", "")
        if username in excluded_usernames:
            continue

        android_id = token_record.get("android_id_yeni", "").strip()
        user_agent = token_record.get("user_agent", "").strip()
        device_id = token_record.get("device_id", "").strip()
        token_value = token_record.get("token", "").strip()

        if not android_id or not user_agent or not device_id or not token_value:
            changed = deactivate_token(
                tokens,
                username,
                "Bu hesapta zorunlu bilgiler eksik (token/android_id/user_agent/device_id)",
            ) or changed
            continue

        if validate_token(token_record):
            if changed:
                save_tokens(tokens)
            return token_record

        changed = deactivate_token(
            tokens,
            username,
            "Bu hesabin oturumu Instagram'dan cikis yapildi",
        ) or changed

    if changed:
        save_tokens(tokens)
    return None


def fetch_comments_with_failover(media_id):
    max_retries = 10
    retry_count = 0
    tried_usernames = set()
    usernames = set()
    token_record = get_working_active_token()

    while retry_count < max_retries:
        if not token_record or not token_record.get("token"):
            return set()

        current_username = token_record.get("username", "bilinmeyen")
        print(f"Token kullaniliyor: @{current_username}")

        try:
            result = fetch_comment_usernames(media_id, token_record)
        except Exception as error:
            print(f"Yorum cekme hatasi: {error}")
            result = {"ok": False, "status": 500, "usernames": usernames}

        usernames = result.get("usernames", set())

        if result.get("ok"):
            print(f"Basari! Toplam {len(usernames)} kullanici bulundu.")
            return usernames

        tokens = load_tokens()
        deactivate_token(tokens, current_username, "Bu hesabin oturumu Instagram'dan cikis yapildi")
        save_tokens(tokens)

        retry_count += 1
        tried_usernames.add(current_username)
        token_record = get_working_active_token(tried_usernames)
        if not token_record:
            break

    return usernames


def resolve_current_user(token, user_agent, android_id, device_id):
    response = fetch_current_user(token, user_agent, android_id, device_id, timeout=5)
    if response.status_code != 200:
        return None
    return response.json().get("user", {})


def upsert_login_token(username, password, token, android_id, user_agent, device_id):
    tokens = load_tokens()
    existing = next((item for item in tokens if item.get("username") == username), None)

    if existing:
        existing["password"] = password
        existing["token"] = token
        existing["android_id_yeni"] = android_id
        existing["user_agent"] = user_agent
        existing["device_id"] = device_id
        existing["is_active"] = True
        clear_logout_state(existing)
    else:
        user_data = resolve_current_user(token, user_agent, android_id, device_id) or {}
        tokens.append(
            {
                "username": username,
                "full_name": user_data.get("full_name", ""),
                "password": password,
                "token": token,
                "android_id_yeni": android_id,
                "user_agent": user_agent,
                "device_id": device_id,
                "is_active": True,
                "added_at": str(datetime.now()),
            }
        )

    save_tokens(tokens)


def relogin_saved_user(username):
    tokens = load_tokens()
    target = next((item for item in tokens if item.get("username") == username), None)
    if not target:
        return {"ok": False, "code": 404, "message": "Token bulunamadi"}

    required = [
        str(target.get("password", "")).strip(),
        str(target.get("android_id_yeni", "")).strip(),
        str(target.get("user_agent", "")).strip(),
        str(target.get("device_id", "")).strip(),
    ]
    if not all(required):
        return {"ok": False, "code": 400, "message": "Bu hesap icin zorunlu bilgiler eksik"}

    new_token, new_android_id, new_user_agent, new_device_id = giris_yap(
        username,
        target["password"],
        target["android_id_yeni"],
        target["user_agent"],
        target["device_id"],
    )

    if not new_token:
        return {"ok": False, "code": 400, "message": "Giris basarisiz"}

    target["token"] = new_token
    target["android_id_yeni"] = new_android_id
    target["user_agent"] = new_user_agent
    target["device_id"] = new_device_id
    target["is_active"] = True
    clear_logout_state(target)
    save_tokens(tokens)

    return {"ok": True, "message": f"@{username} icin token basariyla yenilendi"}
