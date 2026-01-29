"""
VoxParaguay 2026 - Test Configuration
Pytest fixtures and configuration
"""

import pytest
import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
