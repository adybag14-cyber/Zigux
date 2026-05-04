#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    override = os.environ.get("ZIGUX_PHASE1_ROOT")
    if override:
        return Path(override)
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = repo_root()

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-bitmap-validator-anchors.py",
    "scripts/zigux/check-phase1-find-bit-validator-anchors.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-validation-route-inventory.py",
    "scripts/zigux/check-phase1-parity.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/tests/README.md",
]

DOCS_ROOT_LINES = {
    "docs_root_phase1_closure_packet_count": (
        "Documentation/zigux/README.md",
        "- `Documentation/zigux/phase1-closure.md` remains the dedicated closure packet for the bounded host-side `tools/lib/*.zig` helper tranche, and `zigux/tests/fixtures/phase1_helper_manifest.json` plus `zigux/tests/phase1_helpers.zig` keep the closed helper inventory and parity-backed replay surface explicit from the docs root.",
        1,
    ),
    "docs_root_phase1_entrypoints_count": (
        "Documentation/zigux/README.md",
        "- `python3 scripts/zigux/validate-phase1.py`, `python3 scripts/zigux/validate-phase1-closure.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` are the current validator-first and replay entrypoints for that bounded host-side helper packet.",
        1,
    ),
}

CHECKLIST_LINES = {
    "review_checklist_phase1_packet_count": (
        "Documentation/zigux/review-checklist.md",
        "- if the change touches the closed Phase 1 host-helper packet, do `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` still agree on the same closed helper inventory, validator-first replay path, and fail-closed checker stack?",
        1,
    ),
}

SCRIPTS_ROOT_LINES = {
    "scripts_root_phase1_validator_first_count": (
        "scripts/zigux/README.md",
        "- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.",
        1,
    ),
    "scripts_root_phase1_packet_alignment_count": (
        "scripts/zigux/README.md",
        "- `Documentation/zigux/README.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` stay aligned as the bounded Phase 1 helper inventory and validator-first replay packet.",
        1,
    ),
    "scripts_root_phase1_review_hooks_count": (
        "scripts/zigux/README.md",
        "- `check-phase1-bitmap-validator-anchors.py --self-test`, `check-phase1-bitmap-validator-anchors.py`, `check-phase1-find-bit-validator-anchors.py --self-test`, `check-phase1-find-bit-validator-anchors.py`, `check-phase1-route-summary-counts.py --self-test`, `check-phase1-route-summary-counts.py`, `check-phase1-validation-route-inventory.py --self-test`, `check-phase1-validation-route-inventory.py`, `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.",
        1,
    ),
}

TESTS_ROOT_LINES = {
    "tests_root_phase1_checker_stack_count": (
        "zigux/tests/README.md",
        "- keep the closed Phase 1 host-helper packet reviewable through `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` so the tests root names the same validator-first replay and fail-closed checker stack as the docs root, scripts root, workflow, and Makefile surfaces.",
        1,
    ),
}

WORKFLOW_LINES = {
    "workflow_phase1_validate_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1.py --self-test",
        1,
    ),
    "workflow_phase1_validate_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1.py",
        1,
    ),
    "workflow_phase1_bitmap_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
        1,
    ),
    "workflow_phase1_bitmap_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py",
        1,
    ),
    "workflow_phase1_find_bit_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
        1,
    ),
    "workflow_phase1_find_bit_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py",
        1,
    ),
    "workflow_phase1_route_summary_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        1,
    ),
    "workflow_phase1_route_summary_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        1,
    ),
    "workflow_phase1_route_inventory_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test",
        1,
    ),
    "workflow_phase1_route_inventory_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-validation-route-inventory.py",
        1,
    ),
    "workflow_phase1_parity_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
        1,
    ),
    "workflow_phase1_parity_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-parity.py",
        1,
    ),
    "workflow_phase1_bench_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        1,
    ),
    "workflow_phase1_bench_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-bench.py",
        1,
    ),
    "workflow_phase1_closure_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        1,
    ),
    "workflow_phase1_closure_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        1,
    ),
}

