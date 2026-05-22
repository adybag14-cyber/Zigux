#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 bootstrap installer packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

NOTES_MARKERS = (
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "the pinned-channel, pinned-archive integrity, local-first archive workflow, third_party README contract, installer, toolchain-pinning, pin-scope, kbuild-route, tests-root reminder, direct cross-route, cross-selftest alignment, required-make-route, docs-shared-reminder, manifest, artifact-support, genksyms bridge, kconfig bridge, fixdep governance and parity packet",
    "Keep future Phase 2 follow-up inside one current packet surface at a time: toolchain pinning, toolchain pin-scope alignment, installer-path truthfulness",
)

REVIEW_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "installer helper",
    "direct cross-route surfaces explicit beside the shipped toolchain and kbuild reminder packet",
)

TESTS_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
)

WORKFLOW_LINES = (
    "- name: Self-test current Lane 05 local archive README checker",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "- name: Check current Lane 05 local archive README packet",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "- name: Self-test current Zig installer helper",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "- name: Self-test current Phase 2 fixdep gate checker",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "phase2: phase2-validate",
)

INSTALL_ZIG_MARKERS = (
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "def copy_url_to_file_with_curl(",
    "def copy_url_to_file(",
    "def load_index(",
    "def resolve_target(",
    "def extract_archive(",
    "def append_github_path(",
    'parser.add_argument("--resolve-only"',
    'parser.add_argument("--self-test"',
    "print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')",
    "print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
)

EXPECTED_PHASE = "Phase 2"
EXPECTED_TARGET_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = ["phase2-toolchain", "phase2-validate", "phase2-cross"]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(NOTES_MARKERS)
    + len(REVIEW_MARKERS)
    + len(SCRIPTS_MARKERS)
    + len(TESTS_MARKERS)
    + len(WORKFLOW_LINES)
    + len(WORKFLOW_LINES)
    + len(MAKEFILE_MARKERS)
    + len(MAKEFILE_MARKERS)
    + len(INSTALL_ZIG_MARKERS)
    + 8
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_policy_issues(payload: object) -> list[tuple[str, str]]:
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    issues: list[tuple[str, str]] = []
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))

    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    if not isinstance(channel, str) or not channel:
        issues.append(("INVALID_POLICY", "channel"))
    if not isinstance(minimum_version, str) or not minimum_version:
        issues.append(("INVALID_POLICY", "minimum_version"))
    if isinstance(channel, str) and isinstance(minimum_version, str) and channel != minimum_version:
        issues.append(("INVALID_POLICY", "channel_minimum_version_mismatch"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_TARGET_SCOPE:
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
        if upgrade_policy.get("archive_target_scope") != EXPECTED_TARGET_SCOPE:
            issues.append(("INVALID_POLICY", "archive_target_scope"))
        if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
            issues.append(("INVALID_POLICY", "required_make_routes"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(collect_missing_markers(read_text(resolve_path(root, BOOTSTRAP_NOTES)), NOTES_MARKERS, "MISSING_NOTES_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, REVIEW_CHECKLIST)), REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, SCRIPTS_README)), SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_missing_markers(read_text(resolve_path(root, TESTS_README)), TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINES",
            "DUPLICATE_WORKFLOW_LINES",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_MARKERS,
            "MISSING_MAKEFILE_MARKERS",
            "DUPLICATE_MAKEFILE_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, INSTALL_ZIG)),
            INSTALL_ZIG_MARKERS,
            "MISSING_INSTALLER_MARKERS",
        )
    )

    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
    else:
        issues.extend(collect_policy_issues(payload))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    print("PHASE2_BOOTSTRAP_INSTALLER_PACKET=fail")
    for code, value in issues:
        print(f"{code}:{value}")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "# Notes\n" + "\n".join(f"- {marker}" for marker in NOTES_MARKERS) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "# Review\n" + "\n".join(f"- {marker}" for marker in REVIEW_MARKERS) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "# Scripts\n" + "\n".join(f"- {marker}" for marker in SCRIPTS_MARKERS) + "\n")
    write_text(resolve_path(root, TESTS_README), "# Tests\n" + "\n".join(f"- {marker}" for marker in TESTS_MARKERS) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(resolve_path(root, INSTALL_ZIG), "#!/usr/bin/env python3\n" + "\n".join(INSTALL_ZIG_MARKERS) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_TARGET_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def mutate_policy(root: Path, mutator) -> None:
    path = resolve_path(root, TOOLCHAIN_POLICY)
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_installer_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker_set, path_ref, code in (
            (NOTES_MARKERS, BOOTSTRAP_NOTES, "MISSING_NOTES_MARKERS"),
            (REVIEW_MARKERS, REVIEW_CHECKLIST, "MISSING_REVIEW_MARKERS"),
            (SCRIPTS_MARKERS, SCRIPTS_README, "MISSING_SCRIPTS_MARKERS"),
            (TESTS_MARKERS, TESTS_README, "MISSING_TESTS_MARKERS"),
        ):
            for marker in marker_set:
                build_self_test_root(root)
                path = resolve_path(root, path_ref)
                path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
                assert (code, marker) in collect_issues(root)
                checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINES", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINES", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_MARKERS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in INSTALL_ZIG_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, INSTALL_ZIG)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_INSTALLER_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        policy_cases = (
            (lambda payload: payload.__setitem__("phase", "Phase 3"), ("INVALID_POLICY", "phase='Phase 3'")),
            (lambda payload: payload.__setitem__("channel", ""), ("INVALID_POLICY", "channel")),
            (lambda payload: payload.__setitem__("minimum_version", ""), ("INVALID_POLICY", "minimum_version")),
            (lambda payload: payload.__setitem__("minimum_version", "0.16.0"), ("INVALID_POLICY", "channel_minimum_version_mismatch")),
            (lambda payload: payload.__setitem__("archive_sha256", "broken"), ("INVALID_POLICY", "archive_sha256")),
            (lambda payload: payload.__setitem__("archive_sha256", {"aarch64-linux": "3" * 64}), ("INVALID_POLICY", "archive_sha256_keys=['aarch64-linux']")),
            (lambda payload: payload.__setitem__("upgrade_policy", "broken"), ("INVALID_POLICY", "upgrade_policy")),
            (lambda payload: payload["upgrade_policy"].__setitem__("required_make_routes", ["phase2-toolchain"]), ("INVALID_POLICY", "required_make_routes")),
        )
        for mutator, expected_issue in policy_cases:
            build_self_test_root(root)
            mutate_policy(root, mutator)
            assert expected_issue in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_INSTALLER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_INSTALLER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(target: Path) -> None:
    build_self_test_root(target.resolve())
    print(f"PHASE2_BOOTSTRAP_INSTALLER_PACKET_SAMPLE_ROOT={target.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current directly readable Phase 2 bootstrap installer packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample repository root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_INSTALLER_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_INSTALLER_PACKET_NOTES_MARKER_COUNT={len(NOTES_MARKERS)}")
    print(f"PHASE2_BOOTSTRAP_INSTALLER_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_INSTALLER_PACKET_INSTALLER_MARKER_COUNT={len(INSTALL_ZIG_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
