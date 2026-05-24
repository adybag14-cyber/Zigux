#!/usr/bin/env python3
"""Guard the current Phase 6 bootstrap helper packet."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

DOCS_README = Path("Documentation/zigux/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
BUILD_FILE = Path("zigux/tests/phase6_build.zig")
VALIDATOR = Path("scripts/zigux/validate-phase6.py")
EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")

DOCS_MARKERS = (
    "Phase 6 notes - `Documentation/zigux/phase6-helper-evidence-catalog.md` - `Documentation/zigux/phase6-helper-parity-catalog.md` - `Documentation/zigux/phase6-perf-gate-survey.md`",
    "* current `master` directly serves the four roadmap-backed helper anchors through `lib/base64.zig`, `lib/bsearch.zig`, `lib/checksum.zig`, and `lib/hexdump.zig`",
    "* `python3 scripts/zigux/check-phase6-shared-surface.py --self-test`, `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test`, `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-perf` replay the bounded current Phase 6 reminder packet without widening it into missing parity companions or helper-local implementation follow-through.",
)

WORKFLOW_LINES = (
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: make -C zigux phase6-perf",
)

MAKEFILE_MARKERS = (
    "phase6-validate:",
    "$(PYTHON) scripts/zigux/validate-phase6.py",
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf-matrix-test:",
    "phase6-hexdump-perf:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
)

BUILD_MARKERS = (
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    'const test_step = b.step("test", "Run Phase 6 helper tests");',
)

VALIDATOR_MARKERS = (
    'HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")',
    'HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")',
    'WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")',
    'SHARED_SURFACE_CHECKER = Path("scripts/zigux/check-phase6-shared-surface.py")',
    'PRESENT_ENTRYPOINTS_CHECKER = Path("scripts/zigux/check-phase6-present-entrypoints.py")',
    'BASE64_BSEARCH_PERF_MARKERS_CHECKER = Path(',
    'CHECKSUM_HEXDUMP_PERF_MARKERS_CHECKER = Path(',
    'HEXDUMP_ROUTE_CHECKER = Path("scripts/zigux/check-phase6-hexdump-route.py")',
    'EXPECTED_SHARED_PERF_WRAPPER = "make -C zigux phase6-perf"',
)

EXPECTED_EVIDENCE_PACKET = "phase6-helper-evidence"
EXPECTED_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-24"

EXPECTED_EVIDENCE_COMPANIONS = (
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
)

EXPECTED_PARITY_EVIDENCE = (
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
)

SELF_TEST_CASE_COUNT = 16


def resolve(root: Path, relative: Path) -> Path:
    return root / relative


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase6 bootstrap helper packet checker missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"phase6 bootstrap helper packet checker invalid JSON in {path.as_posix()}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"phase6 bootstrap helper packet checker expected object JSON: {path.as_posix()}")
    return payload


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(path: Path, text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase6 bootstrap helper packet checker missing {label} marker in {path.as_posix()}: {marker}"
            )


def require_exact_lines(path: Path, text: str, markers: tuple[str, ...], label: str) -> None:
    lines = tuple(line.strip() for line in text.splitlines())
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count == 0:
            raise SystemExit(
                f"phase6 bootstrap helper packet checker missing {label} line in {path.as_posix()}: {marker}"
            )
        if count != 1:
            raise SystemExit(
                f"phase6 bootstrap helper packet checker duplicate {label} line in {path.as_posix()}: {marker}:count={count}"
            )


def require_list_contains(label: str, values: object, expected_items: tuple[str, ...]) -> None:
    if not isinstance(values, list):
        raise SystemExit(f"phase6 bootstrap helper packet checker missing list: {label}")
    missing = [item for item in expected_items if item not in values]
    if missing:
        raise SystemExit(
            f"phase6 bootstrap helper packet checker {label} missing items: {', '.join(missing)}"
        )


def check_repo(root: Path) -> None:
    docs_text = read_text(resolve(root, DOCS_README))
    workflow_text = read_text(resolve(root, WORKFLOW))
    makefile_text = read_text(resolve(root, MAKEFILE))
    build_text = read_text(resolve(root, BUILD_FILE))
    validator_text = read_text(resolve(root, VALIDATOR))
    evidence_manifest = read_json(resolve(root, EVIDENCE_MANIFEST))
    parity_manifest = read_json(resolve(root, PARITY_MANIFEST))

    require_markers(resolve(root, DOCS_README), docs_text, DOCS_MARKERS, "docs")
    require_exact_lines(resolve(root, WORKFLOW), workflow_text, WORKFLOW_LINES, "workflow")
    require_markers(resolve(root, MAKEFILE), makefile_text, MAKEFILE_MARKERS, "Makefile")
    require_markers(resolve(root, BUILD_FILE), build_text, BUILD_MARKERS, "build")
    require_markers(resolve(root, VALIDATOR), validator_text, VALIDATOR_MARKERS, "validator")

    if evidence_manifest.get("packet") != EXPECTED_EVIDENCE_PACKET:
        raise SystemExit("phase6 bootstrap helper packet checker evidence packet drift")
    if parity_manifest.get("packet") != EXPECTED_PARITY_PACKET:
        raise SystemExit("phase6 bootstrap helper packet checker parity packet drift")
    if evidence_manifest.get("phase") != EXPECTED_PHASE:
        raise SystemExit("phase6 bootstrap helper packet checker evidence phase drift")
    if parity_manifest.get("phase") != EXPECTED_PHASE:
        raise SystemExit("phase6 bootstrap helper packet checker parity phase drift")
    if evidence_manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise SystemExit("phase6 bootstrap helper packet checker evidence surveyed-head drift")
    if parity_manifest.get("surveyed_head") != EXPECTED_SURVEYED_HEAD:
        raise SystemExit("phase6 bootstrap helper packet checker parity surveyed-head drift")

    require_list_contains(
        "evidence current_direct_readback_companions",
        evidence_manifest.get("current_direct_readback_companions"),
        EXPECTED_EVIDENCE_COMPANIONS,
    )
    require_list_contains(
        "parity shared_direct_evidence",
        parity_manifest.get("shared_direct_evidence"),
        EXPECTED_PARITY_EVIDENCE,
    )


def scaffold_repo(root: Path) -> None:
    write_text(resolve(root, DOCS_README), "\n".join(DOCS_MARKERS) + "\n")
    write_text(resolve(root, WORKFLOW), "\n".join(WORKFLOW_LINES) + "\n")
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(resolve(root, BUILD_FILE), "\n".join(BUILD_MARKERS) + "\n")
    write_text(resolve(root, VALIDATOR), "\n".join(VALIDATOR_MARKERS) + "\n")
    write_text(
        resolve(root, EVIDENCE_MANIFEST),
        json.dumps(
            {
                "packet": EXPECTED_EVIDENCE_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "current_direct_readback_companions": list(EXPECTED_EVIDENCE_COMPANIONS),
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, PARITY_MANIFEST),
        json.dumps(
            {
                "packet": EXPECTED_PARITY_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "shared_direct_evidence": list(EXPECTED_PARITY_EVIDENCE),
            },
            indent=2,
        )
        + "\n",
    )


def expect_marker_failure(root: Path, path: Path, marker: str) -> None:
    original = read_text(path)
    if marker not in original:
        raise AssertionError(f"self-test marker not found: {marker}")
    write_text(path, original.replace(marker, "", 1))
    try:
        check_repo(root)
    except SystemExit as exc:
        if marker not in str(exc):
            raise AssertionError(f"expected marker {marker!r} in failure, got {exc!s}") from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        write_text(path, original)


def expect_json_failure(path: Path, payload: dict[str, object], expected: str) -> None:
    original = read_text(path)
    write_text(path, json.dumps(payload, indent=2) + "\n")
    try:
        check_repo(path.parents[2])
    except SystemExit as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r} in failure, got {exc!s}") from exc
    else:
        raise AssertionError("expected JSON validation failure")
    finally:
        write_text(path, original)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_bootstrap_helper_packet_") as tmp_dir:
        root = Path(tmp_dir)
        scaffold_repo(root)
        check_repo(root)

        cases_run = 0
        for path, marker in (
            (resolve(root, DOCS_README), DOCS_MARKERS[0]),
            (resolve(root, DOCS_README), DOCS_MARKERS[2]),
            (resolve(root, WORKFLOW), WORKFLOW_LINES[0]),
            (resolve(root, WORKFLOW), WORKFLOW_LINES[2]),
            (resolve(root, MAKEFILE), MAKEFILE_MARKERS[0]),
            (resolve(root, MAKEFILE), MAKEFILE_MARKERS[-1]),
            (resolve(root, BUILD_FILE), BUILD_MARKERS[0]),
            (resolve(root, BUILD_FILE), BUILD_MARKERS[-1]),
            (resolve(root, VALIDATOR), VALIDATOR_MARKERS[0]),
            (resolve(root, VALIDATOR), VALIDATOR_MARKERS[-1]),
        ):
            expect_marker_failure(root, path, marker)
            cases_run += 1

        evidence_path = resolve(root, EVIDENCE_MANIFEST)
        parity_path = resolve(root, PARITY_MANIFEST)
        expect_json_failure(
            evidence_path,
            {
                "packet": "wrong",
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "current_direct_readback_companions": list(EXPECTED_EVIDENCE_COMPANIONS),
            },
            "evidence packet drift",
        )
        cases_run += 1
        expect_json_failure(
            evidence_path,
            {
                "packet": EXPECTED_EVIDENCE_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "current_direct_readback_companions": ["zigux/Makefile"],
            },
            "evidence current_direct_readback_companions missing items",
        )
        cases_run += 1
        expect_json_failure(
            parity_path,
            {
                "packet": EXPECTED_PARITY_PACKET,
                "phase": "wrong",
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "shared_direct_evidence": list(EXPECTED_PARITY_EVIDENCE),
            },
            "parity phase drift",
        )
        cases_run += 1
        expect_json_failure(
            parity_path,
            {
                "packet": EXPECTED_PARITY_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": EXPECTED_SURVEYED_HEAD,
                "shared_direct_evidence": ["zigux/Makefile"],
            },
            "parity shared_direct_evidence missing items",
        )
        cases_run += 1

        scaffold_repo(root)
        resolve(root, VALIDATOR).unlink()
        try:
            check_repo(root)
        except SystemExit as exc:
            if VALIDATOR.as_posix() not in str(exc):
                raise AssertionError(f"expected missing validator path in failure, got {exc!s}") from exc
        else:
            raise AssertionError("expected missing file failure")
        cases_run += 1

        scaffold_repo(root)
        duplicate_workflow = "\n".join((*WORKFLOW_LINES, WORKFLOW_LINES[0])) + "\n"
        write_text(resolve(root, WORKFLOW), duplicate_workflow)
        try:
            check_repo(root)
        except SystemExit as exc:
            if "duplicate workflow line" not in str(exc):
                raise AssertionError(f"expected duplicate workflow failure, got {exc!s}") from exc
        else:
            raise AssertionError("expected duplicate workflow failure")
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_BOOTSTRAP_HELPER_PACKET_SELF_TEST=pass")
    print(f"PHASE6_BOOTSTRAP_HELPER_PACKET_SELF_TEST_CASE_COUNT={cases_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in packet self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    check_repo(root)
    print("PHASE6_BOOTSTRAP_HELPER_PACKET=pass")
    print(f"PHASE6_BOOTSTRAP_HELPER_PACKET_WORKFLOW={resolve(root, WORKFLOW)}")
    print(f"PHASE6_BOOTSTRAP_HELPER_PACKET_MAKEFILE={resolve(root, MAKEFILE)}")
    print(f"PHASE6_BOOTSTRAP_HELPER_PACKET_BUILD={resolve(root, BUILD_FILE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