MAKEFILE_LINES = {
    "makefile_phase1_bitmap_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test",
        1,
    ),
    "makefile_phase1_bitmap_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bitmap-validator-anchors.py",
        1,
    ),
    "makefile_phase1_find_bit_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test",
        1,
    ),
    "makefile_phase1_find_bit_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-find-bit-validator-anchors.py",
        1,
    ),
    "makefile_phase1_route_summary_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        1,
    ),
    "makefile_phase1_route_summary_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
        1,
    ),
    "makefile_phase1_route_inventory_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-validation-route-inventory.py --self-test",
        1,
    ),
    "makefile_phase1_route_inventory_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-validation-route-inventory.py",
        1,
    ),
    "makefile_phase1_validate_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py --self-test",
        1,
    ),
    "makefile_phase1_validate_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1.py",
        1,
    ),
    "makefile_phase1_parity_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py --self-test",
        1,
    ),
    "makefile_phase1_parity_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-parity.py",
        1,
    ),
    "makefile_phase1_bench_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py --self-test",
        1,
    ),
    "makefile_phase1_bench_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-bench.py",
        1,
    ),
    "makefile_phase1_closure_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py --self-test",
        1,
    ),
    "makefile_phase1_closure_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase1-closure.py",
        1,
    ),
}

ALL_TARGETS = {}
ALL_TARGETS.update(DOCS_ROOT_LINES)
ALL_TARGETS.update(CHECKLIST_LINES)
ALL_TARGETS.update(SCRIPTS_ROOT_LINES)
ALL_TARGETS.update(TESTS_ROOT_LINES)
ALL_TARGETS.update(WORKFLOW_LINES)
ALL_TARGETS.update(MAKEFILE_LINES)


def read_lines(rel: str) -> list[str]:
    return (ROOT / rel).read_text(encoding="utf-8").splitlines()


def exact_count(lines: list[str], marker: str) -> int:
    return sum(1 for line in lines if line.strip() == marker)


def fail(items: list[str]) -> int:
    print("PHASE1_VALIDATION_ROUTE_INVENTORY=fail")
    print("MISSING_PHASE1_VALIDATION_ROUTE_INVENTORY_START")
    for item in items:
        print(item)
    print("MISSING_PHASE1_VALIDATION_ROUTE_INVENTORY_END")
    return 1


