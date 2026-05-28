#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain-checker packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md"
TESTS_README = "zigux/tests/README.md"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
TOOLCHAIN_CHECKER = "scripts/zigux/check-zig-toolchain.py"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

SURFACE_PATHS = (
    BOOTSTRAP_NOTES,
    REVIEW_CHECKLIST,
    TESTS_README,
    WORKFLOW,
    MAKEFILE,
    TOOLCHAIN_CHECKER,
    POLICY,
)

SHARED_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

BOOTSTRAP_ONLY_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`third_party/README.md`",
)

TESTS_ONLY_MARKERS = (
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
    "run: make -C zigux phase2",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
)

TOOLCHAIN_CHECKER_MARKERS = (
    'parser.add_argument("--allow-missing"',
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    'parser.add_argument("--zig"',
    "def resolve_zig_executable(",
    "def resolve_policy_archive(",
    "def validate_policy_archive(",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": [
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    ],
}

EXPECTED_SELF_TEST_CASE_COUNT = 18


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(root: Path, rel: str) -> str:
    path = resolve(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = resolve(root, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
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

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))
    if payload.get("channel") != EXPECTED_POLICY["channel"]:
        issues.append(("INVALID_POLICY", f"channel={payload.get('channel')!r}"))
    if payload.get("minimum_version") != EXPECTED_POLICY["minimum_version"]:
        issues.append(("INVALID_POLICY", f"minimum_version={payload.get('minimum_version')!r}"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY", "upgrade_policy"))
        return issues

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("INVALID_POLICY", "channel_minimum_lockstep"))
    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("INVALID_POLICY", "archive_target_scope"))
    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(("INVALID_POLICY", "required_make_routes"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    elif list(archive_sha256.keys()) != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("INVALID_POLICY", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in SURFACE_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_SURFACE_PATH", rel))
    if issues:
        return issues

    bootstrap_notes = read_text(root, BOOTSTRAP_NOTES)
    review = read_text(root, REVIEW_CHECKLIST)
    tests = read_text(root, TESTS_README)
    workflow = read_text(root, WORKFLOW)
    makefile = read_text(root, MAKEFILE)
    checker = read_text(root, TOOLCHAIN_CHECKER)

    issues.extend(collect_marker_issues(bootstrap_notes, SHARED_MARKERS, "MISSING_BOOTSTRAP_MARKER"))
    issues.extend(collect_marker_issues(bootstrap_notes, BOOTSTRAP_ONLY_MARKERS, "MISSING_BOOTSTRAP_MARKER"))
    issues.extend(collect_marker_issues(review, SHARED_MARKERS, "MISSING_REVIEW_MARKER"))
    issues.extend(collect_marker_issues(tests, SHARED_MARKERS, "MISSING_TESTS_MARKER"))
    issues.extend(collect_marker_issues(tests, TESTS_ONLY_MARKERS, "MISSING_TESTS_MARKER"))
    issues.extend(
        collect_exact_line_issues(workflow, WORKFLOW_LINES, "MISSING_WORKFLOW_LINE", "DUPLICATE_WORKFLOW_LINE")
    )
    issues.extend(
        collect_exact_line_issues(makefile, MAKEFILE_LINES, "MISSING_MAKEFILE_LINE", "DUPLICATE_MAKEFILE_LINE")
    )
    issues.extend(collect_marker_issues(checker, TOOLCHAIN_CHECKER_MARKERS, "MISSING_TOOLCHAIN_CHECKER_MARKER"))

    try:
        payload = json.loads(read_text(root, POLICY))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
    else:
        issues.extend(validate_policy(payload))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    shared_text = "\n".join(f"- {marker}" for marker in SHARED_MARKERS)
    bootstrap_only_text = "\n".join(f"- {marker}" for marker in BOOTSTRAP_ONLY_MARKERS)
    tests_only_text = "\n".join(f"- {marker}" for marker in TESTS_ONLY_MARKERS)
    write_text(
        root,
        BOOTSTRAP_NOTES,
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "## Current direct packet",
                "",
                shared_text,
                bootstrap_only_text,
                "",
            )
        )
        + "\n",
    )
    write_text(root, REVIEW_CHECKLIST, "\n".join(("# Review Checklist", "", shared_text, "")) + "\n")
    write_text(
        root,
        TESTS_README,
        "\n".join(("# zigux/tests", "", shared_text, tests_only_text, "")) + "\n",
    )
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")
    write_text(root, MAKEFILE, "\n".join(("PYTHON ?= python3", "PHASE2_SCRIPT_ROOT := ../scripts/zigux", "", *MAKEFILE_LINES)) + "\n")
    write_text(root, TOOLCHAIN_CHECKER, "\n".join(("#!/usr/bin/env python3", *TOOLCHAIN_CHECKER_MARKERS)) + "\n")
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": EXPECTED_POLICY["phase"],
                "channel": EXPECTED_POLICY["channel"],
                "minimum_version": EXPECTED_POLICY["minimum_version"],
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_POLICY["archive_target_scope"],
                    "required_make_routes": EXPECTED_POLICY["required_make_routes"],
                },
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> None:
    build_sample_root(root)


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_checker_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, BOOTSTRAP_NOTES, read_text(root, BOOTSTRAP_NOTES).replace(SHARED_MARKERS[0], "", 1))
        assert ("MISSING_BOOTSTRAP_MARKER", SHARED_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, BOOTSTRAP_NOTES, read_text(root, BOOTSTRAP_NOTES).replace(BOOTSTRAP_ONLY_MARKERS[-1], "", 1))
        assert ("MISSING_BOOTSTRAP_MARKER", BOOTSTRAP_ONLY_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, REVIEW_CHECKLIST, read_text(root, REVIEW_CHECKLIST).replace(SHARED_MARKERS[-1], "", 1))
        assert ("MISSING_REVIEW_MARKER", SHARED_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, TESTS_README, read_text(root, TESTS_README).replace(TESTS_ONLY_MARKERS[-1], "", 1))
        assert ("MISSING_TESTS_MARKER", TESTS_ONLY_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[-1]))
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[-1]))
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[0]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, TOOLCHAIN_CHECKER, read_text(root, TOOLCHAIN_CHECKER).replace(TOOLCHAIN_CHECKER_MARKERS[-1], "", 1))
        assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", TOOLCHAIN_CHECKER_MARKERS[-1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, POLICY))
        payload["phase"] = "Phase 3"
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_POLICY", "phase='Phase 3'") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, POLICY))
        payload["minimum_version"] = "0.16.0"
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_POLICY", "minimum_version='0.16.0'") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, POLICY))
        payload["upgrade_policy"]["channel_minimum_lockstep"] = False
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_POLICY", "channel_minimum_lockstep") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, POLICY))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_POLICY", "archive_target_scope") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        payload = json.loads(read_text(root, POLICY))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_text(root, POLICY, json.dumps(payload, indent=2) + "\n")
        assert ("INVALID_POLICY", "required_make_routes") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, POLICY, "{not-json}\n")
        assert any(code == "INVALID_POLICY_JSON" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        resolve(root, TOOLCHAIN_CHECKER).unlink()
        assert ("MISSING_SURFACE_PATH", TOOLCHAIN_CHECKER) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        resolve(root, WORKFLOW).unlink()
        assert ("MISSING_SURFACE_PATH", WORKFLOW) in collect_issues(root)
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 toolchain-checker packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_TOOLCHAIN_CHECKER_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_CHECKER_MARKER_COUNT={len(SHARED_MARKERS) + len(BOOTSTRAP_ONLY_MARKERS) + len(TESTS_ONLY_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_CHECKER_REQUIRED_STEP_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_TOOLCHAIN_CHECKER_REQUIRED_ROUTE_COUNT={len(EXPECTED_POLICY['required_make_routes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
