#!/usr/bin/env python3
"""Guard the current Phase 6 helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_HELPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_DIRECT_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]
EXPECTED_ROADMAP_ANCHORS = [
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
]
EXPECTED_REPO_REALITY_GAPS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
]
EXPECTED_BSEARCH_CHECKER = "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"
REQUIRED_HELPER_PATHS = [
    Path("lib/base64.zig"),
    Path("lib/bsearch.zig"),
    Path("lib/checksum.zig"),
    Path("lib/hexdump.zig"),
]
REQUIRED_CATALOG_SNIPPETS = [
    "- lane scope: shared helper-evidence rows and machine-readable manifest only",
    "- directly readable shared build foothold: `zigux/tests/phase6_build.zig`",
    "- directly readable shared Makefile wrapper surface: `zigux/Makefile`",
    "- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`",
    "- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- `scripts/zigux/check-phase6-hexdump-packet.py`",
]
REQUIRED_BUILD_SNIPPETS = [
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
]
REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-base64-perf:",
    "$(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-bsearch-test:",
    "$(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-review:",
    "$(PYTHON) scripts/zigux/check-phase6-hexdump-route.py",
]
SURVEYED_HEAD_PATTERN = re.compile(r"^- surveyed head: `([^`]+)`$", re.M)
SELF_TEST_CASE_COUNT = 8

CATALOG_SCAFFOLD = """# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `61e026c`
- lane scope: shared helper-evidence rows and machine-readable manifest only
- shared scripts-root reminder: `scripts/zigux/README.md`
- shared tests-root reminder: `zigux/tests/README.md`
- shared docs-root reminder: `Documentation/zigux/README.md`
- directly readable shared build foothold: `zigux/tests/phase6_build.zig`
- directly readable shared Makefile wrapper surface: `zigux/Makefile`
- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`
- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`

## Current direct-readback warning

- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/phase6_base64_c_casegen.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `scripts/zigux/check-phase6-hexdump-packet.py`

## Current helper-evidence rows

### bsearch

- dedicated corpus checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`

### checksum

- direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`

### hexdump

- helper-local packet checker: `scripts/zigux/check-phase6-hexdump-packet.py`
"""

BUILD_SCAFFOLD = """const std = @import("std");
pub fn build(b: *std.Build) void {
    const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");
    const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");
    const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");
    const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");
    _ = base64_perf_step;
    _ = bsearch_test_step;
    _ = checksum_perf_step;
    _ = hexdump_review_step;
}
"""

MAKEFILE_SCAFFOLD = """PYTHON ?= python3
ZIG ?= zig
phase6-base64-perf:
	cd .. && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all
phase6-bsearch-test:
	cd .. && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all
phase6-checksum-perf:
	cd .. && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all
phase6-hexdump-review:
	cd .. && $(PYTHON) scripts/zigux/check-phase6-hexdump-route.py
"""

MANIFEST_SCAFFOLD = {
    "packet": EXPECTED_PACKET,
    "phase": EXPECTED_PHASE,
    "surveyed_head": "61e026c",
    "lane_scope": EXPECTED_LANE_SCOPE,
    "current_direct_readback_companions": EXPECTED_DIRECT_COMPANIONS,
    "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
    "helpers": [
        {
            "key": "base64",
            "checker_surfaces": [
                "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
                "zigux/tests/phase6_base64_c_parity.zig",
                "zigux/tests/phase6_base64_c_casegen.zig",
                "zigux/tests/fixtures/phase6_base64_c_harness.c",
                "scripts/zigux/check-phase6-base64-c-parity.py",
            ],
            "current_review_posture": "direct-helper-readback-restored",
        },
        {
            "key": "bsearch",
            "checker_surfaces": [EXPECTED_BSEARCH_CHECKER],
            "current_review_posture": "direct-helper-readback-restored",
        },
        {
            "key": "checksum",
            "checker_surfaces": [
                "zigux/tests/phase6_checksum_c_parity.zig",
                "zigux/tests/fixtures/phase6_checksum_c_harness.c",
                "scripts/zigux/check-phase6-checksum-c-parity.py",
            ],
            "current_review_posture": "direct-helper-readback-restored",
        },
        {
            "key": "hexdump",
            "checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"],
            "current_review_posture": "direct-readback-limited",
        },
    ],
    "current_repo_reality_gaps": EXPECTED_REPO_REALITY_GAPS,
}


class ValidationError(RuntimeError):
    """Raised when the Phase 6 helper-evidence packet drifts."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def extract_surveyed_head(content: str) -> str:
    match = SURVEYED_HEAD_PATTERN.search(content)
    if match is None:
        raise ValidationError(
            f"missing expected Phase 6 marker in {CATALOG_PATH.as_posix()}: - surveyed head: `<sha>`"
        )
    return match.group(1)


def require_missing_paths(repo_root: Path, paths: list[str]) -> None:
    for rel_path in paths:
        if (repo_root / rel_path).exists():
            raise ValidationError(f"expected repo-reality gap path to remain absent: {rel_path}")


def helper_by_key(helpers: list[dict[str, object]], key: str) -> dict[str, object]:
    for helper in helpers:
        if helper.get("key") == key:
            return helper
    raise ValidationError(f"missing helper entry for {key}")


