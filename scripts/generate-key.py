#!/usr/bin/env python3
"""
VoxParaguay 2026 - Encryption Key Generator
Generates a secure 256-bit encryption key for Law 7593/2025 compliance
"""

import base64
import os


def generate_key():
    """Generate a 32-byte (256-bit) encryption key."""
    key = os.urandom(32)
    return base64.b64encode(key).decode('utf-8')


if __name__ == "__main__":
    key = generate_key()
    print("\n🔐 VoxParaguay 2026 - Clave de Encriptación")
    print("=" * 50)
    print(f"\nENCRYPTION_KEY={key}")
    print("\n⚠️  Guarde esta clave en un lugar seguro.")
    print("    Esta clave es requerida por la Ley 7593/2025.")
    print("    No la comparta ni la incluya en el control de versiones.\n")
