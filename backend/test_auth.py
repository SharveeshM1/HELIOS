from core import auth


def test_signed_token_carries_role_and_permissions(monkeypatch):
    monkeypatch.setattr(
        auth,
        "AUTH_SECRET",
        "test-secret"
    )
    token = auth.issue_token(
        {
            "id": "user-1",
            "username": "operator",
            "role": "operator"
        }
    )
    payload = auth.verify_token(
        token
    )

    assert payload["username"] == "operator"
    assert auth.has_permission(
        payload,
        "execute"
    )
    assert not auth.has_permission(
        payload,
        "commit"
    )


def test_password_hash_verification_is_salted():
    first = auth._hash_password(
        "secret"
    )
    second = auth._hash_password(
        "secret"
    )

    assert first != second
    assert auth._verify_password(
        "secret",
        first
    )
    assert not auth._verify_password(
        "wrong",
        first
    )
