import base64
import hashlib
import hmac
import json
import secrets
import time
import uuid
from typing import Dict

from core.runtime_config import ADMIN_PASSWORD
from core.runtime_config import ADMIN_USERNAME
from core.runtime_config import AUTH_SECRET
from core.runtime_config import TOKEN_TTL_MINUTES
from core.runtime_store import load_document
from core.runtime_store import save_document


ROLE_PERMISSIONS = {
    "viewer": {
        "read"
    },
    "operator": {
        "read",
        "execute",
        "write"
    },
    "admin": {
        "read",
        "execute",
        "write",
        "commit",
        "admin"
    }
}


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(
        data
    ).decode(
        "ascii"
    ).rstrip(
        "="
    )


def _decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(
        data
        + "=" * (
            -len(
                data
            ) % 4
        )
    )


def _hash_password(
    password: str,
    salt: str | None = None
) -> str:
    salt = salt or secrets.token_hex(
        16
    )
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(
            "utf-8"
        ),
        salt.encode(
            "utf-8"
        ),
        240000
    )
    return f"{salt}${digest.hex()}"


def _verify_password(
    password: str,
    stored: str
) -> bool:
    try:
        salt, expected = stored.split(
            "$",
            1
        )
    except ValueError:
        return False

    actual = _hash_password(
        password,
        salt
    ).split(
        "$",
        1
    )[1]
    return hmac.compare_digest(
        actual,
        expected
    )


def load_users() -> list[Dict]:
    users = load_document(
        "auth_users",
        []
    )
    if not isinstance(
        users,
        list
    ):
        users = []

    if (
        ADMIN_PASSWORD
        and not any(
            user.get(
                "username"
            )
            == ADMIN_USERNAME
            for user in users
        )
    ):
        users.append(
            {
                "id": str(
                    uuid.uuid4()
                ),
                "username": ADMIN_USERNAME,
                "password_hash": _hash_password(
                    ADMIN_PASSWORD
                ),
                "role": "admin",
                "active": True
            }
        )
        save_document(
            "auth_users",
            users
        )

    return users


def create_user(
    username: str,
    password: str,
    role: str = "viewer"
) -> Dict:
    username = str(
        username
    ).strip()
    if not username:
        raise ValueError(
            "Username is required."
        )
    if len(
        password
    ) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )
    role = role if role in ROLE_PERMISSIONS else "viewer"
    users = load_users()

    if any(
        user.get(
            "username"
        )
        == username
        for user in users
    ):
        raise ValueError(
            "Username already exists."
        )

    user = {
        "id": str(
            uuid.uuid4()
        ),
        "username": username,
        "password_hash": _hash_password(
            password
        ),
        "role": role,
        "active": True
    }
    users.append(
        user
    )
    save_document(
        "auth_users",
        users
    )
    return public_user(
        user
    )


def public_user(
    user: Dict
) -> Dict:
    return {
        key: value
        for key, value in user.items()
        if key != "password_hash"
    }


def authenticate_user(
    username: str,
    password: str
) -> Dict | None:
    for user in load_users():
        if (
            user.get(
                "username"
            )
            == username
            and user.get(
                "active",
                False
            )
            and _verify_password(
                password,
                user.get(
                    "password_hash",
                    ""
                )
            )
        ):
            return public_user(
                user
            )
    return None


def issue_token(
    user: Dict
) -> str:
    if not AUTH_SECRET:
        raise ValueError(
            "HELIOS_AUTH_SECRET is not configured."
        )

    payload = {
        "sub": user.get(
            "id"
        ),
        "username": user.get(
            "username"
        ),
        "role": user.get(
            "role",
            "viewer"
        ),
        "exp": int(
            time.time()
        )
        + TOKEN_TTL_MINUTES * 60
    }
    encoded = _encode(
        json.dumps(
            payload,
            separators=(
                ",",
                ":"
            )
        ).encode(
            "utf-8"
        )
    )
    signature = _encode(
        hmac.new(
            AUTH_SECRET.encode(
                "utf-8"
            ),
            encoded.encode(
                "ascii"
            ),
            hashlib.sha256
        ).digest()
    )
    return f"{encoded}.{signature}"


def verify_token(
    token: str
) -> Dict | None:
    if not AUTH_SECRET or "." not in token:
        return None

    encoded, signature = token.split(
        ".",
        1
    )
    expected = _encode(
        hmac.new(
            AUTH_SECRET.encode(
                "utf-8"
            ),
            encoded.encode(
                "ascii"
            ),
            hashlib.sha256
        ).digest()
    )
    if not hmac.compare_digest(
        signature,
        expected
    ):
        return None

    try:
        payload = json.loads(
            _decode(
                encoded
            )
        )
    except Exception:
        return None

    if int(
        payload.get(
            "exp",
            0
        )
    ) <= int(
        time.time()
    ):
        return None

    return payload


def has_permission(
    user: Dict | None,
    permission: str
) -> bool:
    if user is None:
        return False
    return permission in ROLE_PERMISSIONS.get(
        user.get(
            "role",
            "viewer"
        ),
        set()
    )
