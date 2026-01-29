"""
VoxParaguay 2026 - Security Module Tests
Tests for KeyRotationManager and encryption utilities
"""

import pytest
import os
import base64
from unittest.mock import patch, MagicMock
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Adjust import path for project structure
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# --- 測試配置 ---
@pytest.fixture
def mock_keys():
    """生成測試用的隨機金鑰"""
    key_v1 = base64.b64encode(os.urandom(32)).decode()
    key_v2 = base64.b64encode(os.urandom(32)).decode()
    blind_key = base64.b64encode(os.urandom(32)).decode()
    return key_v1, key_v2, blind_key


@pytest.fixture
def manager(mock_keys):
    """初始化 KeyRotationManager 實例，使用 mock 的 settings"""
    key_v1, key_v2, blind_key = mock_keys

    # Create a mock settings object
    mock_settings = MagicMock()
    mock_settings.ENCRYPTION_KEY = key_v1
    mock_settings.ENCRYPTION_KEY_V2 = key_v2
    mock_settings.BLIND_INDEX_KEY = blind_key

    # Patch settings and reset singleton
    with patch('app.utils.security.settings', mock_settings):
        # Clear singleton to force re-initialization with mocked settings
        import app.utils.security as security_module
        security_module._key_manager = None

        from app.utils.security import KeyRotationManager
        manager = KeyRotationManager()

        yield manager

        # Cleanup
        security_module._key_manager = None


# --- 測試案例 ---

def test_v1_data_compatibility(manager, mock_keys):
    """
    驗證測試：手動建立一個 v1 格式的密文，檢查系統是否能正確解密
    """
    key_v1_raw = base64.b64decode(mock_keys[0])
    plain_text = "Datos Sensibles de Paraguay"

    # 手動模擬 v1 加密過程
    aesgcm = AESGCM(key_v1_raw)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode(), None)
    v1_payload = f"v1:{base64.b64encode(nonce + ciphertext).decode('utf-8')}"

    # 執行解密
    decrypted = manager.decrypt_any(v1_payload)

    assert decrypted == plain_text
    assert decrypted != "ERROR_DECRYPTION"


def test_new_encryption_uses_v2(manager):
    """
    驗證測試：新加密的數據必須預設使用最新的 v2 版本
    """
    plain_text = "Nuevo Registro 2026"
    encrypted_payload = manager.encrypt_new(plain_text)

    assert encrypted_payload.startswith("v2:")

    # 驗證新數據解密是否正常
    decrypted = manager.decrypt_any(encrypted_payload)
    assert decrypted == plain_text


def test_batch_rotation_migration(manager):
    """
    驗證測試：模擬批次遷移任務，將舊數據清單從 v1 升級為 v2
    """
    # 建立一組 v1 的舊數據
    old_data = [
        manager.encrypt_with_version("Dato 1", "v1"),
        manager.encrypt_with_version("Dato 2", "v1")
    ]

    # 執行輪轉遷移
    updated_data = manager.rotate_data_task(old_data)

    for item in updated_data:
        assert item.startswith("v2:")
        assert manager.decrypt_any(item) in ["Dato 1", "Dato 2"]


def test_invalid_version_handling(manager):
    """
    驗證測試：如果版本號不存在或格式錯誤，系統應返回錯誤標記而非崩潰
    """
    invalid_payload = "v99:some_random_base64"
    result = manager.decrypt_any(invalid_payload)

    assert result == "ERROR_DECRYPTION"


def test_legacy_format_without_version(manager, mock_keys):
    """
    驗證測試：舊格式（無版本前綴）應被視為 v1
    """
    key_v1_raw = base64.b64decode(mock_keys[0])
    plain_text = "Legacy Data"

    # 建立無版本前綴的密文（舊格式）
    aesgcm = AESGCM(key_v1_raw)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode(), None)
    legacy_payload = base64.b64encode(nonce + ciphertext).decode('utf-8')

    # 應能正確解密
    decrypted = manager.decrypt_any(legacy_payload)
    assert decrypted == plain_text


def test_re_encrypt_updates_version(manager):
    """
    驗證測試：re_encrypt 應將舊版本數據升級到當前版本
    """
    plain_text = "Data to Upgrade"

    # 使用 v1 加密
    v1_encrypted = manager.encrypt_with_version(plain_text, "v1")
    assert v1_encrypted.startswith("v1:")

    # 重新加密到 v2
    v2_encrypted = manager.re_encrypt(v1_encrypted)
    assert v2_encrypted.startswith("v2:")

    # 驗證數據完整性
    assert manager.decrypt_any(v2_encrypted) == plain_text


def test_is_current_version_check(manager):
    """
    驗證測試：is_current_version 應正確判斷版本
    """
    plain_text = "Test Data"

    v1_encrypted = manager.encrypt_with_version(plain_text, "v1")
    v2_encrypted = manager.encrypt_with_version(plain_text, "v2")

    assert manager.is_current_version(v1_encrypted) is False
    assert manager.is_current_version(v2_encrypted) is True
    assert manager.is_current_version("") is True  # Empty is considered current
