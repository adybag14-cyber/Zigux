#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

README_PATH = Path("third_party/README.md")
DOCS_PATH = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
LOCAL_FIRST_CHECKER_PATH = Path("scripts/zigux/check-lane05-local-first-archive-workflow.py")
README_CHECKER_PATH = Path("scripts/zigux/check-lane05-local-archive-readme.py")
INSTALL_CHECKER_PATH = Path("scripts/zigux/check-lane05-install-zig-archive-verification.py")

EXPECTED_TARGET = "x86_64-linux"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_FILE = f"third_party/zig-{EXPECTED_TARGET}-{EXPECTED_CHANNEL}.tar.xz"
EXPECTED_PARTS_DIR = f"{EXPECTED_FILE}.parts"
EXPECTED_SHA = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
EXPECTED_SIZE = "58159088"
EXPECTED_ARCHIVE_COMMAND = (
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
    f"{EXPECTED_FILE} --archive-target {EXPECTED_TARGET}"
)

README_MARKERS = (
    "# Zigux third-party archives",
    "This directory is reserved for trusted archive payloads",
    f"`{EXPECTED_TARGET}`",
    f"`{EXPECTED_CHANNEL}`",
    f"`{EXPECTED_FILE}`",
    f"`{EXPECTED_SHA}`",
    f"`{EXPECTED_SIZE}` bytes",
    f"`{EXPECTED_ARCHIVE_COMMAND}`",
    f"`{EXPECTED_PARTS_DIR}`",
    "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle",
    "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/check-lane05-stage-helper-contract.py`",
    "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
)

DOCS_MARKERS = (
    f"`{EXPECTED_FILE}`",
    "`third_party/README.md` is directly readable on current `master`",
    f"`{EXPECTED_ARCHIVE_COMMAND}` replay contract",
    "tries `community-mirrors.txt` before the direct Zig download URL",
    "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
)

WORKFLOW_MARKERS = (
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "rm -f \"$archive_path\" \"$mirror_file\"",
    "rm -rf \"$extract_root\"",
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
)

LOCAL_FIRST_CHECKER_MARKERS = (
    "THIRD_PARTY_PATH = \"- 'third_party/**'\"",
    "README_SELF_TEST_STEP = \"- name: Self-test current Lane 05 local archive README checker\"",
    "README_CHECK_STEP = \"- name: Check current Lane 05 local archive README packet\"",
    "PHASE2_TOOL_MANIFEST_SELF_TEST_STEP = \"- name: Self-test current Phase 2 tool manifest checker\"",
)

README_CHECKER_MARKERS = (
    "README_PATH = Path(\"third_party/README.md\")",
    "POLICY_PATH = Path(\"scripts/zigux/zig-toolchain-policy.json\")",
    "EXPECTED_ARCHIVE_SIZES = {",
    "community-mirrors.txt",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
)

INSTALL_CHECKER_MARKERS = (
    "INSTALL_ZIG = Path(\"scripts/zigux/install-zig.py\")",
    "TOOLCHAIN_POLICY = Path(\"scripts/zigux/zig-toolchain-policy.json\")",
    "expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
)

COMPANION_PATHS = (
    README_PATH,
    DOCS_PATH,
    WORKFLOW_PATH,
    POLICY_PATH,
    LOCAL_FIRST_CHECKER_PATH,
    README_CHECKER_PATH,
    INSTALL_CHECKER_PATH,
)


def read_text(root: Path, relpath: Path) -> str:
    path = root / relpath
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {relpath}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise ValueError(f"{label} missing markers: {', '.join(missing)}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        return
    if earlier_index >= later_index:
        raise ValueError(f"{label} out of order: `{earlier}` must appear before `{later}`")


def load_policy(root: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(root, POLICY_PATH))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {POLICY_PATH}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid JSON shape in {POLICY_PATH}")
    return payload


def validate_policy(payload: dict[str, object]) -> None:
    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    archive_sha256 = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")

    if channel != EXPECTED_CHANNEL:
        raise ValueError(f"{POLICY_PATH} channel drifted from {EXPECTED_CHANNEL}")
    if minimum_version != EXPECTED_CHANNEL:
        raise ValueError(f"{POLICY_PATH} minimum_version drifted from {EXPECTED_CHANNEL}")
    if not isinstance(archive_sha256, dict):
        raise ValueError(f"{POLICY_PATH} archive_sha256 is not an object")
    if archive_sha256.get(EXPECTED_TARGET) != EXPECTED_SHA:
        raise ValueError(f"{POLICY_PATH} archive_sha256 for {EXPECTED_TARGET} drifted")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"{POLICY_PATH} upgrade_policy is not an object")
    targets = upgrade_policy.get("archive_target_scope")
    if targets != [EXPECTED_TARGET]:
        raise ValueError(f"{POLICY_PATH} archive_target_scope drifted from [{EXPECTED_TARGET}]")


