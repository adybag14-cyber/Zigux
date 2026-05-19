#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pin-scope packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"

DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "pinned archive-integrity replay",
    "pinned Zig toolchain",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2`",
    "same pinned toolchain",
)

TESTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "pinned `x86_64-linux` bootstrap archive note",
    "repo-local `.zig-toolchain` fallback reused",
)

BOOTSTRAP_MARKERS = (
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "pinned-archive integrity paths",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
)

MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def load_min_version(",
    "def load_pinned_channel(",
    "def iter_repo_local_zig_candidates(",
    "def resolve_zig_executable(",
    "def is_executable_file(",
    "def normalize_explicit_archive_path(",
    "def describe_invalid_explicit_archive_path(",
    "def validate_policy_archive(",
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive-target"',
    'add_search_root(parent / ".zig-toolchain")',
    "if not os.access(normalized, os.X_OK):",
    "if is_executable_file(candidate):",
    "if path.name != expected_filename:",
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}")',
    "resolved = archive_path or normalize_explicit_archive_path(explicit_archive)",
    "return explicit_target, normalize_explicit_archive_path(explicit_archive) if explicit_archive is not None else None",
    'expect_raises(lambda: normalize_explicit_zig_path(str(nonexec_zig)), "explicit zig path is not executable")',
    'os.environ["HOME"] = str(root)',
    'resolve_policy_archive("~/archive-under-home.tar.xz", "x86_64-linux", root=root, policy_path=policy_path)',
    'explicit_archive="~/archive-under-home.tar.xz"',
    'validate_policy_archive(renamed_archive_path, "x86_64-linux", policy_path=policy_path)',
    'describe_invalid_explicit_archive_path(explicit_archive_dir)',
    'parser.add_argument("--allow-missing"',
)

EXPECTED_PHASE = "Phase 2"
EXPECTED_TARGETS = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = ["phase2-toolchain", "phase2-validate"]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(DOCS_ROOT_MARKERS)
    + len(REVIEW_MARKERS)
    + len(TESTS_MARKERS)
    + len(BOOTSTRAP_MARKERS)
    + len(WORKFLOW_MARKERS)
    + len(WORKFLOW_MARKERS)
    + len(MAKEFILE_MARKERS)
    + len(MAKEFILE_MARKERS)
    + len(TOOLCHAIN_CHECKER_MARKERS)
    + 13
    + 8
)


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


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
    if isinstance(channel, str) and isinstance(minimum_version, str) and channel != minimum_version:
        issues.append(("INVALID_POLICY", "channel_minimum_version_mismatch"))

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
        collect_missing_markers(
            read_text(resolve_path(root, DOCS_ROOT_README)),
            DOCS_ROOT_MARKERS,
            "MISSING_DOCS_ROOT_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, REVIEW_CHECKLIST)),
            REVIEW_MARKERS,
            "MISSING_REVIEW_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TESTS_README)),
            TESTS_MARKERS,
            "MISSING_TESTS_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, BOOTSTRAP_NOTES)),
            BOOTSTRAP_MARKERS,
            "MISSING_BOOTSTRAP_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_MARKERS,
            "MISSING_WORKFLOW_MARKERS",
            "DUPLICATE_WORKFLOW_MARKERS",
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
            read_text(resolve_path(root, TOOLCHAIN_CHECKER)),
            TOOLCHAIN_CHECKER_MARKERS,
            "MISSING_TOOLCHAIN_CHECKER_MARKERS",
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

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=fail")
    print("INVALID_PHASE2_TOOLCHAIN_PIN_SCOPE_START")
    for code, values in grouped.items():
        for value in values:
            print(f"{code}:{value}")
    print("INVALID_PHASE2_TOOLCHAIN_PIN_SCOPE_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_ROOT_README), "\n".join(["# docs", *DOCS_ROOT_MARKERS]) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(["# tests", *TESTS_MARKERS]) + "\n")
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(["# bootstrap", *BOOTSTRAP_MARKERS]) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(WORKFLOW_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_CHECKER),
        "\n".join(["#!/usr/bin/env python3", *TOOLCHAIN_CHECKER_MARKERS]) + "\n",
    )
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
                    "archive_target_scope": EXPECTED_TARGETS,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def assert_policy_issue(root: Path, mutator, expected_issue: tuple[str, str]) -> None:
    path = resolve_path(root, TOOLCHAIN_POLICY)
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    assert expected_issue in collect_issues(root)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pin_scope_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in DOCS_ROOT_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_ROOT_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_DOCS_ROOT_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in REVIEW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, REVIEW_CHECKLIST)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_REVIEW_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in TESTS_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TESTS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TESTS_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in BOOTSTRAP_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_MARKERS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_MARKERS", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TOOLCHAIN_CHECKER)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TOOLCHAIN_CHECKER_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        policy_cases = (
            (lambda payload: payload.__setitem__("phase", "Phase 3"), ("INVALID_POLICY", "phase='Phase 3'")),
            (lambda payload: payload.__setitem__("channel", ""), ("INVALID_POLICY", "channel")),
            (lambda payload: payload.__setitem__("minimum_version", ""), ("INVALID_POLICY", "minimum_version")),
            (
                lambda payload: payload.__setitem__("minimum_version", "0.16.0"),
                ("INVALID_POLICY", "channel_minimum_version_mismatch"),
            ),
            (lambda payload: payload.__setitem__("archive_sha256", "broken"), ("INVALID_POLICY", "archive_sha256")),
            (
                lambda payload: payload.__setitem__("archive_sha256", {"aarch64-linux": "3" * 64}),
                ("INVALID_POLICY", "archive_sha256_keys=['aarch64-linux']"),
            ),
            (
                lambda payload: payload.__setitem__("archive_sha256", {"x86_64-linux": "abc"}),
                ("INVALID_POLICY", "archive_sha256[x86_64-linux]"),
            ),
            (lambda payload: payload.__setitem__("upgrade_policy", "broken"), ("INVALID_POLICY", "upgrade_policy")),
            (
                lambda payload: payload["upgrade_policy"].__setitem__("channel_minimum_lockstep", False),
                ("INVALID_POLICY", "channel_minimum_lockstep"),
            ),
            (
                lambda payload: payload["upgrade_policy"].__setitem__("archive_target_scope", ["aarch64-linux"]),
                ("INVALID_POLICY", "archive_target_scope"),
            ),
            (
                lambda payload: payload["upgrade_policy"].__setitem__("required_make_routes", ["phase2-toolchain"]),
                ("INVALID_POLICY", "required_make_routes"),
            ),
        )

        for mutator, expected_issue in policy_cases:
            build_self_test_root(root)
            assert_policy_issue(root, mutator, expected_issue)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("[]\n", encoding="utf-8")
        assert ("INVALID_POLICY", "expected JSON object") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text("{not-json}\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_POLICY_JSON" for code, _ in issues)
        checks_run += 1

        for path in (
            DOCS_ROOT_README,
            REVIEW_CHECKLIST,
            TESTS_README,
            BOOTSTRAP_NOTES,
            WORKFLOW,
            MAKEFILE,
            TOOLCHAIN_CHECKER,
            TOOLCHAIN_POLICY,
        ):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the current directly readable Phase 2 toolchain pin-scope packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_PIN_SCOPE=pass")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_TESTS_MARKER_COUNT={len(TESTS_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PIN_SCOPE_MAKEFILE_MARKER_COUNT={len(MAKEFILE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
