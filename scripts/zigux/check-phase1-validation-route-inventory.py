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
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


ROOT = repo_root()

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-tests-root-review-companion.md",
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

TARGETS = {
    "docs_root_phase1_closure_packet_count": (
        "Documentation/zigux/README.md",
        "- `Documentation/zigux/phase1-closure.md` remains the dedicated closure packet for the bounded host-side `tools/lib/*.zig` helper tranche, and `zigux/tests/fixtures/phase1_helper_manifest.json` plus `zigux/tests/phase1_helpers.zig` keep the closed helper inventory and parity-backed replay surface explicit from the docs root.",
        1,
    ),
    "docs_root_phase1_companion_count": (
        "Documentation/zigux/README.md",
        "- `Documentation/zigux/phase1-tests-root-review-companion.md` keeps the tests-root ownership view, shared reviewer surface, and fail-closed checker stack explicit for that same closed Phase 1 helper packet, so the docs root does not leave the narrower tests-root review path implicit behind the broader closure note.",
        1,
    ),
    "docs_root_phase1_entrypoints_count": (
        "Documentation/zigux/README.md",
        "- `python3 scripts/zigux/validate-phase1.py`, `python3 scripts/zigux/validate-phase1-closure.py`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` are the current validator-first and replay entrypoints for that bounded host-side helper packet.",
        1,
    ),
    "review_checklist_phase1_packet_count": (
        "Documentation/zigux/review-checklist.md",
        "- if the change touches the closed Phase 1 host-helper packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-tests-root-review-companion.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` still agree on the same closed helper inventory, validator-first replay path, and fail-closed checker stack?",
        1,
    ),
    "scripts_root_phase1_validator_first_count": (
        "scripts/zigux/README.md",
        "- `validate-phase1.py` is the validator-first entrypoint for the closed host-helper packet around `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/string.zig`, and `tools/lib/rbtree.zig` plus the bounded supporting helpers and committed `zigux/tests/fixtures/phase1_helpers.json` corpus.",
        1,
    ),
    "scripts_root_phase1_packet_alignment_count": (
        "scripts/zigux/README.md",
        "- `Documentation/zigux/README.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-tests-root-review-companion.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` stay aligned as the bounded Phase 1 helper inventory and validator-first replay packet.",
        1,
    ),
    "scripts_root_phase1_review_hooks_count": (
        "scripts/zigux/README.md",
        "- `check-phase1-bitmap-validator-anchors.py --self-test`, `check-phase1-bitmap-validator-anchors.py`, `check-phase1-find-bit-validator-anchors.py --self-test`, `check-phase1-find-bit-validator-anchors.py`, `check-phase1-route-summary-counts.py --self-test`, `check-phase1-route-summary-counts.py`, `check-phase1-validation-route-inventory.py --self-test`, `check-phase1-validation-route-inventory.py`, `check-phase1-parity.py --self-test`, `check-phase1-parity.py`, `check-phase1-bench.py --self-test`, `check-phase1-bench.py`, `validate-phase1-closure.py --self-test`, and `validate-phase1-closure.py` are the bounded fail-closed review hooks around that same closed Phase 1 helper tranche.",
        1,
    ),
    "tests_root_phase1_checker_stack_count": (
        "zigux/tests/README.md",
        "- keep the closed Phase 1 host-helper packet reviewable through `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `scripts/zigux/check-phase1-route-summary-counts.py`, `scripts/zigux/check-phase1-validation-route-inventory.py`, `scripts/zigux/check-phase1-parity.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/validate-phase1-closure.py`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `zigux/tests/phase1_helpers.zig`, and `zigux/tests/phase1_bench.zig` so the tests root names the same validator-first replay and fail-closed checker stack as the docs root, scripts root, workflow, and Makefile surfaces.",
        1,
    ),
    "companion_shared_surface_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `Documentation/zigux/phase1-tests-root-review-companion.md`",
        1,
    ),
    "companion_validate_phase1_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/validate-phase1.py --self-test`",
        1,
    ),
    "companion_route_inventory_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test`",
        1,
    ),
    "companion_validate_phase1_closure_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/validate-phase1-closure.py --self-test`",
        1,
    ),
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
    for label, (rel, marker, expected_count) in TARGETS.items():
        lines = cached_lines.setdefault(rel, read_lines(rel))
        actual_count = exact_count(lines, marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    if missing:
        return fail(missing)

    print("PHASE1_VALIDATION_ROUTE_INVENTORY=pass")
    print(f"PHASE1_VALIDATION_ROUTE_INVENTORY_TARGET_COUNT={len(TARGETS)}")
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
    docs_entries = [TARGETS[label][1] for label in (
        "docs_root_phase1_closure_packet_count",
        "docs_root_phase1_companion_count",
        "docs_root_phase1_entrypoints_count",
    )]
    checklist_entries = [TARGETS["review_checklist_phase1_packet_count"][1]]
    scripts_entries = [TARGETS[label][1] for label in (
        "scripts_root_phase1_validator_first_count",
        "scripts_root_phase1_packet_alignment_count",
        "scripts_root_phase1_review_hooks_count",
    )]
    tests_entries = [TARGETS["tests_root_phase1_checker_stack_count"][1]]
    companion_entries = [TARGETS[label][1] for label in (
        "companion_shared_surface_count",
        "companion_validate_phase1_self_test_count",
        "companion_route_inventory_self_test_count",
        "companion_validate_phase1_closure_self_test_count",
    )]
    workflow_entries = [TARGETS[label][1] for label in TARGETS if label.startswith("workflow_")]
    makefile_entries = [TARGETS[label][1] for label in TARGETS if label.startswith("makefile_")]

    baseline_by_file = {
        "Documentation/zigux/README.md": docs_entries,
        "Documentation/zigux/review-checklist.md": checklist_entries,
        "Documentation/zigux/phase1-tests-root-review-companion.md": companion_entries,
        "scripts/zigux/README.md": scripts_entries,
        "zigux/tests/README.md": tests_entries,
        ".github/workflows/zigux-bootstrap.yml": workflow_entries,
        "zigux/Makefile": makefile_entries,
    }

    with tempfile.TemporaryDirectory(prefix="phase1-validation-route-inventory-") as tmp:
        root = Path(tmp)
        script = root / "scripts/zigux/check-phase1-validation-route-inventory.py"
        for rel in REQUIRED_FILES:
            write(root / rel, "// fixture\n")
        write(script, Path(__file__).read_text(encoding="utf-8"))
        for rel, entries in baseline_by_file.items():
            write(root / rel, fixture_text(entries))
        write(root / "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md", "phase1 ledger fixture\n")

        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        baseline = subprocess.run([sys.executable, str(script)], env=env, capture_output=True, text=True, check=False)
        if baseline.returncode != 0:
            raise SystemExit(f"phase1-validation-route-inventory-self-test:baseline:{baseline.stdout or baseline.stderr}")

        total_cases = 1
        for label, (rel, marker, _expected) in TARGETS.items():
            expect_missing_and_duplicate(script, root, rel, baseline_by_file[rel], label, marker)
            total_cases += 2

        missing_file_cases = {
            "Documentation/zigux/README.md": fixture_text(docs_entries),
            "Documentation/zigux/phase1-tests-root-review-companion.md": fixture_text(companion_entries),
            "Documentation/zigux/review-checklist.md": fixture_text(checklist_entries),
            "scripts/zigux/README.md": fixture_text(scripts_entries),
            "scripts/zigux/validate-phase1.py": "// fixture\n",
            "scripts/zigux/check-phase1-bitmap-validator-anchors.py": "// fixture\n",
            "scripts/zigux/check-phase1-find-bit-validator-anchors.py": "// fixture\n",
            "scripts/zigux/check-phase1-route-summary-counts.py": "// fixture\n",
            "scripts/zigux/check-phase1-parity.py": "// fixture\n",
            "scripts/zigux/check-phase1-bench.py": "// fixture\n",
            "scripts/zigux/validate-phase1-closure.py": "// fixture\n",
            ".github/workflows/zigux-bootstrap.yml": fixture_text(workflow_entries),
            "zigux/tests/README.md": fixture_text(tests_entries),
            "zigux/Makefile": fixture_text(makefile_entries),
            "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md": "phase1 ledger fixture\n",
        }
        for rel, baseline_text in missing_file_cases.items():
            path = root / rel
            path.unlink()
            expect_failure(script, root, f"missing_file:{rel}")
            write(path, baseline_text)
            total_cases += 1

    print("PHASE1_VALIDATION_ROUTE_INVENTORY_SELF_TEST=pass")
    print(f"PHASE1_VALIDATION_ROUTE_INVENTORY_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
