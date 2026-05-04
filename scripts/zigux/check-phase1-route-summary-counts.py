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

REQUIRED_MARKERS = {
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
    "docs_root_phase1_companion_checks_count": (
        "Documentation/zigux/README.md",
        "- `python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py`, `python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py`, `python3 scripts/zigux/check-phase1-route-summary-counts.py`, `python3 scripts/zigux/check-phase1-validation-route-inventory.py`, `python3 scripts/zigux/check-phase1-parity.py`, and `python3 scripts/zigux/check-phase1-bench.py` are the dedicated fail-closed companion checks that keep the closed helper inventory, anchor evidence, replay routes, and benchmark packet aligned across the docs root, scripts root, tests root, Makefile, and bootstrap workflow.",
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
}

REQUIRED_ROUTE_LINES = {
    "makefile_phase1_route_summary_self_test_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        1,
    ),
    "makefile_phase1_route_summary_run_count": (
        "zigux/Makefile",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase1-route-summary-counts.py",
        1,
    ),
    "workflow_phase1_route_summary_self_test_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        1,
    ),
    "workflow_phase1_route_summary_run_count": (
        ".github/workflows/zigux-bootstrap.yml",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        1,
    ),
}

COMPANION_ROUTE_LINES = {
    "companion_phase1_validate_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/validate-phase1.py --self-test`",
        1,
    ),
    "companion_phase1_bitmap_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py --self-test`",
        1,
    ),
    "companion_phase1_bitmap_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-bitmap-validator-anchors.py`",
        1,
    ),
    "companion_phase1_find_bit_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py --self-test`",
        1,
    ),
    "companion_phase1_find_bit_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-find-bit-validator-anchors.py`",
        1,
    ),
    "companion_phase1_route_summary_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test`",
        1,
    ),
    "companion_phase1_route_summary_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        1,
    ),
    "companion_phase1_validation_route_inventory_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-validation-route-inventory.py --self-test`",
        1,
    ),
    "companion_phase1_validation_route_inventory_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-validation-route-inventory.py`",
        1,
    ),
    "companion_phase1_parity_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-parity.py --self-test`",
        1,
    ),
    "companion_phase1_parity_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-parity.py`",
        1,
    ),
    "companion_phase1_bench_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-bench.py --self-test`",
        1,
    ),
    "companion_phase1_bench_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/check-phase1-bench.py`",
        1,
    ),
    "companion_phase1_validate_phase1_closure_self_test_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/validate-phase1-closure.py --self-test`",
        1,
    ),
    "companion_phase1_validate_phase1_closure_count": (
        "Documentation/zigux/phase1-tests-root-review-companion.md",
        "- `python3 scripts/zigux/validate-phase1-closure.py`",
        1,
    ),
}

CLOSURE_ROUTE_LINES = {
    "closure_phase1_parity_gate_count": (
        "Documentation/zigux/phase1-closure.md",
        "- `PHASE1_PARITY_GATE=python3 scripts/zigux/check-phase1-parity.py`",
        1,
    ),
    "closure_phase1_parity_self_test_gate_count": (
        "Documentation/zigux/phase1-closure.md",
        "- `PHASE1_PARITY_SELF_TEST_GATE=python3 scripts/zigux/check-phase1-parity.py --self-test`",
        1,
    ),
    "closure_phase1_bench_check_gate_count": (
        "Documentation/zigux/phase1-closure.md",
        "- `PHASE1_BENCH_CHECK_GATE=python3 scripts/zigux/check-phase1-bench.py`",
        1,
    ),
    "closure_phase1_bench_self_test_gate_count": (
        "Documentation/zigux/phase1-closure.md",
        "- `PHASE1_BENCH_SELF_TEST_GATE=python3 scripts/zigux/check-phase1-bench.py --self-test`",
        1,
    ),
    "closure_phase1_closure_gate_count": (
        "Documentation/zigux/phase1-closure.md",
        "- `PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py`",
        1,
    ),
    "closure_phase1_closure_self_test_gate_count": (
        "Documentation/zigux/phase1-closure.md",
        "- `PHASE1_CLOSURE_SELF_TEST_GATE=python3 scripts/zigux/validate-phase1-closure.py --self-test`",
        1,
    ),
}


