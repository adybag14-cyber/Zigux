#!/usr/bin/env python3
"""Guard the live Phase 2 review-checklist toolchain packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
REVIEW = "Documentation/zigux/review-checklist.md"
BOOTSTRAP = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
SCRIPTS = "scripts/zigux/README.md"
TESTS = "zigux/tests/README.md"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
TOOLCHAIN = "scripts/zigux/check-zig-toolchain.py"
PIN_SCOPE = "scripts/zigux/check-phase2-toolchain-pin-scope.py"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
CROSS = "scripts/zigux/check-phase2-cross.py"
THIRD_PARTY = "third_party/README.md"
CROSS_TARGETS = "zigux/tests/fixtures/phase2_cross_targets.json"

CHANNEL = "0.17.0-dev.87+9b177a7d2"
ARCHIVE_TARGET = "x86_64-linux"
ARCHIVE_PATH = f"third_party/zig-{ARCHIVE_TARGET}-{CHANNEL}.tar.xz"
REQUIRED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

REVIEW_MARKERS = (
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive {ARCHIVE_PATH} --archive-target {ARCHIVE_TARGET}`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    f"`{CROSS_TARGETS}`",
    *tuple(f"`make -C zigux {route}`" for route in (*REQUIRED_ROUTES, "phase2")),
)

BOOTSTRAP_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    f"`{THIRD_PARTY}`",
    f"`{CROSS_TARGETS}`",
    *tuple(f"`make -C zigux {route}`" for route in (*REQUIRED_ROUTES, "phase2")),
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    f"`{THIRD_PARTY}`",
    *tuple(f"`make -C zigux {route}`" for route in (*REQUIRED_ROUTES, "phase2")),
)

TESTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    f"`{THIRD_PARTY}`",
    f"`{ARCHIVE_PATH}`",
    f"`{CROSS_TARGETS}`",
    *tuple(f"`make -C zigux {route}`" for route in (*REQUIRED_ROUTES, "phase2")),
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    *tuple(f"run: make -C zigux {route}" for route in (*REQUIRED_ROUTES, "phase2")),
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-genksyms:",
    "phase2-fixdep:",
)

TOOLCHAIN_MARKERS = (
    'parser.add_argument("--allow-missing"',
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    'parser.add_argument("--zig"',
    "def emit_policy_summary(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
)

SURFACE_PATHS = (
    POLICY,
    TOOLCHAIN,
    PIN_SCOPE,
    INSTALL_ZIG,
    CROSS,
    THIRD_PARTY,
    CROSS_TARGETS,
    REVIEW,
    BOOTSTRAP,
    SCRIPTS,
    TESTS,
    WORKFLOW,
    MAKEFILE,
)


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
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


def replace_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def collect_marker_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_line_issues(text: str, markers: tuple[str, ...], missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = json.loads(read_text(resolve(root, POLICY)))
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]
    upgrade = payload.get("upgrade_policy")
    if not isinstance(upgrade, dict):
        return [("INVALID_UPGRADE_POLICY", type(upgrade).__name__)]
    issues: list[tuple[str, str]] = []
    if payload.get("channel") != CHANNEL:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))
    if payload.get("minimum_version") != CHANNEL:
        issues.append(("POLICY_MINIMUM_MISMATCH", repr(payload.get("minimum_version"))))
    if upgrade.get("archive_target_scope") != [ARCHIVE_TARGET]:
        issues.append(("POLICY_ARCHIVE_SCOPE_MISMATCH", repr(upgrade.get("archive_target_scope"))))
    if upgrade.get("required_make_routes") != list(REQUIRED_ROUTES):
        issues.append(("POLICY_ROUTE_LIST_MISMATCH", repr(upgrade.get("required_make_routes"))))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    review = read_text(resolve(root, REVIEW))
    bootstrap = read_text(resolve(root, BOOTSTRAP))
    scripts = read_text(resolve(root, SCRIPTS))
    tests = read_text(resolve(root, TESTS))
    workflow = read_text(resolve(root, WORKFLOW))
    makefile = read_text(resolve(root, MAKEFILE))
    toolchain = read_text(resolve(root, TOOLCHAIN))

    issues.extend(collect_marker_issues(review, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_marker_issues(bootstrap, BOOTSTRAP_MARKERS, "MISSING_BOOTSTRAP_MARKERS"))
    issues.extend(collect_marker_issues(scripts, SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_marker_issues(tests, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_line_issues(workflow, WORKFLOW_LINES, "MISSING_WORKFLOW_LINES", "DUPLICATE_WORKFLOW_LINES"))
    issues.extend(collect_line_issues(makefile, MAKEFILE_LINES, "MISSING_MAKEFILE_LINES", "DUPLICATE_MAKEFILE_LINES"))
    issues.extend(collect_marker_issues(toolchain, TOOLCHAIN_MARKERS, "MISSING_TOOLCHAIN_MARKERS"))

    for rel in SURFACE_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_SURFACE_PATHS", rel))

    issues.extend(collect_policy_issues(root))
    return issues


def build_sample_root(root: Path) -> None:
    route_markers = tuple(f"`make -C zigux {route}`" for route in (*REQUIRED_ROUTES, "phase2"))
    write_text(resolve(root, REVIEW), "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write_text(resolve(root, BOOTSTRAP), "\n".join(["# bootstrap", *BOOTSTRAP_MARKERS]) + "\n")
    write_text(resolve(root, SCRIPTS), "\n".join(["# scripts", *SCRIPTS_MARKERS]) + "\n")
    write_text(resolve(root, TESTS), "\n".join(["# tests", *TESTS_MARKERS]) + "\n")
    write_text(resolve(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve(root, TOOLCHAIN), "\n".join(["#!/usr/bin/env python3", *TOOLCHAIN_MARKERS]) + "\n")
    write_text(resolve(root, PIN_SCOPE), "present\n")
    write_text(resolve(root, INSTALL_ZIG), "present\n")
    write_text(resolve(root, CROSS), "present\n")
    write_text(resolve(root, THIRD_PARTY), f"# third_party\n\n`{ARCHIVE_PATH}`\n")
    write_text(resolve(root, CROSS_TARGETS), "{\n  \"targets\": []\n}\n")
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": CHANNEL,
                "minimum_version": CHANNEL,
                "archive_sha256": {ARCHIVE_TARGET: "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [ARCHIVE_TARGET],
                    "required_make_routes": list(REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    _ = route_markers


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_review_checklist_packet_") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        marker_cases = (
            (REVIEW, REVIEW_MARKERS[0], "MISSING_REVIEW_MARKERS"),
            (REVIEW, REVIEW_MARKERS[-1], "MISSING_REVIEW_MARKERS"),
            (BOOTSTRAP, BOOTSTRAP_MARKERS[0], "MISSING_BOOTSTRAP_MARKERS"),
            (BOOTSTRAP, BOOTSTRAP_MARKERS[-1], "MISSING_BOOTSTRAP_MARKERS"),
            (SCRIPTS, SCRIPTS_MARKERS[0], "MISSING_SCRIPTS_MARKERS"),
            (SCRIPTS, SCRIPTS_MARKERS[-1], "MISSING_SCRIPTS_MARKERS"),
            (TESTS, TESTS_MARKERS[0], "MISSING_TESTS_MARKERS"),
            (TESTS, TESTS_MARKERS[-1], "MISSING_TESTS_MARKERS"),
            (TOOLCHAIN, TOOLCHAIN_MARKERS[0], "MISSING_TOOLCHAIN_MARKERS"),
            (TOOLCHAIN, TOOLCHAIN_MARKERS[-1], "MISSING_TOOLCHAIN_MARKERS"),
        )
        for rel, marker, code in marker_cases:
            build_sample_root(root)
            path = resolve(root, rel)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (code, marker) in collect_issues(root)
            checks += 1

        line_cases = (
            (WORKFLOW, WORKFLOW_LINES[0], "MISSING_WORKFLOW_LINES"),
            (WORKFLOW, WORKFLOW_LINES[-1], "MISSING_WORKFLOW_LINES"),
            (MAKEFILE, MAKEFILE_LINES[0], "MISSING_MAKEFILE_LINES"),
            (MAKEFILE, MAKEFILE_LINES[-1], "MISSING_MAKEFILE_LINES"),
        )
        for rel, marker, code in line_cases:
            build_sample_root(root)
            path = resolve(root, rel)
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert (code, marker) in collect_issues(root)
            checks += 1

        duplicate_cases = (
            (WORKFLOW, WORKFLOW_LINES[0], "DUPLICATE_WORKFLOW_LINES"),
            (MAKEFILE, MAKEFILE_LINES[0], "DUPLICATE_MAKEFILE_LINES"),
        )
        for rel, marker, code in duplicate_cases:
            build_sample_root(root)
            path = resolve(root, rel)
            text = path.read_text(encoding="utf-8")
            path.write_text(replace_exact_line(text, marker, marker + "\n" + marker), encoding="utf-8")
            assert (code, f"{marker}:count=2") in collect_issues(root)
            checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["channel"] = "0.17.0"
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_CHANNEL_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "POLICY_ROUTE_LIST_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        resolve(root, CROSS_TARGETS).unlink()
        assert ("MISSING_SURFACE_PATHS", CROSS_TARGETS) in collect_issues(root)
        checks += 1

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the live Phase 2 review-checklist toolchain packet stays aligned.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_BOOTSTRAP_MARKER_COUNT={len(BOOTSTRAP_MARKERS)}")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_REQUIRED_ROUTE_COUNT={len(REQUIRED_ROUTES) + 1}")
    print(f"PHASE2_REVIEW_CHECKLIST_TOOLCHAIN_PACKET_SURFACE_PATH_COUNT={len(SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
