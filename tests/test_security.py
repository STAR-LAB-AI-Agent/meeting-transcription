import pytest

from src import security


def test_traversal_relative_rejected():
    with pytest.raises(security.SecurityError):
        security.validate_path("../../../etc/passwd")


def test_traversal_absolute_rejected():
    with pytest.raises(security.SecurityError):
        security.validate_path("C:/Windows/System32/config/SAM")


def test_allowed_read_path():
    p = security.validate_path("examples/demo_transcript.json", write=False)
    assert p.exists()


def test_write_outside_whitelist_rejected():
    with pytest.raises(security.SecurityError):
        security.validate_path("README.md", write=True)


def test_redact_secrets():
    text = "api_key=sk-abcdefghijklmnop1234 token=ghp_ABCDEFGHIJKLMNOP"
    out = security.redact_secrets(text)
    assert "sk-abcdefghijklmnop1234" not in out
    assert "ghp_ABCDEFGHIJKLMNOP" not in out
    assert "[REDACTED]" in out
