import html

from flask import Blueprint, jsonify, render_template, request

from donustur import donustur
from log_in import giris_yap

from app_core.storage import load_exemptions, save_exemptions
from app_core.token_service import fetch_comments_with_failover, get_working_active_token, upsert_login_token


main_bp = Blueprint("main", __name__)


def get_exempted_users(post_link):
    exemptions = load_exemptions()
    post_link_decoded = html.unescape(post_link)
    return set(exemptions.get(post_link_decoded, []))


@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        active_working_token = get_working_active_token()
        if not active_working_token:
            return render_template(
                "form.html",
                token_error_message="Tum hesaplar cikis yapmis gorunuyor. Lutfen admin panelden gecerli bir token girin.",
            )

        link = request.form["post_link"]
        media_id = donustur(link)
        all_usernames = fetch_comments_with_failover(media_id)

        grup_uye = request.form["grup_uye"]
        grup_uye_kullanicilar = set(grup_uye.split())
        sponsor = []
        izinli_uyeler = get_exempted_users(link)
        eksikler = grup_uye_kullanicilar - izinli_uyeler - all_usernames - set(sponsor)

        return render_template("result.html", eksikler=eksikler, post_link=link)

    return render_template("form.html")


@main_bp.route("/add_exemption", methods=["POST"])
def add_exemption():
    try:
        data = request.get_json() or {}
        post_link = data.get("post_link")
        username = data.get("username")

        if not post_link or not username:
            return jsonify({"success": False, "message": "Paylasim linki ve kullanici adi gerekli"}), 400

        post_link_decoded = html.unescape(post_link)
        exemptions = load_exemptions()

        if post_link_decoded not in exemptions:
            exemptions[post_link_decoded] = []

        if username not in exemptions[post_link_decoded]:
            exemptions[post_link_decoded].append(username)
            save_exemptions(exemptions)

        return jsonify({"success": True, "message": f"@{username} izinli kullanicilar listesine eklendi"})
    except Exception as error:
        return jsonify({"success": False, "message": f"Hata: {error}"}), 500


@main_bp.route("/token_al")
def token_page():
    return render_template("token.html")


@main_bp.route("/giris_yaps", methods=["POST"])
def login_and_get_token():
    username = request.form.get("kullanici_adi", "").strip()
    password = request.form.get("sifre", "").strip()
    android_id = request.form.get("android_id", "").strip()
    user_agent = request.form.get("user_agent", "").strip()
    device_id = request.form.get("device_id", "").strip()

    if not username or not password or not android_id or not user_agent or not device_id:
        return jsonify({"token": None, "message": "kullanici_adi, sifre, android_id, user_agent ve device_id zorunludur"}), 400

    token_value, android_id, user_agent, device_id = giris_yap(
        username, password, android_id, user_agent, device_id
    )

    if token_value:
        upsert_login_token(username, password, token_value, android_id, user_agent, device_id)

    return jsonify(
        {
            "token": token_value,
            "android_id_yeni": android_id,
            "user_agent": user_agent,
            "device_id": device_id,
        }
    )
