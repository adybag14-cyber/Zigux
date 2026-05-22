#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
INSTALLER_PATH = Path("scripts/zigux/install-zig.py")
DEV_CHANNEL = "0.17.0-dev.87+9b177a7d2"
RELEASE_CHANNEL = "0.16.0"

REQUIRED_MARKERS = (
    "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:",
    "suffix = '.zip' if system_key == 'windows' else '.tar.xz'",
    "if '-dev.' in channel:",
    "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
    "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'",
    "entry = index.get(channel)",
    "if entry is None and VERSION_KEY_RE.fullmatch(channel):",
    "for candidate in index.values():",
    "if isinstance(candidate, dict) and candidate.get('version') == channel:",
    "        if entry is None:\n            return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
    "except (TimeoutError, urllib.error.URLError):",
    "        if not is_explicit_version(channel):\n            raise\n        return {}",
    "assert resolve_target(",
    f"assert load_index('{DEV_CHANNEL}') == {{}}",
    "raise AssertionError('expected non-explicit channel timeout to fail')",
)

ORDERED_MARKER_PAIRS = (
    (
        "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:",
        "def resolve_target(index: dict, channel: str, arch_key: str, system_key: str) -> tuple[str, str, str]:",
    ),
    (
        "entry = index.get(channel)",
        "if entry is None and VERSION_KEY_RE.fullmatch(channel):",
    ),
    (
        "if entry is None and VERSION_KEY_RE.fullmatch(channel):",
        "for candidate in index.values():",
    ),
    (
        "for candidate in index.values():",
        "        if entry is None:\n            return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
    ),
    (
        "def load_index(channel: str) -> dict:",
        "except (TimeoutError, urllib.error.URLError):",
    ),
    (
        "except (TimeoutError, urllib.error.URLError):",
        "        if not is_explicit_version(channel):\n            raise\n        return {}",
    ),
)


def load_text(root: Path) -> str:
    path = root / INSTALLER_PATH
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"lane05 install-zig index fallback checker missing installer: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 install-zig index fallback checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 install-zig index fallback checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 install-zig index fallback checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 install-zig index fallback checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_root(root: Path) -> tuple[int, str]:
    text = load_text(root)
    for marker in REQUIRED_MARKERS:
        require_marker(text, marker, "installer marker")
        require_exact_count(text, marker, 1, "installer marker")
    for earlier, later in ORDERED_MARKER_PAIRS:
        require_order(text, earlier, later, "installer fallback order")
    return len(REQUIRED_MARKERS), DEV_CHANNEL


def write_sample_root(root: Path) -> None:
    scripts_dir = root / "scripts" / "zigux"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "install-zig.py").write_text(
        "\n".join(
            (
                "import urllib.error",
                "",
                "VERSION_KEY_RE = object()",
                "",
                "def is_explicit_version(channel: str) -> bool:",
                "    return channel.startswith('0.')",
                "",
                "def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:",
                "    suffix = '.zip' if system_key == 'windows' else '.tar.xz'",
                "    if '-dev.' in channel:",
                "        return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
                "    return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'",
                "",
                "def resolve_target(index: dict, channel: str, arch_key: str, system_key: str) -> tuple[str, str, str]:",
                "    target_key = f'{arch_key}-{system_key}'",
                "    entry = index.get(channel)",
                "    if entry is None and VERSION_KEY_RE.fullmatch(channel):",
                "        for candidate in index.values():",
                "            if isinstance(candidate, dict) and candidate.get('version') == channel:",
                "                entry = candidate",
                "                break",
                "        if entry is None:",
                "            return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
                "    return target_key, channel, 'https://example.invalid/zig.tar.xz'",
                "",
                "def read_index() -> dict:",
                "    return {}",
                "",
                "def load_index(channel: str) -> dict:",
                "    try:",
                "        return read_index()",
                "    except (TimeoutError, urllib.error.URLError):",
                "        if not is_explicit_version(channel):",
                "            raise",
                "        return {}",
                "",
                "def run_self_test() -> int:",
                "    assert resolve_target(",
                "        {'0.16.0': {'version': '0.16.0'}},",
                f"        '{DEV_CHANNEL}',",
                "        'x86_64',",
                "        'linux',",
                "    ) == (",
                "        'x86_64-linux',",
                f"        '{DEV_CHANNEL}',",
                f"        'https://ziglang.org/builds/zig-x86_64-linux-{DEV_CHANNEL}.tar.xz',",
                "    )",
                f"    assert load_index('{DEV_CHANNEL}') == {{}}",
                "    raise AssertionError('expected non-explicit channel timeout to fail')",
                "",
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_index_fallback_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert check_root(root) == (len(REQUIRED_MARKERS), DEV_CHANNEL)
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_index_fallback_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_root(root)
            except SystemExit as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected check_root to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / INSTALLER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing installer marker",
    )
    expect_failure(
        lambda root: (root / INSTALLER_PATH).write_text(
            load_text(root).replace(
                "return target_key, channel, infer_tarball_url(channel, target_key, system_key)",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "missing installer marker",
    )
    expect_failure(
        lambda root: (root / INSTALLER_PATH).write_text(
            load_text(root).replace(
                "if not is_explicit_version(channel):\n            raise\n        return {}",
                "return {}\n        if not is_explicit_version(channel):\n            raise",
                1,
            ),
            encoding="utf-8",
        ),
        "missing installer marker",
    )
    expect_failure(
        lambda root: (root / INSTALLER_PATH).write_text(
            load_text(root) + f"assert load_index('{DEV_CHANNEL}') == {{}}\n",
            encoding="utf-8",
        ),
        "expected exactly 1 occurrences",
    )
    expect_failure(
        lambda root: (root / INSTALLER_PATH).write_text(
            load_text(root).replace(
                "return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'",
                "return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'",
                1,
            ),
            encoding="utf-8",
        ),
        "expected exactly 1 occurrences",
    )

    print("LANE05_INSTALL_ZIG_INDEX_FALLBACK_SELF_TEST=pass")
    print(f"LANE05_INSTALL_ZIG_INDEX_FALLBACK_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 install-zig explicit-version fallback contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for local replay.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    marker_count, channel = check_root(args.root.resolve())
    print("LANE05_INSTALL_ZIG_INDEX_FALLBACK=pass")
    print(f"LANE05_INSTALL_ZIG_INDEX_FALLBACK_MARKER_COUNT={marker_count}")
    print(f"LANE05_INSTALL_ZIG_INDEX_FALLBACK_CHANNEL={channel}")
    print(f"LANE05_INSTALL_ZIG_INDEX_FALLBACK_RELEASE_CHANNEL={RELEASE_CHANNEL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
