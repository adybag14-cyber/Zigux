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
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
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
        "current_review_posture": "direct-readback-limited",
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
        "current_review_posture": "direct-readback-limited",
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
        "current_review_posture": "direct-readback-limited",
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
    "zigux/tests/phase6_helper_parity_manifest.json",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
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
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "- `zigux/tests/phase6_helper_parity_manifest.json`",
    "- `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    "- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
    "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
    "- direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- current review posture: the roadmap-backed base64 packet now has directly readable helper-local evidence through `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `Documentation/zigux/phase6-base64-slice.md`, while the dedicated slowdown and C-parity companions still need fresh direct reads before they are presented as current shipped evidence",
    "- current review posture: the roadmap-backed bsearch packet still names the right parity and comparison-budget surfaces, but current direct evidence is limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replays and corpus checker again",
    "- current review posture: the roadmap-backed checksum packet remains intentionally bounded, but current direct evidence is limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again",
    "- current review posture: the roadmap-backed hexdump packet still points at the right formatting and slowdown surfaces, but current direct evidence is limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay, checker, and perf companions again",
    "## Last-known shared replay inventory",
    "- `make -C zigux phase6-hexdump-perf`",
]

CATALOG_SURVEYED_HEAD_PATTERN = re.compile(r"^- surveyed head: `([^`]+)`$", re.M)


class ValidationError(RuntimeError):
    """Raised when a required Phase 6 marker is missing."""


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

    catalog_content = read_text(catalog_path)
    require_snippets(catalog_path, catalog_content, REQUIRED_CATALOG_SNIPPETS)
    catalog_head = extract_catalog_surveyed_head(catalog_content)

    manifest = json.loads(read_text(manifest_path))
    if manifest["surveyed_head"] != catalog_head:
        raise ValidationError(
            "Phase 6 surveyed-head mismatch between "
            f"{HELPER_EVIDENCE_CATALOG_PATH.as_posix()} ({catalog_head}) and "
            f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()} ({manifest['surveyed_head']})"
        )
    if manifest["current_direct_readback_companions"] != REQUIRED_DIRECT_READBACK_COMPANIONS:
        raise ValidationError("Phase 6 direct-readback companions mismatch")
    if manifest["helpers"] != EXPECTED_HELPERS:
        raise ValidationError("Phase 6 helper manifest helper packet mismatch")
    if manifest["current_repo_reality_gaps"] != EXPECTED_CURRENT_REPO_REALITY_GAPS:
        raise ValidationError("Phase 6 repo-reality gaps mismatch")
    if (
        manifest["last_known_shared_replay_inventory"]
        != EXPECTED_LAST_KNOWN_SHARED_REPLAY_INVENTORY
    ):
        raise ValidationError("Phase 6 shared replay inventory mismatch")

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
            "- surveyed head: `840f388`",
            "",
            *REQUIRED_CATALOG_SNIPPETS,
            "",
        ]
    )


def scaffold_manifest() -> str:
    return json.dumps(
        {
            "packet": "phase6-helper-evidence",
            "phase": "Phase 6",
            "surveyed_head": "840f388",
            "current_direct_readback_companions": REQUIRED_DIRECT_READBACK_COMPANIONS,
            "roadmap_anchors": [
                "lib/base64.c",
                "lib/bsearch.c",
                "lib/checksum.c",
                "lib/hexdump.c",
            ],
            "helpers": EXPECTED_HELPERS,
            "current_repo_reality_gaps": EXPECTED_CURRENT_REPO_REALITY_GAPS,
            "last_known_shared_replay_inventory": EXPECTED_LAST_KNOWN_SHARED_REPLAY_INVENTORY,
        },
        indent=2,
    ) + "\n"


def scaffold_repo(root: Path) -> None:
    write(root / HELPER_EVIDENCE_CATALOG_PATH, scaffold_catalog())
    write(root / HELPER_EVIDENCE_MANIFEST_PATH, scaffold_manifest())
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

        write(catalog_path, read_text(catalog_path).replace(REQUIRED_CATALOG_SNIPPETS[0] + "\n", "", 1))
        expect_failure(root, REQUIRED_CATALOG_SNIPPETS[0])
        cases_run += 1
        scaffold_repo(root)

        write(catalog_path, read_text(catalog_path).replace("- surveyed head: `840f388`\n", "", 1))
        expect_failure(root, "- surveyed head: `<sha>`")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["current_direct_readback_companions"] = manifest["current_direct_readback_companions"][:-1]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "direct-readback companions mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = json.loads(read_text(manifest_path))
        manifest["helpers"][0]["checker_surfaces"] = manifest["helpers"][0]["checker_surfaces"][1:]
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

        write(manifest_path, "{\n")
        expect_failure(root, "Expecting property name enclosed in double quotes")
        cases_run += 1
        scaffold_repo(root)

        (root / HELPER_EVIDENCE_MANIFEST_PATH).unlink()
        expect_failure(root, HELPER_EVIDENCE_MANIFEST_PATH.as_posix())
        cases_run += 1
        scaffold_repo(root)

        (root / REQUIRED_HELPER_PATHS[0]).unlink()
        expect_failure(root, REQUIRED_HELPER_PATHS[0].as_posix())
        cases_run += 1

    print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
    print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
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
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1

    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())