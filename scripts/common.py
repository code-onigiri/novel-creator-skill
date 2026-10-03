#!/usr/bin/env python3
"""Shared Utility Module - Eliminate Code Duplication

This module centrally manages all shared utility functions across scripts,
avoiding duplicate definitions in multiple files. It mainly supports the
creation workflow for million-character-level long novels.
"""

import functools
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# =============================================================================
# Precompiled Regular Expressions (Performance Optimization)
# =============================================================================

_CHAPTER_RE = re.compile(r"^第\d+章.*\.md$")
_SLUGIFY_RE = re.compile(r"[^0-9A-Za-z\u4e00-\u9fff_-]+")
_CHARS_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_ENGLISH_RE = re.compile(r"[A-Za-z]{3,}")
_CHAPTER_NO_RE = re.compile(r"第(\d+)章")

# =============================================================================
# File System Operations
# =============================================================================


def ensure_dir(path: Path) -> None:
    """Ensure directory exists, create recursively if not.

    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path, default: str = "") -> str:
    """Safely read a text file.

    Args:
        path: File path
        default: Default value if file does not exist

    Returns:
        File content, or default value
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        print(f"[WARN] File encoding issue {path}: {e}")
        return path.read_text(encoding="utf-8", errors="replace")
    except (FileNotFoundError, PermissionError):
        return default


def write_text(path: Path, content: str) -> bool:
    """Safely write a text file.

    Args:
        path: File path
        content: Content to write

    Returns:
        Whether the write succeeded
    """
    try:
        ensure_dir(path.parent)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        return True
    except (IOError, PermissionError) as e:
        # Use print instead of logging to be consistent with existing code
        print(f"[ERROR] Failed to write {path}: {e}")
        return False


# =============================================================================
# JSON Operations
# =============================================================================


def load_json(
    path: Path,
    default: Optional[Dict[str, Any]] = None,
    required_keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Safely load a JSON file, with support for defaults and key validation.

    Args:
        path: JSON file path
        default: Default value on load failure
        required_keys: List of required keys

    Returns:
        Parsed dictionary, or default value
    """
    if default is None:
        default = {}

    if not path.exists():
        return default.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)

        if not isinstance(obj, dict):
            return default.copy()

        # Validate required fields
        if required_keys:
            missing = [k for k in required_keys if k not in obj]
            if missing:
                return default.copy()

        return obj

    except (json.JSONDecodeError, IOError, KeyError):
        return default.copy()


def save_json(
    path: Path, payload: Dict[str, Any], indent: int = 2
) -> bool:
    """Safely save a JSON file.

    Args:
        path: File path
        payload: Dictionary to save
        indent: Number of indent spaces

    Returns:
        Whether the save succeeded
    """
    try:
        ensure_dir(path.parent)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=indent)
        return True
    except (IOError, TypeError) as e:
        print(f"[ERROR] Failed to save JSON {path}: {e}")
        return False


# =============================================================================
# Text Processing
# =============================================================================


def slugify(text: str) -> str:
    """Convert text to a URL/filename-friendly slug.

    Preserves Chinese characters, letters, digits, underscores, and hyphens.

    Args:
        text: Raw text

    Returns:
        Converted slug
    """
    s = _SLUGIFY_RE.sub("-", text).strip("-")
    return s or "chapter"


def normalize_text(text: str) -> str:
    """Replace consecutive whitespace with a single space."""
    return re.sub(r"\s+", " ", text).strip()


def count_chars(text: str, include_spaces: bool = False) -> int:
    """Count text characters (unified method).

    For Chinese novels, counting Chinese characters is usually more accurate.
    This method supports both:
    - Pure Chinese character count (default)
    - Count all non-whitespace characters

    Args:
        text: Input text
        include_spaces: Whether to include spaces and punctuation

    Returns:
        Character count
    """
    if include_spaces:
        # Count all non-whitespace characters
        return len(re.sub(r"\s+", "", text))
    else:
        # Count only Chinese characters (more accurate for Chinese novels)
        return len(re.findall(r'[\u4e00-\u9fff]', text))


def sha1_text(text: str) -> str:
    """Compute the SHA1 hash of text.

    Args:
        text: Input text

    Returns:
        SHA1 hash string
    """
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def file_sha1(path: Path) -> str:
    """Compute the SHA1 hash of a file.

    Args:
        path: File path

    Returns:
        SHA1 hash of file content, empty string if file not found
    """
    if not path.exists():
        return ""
    return sha1_text(path.read_text(encoding="utf-8", errors="ignore"))


# =============================================================================
# Chapter Utilities
# =============================================================================


def is_chapter_file(filename: str) -> bool:
    """Determine whether a filename is a chapter file.

    Chapter filename format: ChapterXX[Title].md

    Args:
        filename: Filename

    Returns:
        Whether it is a chapter file
    """
    return bool(_CHAPTER_RE.match(filename))


def chapter_no_from_name(filename: str) -> int:
    """Extract chapter number from chapter filename.

    Args:
        filename: Chapter filename, e.g. Chapter15 Breakthrough.md

    Returns:
        Chapter number, 0 on failure
    """
    match = _CHAPTER_NO_RE.search(filename)
    if match:
        return int(match.group(1))
    return 0


def normalize_chapter_filename(chapter_no: int, title: str = "") -> str:
    """Generate a normalized chapter filename.

    Args:
        chapter_no: Chapter number
        title: Chapter title (optional)

    Returns:
        Standardized filename, e.g. Chapter15 Breakthrough.md
    """
    if title:
        clean_title = re.sub(r'[<>:"/\\|?*]', '', title).strip()
        return f"Chapter{chapter_no} {clean_title}.md"
    return f"Chapter{chapter_no}.md"


# =============================================================================
# Caching Utilities
# =============================================================================


def generate_cache_key(*components: str) -> str:
    """Generate a cache key.

    Args:
        *components: Cache key components

    Returns:
        Hashed cache key
    """
    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


# =============================================================================
# Version Information
# =============================================================================

__version__ = "1.0.0"
__all__ = [
    # File system
    "ensure_dir",
    "read_text",
    "write_text",
    # JSON
    "load_json",
    "save_json",
    # Text processing
    "slugify",
    "normalize_text",
    "sha1_text",
    "file_sha1",
    # Chapter related
    "is_chapter_file",
    "chapter_no_from_name",
    "normalize_chapter_filename",
    # Caching
    "generate_cache_key",
]