def validate_root(root: Path) -> tuple[int, int, int, int]:
    readme_text = read_text(root, README_PATH)
    docs_text = read_text(root, DOCS_PATH)
    workflow_text = read_text(root, WORKFLOW_PATH)
    local_first_checker_text = read_text(root, LOCAL_FIRST_CHECKER_PATH)
    readme_checker_text = read_text(root, README_CHECKER_PATH)
    install_checker_text = read_text(root, INSTALL_CHECKER_PATH)
    policy = load_policy(root)

    validate_policy(policy)
    require_markers(readme_text, README_MARKERS, str(README_PATH))
    require_markers(docs_text, DOCS_MARKERS, str(DOCS_PATH))
    require_markers(workflow_text, WORKFLOW_MARKERS, str(WORKFLOW_PATH))
    require_markers(local_first_checker_text, LOCAL_FIRST_CHECKER_MARKERS, str(LOCAL_FIRST_CHECKER_PATH))
    require_markers(readme_checker_text, README_CHECKER_MARKERS, str(README_CHECKER_PATH))
    require_markers(install_checker_text, INSTALL_CHECKER_MARKERS, str(INSTALL_CHECKER_PATH))

    require_order(
        readme_text,
        f"`{EXPECTED_FILE}`",
        f"`{EXPECTED_PARTS_DIR}`",
        str(README_PATH),
    )
    require_order(
        readme_text,
        f"`{EXPECTED_PARTS_DIR}`",
        "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
        str(README_PATH),
    )
    require_order(
        workflow_text,
        "if try_local_archive; then",
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        str(WORKFLOW_PATH),
    )
    require_order(
        workflow_text,
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        'if try_download "$ZIGUX_ZIG_URL"; then',
        str(WORKFLOW_PATH),
    )

    return (
        len(README_MARKERS),
        len(DOCS_MARKERS),
        len(WORKFLOW_MARKERS),
        len(COMPANION_PATHS),
    )


def sample_policy_json() -> str:
    return (
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {EXPECTED_TARGET: EXPECTED_SHA},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [EXPECTED_TARGET],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-tools",
                        "phase2-kconfig",
                        "phase2-cross",
                        "phase2-genksyms",
                        "phase2-fixdep",
                        "phase2-validate",
                    ],
                },
            },
            indent=2,
        )
        + "\n"
    )


def sample_readme_text() -> str:
    return f"""# Zigux third-party archives

This directory is reserved for trusted archive payloads that Lane 05 bootstrap CI
can validate locally before it falls back to network downloads.

## Current pinned Zig archive contract

- target: `{EXPECTED_TARGET}`
- channel: `{EXPECTED_CHANNEL}`
- file: `{EXPECTED_FILE}`
- sha256: `{EXPECTED_SHA}`
- size: `{EXPECTED_SIZE}` bytes

## Validation

- `{EXPECTED_ARCHIVE_COMMAND}`

## Bootstrap order

- Lane 05 bootstrap first reuses and validates `{EXPECTED_FILE}` when that pinned archive is present.
- If the exact archive file is absent but `{EXPECTED_PARTS_DIR}` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.
- Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.
- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards for that local-first archive path.
- `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.
"""


def sample_docs_text() -> str:
    return f"""# Phase 2 Toolchain Bootstrap Notes

## Current direct packet

- `scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` are directly readable on current `master`.
- `third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename `{EXPECTED_FILE}`, digest, size, duplicate-copy boundary, and `{EXPECTED_ARCHIVE_COMMAND}` replay contract explicit beside the policy-driven toolchain packet.
- `.github/workflows/zigux-bootstrap.yml` also derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, and `ZIGUX_ZIG_URL` from `scripts/zigux/zig-toolchain-policy.json`, tries `community-mirrors.txt` before the direct Zig download URL, and reruns `python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"` inside each install attempt.
- `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle before retrying the mirror or direct-download path.
- `scripts/zigux/check-lane05-local-first-archive-workflow.py`, `scripts/zigux/check-lane05-local-archive-readme.py`, and `scripts/zigux/check-lane05-install-zig-archive-verification.py` are the current shipped archive-order, archive-readme, and archive-verification guards.
"""


