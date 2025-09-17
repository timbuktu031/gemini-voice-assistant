# utils/__init__.py
"""
유틸리티 모듈 패키지
"""

from .text_utils import (
    setup_encoding,
    clean_text,
    safe_input,
    detect_real_time_query
)

__all__ = [
    'setup_encoding',
    'clean_text', 
    'safe_input',
    'detect_real_time_query'
]