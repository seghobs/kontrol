from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app_core.config import ADMIN_PASSWORD
from app_core.instagram_api import fetch_current_user, validate_token
from app_core.storage import load_tokens, save_tokens
from app_core.token_service import clear_logout_state, relogin_saved_user


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Yetkisiz erisim"}), 401
    return None


@admin_bp.route("", methods=["GET"])
@admin_bp.route("/", methods=["GET"])
def panel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))
    return render_template("admin.html")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin.panel"))
        return render_template("admin_login.html", error=True)
    return render_template("admin_login.html", error=False)


@admin_bp.route("/logout", methods=["GET"])
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/get_tokens", methods=["GET"])
def get_tokens():
    auth_error = _require_admin()
    if auth_error:
        return auth_error
    return jsonify({"success": True, "tokens": load_tokens()})


@admin_bp.route("/add_token", methods=["POST"])
def add_token():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    try:
        data = request.get_json() or {}
        required_fields = ["token", "android_id", "user_agent", "device_id", "password"]
        if not all(str(data.get(field, "")).strip() for field in required_fields):
            return jsonify({"success": False, "message": "Tum alanlar zorunlu"}), 400

        response = fetch_current_user(
            token=data["token"],
            user_agent=data["user_agent"],
            android_id=data["android_id"],
            device_id=data["device_id"],
            timeout=5,
        )
        if response.status_code != 200:
            return jsonify({"success": False, "message": "Token gecersiz"}), 400

        user_data = response.json().get("user", {})
        username = user_data.get("username")
        full_name = user_data.get("full_name", "")
        if not username:
            return jsonify({"success": False, "message": "Kullanici adi alinamadi"}), 400

        tokens = load_tokens()
        new_token = {
            "username": username,
            "full_name": full_name,
            "password": data["password"].strip(),
            "token": data["token"],
            "android_id_yeni": data["android_id"],
            "user_agent": data["user_agent"],
            "device_id": data["device_id"],
            "is_active": data.get("is_active", True),
            "added_at": data.get("added_at", str(datetime.now())),
        }

        replaced = False
        for idx, token in enumerate(tokens):
            if token.get("username") == username:
                tokens[idx] = new_token
                replaced = True
                break
        if not replaced:
            tokens.append(new_token)

        save_tokens(tokens)
        return jsonify(
            {
                "success": True,
                "message": f"@{username} ({full_name}) icin token {'guncellendi' if replaced else 'eklendi'}",
                "username": username,
                "full_name": full_name,
            }
        )
    except Exception as error:
        return jsonify({"success": False, "message": f"Token eklenemedi: {error}"}), 500


@admin_bp.route("/delete_token", methods=["POST"])
def delete_token():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"success": False, "message": "Kullanici adi belirtilmedi"}), 400

    tokens = [item for item in load_tokens() if item.get("username") != username]
    save_tokens(tokens)
    return jsonify({"success": True, "message": f"{username} icin token silindi"})


@admin_bp.route("/toggle_token", methods=["POST"])
def toggle_token():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"success": False, "message": "Kullanici adi belirtilmedi"}), 400

    tokens = load_tokens()
    for token in tokens:
        if token.get("username") == username:
            token["is_active"] = not token.get("is_active", False)
            if token["is_active"]:
                clear_logout_state(token)
            save_tokens(tokens)
            status = "aktif" if token["is_active"] else "pasif"
            return jsonify({"success": True, "message": f"{username} icin token {status} yapildi", "is_active": token["is_active"]})

    return jsonify({"success": False, "message": "Token bulunamadi"}), 404


@admin_bp.route("/update_token", methods=["POST"])
def update_token():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    try:
        data = request.get_json() or {}
        required_fields = ["username", "token", "android_id", "user_agent", "device_id", "password"]
        if not all(str(data.get(field, "")).strip() for field in required_fields):
            return jsonify({"success": False, "message": "Tum alanlar zorunlu"}), 400

        validate_response = fetch_current_user(
            token=data["token"],
            user_agent=data["user_agent"],
            android_id=data["android_id"],
            device_id=data["device_id"],
            timeout=5,
        )
        if validate_response.status_code != 200:
            return jsonify({"success": False, "message": "Yeni token gecersiz"}), 400

        tokens = load_tokens()
        for token in tokens:
            if token.get("username") == data["username"]:
                token["token"] = data["token"]
                token["android_id_yeni"] = data["android_id"]
                token["user_agent"] = data["user_agent"]
                token["device_id"] = data["device_id"]
                token["password"] = data["password"]
                token["is_active"] = True
                clear_logout_state(token)
                save_tokens(tokens)
                return jsonify({"success": True, "message": f"@{data['username']} icin token basariyla guncellendi"})

        return jsonify({"success": False, "message": "Token bulunamadi"}), 404
    except Exception as error:
        return jsonify({"success": False, "message": f"Token guncellenemedi: {error}"}), 500


@admin_bp.route("/relogin_token", methods=["POST"])
def relogin_token():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"success": False, "message": "Kullanici adi belirtilmedi"}), 400

    result = relogin_saved_user(username)
    if not result.get("ok"):
        return jsonify({"success": False, "message": result.get("message")}), result.get("code", 400)
    return jsonify({"success": True, "message": result.get("message")})


@admin_bp.route("/validate_token", methods=["POST"])
def validate_token_route():
    auth_error = _require_admin()
    if auth_error:
        return auth_error

    data = request.get_json() or {}
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"success": False, "message": "Kullanici adi belirtilmedi"}), 400

    tokens = load_tokens()
    for token in tokens:
        if token.get("username") == username:
            is_valid = validate_token(token)
            if not is_valid and token.get("is_active", False):
                token["is_active"] = False
                token["logout_reason"] = "Bu hesabin oturumu Instagram'dan cikis yapildi"
                token["logout_time"] = str(datetime.now())
                save_tokens(tokens)
            return jsonify({"success": True, "is_valid": is_valid, "is_active": token.get("is_active", False)})

    return jsonify({"success": False, "message": "Token bulunamadi"}), 404