def sample_workflow_text() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          repo_archive_parts_dir="${repo_archive_path}.parts"
          rm -f "$archive_path" "$mirror_file"
          rm -rf "$extract_root"
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            download_success=1
          fi
          if try_download "$ZIGUX_ZIG_URL"; then
            download_success=1
          fi
      - name: Self-test current Lane 05 local-first archive checker
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
      - name: Check current Lane 05 local-first archive packet
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
      - name: Self-test current Lane 05 local archive README checker
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test
      - name: Check current Lane 05 local archive README packet
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
      - name: Self-test current Lane 05 install-zig archive verification checker
        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test
      - name: Check current Lane 05 install-zig archive verification packet
        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py
      - name: Self-test current staged pinned Zig archive helper
        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
"""


def sample_local_first_checker_text() -> str:
    return """THIRD_PARTY_PATH = "- 'third_party/**'"
README_SELF_TEST_STEP = "- name: Self-test current Lane 05 local archive README checker"
README_CHECK_STEP = "- name: Check current Lane 05 local archive README packet"
PHASE2_TOOL_MANIFEST_SELF_TEST_STEP = "- name: Self-test current Phase 2 tool manifest checker"
"""


def sample_readme_checker_text() -> str:
    return """README_PATH = Path("third_party/README.md")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
EXPECTED_ARCHIVE_SIZES = {
    "x86_64-linux": 58_159_088,
}
required_markers = [
    "community-mirrors.txt",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
]
"""


def sample_install_checker_text() -> str:
    return """INSTALL_ZIG = Path("scripts/zigux/install-zig.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)
print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    write_text(root / README_PATH, sample_readme_text())
    write_text(root / DOCS_PATH, sample_docs_text())
    write_text(root / WORKFLOW_PATH, sample_workflow_text())
    write_text(root / POLICY_PATH, sample_policy_json())
    write_text(root / LOCAL_FIRST_CHECKER_PATH, sample_local_first_checker_text())
    write_text(root / README_CHECKER_PATH, sample_readme_checker_text())
    write_text(root / INSTALL_CHECKER_PATH, sample_install_checker_text())


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"missing self-test marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane18_third_party_packet_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert validate_root(root) == (
            len(README_MARKERS),
            len(DOCS_MARKERS),
            len(WORKFLOW_MARKERS),
            len(COMPANION_PATHS),
        )
        case_count += 1

        write_sample_root(root)
        readme_path = root / README_PATH
        readme_path.write_text(
            replace_once(
                readme_path.read_text(encoding="utf-8"),
                "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
                "falls back to mirrors later",
            ),
            encoding="utf-8",
        )
        try:
            validate_root(root)
        except ValueError as exc:
            assert str(README_PATH) in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected README marker failure")

        write_sample_root(root)
        docs_path = root / DOCS_PATH
        docs_path.write_text(
            replace_once(
                docs_path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-lane05-local-archive-readme.py`",
                "`scripts/zigux/check-lane05-other-helper.py`",
            ),
            encoding="utf-8",
        )
        try:
            validate_root(root)
        except ValueError as exc:
            assert str(DOCS_PATH) in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected docs marker failure")

        write_sample_root(root)
        workflow_path = root / WORKFLOW_PATH
        workflow_path.write_text(
            replace_once(
                workflow_path.read_text(encoding="utf-8"),
                'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
                'if try_download "$ZIGUX_ZIG_URL"; then',
            ),
            encoding="utf-8",
        )
        try:
            validate_root(root)
        except ValueError as exc:
            assert str(WORKFLOW_PATH) in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected workflow order failure")

        write_sample_root(root)
        policy_path = root / POLICY_PATH
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["archive_sha256"][EXPECTED_TARGET] = "0" * 64
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            validate_root(root)
        except ValueError as exc:
            assert str(POLICY_PATH) in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected policy drift failure")

        write_sample_root(root)
        checker_path = root / README_CHECKER_PATH
        checker_path.write_text(
            replace_once(
                checker_path.read_text(encoding="utf-8"),
                "community-mirrors.txt",
                "mirror-list.txt",
            ),
            encoding="utf-8",
        )
        try:
            validate_root(root)
        except ValueError as exc:
            assert str(README_CHECKER_PATH) in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected checker marker failure")

    print("PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live Phase 2 third_party toolchain packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for positive replay and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        readme_count, docs_count, workflow_count, companion_count = validate_root(args.root.resolve())
    except ValueError as exc:
        print("PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET=fail")
        print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_ROOT={args.root.resolve()}")
        print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_NOTE={exc}")
        return 1

    print("PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_ROOT={args.root.resolve()}")
    print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_README_MARKER_COUNT={readme_count}")
    print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_DOCS_MARKER_COUNT={docs_count}")
    print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_WORKFLOW_MARKER_COUNT={workflow_count}")
    print(f"PHASE2_THIRD_PARTY_TOOLCHAIN_PACKET_COMPANION_PATH_COUNT={companion_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
