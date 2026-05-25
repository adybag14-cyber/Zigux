#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"

EXPECTED_VALIDATORS = (
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "python3 scripts/zigux/check-kconfig-bridge.py",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "python3 scripts/zigux/check-phase2-cross.py --self-test",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "python3 scripts/zigux/check-phase2-required-make-routes.py",
    "python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "zig test scripts/zigux/genksyms.zig",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "python3 scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "python3 scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_SHARED_MAKE_ROUTES = (
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

REQUIRED_CLOSURE_MARKERS = (
    "`python3 scripts/zigux/validate-phase2.py`",
    "`python3 scripts/zigux/validate-phase2-closure.py --self-test`",
    "`python3 scripts/zigux/validate-phase2-closure.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/validate-phase2.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig: phase2-toolchain",
    "phase2-cross:",
    "phase2-genksyms: phase2-toolchain",
    "phase2-fixdep: phase2-toolchain",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)


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


def extract_packet(text: str, prefix: str) -> tuple[str, ...]:
    for line in text.splitlines():
        stripped = line.strip()
        candidate = stripped
        if candidate.startswith("- "):
            candidate = candidate[2:].strip()
        if candidate.startswith("`") and candidate.endswith("`"):
            candidate = candidate[1:-1]
        if candidate.startswith(prefix):
            payload = candidate[len(prefix) :]
            if not payload:
                return ()
            return tuple(part.strip() for part in payload.split(","))
    return ()


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(root / PHASE2_CLOSURE.relative_to(ROOT))
    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    validator_packet = extract_packet(closure_text, "PHASE2_CLOSURE_VALIDATORS=")
    if validator_packet != EXPECTED_VALIDATORS:
        issues.append(("PHASE2_CLOSURE_VALIDATORS_MISMATCH", repr(validator_packet)))

    route_packet = extract_packet(closure_text, "PHASE2_SHARED_MAKE_ROUTES=")
    if route_packet != EXPECTED_SHARED_MAKE_ROUTES:
        issues.append(("PHASE2_SHARED_MAKE_ROUTES_MISMATCH", repr(route_packet)))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_VALIDATOR_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    closure_lines = [
        "# Phase 2 Closure",
        "",
        "## Closure Validation",
        "",
        *[f"- {marker}" for marker in REQUIRED_CLOSURE_MARKERS],
        "",
        "- PHASE2_CLOSURE_VALIDATORS=" + ",".join(EXPECTED_VALIDATORS),
        "- PHASE2_SHARED_MAKE_ROUTES=" + ",".join(EXPECTED_SHARED_MAKE_ROUTES),
        "",
    ]
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "",
        *REQUIRED_MAKEFILE_LINES,
    ]
    write_text(root / PHASE2_CLOSURE.relative_to(ROOT), "\n".join(closure_lines))
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(workflow_lines) + "\n")
    write_text(root / MAKEFILE.relative_to(ROOT), "\n".join(makefile_lines) + "\n")


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validator_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = root / PHASE2_CLOSURE.relative_to(ROOT)
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), "`python3 scripts/zigux/validate-phase2-closure.py`"),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_MARKER", "`python3 scripts/zigux/validate-phase2-closure.py`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE.relative_to(ROOT)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "make -C zigux phase2-fixdep,make -C zigux phase2-validate",
                "make -C zigux phase2-validate",
            ),
            encoding="utf-8",
        )
        assert any(code == "PHASE2_SHARED_MAKE_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE.relative_to(ROOT)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test,python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
                "python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
            ),
            encoding="utf-8",
        )
        assert any(code == "PHASE2_CLOSURE_VALIDATORS_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        workflow_path = root / WORKFLOW.relative_to(ROOT)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), "run: make -C zigux phase2-validate", "run: make -C zigux phase2"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", "run: make -C zigux phase2-validate") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = root / MAKEFILE.relative_to(ROOT)
        makefile_path.write_text(
            replace_exact_line(
                makefile_path.read_text(encoding="utf-8"),
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
                "# removed",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the current Phase 2 closure validator and shared make-route packet aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATOR_PACKET=pass")
    print(f"PHASE2_CLOSURE_VALIDATOR_COUNT={len(EXPECTED_VALIDATORS)}")
    print(f"PHASE2_CLOSURE_SHARED_ROUTE_COUNT={len(EXPECTED_SHARED_MAKE_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
