#!/usr/bin/env python3
"""Validate the current Phase 6 shared helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HELPER_EVIDENCE_CATALOG = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")
PHASE6_BUILD = Path("zigux/tests/phase6_build.zig")
MAKEFILE = Path("zigux/Makefile")
SHARED_SURFACE_CHECKER = Path("scripts/zigux/check-phase6-shared-surface.py")
PRESENT_ENTRYPOINTS_CHECKER = Path("scripts/zigux/check-phase6-present-entrypoints.py")
HEXDUMP_PACKET_CHECKER = Path("scripts/zigux/check-phase6-hexdump-packet.py")
HEXDUMP_ROUTE_CHECKER = Path("scripts/zigux/check-phase6-hexdump-route.py")

REQUIRED_FILES = [
    HELPER_EVIDENCE_CATALOG,
    HELPER_EVIDENCE_MANIFEST,
    HELPER_PARITY_MANIFEST,
    PHASE6_BUILD,
    MAKEFILE,
    SHARED_SURFACE_CHECKER,
    PRESENT_ENTRYPOINTS_CHECKER,
    HEXDUMP_PACKET_CHECKER,
    HEXDUMP_ROUTE_CHECKER,
]

EXPECTED_HELPER_EVIDENCE_PACKET = "phase6-helper-evidence"
EXPECTED_HELPER_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_SHARED_PERF_WRAPPER = "make -C zigux phase6-perf"
EXPECTED_SHARED_PERF_WRAPPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_SHARED_REPLAY_INVENTORY = [
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-validate:",
    "$(PYTHON) scripts/zigux/validate-phase6.py",
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf-matrix-test:",
    "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_BUILD_SNIPPETS = [
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_perf_root_module = b.createModule(.{',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    "const checksum_perf_matrix_test_step = b.step(",
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
]

REQUIRED_CATALOG_SNIPPETS = [
    "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
    "## Roadmap perf-gap readback",
    "## Current shared replay inventory",
    "- `make -C zigux phase6-bsearch-perf`",
    "- `make -C zigux phase6-checksum-perf-matrix-test`",
]

SELF_TEST_CASE_COUNT = 7


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def extract_shared_perf_wrapper_keys(helper_parity_manifest: dict[str, object]) -> list[str]:
    helpers = helper_parity_manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helper parity helpers missing")

    keys: list[str] = []
    for helper in helpers:
        if not isinstance(helper, dict):
            continue
        current_perf_evidence = helper.get("current_perf_evidence")
        if not isinstance(current_perf_evidence, dict):
            continue
        routes = current_perf_evidence.get("linux_style_rerun_routes")
        if isinstance(routes, list) and EXPECTED_SHARED_PERF_WRAPPER in routes:
            key = helper.get("key")
            if isinstance(key, str):
                keys.append(key)
    return keys


def run_checker(root: Path, checker: Path, flag: str) -> None:
    result = subprocess.run([sys.executable, str(root / checker), flag, str(root)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker.as_posix()} failed: {detail}")


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    helper_evidence_manifest = read_json(root / HELPER_EVIDENCE_MANIFEST)
    helper_parity_manifest = read_json(root / HELPER_PARITY_MANIFEST)
    if helper_evidence_manifest.get("packet") != EXPECTED_HELPER_EVIDENCE_PACKET:
        raise ValidationError("phase6 helper evidence packet drift")
    if helper_parity_manifest.get("packet") != EXPECTED_HELPER_PARITY_PACKET:
        raise ValidationError("phase6 helper parity packet drift")
    if helper_evidence_manifest.get("phase") != EXPECTED_PHASE or helper_parity_manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 phase drift")
    if helper_evidence_manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 roadmap anchors drift")
    if helper_evidence_manifest.get("current_shared_replay_inventory") != EXPECTED_SHARED_REPLAY_INVENTORY:
        raise ValidationError("phase6 shared replay inventory drift")
    if extract_shared_perf_wrapper_keys(helper_parity_manifest) != EXPECTED_SHARED_PERF_WRAPPER_KEYS:
        raise ValidationError("phase6 shared perf wrapper route drift")

    require_snippets(root / MAKEFILE, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(root / PHASE6_BUILD, REQUIRED_BUILD_SNIPPETS)
    require_snippets(root / HELPER_EVIDENCE_CATALOG, REQUIRED_CATALOG_SNIPPETS)

    run_checker(root, SHARED_SURFACE_CHECKER, "--repo-root")
    run_checker(root, PRESENT_ENTRYPOINTS_CHECKER, "--repo-root")
    run_checker(root, HEXDUMP_PACKET_CHECKER, "--repo-root")
    run_checker(root, HEXDUMP_ROUTE_CHECKER, "--root")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / HELPER_EVIDENCE_CATALOG, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_EVIDENCE_MANIFEST, json.dumps({
        "packet": EXPECTED_HELPER_EVIDENCE_PACKET,
        "phase": EXPECTED_PHASE,
        "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
        "current_shared_replay_inventory": EXPECTED_SHARED_REPLAY_INVENTORY,
    }, indent=2) + "\n")
    write(root / HELPER_PARITY_MANIFEST, json.dumps({
        "packet": EXPECTED_HELPER_PARITY_PACKET,
        "phase": EXPECTED_PHASE,
        "helpers": [
            {
                "key": "base64",
                "current_perf_evidence": {
                    "linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER],
                },
            },
            {
                "key": "bsearch",
                "current_perf_evidence": {
                    "linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER],
                },
            },
            {
                "key": "checksum",
                "current_perf_evidence": {
                    "linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER],
                },
            },
            {
                "key": "hexdump",
                "current_perf_evidence": {
                    "linux_style_rerun_routes": [EXPECTED_SHARED_PERF_WRAPPER],
                },
            },
        ],
    }, indent=2) + "\n")
    write(root / PHASE6_BUILD, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    for checker in [SHARED_SURFACE_CHECKER, PRESENT_ENTRYPOINTS_CHECKER, HEXDUMP_PACKET_CHECKER, HEXDUMP_ROUTE_CHECKER]:
        write(root / checker, "#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")


def expect_failure(fn) -> None:
    try:
        fn()
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        write(root / MAKEFILE, read_text(root / MAKEFILE).replace("phase6-bsearch-perf:\n", "", 1))
        expect_failure(lambda: validate(root))
        cases_run += 1
        scaffold_repo(root)
        write(root / PHASE6_BUILD, read_text(root / PHASE6_BUILD).replace('const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");\n', "", 1))
        expect_failure(lambda: validate(root))
        cases_run += 1
        scaffold_repo(root)
        write(root / MAKEFILE, read_text(root / MAKEFILE).replace("phase6-checksum-perf-matrix-test:\n", "", 1))
        expect_failure(lambda: validate(root))
        cases_run += 1
        scaffold_repo(root)
        write(root / PHASE6_BUILD, read_text(root / PHASE6_BUILD).replace("const checksum_perf_matrix_test_step = b.step(\n", "", 1))
        expect_failure(lambda: validate(root))
        cases_run += 1
        scaffold_repo(root)
        write(root / HELPER_EVIDENCE_CATALOG, read_text(root / HELPER_EVIDENCE_CATALOG).replace("- `make -C zigux phase6-checksum-perf-matrix-test`\n", "", 1))
        expect_failure(lambda: validate(root))
        cases_run += 1
        scaffold_repo(root)
        manifest = read_json(root / HELPER_EVIDENCE_MANIFEST)
        manifest["current_shared_replay_inventory"].remove("make -C zigux phase6-checksum-perf-matrix-test")
        write(root / HELPER_EVIDENCE_MANIFEST, json.dumps(manifest, indent=2) + "\n")
        expect_failure(lambda: validate(root))
        cases_run += 1
        scaffold_repo(root)
        parity_manifest = read_json(root / HELPER_PARITY_MANIFEST)
        parity_manifest["helpers"][1]["current_perf_evidence"]["linux_style_rerun_routes"] = []
        write(root / HELPER_PARITY_MANIFEST, json.dumps(parity_manifest, indent=2) + "\n")
        expect_failure(lambda: validate(root))
        cases_run += 1
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE6_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_VALIDATION=fail: {exc}")
        return 1
    print("PHASE6_VALIDATION=pass")
    print(f"PHASE6_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE6_REQUIRED_MARKER_COUNT={len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_BUILD_SNIPPETS) + len(REQUIRED_CATALOG_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
