#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = "scripts/zigux/validate-phase2.py"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    VALIDATOR,
    WORKFLOW,
    MAKEFILE,
    POLICY,
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/validate-phase2-closure.py",
)

EXPECTED_POLICY_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

VALIDATOR_REQUIRED_MARKERS = (
    'MAKEFILE = "zigux/Makefile"',
    'WORKFLOW = ".github/workflows/zigux-bootstrap.yml"',
    '"scripts/zigux/check-phase2-kbuild-routes.py"',
    '"scripts/zigux/check-phase2-cross.py"',
    '"scripts/zigux/check-phase2-cross-selftest-alignment.py"',
    '"scripts/zigux/check-phase2-required-make-routes.py"',
    '"scripts/zigux/check-phase2-docs-shared-reminder.py"',
    '"scripts/zigux/check-phase2-tool-manifest.py"',
    '"scripts/zigux/check-phase2-artifact-tools-manifest.py"',
    '"scripts/zigux/check-phase2-toolchain-pinning.py"',
    '"scripts/zigux/check-phase2-toolchain-pin-scope.py"',
    '"scripts/zigux/check-genksyms-bridge.py"',
    '"scripts/zigux/check-phase2-genksyms-selftest-alignment.py"',
    '"scripts/zigux/check-phase2-fixdep-gate.py"',
    '"scripts/zigux/check-fixdep-diff.py"',
    '"run: make -C zigux phase2-toolchain"',
    '"run: make -C zigux phase2-tools"',
    '"run: make -C zigux phase2-kconfig"',
    '"run: make -C zigux phase2-cross"',
    '"run: make -C zigux phase2-genksyms"',
    '"run: make -C zigux phase2-fixdep"',
    '"run: make -C zigux phase2-validate"',
    '".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"',
    '"phase2-toolchain:"',
    '"phase2-tools:"',
    '"phase2-kconfig:"',
    '"phase2-cross:"',
    '"phase2-genksyms:"',
    '"phase2-fixdep:"',
    '"phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py"',
    '"$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py"',
)

WORKFLOW_REQUIRED_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_REQUIRED_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-kconfig:",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-fixdep-gate.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-fixdep-diff.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)

REQUIRED_PHASE2_PHONY_TARGETS = set(
    "phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2".split()
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str, replacement: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith(".PHONY:"):
            continue
        _, suffix = stripped.split(":", 1)
        targets.update(token for token in suffix.strip().split() if token)
    return targets


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    validator_text = read_text(root, VALIDATOR)
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)
    policy_text = read_text(root, POLICY)

    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
        return issues

    required_make_routes = policy.get("upgrade_policy", {}).get("required_make_routes")
    if required_make_routes != list(EXPECTED_POLICY_ROUTES):
        issues.append(
            (
                "POLICY_ROUTE_MISMATCH",
                ",".join(required_make_routes) if isinstance(required_make_routes, list) else repr(required_make_routes),
            )
        )

    for marker in VALIDATOR_REQUIRED_MARKERS:
        count = validator_text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count={count}"))

    for marker in WORKFLOW_REQUIRED_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    phony_targets = phony_targets_present(makefile_text)
    missing_phony = sorted(REQUIRED_PHASE2_PHONY_TARGETS - phony_targets)
    for target in missing_phony:
        issues.append(("MISSING_MAKEFILE_PHONY_TARGET", target))

    for marker in MAKEFILE_REQUIRED_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_PHASE2_VALIDATE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    validator_lines = [
        "from pathlib import Path",
        'MAKEFILE = "zigux/Makefile"',
        'WORKFLOW = ".github/workflows/zigux-bootstrap.yml"',
        'POLICY = "scripts/zigux/zig-toolchain-policy.json"',
        "REQUIRED_PATHS = (",
    ]
    validator_lines.extend(f"    {marker}," for marker in VALIDATOR_REQUIRED_MARKERS[2:15])
    validator_lines.extend(
        (
            ")",
            "REQUIRED_WORKFLOW_LINES = (",
        )
    )
    validator_lines.extend(f"    {marker}," for marker in VALIDATOR_REQUIRED_MARKERS[15:22])
    validator_lines.extend(
        (
            ")",
            'REQUIRED_PHASE2_PHONY_LINE = ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"',
            "REQUIRED_MAKEFILE_LINES = (",
        )
    )
    validator_lines.extend(f"    {marker}," for marker in VALIDATOR_REQUIRED_MARKERS[23:])
    validator_lines.append(")")
    write_text(root, VALIDATOR, "\n".join(validator_lines) + "\n")

    write_text(
        root,
        WORKFLOW,
        "\n".join(("name: zigux-bootstrap", *WORKFLOW_REQUIRED_LINES)) + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2",
                *MAKEFILE_REQUIRED_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "upgrade_policy": {
                    "required_make_routes": list(EXPECTED_POLICY_ROUTES),
                }
            },
            indent=2,
        )
        + "\n",
    )

    for rel in REQUIRED_PATHS[4:]:
        write_text(root, rel, "present\n")


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="zigux_lane03_phase2_validate_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        (root / "scripts/zigux/check-phase2-tool-manifest.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/check-phase2-tool-manifest.py") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["required_make_routes"] = [
            "phase2-toolchain",
            "phase2-tools",
            "phase2-kconfig",
            "phase2-cross",
            "phase2-validate",
        ]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert (
            "POLICY_ROUTE_MISMATCH",
            "phase2-toolchain,phase2-tools,phase2-kconfig,phase2-cross,phase2-validate",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            VALIDATOR,
            replace_once(
                read_text(root, VALIDATOR),
                '"run: make -C zigux phase2-genksyms"',
                '"run: make -C zigux phase2-genksyms-missing"',
            ),
        )
        assert ('MISSING_VALIDATOR_MARKER', '"run: make -C zigux phase2-genksyms"') in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_once(
                read_text(root, WORKFLOW),
                "run: make -C zigux phase2-fixdep",
                "run: make -C zigux phase2-fixdep-missing",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", "run: make -C zigux phase2-fixdep") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_once(
                read_text(root, MAKEFILE),
                "phase2-genksyms:",
                "phase2-genksyms-disabled:",
            ),
        )
        assert ("MISSING_MAKEFILE_LINE", "phase2-genksyms:") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_once(
                read_text(root, MAKEFILE),
                "phase2-fixdep",
                "phase2-fixdep-disabled",
            ),
        )
        assert ("MISSING_MAKEFILE_PHONY_TARGET", "phase2-fixdep") in collect_issues(root)
        checks += 1

    print("LANE03_PHASE2_VALIDATE_SELF_TEST=pass")
    print(f"LANE03_PHASE2_VALIDATE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current validate-phase2 packet stays aligned with the Lane 03 toolchain routes."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PHASE2_VALIDATE=pass")
    print(f"LANE03_PHASE2_VALIDATE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_PHASE2_VALIDATE_VALIDATOR_MARKER_COUNT={len(VALIDATOR_REQUIRED_MARKERS)}")
    print(f"LANE03_PHASE2_VALIDATE_WORKFLOW_LINE_COUNT={len(WORKFLOW_REQUIRED_LINES)}")
    print(f"LANE03_PHASE2_VALIDATE_MAKEFILE_LINE_COUNT={len(MAKEFILE_REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
