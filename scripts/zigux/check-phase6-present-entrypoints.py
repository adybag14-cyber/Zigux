#!/usr/bin/env python3
"""Guard the current Phase 6 helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

HELPER_EVIDENCE_CATALOG_PATH = Path(
    "Documentation/zigux/phase6-helper-evidence-catalog.md"
)
HELPER_EVIDENCE_MANIFEST_PATH = Path(
    "zigux/tests/phase6_helper_evidence_manifest.json"
)
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_ROADMAP_ANCHORS = [
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
]

REQUIRED_HELPER_PATHS = [
    Path("lib/base64.zig"),
    Path("lib/bsearch.zig"),
    Path("lib/checksum.zig"),
    Path("lib/hexdump.zig"),
]

REQUIRED_DIRECT_READBACK_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase6_build.zig",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]

REQUIRED_BUILD_SNIPPETS = [
    'const base64_perf_root_module = b.createModule(.{',
    '.root_source_file = b.path("phase6_base64_perf.zig"),',
    'const bsearch_lower_bound_c_abi_root_module = b.createModule(.{',
    '.root_source_file = b.path("phase6_bsearch_c_abi_budget.zig"),',
    'const checksum_perf_root_module = b.createModule(.{',
    'const hexdump_perf_root_module = b.createModule(.{',
    'const base64_test_step = b.step("phase6-base64-test", "Run Phase 6 base64 helper tests");',
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
    'const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    "test_step.dependOn(&run_base64_tests.step);",
    "test_step.dependOn(&run_checksum_tests.step);",
    "test_step.dependOn(&run_hexdump_tests.step);",
]

EXPECTED_HELPERS = [
    {
        "key": "base64",
        "roadmap_anchor": "lib/base64.c",
        "zig_helper": "lib/base64.zig",
        "focused_helper_replay": "zigux/tests/phase6_base64.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",
        "fixture_surfaces": [
            "zigux/tests/fixtures/phase6_base64_vectors.zig",
            "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
        ],
        "checker_surfaces": [
            "zigux/tests/phase6_base64_c_parity.zig",
            "zigux/tests/phase6_base64_c_casegen.zig",
            "zigux/tests/fixtures/phase6_base64_c_harness.c",
            "scripts/zigux/check-phase6-base64-c-parity.py",
        ],
        "slice_note": "Documentation/zigux/phase6-base64-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
    {
        "key": "bsearch",
        "roadmap_anchor": "lib/bsearch.c",
        "zig_helper": "lib/bsearch.zig",
        "focused_helper_replay": "zigux/tests/phase6_bsearch.zig",
        "focused_c_abi_replays": [
            "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
            "zigux/tests/phase6_bsearch_c_abi_budget.zig",
        ],
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_bsearch_vectors.zig"],
        "checker_surfaces": ["scripts/zigux/check-phase6-bsearch-corpus-evidence.py"],
        "slice_note": "Documentation/zigux/phase6-bsearch-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
    {
        "key": "checksum",
        "roadmap_anchor": "lib/checksum.c",
        "zig_helper": "lib/checksum.zig",
        "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
        "checker_surfaces": [
            "zigux/tests/phase6_checksum_c_parity.zig",
            "zigux/tests/fixtures/phase6_checksum_c_harness.c",
            "scripts/zigux/check-phase6-checksum-c-parity.py",
        ],
        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
    {
        "key": "hexdump",
        "roadmap_anchor": "lib/hexdump.c",
        "zig_helper": "lib/hexdump.zig",
        "focused_helper_replay": "zigux/tests/phase6_hexdump.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",
        "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_hexdump_vectors.zig"],
        "checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"],
        "slice_note": "Documentation/zigux/phase6-hexdump-slice.md",
        "perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md",
        "current_review_posture": "direct-readback-limited",
    },
]

EXPECTED_CURRENT_REPO_REALITY_GAPS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
]

EXPECTED_LAST_KNOWN_SHARED_REPLAY_INVENTORY = [
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-hexdump-review",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-perf",
]

REQUIRED_CATALOG_SNIPPETS = [
    "- lane scope: shared helper-evidence rows and machine-readable manifest only",
    "- directly readable shared build foothold: `zigux/tests/phase6_build.zig`",
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "- `Documentation/zigux/phase6-hexdump-slice.md`",
    "- `Documentation/zigux/phase6-hexdump-perf-refresh.md`",
    "- `zigux/tests/phase6_helper_parity_manifest.json`",
    "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
    "- direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- current review posture: the roadmap-backed base64 packet now has directly readable helper-local evidence through `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `Documentation/zigux/phase6-base64-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence",
    "- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
    "- last-known companion packet members still needing fresh direct reads: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the dedicated corpus checker still needs fresh direct reads before it is presented as current shipped evidence",
    "- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `Documentation/zigux/phase6-checksum-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence",
    "- current review posture: direct helper-local evidence is readable again through `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders, while the perf-matrix preflight, helper-local checker, perf refresh note, and slice note still need fresh direct reads before they are presented as current shipped evidence",
    "## Last-known shared replay inventory",
    "- `make -C zigux phase6-hexdump-perf`",
]

CATALOG_SURVEYED_HEAD_PATTERN = re.compile(r"^- surveyed head: `([^`]+)`$", re.M)
SELF_TEST_CASE_COUNT = 33


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, content: str, snippets: list[str]) -> None:
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}"
            )


def require_missing_paths(repo_root: Path, paths: list[str]) -> None:
    for relative_path in paths:
        if (repo_root / relative_path).exists():
            raise ValidationError(
                f"expected repo-reality gap path to remain absent: {relative_path}"
            )


def extract_catalog_surveyed_head(content: str) -> str:
    match = CATALOG_SURVEYED_HEAD_PATTERN.search(content)
    if match is None:
        raise ValidationError(
            "missing expected Phase 6 marker in "
            f"{HELPER_EVIDENCE_CATALOG_PATH.as_posix()}: - surveyed head: `<sha>`"
        )
    return match.group(1)


def validate(repo_root: Path) -> None:
    catalog_path = repo_root / HELPER_EVIDENCE_CATALOG_PATH
    manifest_path = repo_root / HELPER_EVIDENCE_MANIFEST_PATH
    build_path = repo_root / PHASE6_BUILD_PATH

    catalog_content = read_text(catalog_path)
    require_snippets(catalog_path, catalog_content, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(build_path, read_text(build_path), REQUIRED_BUILD_SNIPPETS)
    catalog_head = extract_catalog_surveyed_head(catalog_content)

    manifest = json.loads(read_text(manifest_path))
    if manifest["packet"] != EXPECTED_PACKET:
        raise ValidationError("Phase 6 helper manifest packet marker mismatch")
    if manifest["phase"] != EXPECTED_PHASE:
        raise ValidationError("Phase 6 helper manifest phase marker mismatch")
    if manifest["surveyed_head"] != catalog_head:
        raise ValidationError("surveyed-head mismatch")
    if manifest["lane_scope"] != EXPECTED_LANE_SCOPE:
        raise ValidationError("Phase 6 helper manifest lane-scope marker mismatch")
    if manifest["current_direct_readback_companions"] != REQUIRED_DIRECT_READBACK_COMPANIONS:
        raise ValidationError("Phase 6 direct-readback companions mismatch")
    if manifest["roadmap_anchors"] != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("Phase 6 roadmap anchor packet mismatch")
    if manifest["helpers"] != EXPECTED_HELPERS:
        raise ValidationError("Phase 6 helper manifest helper packet mismatch")
    if manifest["current_repo_reality_gaps"] != EXPECTED_CURRENT_REPO_REALITY_GAPS:
        raise ValidationError("Phase 6 repo-reality gaps mismatch")
    if (
        manifest["last_known_shared_replay_inventory"]
        != EXPECTED_LAST_KNOWN_SHARED_REPLAY_INVENTORY
    ):
        raise ValidationError("Phase 6 shared replay inventory mismatch")

    require_missing_paths(repo_root, manifest["current_repo_reality_gaps"])

    for helper_path in REQUIRED_HELPER_PATHS:
        if not (repo_root / helper_path).is_file():
            raise ValidationError(f"missing required file: {helper_path.as_posix()}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_catalog() -> str:
    return "\n".join(
        [
            "# Phase 6 Helper Evidence Catalog",
            "",
            "This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.",
            "",
            "- surveyed head: `61e026c`",
            "",
            *REQUIRED_CATALOG_SNIPPETS,
            "",
        ]
    )


def scaffold_manifest() -> str:
    return (
        json.dumps(
            {
                "packet": EXPECTED_PACKET,
                "phase": EXPECTED_PHASE,
                "surveyed_head": "61e026c",
                "lane_scope": EXPECTED_LANE_SCOPE,
                "current_direct_readback_companions": REQUIRED_DIRECT_READBACK_COMPANIONS,
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "helpers": EXPECTED_HELPERS,
                "current_repo_reality_gaps": EXPECTED_CURRENT_REPO_REALITY_GAPS,
                "last_known_shared_replay_inventory": EXPECTED_LAST_KNOWN_SHARED_REPLAY_INVENTORY,
            },
            indent=2,
        )
        + "\n"
    )


def scaffold_build() -> str:
    return "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n"


def scaffold_repo(root: Path) -> None:
    write(root / HELPER_EVIDENCE_CATALOG_PATH, scaffold_catalog())
    write(root / HELPER_EVIDENCE_MANIFEST_PATH, scaffold_manifest())
    write(root / PHASE6_BUILD_PATH, scaffold_build())
    for helper_path in REQUIRED_HELPER_PATHS:
        write(root / helper_path, "// stub\n")


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except (ValidationError, json.JSONDecodeError) as exc:
        if expected not in str(exc):
            raise AssertionError(
                f"expected {expected!r} in validation error, got {str(exc)!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        catalog_path = root / HELPER_EVIDENCE_CATALOG_PATH
        manifest_path = root / HELPER_EVIDENCE_MANIFEST_PATH
        build_path = root / PHASE6_BUILD_PATH

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[0] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[0])
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[1] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[1])
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[5] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[5])
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[6] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[6])
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[7] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[7])
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[16] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[16])
        cases_run += 1
        scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[17] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[17])
        cases_run += 1
        scaffold_repo(root)

        write(catalog_path, read_text(catalog_path).replace("- surveyed head: `61e026c`\n", "", 1))
        expect_failure(root, "- surveyed head: `<sha>`")
        cases_run += 1
        scaffold_repo(root)

        write(
            build_path,
            read_text(build_path).replace(REQUIRED_BUILD_SNIPPETS[0] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_BUILD_SNIPPETS[0])
        cases_run += 1
        scaffold_repo(root)

        write(
            build_path,
            read_text(build_path).replace(REQUIRED_BUILD_SNIPPETS[6] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_BUILD_SNIPPETS[6])
        cases_run += 1
        scaffold_repo(root)

        write(
            build_path,
            read_text(build_path).replace(REQUIRED_BUILD_SNIPPETS[9] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_BUILD_SNIPPETS[9])
        cases_run += 1
        scaffold_repo(root)

        write(
            build_path,
            read_text(build_path).replace(REQUIRED_BUILD_SNIPPETS[14] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_BUILD_SNIPPETS[14])
        cases_run += 1
        scaffold_repo(root)

        write(
            build_path,
            read_text(build_path).replace(REQUIRED_BUILD_SNIPPETS[12] + "\n", "", 1),
        )
        expect_failure(root, REQUIRED_BUILD_SNIPPETS[12])
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["packet"] = "phase6-helper-catalog"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "packet marker mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["phase"] = "Phase Six"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "phase marker mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["surveyed_head"] = "deadbeef"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "surveyed-head mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_direct_readback_companions"] = manifest[
            "current_direct_readback_companions"
        ][:-1]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "direct-readback companions mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_direct_readback_companions"][4] = (
            "zigux/tests/phase6_helper_parity_manifest.json"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "direct-readback companions mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["lane_scope"] = "shared helper-evidence rows only"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "lane-scope marker mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["roadmap_anchors"] = manifest["roadmap_anchors"][:-1]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "roadmap anchor packet mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][0]["checker_surfaces"] = manifest["helpers"][0][
            "checker_surfaces"
        ][1:]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "helper packet mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][2]["slice_note"] = "Documentation/zigux/phase6-checksum-survey.md"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "helper packet mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][2]["current_review_posture"] = (
            "direct-readback-limited"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "helper packet mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][3]["perf_refresh_note"] = (
            "Documentation/zigux/phase6-hexdump-perf-note.md"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "helper packet mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][3]["current_review_posture"] = (
            "direct-helper-readback-restored"
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "helper packet mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_repo_reality_gaps"] = manifest["current_repo_reality_gaps"][:-1]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "repo-reality gaps mismatch")
        cases_run += 1
        scaffold_repo(root)

        first_gap_path = root / EXPECTED_CURRENT_REPO_REALITY_GAPS[0]
        write(first_gap_path, "# returned gap path\n")
        expect_failure(root, EXPECTED_CURRENT_REPO_REALITY_GAPS[0])
        cases_run += 1
        first_gap_path.unlink()
        scaffold_repo(root)

        last_gap_path = root / EXPECTED_CURRENT_REPO_REALITY_GAPS[-1]
        write(last_gap_path, "#!/usr/bin/env python3\n")
        expect_failure(root, EXPECTED_CURRENT_REPO_REALITY_GAPS[-1])
        cases_run += 1
        last_gap_path.unlink()
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["last_known_shared_replay_inventory"] = manifest[
            "last_known_shared_replay_inventory"
        ][:-1]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "shared replay inventory mismatch")
        cases_run += 1
        scaffold_repo(root)

        write(manifest_path, "{\n")
        expect_failure(root, "Expecting property name enclosed in double quotes")
        cases_run += 1
        scaffold_repo(root)

        (root / HELPER_EVIDENCE_MANIFEST_PATH).unlink()
        expect_failure(root, HELPER_EVIDENCE_MANIFEST_PATH.as_posix())
        cases_run += 1
        scaffold_repo(root)

        (root / PHASE6_BUILD_PATH).unlink()
        expect_failure(root, PHASE6_BUILD_PATH.as_posix())
        cases_run += 1
        scaffold_repo(root)

        (root / REQUIRED_HELPER_PATHS[0]).unlink()
        expect_failure(root, REQUIRED_HELPER_PATHS[0].as_posix())
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
    print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1
    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