def validate(repo_root: Path) -> None:
    catalog_path = repo_root / CATALOG_PATH
    manifest_path = repo_root / MANIFEST_PATH

    catalog_content = read_text(catalog_path)
    require_snippets(catalog_path, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)

    surveyed_head = extract_surveyed_head(catalog_content)
    manifest = read_json(manifest_path)

    if manifest.get("packet") != EXPECTED_PACKET:
        raise ValidationError("phase6 helper-evidence packet drift")
    if manifest.get("phase") != EXPECTED_PHASE:
        raise ValidationError("phase6 helper-evidence phase drift")
    if manifest.get("lane_scope") != EXPECTED_LANE_SCOPE:
        raise ValidationError("phase6 helper-evidence lane-scope drift")
    if manifest.get("surveyed_head") != surveyed_head:
        raise ValidationError("phase6 helper-evidence surveyed-head mismatch")
    if manifest.get("current_direct_readback_companions") != EXPECTED_DIRECT_COMPANIONS:
        raise ValidationError("phase6 direct-readback companions mismatch")
    if manifest.get("roadmap_anchors") != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("phase6 roadmap anchor packet mismatch")
    if manifest.get("current_repo_reality_gaps") != EXPECTED_REPO_REALITY_GAPS:
        raise ValidationError("phase6 repo-reality gaps mismatch")

    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helpers list missing")
    if [helper.get("key") for helper in helpers if isinstance(helper, dict)] != EXPECTED_HELPER_KEYS:
        raise ValidationError("phase6 helper key order mismatch")

    bsearch = helper_by_key(helpers, "bsearch")
    if bsearch.get("checker_surfaces") != [EXPECTED_BSEARCH_CHECKER]:
        raise ValidationError("phase6 bsearch checker surface mismatch")
    if bsearch.get("current_review_posture") != "direct-helper-readback-restored":
        raise ValidationError("phase6 bsearch review posture drift")

    checksum = helper_by_key(helpers, "checksum")
    if checksum.get("checker_surfaces") != [
        "zigux/tests/phase6_checksum_c_parity.zig",
        "zigux/tests/fixtures/phase6_checksum_c_harness.c",
        "scripts/zigux/check-phase6-checksum-c-parity.py",
    ]:
        raise ValidationError("phase6 checksum checker surface mismatch")

    require_missing_paths(repo_root, EXPECTED_REPO_REALITY_GAPS)

    for helper_path in REQUIRED_HELPER_PATHS:
        if not (repo_root / helper_path).is_file():
            raise ValidationError(f"missing required file: {helper_path.as_posix()}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / CATALOG_PATH, CATALOG_SCAFFOLD)
    write(root / BUILD_PATH, BUILD_SCAFFOLD)
    write(root / MAKEFILE_PATH, MAKEFILE_SCAFFOLD)
    write(root / MANIFEST_PATH, json.dumps(MANIFEST_SCAFFOLD, indent=2) + "\n")
    for helper_path in REQUIRED_HELPER_PATHS:
        write(root / helper_path, "// stub\n")


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r} in validation error, got {str(exc)!r}") from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_present_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        write(root / CATALOG_PATH, read_text(root / CATALOG_PATH).replace("- surveyed head: `61e026c`\n", "", 1))
        expect_failure(root, "- surveyed head: `<sha>`")
        cases_run += 1
        scaffold_repo(root)

        write(root / CATALOG_PATH, read_text(root / CATALOG_PATH).replace(REQUIRED_CATALOG_SNIPPETS[4] + "\n", "", 1))
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[4])
        cases_run += 1
        scaffold_repo(root)

        write(root / BUILD_PATH, read_text(root / BUILD_PATH).replace(REQUIRED_BUILD_SNIPPETS[1] + "\n", "", 1))
        expect_failure(root, REQUIRED_BUILD_SNIPPETS[1])
        cases_run += 1
        scaffold_repo(root)

        write(root / MAKEFILE_PATH, read_text(root / MAKEFILE_PATH).replace(REQUIRED_MAKEFILE_SNIPPETS[2] + "\n", "", 1))
        expect_failure(root, REQUIRED_MAKEFILE_SNIPPETS[2])
        cases_run += 1
        scaffold_repo(root)

        manifest = read_json(root / MANIFEST_PATH)
        manifest["current_repo_reality_gaps"] = manifest["current_repo_reality_gaps"] + [EXPECTED_BSEARCH_CHECKER]
        write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "phase6 repo-reality gaps mismatch")
        cases_run += 1
        scaffold_repo(root)

        write(root / EXPECTED_REPO_REALITY_GAPS[0], "# returned gap path\n")
        expect_failure(root, EXPECTED_REPO_REALITY_GAPS[0])
        cases_run += 1
        (root / EXPECTED_REPO_REALITY_GAPS[0]).unlink()
        scaffold_repo(root)

        (root / REQUIRED_HELPER_PATHS[0]).unlink()
        expect_failure(root, REQUIRED_HELPER_PATHS[0].as_posix())
        cases_run += 1
        scaffold_repo(root)

        write(root / MANIFEST_PATH, "{\n")
        expect_failure(root, "invalid JSON")
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
    print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to validate (default: current directory tree)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1

    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