def read_lines(rel: str) -> list[str]:
    return (ROOT / rel).read_text(encoding="utf-8").splitlines()


def fail(items: list[str]) -> int:
    print("PHASE1_ROUTE_SUMMARY_COUNTS=fail")
    print("MISSING_PHASE1_ROUTE_SUMMARY_COUNTS_START")
    for item in items:
        print(item)
    print("MISSING_PHASE1_ROUTE_SUMMARY_COUNTS_END")
    return 1


def exact_count(lines: list[str], marker: str) -> int:
    return sum(1 for line in lines if line.strip() == marker)


def main() -> int:
    missing: list[str] = []
    cached_lines: dict[str, list[str]] = {}

    for label, (rel, marker, expected_count) in REQUIRED_MARKERS.items():
        path = ROOT / rel
        if not path.exists():
            missing.append(f"{label}:missing_file:{rel}")
            continue
        lines = cached_lines.setdefault(rel, read_lines(rel))
        actual_count = exact_count(lines, marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    for label, (rel, marker, expected_count) in REQUIRED_ROUTE_LINES.items():
        path = ROOT / rel
        if not path.exists():
            missing.append(f"{label}:missing_file:{rel}")
            continue
        lines = cached_lines.setdefault(rel, read_lines(rel))
        actual_count = exact_count(lines, marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    for label, (rel, marker, expected_count) in COMPANION_ROUTE_LINES.items():
        path = ROOT / rel
        if not path.exists():
            missing.append(f"{label}:missing_file:{rel}")
            continue
        lines = cached_lines.setdefault(rel, read_lines(rel))
        actual_count = exact_count(lines, marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    for label, (rel, marker, expected_count) in CLOSURE_ROUTE_LINES.items():
        path = ROOT / rel
        if not path.exists():
            missing.append(f"{label}:missing_file:{rel}")
            continue
        lines = cached_lines.setdefault(rel, read_lines(rel))
        actual_count = exact_count(lines, marker)
        if actual_count != expected_count:
            missing.append(f"{label}:expected={expected_count}:actual={actual_count}")

    if missing:
        return fail(missing)

    print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")
    print(
        "PHASE1_ROUTE_SUMMARY_COUNT_TARGETS="
        f"{len(REQUIRED_MARKERS) + len(REQUIRED_ROUTE_LINES) + len(COMPANION_ROUTE_LINES) + len(CLOSURE_ROUTE_LINES)}"
    )
    return 0


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fixture_text(entries: list[str]) -> str:
    return "\n".join(entries) + "\n"


def expect_failure(script: Path, root: Path, expected: str) -> None:
    env = dict(os.environ)
    env["ZIGUX_PHASE1_ROOT"] = str(root)
    result = subprocess.run(
        [sys.executable, str(script)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        raise SystemExit(f"phase1-route-summary-self-test:expected_failure:{expected}")
    combined_output = result.stdout + result.stderr
    if expected not in combined_output:
        raise SystemExit(
            "phase1-route-summary-self-test:missing_expected_output:"
            f"expected={expected!r}:actual={combined_output!r}"
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
    expect_failure(
        script,
        root,
        f"{label}:expected=1:actual=0",
    )
    write(path, fixture_text(baseline_entries + [marker]))
    expect_failure(
        script,
        root,
        f"{label}:expected=1:actual=2",
    )
    write(path, fixture_text(baseline_entries))


def self_test() -> int:
    docs_markers = [
        REQUIRED_MARKERS["docs_root_phase1_closure_packet_count"][1],
        REQUIRED_MARKERS["docs_root_phase1_companion_count"][1],
        REQUIRED_MARKERS["docs_root_phase1_entrypoints_count"][1],
        REQUIRED_MARKERS["docs_root_phase1_companion_checks_count"][1],
    ]
    scripts_markers = [
        REQUIRED_MARKERS["scripts_root_phase1_validator_first_count"][1],
        REQUIRED_MARKERS["scripts_root_phase1_packet_alignment_count"][1],
        REQUIRED_MARKERS["scripts_root_phase1_review_hooks_count"][1],
    ]
    makefile_markers = [
        REQUIRED_ROUTE_LINES["makefile_phase1_route_summary_self_test_count"][1],
        REQUIRED_ROUTE_LINES["makefile_phase1_route_summary_run_count"][1],
    ]
    workflow_markers = [
        REQUIRED_ROUTE_LINES["workflow_phase1_route_summary_self_test_count"][1],
        REQUIRED_ROUTE_LINES["workflow_phase1_route_summary_run_count"][1],
    ]
    companion_markers = [
        COMPANION_ROUTE_LINES["companion_phase1_validate_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_bitmap_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_bitmap_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_find_bit_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_find_bit_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_route_summary_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_route_summary_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_validation_route_inventory_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_validation_route_inventory_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_parity_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_parity_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_bench_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_bench_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_validate_phase1_closure_self_test_count"][1],
        COMPANION_ROUTE_LINES["companion_phase1_validate_phase1_closure_count"][1],
    ]
    closure_markers = [
        CLOSURE_ROUTE_LINES["closure_phase1_parity_gate_count"][1],
        CLOSURE_ROUTE_LINES["closure_phase1_parity_self_test_gate_count"][1],
        CLOSURE_ROUTE_LINES["closure_phase1_bench_check_gate_count"][1],
        CLOSURE_ROUTE_LINES["closure_phase1_bench_self_test_gate_count"][1],
        CLOSURE_ROUTE_LINES["closure_phase1_closure_gate_count"][1],
        CLOSURE_ROUTE_LINES["closure_phase1_closure_self_test_gate_count"][1],
    ]

    marker_cases = [
        (
            "Documentation/zigux/README.md",
            docs_markers,
            "docs_root_phase1_closure_packet_count",
            docs_markers[0],
        ),
        (
            "Documentation/zigux/README.md",
            docs_markers,
            "docs_root_phase1_companion_count",
            docs_markers[1],
        ),
        (
            "Documentation/zigux/README.md",
            docs_markers,
            "docs_root_phase1_entrypoints_count",
            docs_markers[2],
        ),
        (
            "Documentation/zigux/README.md",
            docs_markers,
            "docs_root_phase1_companion_checks_count",
            docs_markers[3],
        ),
        (
            "scripts/zigux/README.md",
            scripts_markers,
            "scripts_root_phase1_validator_first_count",
            scripts_markers[0],
        ),
        (
            "scripts/zigux/README.md",
            scripts_markers,
            "scripts_root_phase1_packet_alignment_count",
            scripts_markers[1],
        ),
        (
            "scripts/zigux/README.md",
            scripts_markers,
            "scripts_root_phase1_review_hooks_count",
            scripts_markers[2],
        ),
        (
            "zigux/Makefile",
            makefile_markers,
            "makefile_phase1_route_summary_self_test_count",
            makefile_markers[0],
        ),
        (
            "zigux/Makefile",
            makefile_markers,
            "makefile_phase1_route_summary_run_count",
            makefile_markers[1],
        ),
        (
            ".github/workflows/zigux-bootstrap.yml",
            workflow_markers,
            "workflow_phase1_route_summary_self_test_count",
            workflow_markers[0],
        ),
        (
            ".github/workflows/zigux-bootstrap.yml",
            workflow_markers,
            "workflow_phase1_route_summary_run_count",
            workflow_markers[1],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_validate_self_test_count",
            companion_markers[0],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_bitmap_self_test_count",
            companion_markers[1],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_bitmap_count",
            companion_markers[2],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_find_bit_self_test_count",
            companion_markers[3],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_find_bit_count",
            companion_markers[4],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_route_summary_self_test_count",
            companion_markers[5],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_route_summary_count",
            companion_markers[6],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_validation_route_inventory_self_test_count",
            companion_markers[7],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_validation_route_inventory_count",
            companion_markers[8],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_parity_self_test_count",
            companion_markers[9],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_parity_count",
            companion_markers[10],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_bench_self_test_count",
            companion_markers[11],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_bench_count",
            companion_markers[12],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_validate_phase1_closure_self_test_count",
            companion_markers[13],
        ),
        (
            "Documentation/zigux/phase1-tests-root-review-companion.md",
            companion_markers,
            "companion_phase1_validate_phase1_closure_count",
            companion_markers[14],
        ),
        (
            "Documentation/zigux/phase1-closure.md",
            closure_markers,
            "closure_phase1_parity_gate_count",
            closure_markers[0],
        ),
        (
            "Documentation/zigux/phase1-closure.md",
            closure_markers,
            "closure_phase1_parity_self_test_gate_count",
            closure_markers[1],
        ),
        (
            "Documentation/zigux/phase1-closure.md",
            closure_markers,
            "closure_phase1_bench_check_gate_count",
            closure_markers[2],
        ),
        (
            "Documentation/zigux/phase1-closure.md",
            closure_markers,
            "closure_phase1_bench_self_test_gate_count",
            closure_markers[3],
        ),
        (
            "Documentation/zigux/phase1-closure.md",
            closure_markers,
            "closure_phase1_closure_gate_count",
            closure_markers[4],
        ),
        (
            "Documentation/zigux/phase1-closure.md",
            closure_markers,
            "closure_phase1_closure_self_test_gate_count",
            closure_markers[5],
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-route-summary-") as tmp:
        root = Path(tmp)
        script = root / "scripts/zigux/check-phase1-route-summary-counts.py"
        write(script, Path(__file__).read_text(encoding="utf-8"))
        write(root / "Documentation/zigux/README.md", fixture_text(docs_markers))
        write(root / "scripts/zigux/README.md", fixture_text(scripts_markers))
        write(root / "zigux/Makefile", fixture_text(makefile_markers))
        write(root / ".github/workflows/zigux-bootstrap.yml", fixture_text(workflow_markers))
        write(root / "Documentation/zigux/phase1-tests-root-review-companion.md", fixture_text(companion_markers))
        write(root / "Documentation/zigux/phase1-closure.md", fixture_text(closure_markers))

        env = dict(os.environ)
        env["ZIGUX_PHASE1_ROOT"] = str(root)
        code = os.spawnve(os.P_WAIT, sys.executable, [sys.executable, str(script)], env)
        if code != 0:
            print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=fail")
            return 1

        total_cases = 1
        for rel, baseline_entries, label, marker in marker_cases:
            expect_missing_and_duplicate(script, root, rel, baseline_entries, label, marker)
            total_cases += 2

        missing_file_cases = [
            (
                "Documentation/zigux/README.md",
                fixture_text(docs_markers),
                "docs_root_phase1_closure_packet_count:missing_file:Documentation/zigux/README.md",
            ),
            (
                "scripts/zigux/README.md",
                fixture_text(scripts_markers),
                "scripts_root_phase1_validator_first_count:missing_file:scripts/zigux/README.md",
            ),
            (
                "zigux/Makefile",
                fixture_text(makefile_markers),
                "makefile_phase1_route_summary_self_test_count:missing_file:zigux/Makefile",
            ),
            (
                ".github/workflows/zigux-bootstrap.yml",
                fixture_text(workflow_markers),
                "workflow_phase1_route_summary_self_test_count:missing_file:.github/workflows/zigux-bootstrap.yml",
            ),
            (
                "Documentation/zigux/phase1-tests-root-review-companion.md",
                fixture_text(companion_markers),
                "companion_phase1_validate_self_test_count:missing_file:Documentation/zigux/phase1-tests-root-review-companion.md",
            ),
            (
                "Documentation/zigux/phase1-closure.md",
                fixture_text(closure_markers),
                "closure_phase1_parity_gate_count:missing_file:Documentation/zigux/phase1-closure.md",
            ),
        ]
        for rel, baseline, expected in missing_file_cases:
            path = root / rel
            path.unlink()
            expect_failure(script, root, expected)
            write(path, baseline)
            total_cases += 1

    print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")
    print(f"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST_CASE_COUNT={total_cases}")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv[1:]:
        raise SystemExit(self_test())
    raise SystemExit(main())
