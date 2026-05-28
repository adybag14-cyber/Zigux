#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 pinned installer packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_NOTES = ROOT / "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = ROOT / "scripts/zigux/README.md"
WORKFLOW = ROOT / ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux/Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts/zigux/zig-toolchain-policy.json"
TOOLCHAIN_CHECKER = ROOT / "scripts/zigux/check-zig-toolchain.py"
INSTALLER = ROOT / "scripts/zigux/install-zig.py"

NOTES_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master`",
    "`third_party/README.md` is directly readable on current `master`",
    "`community-mirrors.txt`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "pinned Zig toolchain guard explicit",
)

WORKFLOW_SETUP_MARKERS = (
    "mirror_file=\".zig-toolchain/community-mirrors.txt\"",
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "--parts-dir \"$repo_archive_parts_dir\"",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"",
    "python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"",
    "curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
)

WORKFLOW_STEP_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
)

MAKEFILE_MARKERS = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
)

MAKEFILE_VARIABLE_MARKERS = (
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c ",
    "[\"upgrade_policy\"][\"archive_target_scope\"][0]",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def load_min_version(",
    "def load_pinned_channel(",
    "def resolve_policy_archive(",
    "def validate_policy_archive(",
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive-target"',
    'parser.add_argument("--allow-missing"',
)

INSTALLER_MARKERS = (
    "INDEX_URL = 'https://ziglang.org/download/index.json'",
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "def parse_retry_after(",
    "def retry_delay_seconds(",
    "def copy_url_to_file_with_curl(",
    "def load_index(",
    "def resolve_target(",
    "def extract_archive(",
    "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_STATUS=resolved')",
    "parser.add_argument('--resolve-only'",
    "parser.add_argument('--self-test'",
)

EXPECTED_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGETS = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def count_marker_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def collect_marker_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_marker_occurrences(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def validate_policy(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if not isinstance(channel, str) or not channel:
        issues.append(("INVALID_POLICY", "channel"))
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append(("INVALID_POLICY", "minimum_version"))
    if channel != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY", f"channel={channel!r}"))
    if minimum_version != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY", f"minimum_version={minimum_version!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_TARGETS:
            issues.append(("INVALID_POLICY", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))
        for target, digest in archive_sha256.items():
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                issues.append(("INVALID_POLICY", f"archive_sha256[{target}]"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY", "upgrade_policy"))
    else:
        if upgrade_policy.get("channel_minimum_lockstep") is not True:
            issues.append(("INVALID_POLICY", "channel_minimum_lockstep"))
        if upgrade_policy.get("archive_target_scope") != EXPECTED_TARGETS:
            issues.append(("INVALID_POLICY", "archive_target_scope"))
        if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
            issues.append(("INVALID_POLICY", "required_make_routes"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, PHASE2_NOTES)),
            NOTES_MARKERS,
            "MISSING_NOTES_MARKERS",
            "DUPLICATE_NOTES_MARKERS",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, SCRIPTS_README)),
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKERS",
            "DUPLICATE_SCRIPTS_README_MARKERS",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_SETUP_MARKERS,
            "MISSING_WORKFLOW_SETUP_MARKERS",
            "DUPLICATE_WORKFLOW_SETUP_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_STEP_LINES,
            "MISSING_WORKFLOW_STEP_LINES",
            "DUPLICATE_WORKFLOW_STEP_LINES",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_MARKERS,
            "MISSING_MAKEFILE_MARKERS",
            "DUPLICATE_MAKEFILE_MARKERS",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_VARIABLE_MARKERS,
            "MISSING_MAKEFILE_VARIABLE_MARKERS",
            "DUPLICATE_MAKEFILE_VARIABLE_MARKERS",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, TOOLCHAIN_CHECKER)),
            TOOLCHAIN_CHECKER_MARKERS,
            "MISSING_TOOLCHAIN_CHECKER_MARKERS",
            "DUPLICATE_TOOLCHAIN_CHECKER_MARKERS",
        )
    )
    issues.extend(
        collect_marker_issues(
            read_text(resolve_path(root, INSTALLER)),
            INSTALLER_MARKERS,
            "MISSING_INSTALLER_MARKERS",
            "DUPLICATE_INSTALLER_MARKERS",
        )
    )

    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
    else:
        issues.extend(validate_policy(payload))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_INSTALLER_PACKET=fail")
    print("INVALID_PHASE2_TOOLCHAIN_INSTALLER_PACKET_START")
    for code, values in grouped.items():
        for value in values:
            print(f"{code}:{value}")
    print("INVALID_PHASE2_TOOLCHAIN_INSTALLER_PACKET_END")
    return 1


def build_current_like_root(root: Path) -> None:
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(["# notes", *NOTES_MARKERS]) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(["# scripts/zigux", *SCRIPTS_README_MARKERS]) + "\n")
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(["name: zigux-bootstrap", *WORKFLOW_SETUP_MARKERS, *WORKFLOW_STEP_LINES]) + "\n",
    )
    write_text(
        resolve_path(root, MAKEFILE),
        "\n".join([*MAKEFILE_VARIABLE_MARKERS, "phase2-toolchain:", *MAKEFILE_MARKERS]) + "\n",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_CHECKER),
        "\n".join(["#!/usr/bin/env python3", *TOOLCHAIN_CHECKER_MARKERS]) + "\n",
    )
    write_text(
        resolve_path(root, INSTALLER),
        "\n".join(["#!/usr/bin/env python3", *INSTALLER_MARKERS]) + "\n",
    )
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_TARGETS,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_installer_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_current_like_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for path, marker, expected in (
            (PHASE2_NOTES, NOTES_MARKERS[0], ("MISSING_NOTES_MARKERS", NOTES_MARKERS[0])),
            (SCRIPTS_README, SCRIPTS_README_MARKERS[0], ("MISSING_SCRIPTS_README_MARKERS", SCRIPTS_README_MARKERS[0])),
            (WORKFLOW, WORKFLOW_SETUP_MARKERS[0], ("MISSING_WORKFLOW_SETUP_MARKERS", WORKFLOW_SETUP_MARKERS[0])),
            (MAKEFILE, MAKEFILE_MARKERS[0], ("MISSING_MAKEFILE_MARKERS", MAKEFILE_MARKERS[0])),
            (MAKEFILE, MAKEFILE_VARIABLE_MARKERS[0], ("MISSING_MAKEFILE_VARIABLE_MARKERS", MAKEFILE_VARIABLE_MARKERS[0])),
            (TOOLCHAIN_CHECKER, TOOLCHAIN_CHECKER_MARKERS[0], ("MISSING_TOOLCHAIN_CHECKER_MARKERS", TOOLCHAIN_CHECKER_MARKERS[0])),
            (INSTALLER, INSTALLER_MARKERS[0], ("MISSING_INSTALLER_MARKERS", INSTALLER_MARKERS[0])),
        ):
            build_current_like_root(root)
            target = resolve_path(root, path)
            target.write_text(replace_once(target.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert expected in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        workflow = resolve_path(root, WORKFLOW)
        workflow.write_text(
            replace_exact_line(workflow.read_text(encoding="utf-8"), WORKFLOW_STEP_LINES[0]),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_STEP_LINES", WORKFLOW_STEP_LINES[0]) in collect_issues(root)
        checks_run += 1

        for path, marker, expected in (
            (PHASE2_NOTES, NOTES_MARKERS[0], ("DUPLICATE_NOTES_MARKERS", f"{NOTES_MARKERS[0]}:count=2")),
            (SCRIPTS_README, SCRIPTS_README_MARKERS[0], ("DUPLICATE_SCRIPTS_README_MARKERS", f"{SCRIPTS_README_MARKERS[0]}:count=2")),
            (WORKFLOW, WORKFLOW_SETUP_MARKERS[0], ("DUPLICATE_WORKFLOW_SETUP_MARKERS", f"{WORKFLOW_SETUP_MARKERS[0]}:count=2")),
            (MAKEFILE, MAKEFILE_MARKERS[0], ("DUPLICATE_MAKEFILE_MARKERS", f"{MAKEFILE_MARKERS[0]}:count=2")),
            (MAKEFILE, MAKEFILE_VARIABLE_MARKERS[0], ("DUPLICATE_MAKEFILE_VARIABLE_MARKERS", f"{MAKEFILE_VARIABLE_MARKERS[0]}:count=2")),
            (TOOLCHAIN_CHECKER, TOOLCHAIN_CHECKER_MARKERS[0], ("DUPLICATE_TOOLCHAIN_CHECKER_MARKERS", f"{TOOLCHAIN_CHECKER_MARKERS[0]}:count=2")),
            (INSTALLER, INSTALLER_MARKERS[0], ("DUPLICATE_INSTALLER_MARKERS", f"{INSTALLER_MARKERS[0]}:count=2")),
        ):
            build_current_like_root(root)
            target = resolve_path(root, path)
            target.write_text(replace_once(target.read_text(encoding="utf-8"), marker, marker + marker), encoding="utf-8")
            assert expected in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        workflow = resolve_path(root, WORKFLOW)
        workflow.write_text(
            duplicate_exact_line(workflow.read_text(encoding="utf-8"), WORKFLOW_STEP_LINES[0]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_STEP_LINES", f"{WORKFLOW_STEP_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        policy_cases = (
            (lambda payload: payload.__setitem__("phase", "Phase 3"), ("INVALID_POLICY", "phase='Phase 3'")),
            (lambda payload: payload.__setitem__("channel", "0.17.0-dev.90+abcdef"), ("INVALID_POLICY", "channel='0.17.0-dev.90+abcdef'")),
            (lambda payload: payload["upgrade_policy"].__setitem__("archive_target_scope", ["aarch64-linux"]), ("INVALID_POLICY", "archive_target_scope")),
            (lambda payload: payload["upgrade_policy"].__setitem__("required_make_routes", ["phase2-toolchain"]), ("INVALID_POLICY", "required_make_routes")),
        )
        for mutator, expected in policy_cases:
            build_current_like_root(root)
            policy_path = resolve_path(root, TOOLCHAIN_POLICY)
            payload = json.loads(policy_path.read_text(encoding="utf-8"))
            mutator(payload)
            policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert expected in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_POLICY_JSON" for code, _ in issues)
        checks_run += 1

        for path in (
            PHASE2_NOTES,
            SCRIPTS_README,
            WORKFLOW,
            MAKEFILE,
            TOOLCHAIN_CHECKER,
            INSTALLER,
            TOOLCHAIN_POLICY,
        ):
            build_current_like_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    print("PHASE2_TOOLCHAIN_INSTALLER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current directly readable Phase 2 pinned installer packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_INSTALLER_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_PACKET_NOTES_MARKER_COUNT={len(NOTES_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_PACKET_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_PACKET_WORKFLOW_SETUP_MARKER_COUNT={len(WORKFLOW_SETUP_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_PACKET_WORKFLOW_STEP_LINE_COUNT={len(WORKFLOW_STEP_LINES)}")
    print(f"PHASE2_TOOLCHAIN_INSTALLER_PACKET_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())