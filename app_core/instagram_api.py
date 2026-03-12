import json

import requests

from app_core.config import IG_APP_ID


def build_auth_headers(token, user_agent, android_id, device_id):
    return {
        "authorization": token,
        "user-agent": user_agent,
        "x-ig-app-id": IG_APP_ID,
        "x-ig-android-id": f"android-{android_id}",
        "x-ig-device-id": device_id,
    }


def fetch_current_user(token, user_agent, android_id, device_id, timeout=5):
    headers = build_auth_headers(token, user_agent, android_id, device_id)
    response = requests.get(
        "https://i.instagram.com/api/v1/accounts/current_user/?edit=true",
        headers=headers,
        timeout=timeout,
    )
    return response


def validate_token(token_record):
    try:
        response = fetch_current_user(
            token=token_record.get("token", ""),
            user_agent=token_record.get("user_agent", ""),
            android_id=token_record.get("android_id_yeni", ""),
            device_id=token_record.get("device_id", ""),
            timeout=3,
        )
        return response.status_code == 200
    except Exception:
        return False


def fetch_comment_usernames(media_id, token_record, min_id=None):
    token = token_record.get("token", "")
    user_agent = token_record.get("user_agent", "")
    android_id = token_record.get("android_id_yeni", "")
    device_id = token_record.get("device_id", "")

    headers = {
        "authorization": token,
        "user-agent": user_agent,
        "x-ig-app-locale": "tr_TR",
        "x-ig-device-locale": "tr_TR",
        "x-ig-mapped-locale": "tr_TR",
        "x-ig-android-id": f"android-{android_id}",
        "x-ig-device-id": device_id,
        "x-ig-app-id": IG_APP_ID,
        "x-ig-capabilities": "3brTv10=",
        "x-ig-connection-type": "WIFI",
        "x-fb-connection-type": "WIFI",
        "accept-language": "tr-TR, en-US",
        "x-fb-http-engine": "Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True",
    }

    params = {
        "min_id": min_id,
        "sort_order": "popular",
        "analytics_module": "comments_v2_feed_contextual_profile",
        "can_support_threading": "true",
        "is_carousel_bumped_post": "false",
        "feed_position": "0",
    }

    usernames = set()

    while True:
        response = requests.get(
            f"https://i.instagram.com/api/v1/media/{media_id}/stream_comments/",
            params=params,
            headers=headers,
            timeout=10,
        )

        if response.status_code in [401, 403]:
            return {"ok": False, "status": response.status_code, "usernames": usernames}

        if response.status_code != 200:
            return {"ok": False, "status": response.status_code, "usernames": usernames}

        json_data = None
        for line in response.text.splitlines():
            try:
                json_data = json.loads(line)
                for comment in json_data.get("comments", []):
                    username = comment.get("user", {}).get("username")
                    if username:
                        usernames.add(username)
            except json.JSONDecodeError:
                continue

        if not json_data:
            break

        next_min_id = json_data.get("next_min_id")
        if not next_min_id:
            break
        params["min_id"] = next_min_id

    return {"ok": True, "status": 200, "usernames": usernames}