def main() -> int:
    missing_files = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    if missing_files:
        return fail([f"missing_file:{rel}" for rel in missing_files])

    cached_lines: dict[str, list[str]] = {}
    missing: list[str] = []

    for label, (rel, marker, expected_count) in ALL_TARGETS.items():
        lines = cached_lines.setdefault(rel, read_lines(rel))
        actual_count = exact_count(lines, marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    if missing:
        return fail(missing)

    print("PHASE1_VALIDATION_ROUTE_INVENTORY=pass")
    print(f"PHASE1_VALIDATION_ROUTE_INVENTORY_TARGET_COUNT={len(ALL_TARGETS)}")
    print(f"PHASE1_VALIDATION_ROUTE_INVENTORY_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(entries: list[str]) -> str:
    return "\n".join(entries) + "\n"


def expect_failure(script: Path, root: Path, expected: str) -> None:
    env = dict(os.environ)
    env["ZIGUX_PHASE1_ROOT"] = str(root)
    result = subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True, check=False)
    output = result.stdout + result.stderr
    if result.returncode == 0:
        raise SystemExit(f"phase1-validation-route-inventory-self-test:expected_failure:{expected}")
    if expected not in output:
        raise SystemExit(
            "phase1-validation-route-inventory-self-test:missing_expected_output:"
            f"expected={expected!r}:actual={output!r}"
        )


def expect_missing_and_duplicate(
    script: Path,
    root: Path,
    rel: str,
    baseline_entries: list[str],
    label: str,
    marker: str,
) -> None:
    path = root / rel
    write(path, fixture_text([entry for entry in baseline_entries if entry != marker]))
    expect_failure(script, root, f"{label}:expected=1:actual=0")
    write(path, fixture_text(baseline_entries + [marker]))
    expect_failure(script, root, f"{label}:expected=1:actual=2")
    write(path, fixture_text(baseline_entries))


def self_test() -> int:
    docs_entries = [entry[1] for entry in DOCS_ROOT_LINES.values()]
    checklist_entries = [entry[1] for entry in CHECKLIST_LINES.values()]
    scripts_entries = [entry[1] for entry in SCRIPTS_ROOT_LINES.values()]
    tests_entries = [entry[1] for entry in TESTS_ROOT_LINES.values()]
    workflow_entries = [entry[1] for entry in WORKFLOW_LINES.values()]
    makefile_entries = [entry[1] for entry in MAKEFILE_LINES.values()]

    target_cases = [
        *[(entry[0], docs_entries, label, entry[1]) for label, entry in DOCS_ROOT_LINES.items()],
        *[(entry[0], checklist_entries, label, entry[1]) for label, entry in CHECKLIST_LINES.items()],
        *[(entry[0], scripts_entries, label, entry[1]) for label, entry in SCRIPTS_ROOT_LINES.items()],
        *[(entry[0], tests_entries, label, entry[1]) for label, entry in TESTS_ROOT_LINES.items()],
        *[(entry[0], workflow_entries, label, entry[1]) for label, entry in WORKFLOW_LINES.items()],
        *[(entry[0], makefile_entries, label, entry[1]) for label, entry in MAKEFILE_LINES.items()],
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-validation-route-inventory-") as tmp:
        root = Path(tmp)
        script = root / "scripts/zigux/check-phase1-validation-route-inventory.py"
        for rel in REQUIRED_FILES:
            write(root / rel, "// fixture\n")
        write(script, Path(__file__).read_text(encoding="utf-8"))

        write(root / "Documentation/zigux/README.md", fixture_text(docs_entries))
        write(root / "Documentation/zigux/review-checklist.md", fixture_text(checklist_entries))
        write(root / "scripts/zigux/README.md", fixture_text(scripts_entries))
        write(root / "zigux/tests/README.md", fixture_text(tests_entries))
        write(root / ".github/workflows/zigux-bootstrap.yml", fixture_text(workflow_entries))
        write(root / "zigux/Makefile", fixture_text(makefile_entries))
        write(
            root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
            fixture_text(["phase1 ledger fixture"]),
        )

        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, str(script)], env)
        if code != 0:
            print("PHASE1_VALIDATION_ROUTE_INVENTORY_SELF_TEST=fail")
            return 1

        total_cases = 1
        for rel, baseline_entries, label, marker in target_cases:
            expect_missing_and_duplicate(script, root, rel, baseline_entries, label, marker)
            total_cases += 2

        (root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").unlink()
        expect_failure(script, root, "missing_file:zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
        total_cases += 1

        missing_file_cases = [
            ("Documentation/zigux/review-checklist.md", fixture_text(checklist_entries)),
            ("scripts/zigux/README.md", fixture_text(scripts_entries)),
            ("scripts/zigux/validate-phase1.py", "// fixture\n"),
            ("zigux/tests/README.md", fixture_text(tests_entries)),
            ("zigux/Makefile", fixture_text(makefile_entries)),
        ]
        for rel, baseline in missing_file_cases:
            path = root / rel
            path.unlink()
            expect_failure(script, root, f"missing_file:{rel}")
            write(path, baseline)
            total_cases += 1

    print("PHASE1_VALIDATION_ROUTE_INVENTORY_SELF_TEST=pass")
    print(f"PHASE1_VALIDATION_ROUTE_INVENTORY_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
