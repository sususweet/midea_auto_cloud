import asyncio
import json
import os
import time

SESSION_RECORD_VERSION = 1


def _now_ts() -> int:
    return int(time.time())


def load_all(path: str) -> dict:
    if not os.path.exists(path):
        return {"version": SESSION_RECORD_VERSION, "sessions": {}}
    try:
        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        if not isinstance(data, dict):
            return {"version": SESSION_RECORD_VERSION, "sessions": {}}
        data.setdefault("version", SESSION_RECORD_VERSION)
        data.setdefault("sessions", {})
        if not isinstance(data["sessions"], dict):
            data["sessions"] = {}
        return data
    except Exception:
        return {"version": SESSION_RECORD_VERSION, "sessions": {}}


def save_all(path: str, data: dict):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, sort_keys=True, indent=2)


def _make_record(
    payload: dict,
    now: int | None = None,
    soft_ttl_seconds: int = 24 * 3600,
    hard_ttl_seconds: int = 7 * 24 * 3600,
) -> dict:
    now_ts = _now_ts() if now is None else int(now)
    return {
        "v": SESSION_RECORD_VERSION,
        "saved_at": now_ts,
        "expires_at": now_ts + int(soft_ttl_seconds),
        "hard_expires_at": now_ts + int(hard_ttl_seconds),
        "payload": payload,
    }


def get_session(
    path: str,
    session_key: str,
    password: str,
    account: str,
    server: int | str,
    now: int | None = None,
) -> dict | None:
    now_ts = _now_ts() if now is None else int(now)
    all_data = load_all(path)
    sessions = all_data.get("sessions", {})
    record = sessions.get(session_key)
    if not isinstance(record, dict):
        return None

    hard_expires_at = int(record.get("hard_expires_at", 0) or 0)
    if hard_expires_at > 0 and now_ts >= hard_expires_at:
        sessions.pop(session_key, None)
        save_all(path, all_data)
        return None

    expires_at = int(record.get("expires_at", 0) or 0)
    if expires_at > 0 and now_ts >= expires_at:
        return None

    payload = record.get("payload")
    if not isinstance(payload, dict):
        sessions.pop(session_key, None)
        save_all(path, all_data)
        return None

    if str(payload.get("account")) != str(account):
        return None
    if str(payload.get("server")) != str(server):
        return None
    return payload


def set_session(
    path: str,
    session_key: str,
    payload: dict,
    password: str,
    account: str,
    server: int | str,
    now: int | None = None,
    soft_ttl_seconds: int = 24 * 3600,
    hard_ttl_seconds: int = 7 * 24 * 3600,
):
    all_data = load_all(path)
    all_data.setdefault("sessions", {})
    plain_payload = dict(payload)
    plain_payload["account"] = account
    plain_payload["server"] = server
    all_data["sessions"][session_key] = _make_record(
        payload=plain_payload,
        now=now,
        soft_ttl_seconds=soft_ttl_seconds,
        hard_ttl_seconds=hard_ttl_seconds,
    )
    save_all(path, all_data)


def delete_session(path: str, session_key: str):
    all_data = load_all(path)
    sessions = all_data.get("sessions", {})
    if session_key in sessions:
        sessions.pop(session_key, None)
        save_all(path, all_data)


async def async_load_all(path: str) -> dict:
    return await asyncio.to_thread(load_all, path)


async def async_save_all(path: str, data: dict):
    await asyncio.to_thread(save_all, path, data)


async def async_get_session(
    path: str,
    session_key: str,
    password: str,
    account: str,
    server: int | str,
    now: int | None = None,
) -> dict | None:
    return await asyncio.to_thread(
        get_session,
        path,
        session_key,
        password,
        account,
        server,
        now,
    )


async def async_set_session(
    path: str,
    session_key: str,
    payload: dict,
    password: str,
    account: str,
    server: int | str,
    now: int | None = None,
    soft_ttl_seconds: int = 24 * 3600,
    hard_ttl_seconds: int = 7 * 24 * 3600,
):
    await asyncio.to_thread(
        set_session,
        path,
        session_key,
        payload,
        password,
        account,
        server,
        now,
        soft_ttl_seconds,
        hard_ttl_seconds,
    )


async def async_delete_session(path: str, session_key: str):
    await asyncio.to_thread(delete_session, path, session_key)
