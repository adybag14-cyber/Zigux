#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 install-zig download hardening packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALLER_PATH = Path("scripts/zigux/install-zig.py")

REQUIRED_MARKERS = (
    "RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}",
    "DOWNLOAD_RETRIES = 4",
    "DOWNLOAD_TIMEOUT = 120.0",
    "DOWNLOAD_CHUNK_SIZE = 1024 * 1024",
    "MAX_RETRY_DELAY = 30.0",
    "def parse_retry_after(headers) -> float | None:",
    "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
    "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
    "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
    "def copy_url_to_file_with_curl(",
    "'--retry-all-errors',",
    "'--continue-at',",
    "'--speed-limit',",
    "'--speed-time',",
    "def copy_url_to_file(",
    "if shutil.which('curl') is not None:",
    "copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)",
    "resume_offset = destination.stat().st_size if destination.exists() else 0",
    "request = build_download_request(url, resume_offset)",
    "append = resume_offset > 0 and status == 206",
    "except urllib.error.HTTPError as exc:",
    "except urllib.error.URLError as exc:",
    "time.sleep(",
)

REQUIRED_ORDER = (
    (
        "def parse_retry_after(headers) -> float | None:",
        "def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:",
        "retry-after helpers",
    ),
    (
        "def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:",
        "def copy_response_chunks(response, destination: Path, *, append: bool) -> None:",
        "resume helper order",
    ),
    (
        "def copy_url_to_file_with_curl(",
        "def copy_url_to_file(",
        "curl path before urllib fallback",
    ),
    (
        "if shutil.which('curl') is not None:",
        "for attempt in range(1, retries + 1):",
        "curl preference before urllib retries",
    ),
    (
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
        "request = build_download_request(url, resume_offset)",
        "resume offset before request",
    ),
    (
        "request = build_download_request(url, resume_offset)",
        "append = resume_offset > 0 and status == 206",
        "request before append decision",
    ),
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig download checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig download checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 install-zig download checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig download checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_installer(text: str) -> int:
    for marker in REQUIRED_MARKERS:
        require_marker(text, marker, "installer marker")

    require_exact_count(text, "def copy_url_to_file_with_curl(", 1, "curl download helper")
    require_exact_count(text, "def copy_url_to_file(", 1, "urllib download helper")
    require_exact_count(
        text,
        "resume_offset = destination.stat().st_size if destination.exists() else 0",
        1,
        "resume offset assignment",
    )
    require_exact_count(
        text,
        "append = resume_offset > 0 and status == 206",
        1,
        "append decision",
    )
    require_exact_count(text, "'--continue-at',", 1, "curl resume flag")
    require_exact_count(text, "'--retry-all-errors',", 1, "curl retry-all-errors flag")

    for earlier, later, label in REQUIRED_ORDER:
        require_order(text, earlier, later, label)

    return len(REQUIRED_MARKERS)


def write_sample_root(root: Path) -> None:
    installer_path = root / INSTALLER_PATH
    installer_path.parent.mkdir(parents=True, exist_ok=True)
    installer_path.write_text(
        """#!/usr/bin/env python3
from __future__ import annotations

import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}
DOWNLOAD_RETRIES = 4
DOWNLOAD_TIMEOUT = 120.0
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
MAX_RETRY_DELAY = 30.0

def parse_retry_after(headers) -> float | None:
    return None

def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:
    return default_delay

def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:
    if start_offset <= 0:
        return url
    return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})

def copy_response_chunks(response, destination: Path, *, append: bool) -> None:
    return None

def copy_url_to_file_with_curl(
    url: str,
    destination: Path,
    *,
    retries: int = DOWNLOAD_RETRIES,
    timeout: float = DOWNLOAD_TIMEOUT,
) -> None:
    cmd = [
        'curl',
        '--retry-all-errors',
        '--continue-at',
        '-',
        '--speed-limit',
        '1',
        '--speed-time',
        '30',
        url,
    ]
    return None

def copy_url_to_file(
    url: str,
    destination: Path,
    *,
    retries: int = DOWNLOAD_RETRIES,
    timeout: float = DOWNLOAD_TIMEOUT,
) -> None:
    if shutil.which('curl') is not None:
        copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)
        return
    for attempt in range(1, retries + 1):
        resume_offset = destination.stat().st_size if destination.exists() else 0
        request = build_download_request(url, resume_offset)
        try:
            status = 206
            append = resume_offset > 0 and status == 206
            copy_response_chunks(None, destination, append=append)
            return
        except urllib.error.HTTPError as exc:
            time.sleep(
                retry_delay_seconds(
                    attempt,
                    default_delay=min(1.5 * attempt, 5.0),
                    headers=exc.headers,
                )
            )
        except urllib.error.URLError as exc:
            time.sleep(min(1.5 * attempt, 5.0))
""",
        encoding="utf-8",
    )


def run_self_test() -> int:
    base = """#!/usr/bin/env python3
from __future__ import annotations

import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}
DOWNLOAD_RETRIES = 4
DOWNLOAD_TIMEOUT = 120.0
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
MAX_RETRY_DELAY = 30.0

def parse_retry_after(headers) -> float | None:
    return None

def retry_delay_seconds(attempt: int, *, default_delay: float, headers=None) -> float:
    return default_delay

def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:
    if start_offset <= 0:
        return url
    return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})

def copy_response_chunks(response, destination: Path, *, append: bool) -> None:
    return None

def copy_url_to_file_with_curl(
    url: str,
    destination: Path,
    *,
    retries: int = DOWNLOAD_RETRIES,
    timeout: float = DOWNLOAD_TIMEOUT,
) -> None:
    cmd = [
        'curl',
        '--retry-all-errors',
        '--continue-at',
        '-',
        '--speed-limit',
        '1',
        '--speed-time',
        '30',
        url,
    ]
    return None

def copy_url_to_file(
    url: str,
    destination: Path,
    *,
    retries: int = DOWNLOAD_RETRIES,
    timeout: float = DOWNLOAD_TIMEOUT,
) -> None:
    if shutil.which('curl') is not None:
        copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)
        return
    for attempt in range(1, retries + 1):
        resume_offset = destination.stat().st_size if destination.exists() else 0
        request = build_download_request(url, resume_offset)
        try:
            status = 206
            append = resume_offset > 0 and status == 206
            copy_response_chunks(None, destination, append=append)
            return
        except urllib.error.HTTPError as exc:
            time.sleep(
                retry_delay_seconds(
                    attempt,
                    default_delay=min(1.5 * attempt, 5.0),
                    headers=exc.headers,
                )
            )
        except urllib.error.URLError as exc:
            time.sleep(min(1.5 * attempt, 5.0))
"""
    marker_count = check_installer(base)
    assert marker_count == len(REQUIRED_MARKERS)
    case_count = 1

    def expect_failure(bad_text: str, expected_substring: str) -> None:
        nonlocal case_count
        try:
            check_installer(bad_text)
        except SystemExit as exc:
            assert expected_substring in str(exc), str(exc)
            case_count += 1
            return
        raise AssertionError("expected installer validation to fail")

    expect_failure(base.replace("'--continue-at',\n", "", 1), "'--continue-at',")
    expect_failure(
        base.replace(
            "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})\n",
            "return urllib.request.Request(url)\n",
            1,
        ),
        "return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})",
    )
    expect_failure(
        base.replace(
            "if shutil.which('curl') is not None:\n"
            "        copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)\n"
            "        return\n"
            "    for attempt in range(1, retries + 1):\n",
            "for attempt in range(1, retries + 1):\n"
            "        pass\n"
            "    if shutil.which('curl') is not None:\n"
            "        copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)\n"
            "        return\n",
            1,
        ),
        "curl preference before urllib retries",
    )
    expect_failure(
        base.replace(
            "resume_offset = destination.stat().st_size if destination.exists() else 0\n"
            "        request = build_download_request(url, resume_offset)\n",
            "request = build_download_request(url, 0)\n"
            "        resume_offset = destination.stat().st_size if destination.exists() else 0\n",
            1,
        ),
        "request = build_download_request(url, resume_offset)",
    )
    expect_failure(
        base.replace(
            "append = resume_offset > 0 and status == 206\n",
            "append = status == 206\n",
            1,
        ),
        "append = resume_offset > 0 and status == 206",
    )

    print("LANE05_INSTALL_ZIG_DOWNLOAD_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_DOWNLOAD_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 keeps the install-zig retry and resume contract."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for local replay.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    installer_text = (args.root.resolve() / INSTALLER_PATH).read_text(encoding="utf-8")
    marker_count = check_installer(installer_text)
    print("LANE05_INSTALL_ZIG_DOWNLOAD_CONTRACT=pass")
    print(f"LANE05_INSTALL_ZIG_DOWNLOAD_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_INSTALL_ZIG_DOWNLOAD_CONTRACT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
