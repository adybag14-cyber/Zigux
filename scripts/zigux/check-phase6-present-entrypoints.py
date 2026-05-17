#!/usr/bin/env python3
"""Guard the current Phase 6 helper evidence packet."""

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
BASE64_HELPER_PATH = Path("lib/base64.zig")
BSEARCH_HELPER_PATH = Path("lib/bsearch.zig")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
HEXDUMP_HELPER_PATH = Path("lib/hexdump.zig")
REQUIRED_HELPER_PATHS = [
    BASE64_HELPER_PATH,
    BSEARCH_HELPER_PATH,
    CHECKSUM_HELPER_PATH,
    HEXDUMP_HELPER_PATH,
]
REQUIRED_DIRECT_READBACK_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]
EXPECTED_HELPERS = {
    "base64": {
        "zig_helper": "lib/base64.zig",
        "slice_note": "Documentation/zigux/phase6-base64-slice.md",
        "review_posture": "helper-local-direct-readback-confirmed",
    },
    "bsearch": {
        "zig_helper": "lib/bsearch.zig",
        "slice_note": "Documentation/zigux/phase6-bsearch-slice.md",
        "review_posture": "direct-readback-limited",
    },
    "checksum": {
        "zig_helper": "lib/checksum.zig",
        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
        "review_posture": "direct-readback-limited",
    },
    "hexdump": {
        "zig_helper": "lib/hexdump.zig",
        "slice_note": "Documentation/zigux/phase6-hexdump-slice.md",
        "review_posture": "direct-readback-limited",
    },
}

CATALOG_SURVEYED_HEAD_PATTERN = re.compile(r"^- surveyed head: `([^`]+)`$", re.M)
MANIFEST_SURVEYED_HEAD_PATTERN = re.compile(r'"surveyed_head": "([^"]+)"')

REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "- `zigux/tests/phase6_helper_parity_manifest.json`",
    "- `zigux/tests/phase6_bsearch.zig`",
    "- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
    "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
    "- `zigux/tests/phase6_checksum.zig`",
    "- `zigux/tests/phase6_hexdump.zig`",
    "- `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- `scripts/zigux/check-phase6-hexdump-packet.py`",
    "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
    "### base64",
    "### bsearch",
    "### checksum",
    "### hexdump",
    "- Zig helper: `lib/base64.zig`",
    "- Zig helper: `lib/bsearch.zig`",
    "- Zig helper: `lib/checksum.zig`",
    "- Zig helper: `lib/hexdump.zig`",
    "- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`",
    "- direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- direct corpus evidence checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- helper-local packet checker: `scripts/zigux/check-phase6-hexdump-packet.py`",
    "- current review posture: fresh direct reads now confirm the helper-local base64 replay, fixture, slowdown, and C-parity companions named above, while the broader shared parity and perf reminder routes outside those directly readable base64-local surfaces still stay limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders",
    "- current review posture: the roadmap-backed bsearch packet still names the right parity and comparison-budget surfaces, but current direct evidence is limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replays and corpus checker again",
    "- current review posture: the roadmap-backed checksum packet remains intentionally bounded, but current direct evidence is limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again",
    "- current review posture: the roadmap-backed hexdump packet still points at the right formatting and slowdown surfaces, but current direct evidence is limited to this shared catalog, the machine-readable manifest, and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay, checker, and perf companions again",
    "## Last-known shared replay inventory",
    "- `python3 scripts/zigux/check-phase6-base64-c-parity.py`",
    "- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-base64-perf`",
    "- `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-checksum-perf`",
    "- `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
    "- `make -C zigux phase6-bsearch-test`",
    "- `make -C zigux phase6-hexdump-review`",
    "- `make -C zigux phase6-hexdump-test`",
    "- `make -C zigux phase6-hexdump-perf`",
]

REQUIRED_MANIFEST_SNIPPETS = [
    '"packet": "phase6-helper-evidence"',
    '"phase": "Phase 6"',
    '"surveyed_head": "',
    '"Documentation/zigux/phase6-helper-evidence-catalog.md"',
    '"lib/base64.zig"',
    '"lib/bsearch.zig"',
    '"lib/checksum.zig"',
    '"lib/hexdump.zig"',
    '"Documentation/zigux/phase6-helper-parity-catalog.md"',
    '"Documentation/zigux/phase6-perf-gate-survey.md"',
    '"zigux/tests/phase6_helper_parity_manifest.json"',
    '"make -C zigux phase6-base64-perf"',
    '"make -C zigux phase6-hexdump-perf"',
]

SELF_TEST_CASE_COUNT = len(REQUIRED_CATALOG_SNIPPETS) + 7 + len(REQUIRED_HELPER_PATHS)


class ValidationError(RuntimeError):
    """Raised when a required Phase 6 marker is missing."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> str:
    content = read_text(path)
    return require_snippets_in_content(path, content, snippets)


def require_snippets_in_content(path: Path, content: str, snippets: list[str]) -> str:
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}"
            )
    return content


def extract_catalog_surveyed_head(content: str) -> str:
    match = CATALOG_SURVEYED_HEAD_PATTERN.search(content)
    if match is None:
        raise ValidationError(
            "missing expected Phase 6 marker in "
            f"{HELPER_EVIDENCE_CATALOG_PATH.as_posix()}: - surveyed head: `<sha>`"
        )
    return match.group(1)


def extract_manifest_surveyed_head(content: str) -> str:
    match = MANIFEST_SURVEYED_HEAD_PATTERN.search(content)
    if match is None:
        raise ValidationError(
            "missing expected Phase 6 marker in "
            f'{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}: "surveyed_head": "<sha>"'
        )
    return match.group(1)


def load_manifest_data(path: Path) -> dict:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"invalid JSON in {path.as_posix()}: {exc.msg}"
        ) from exc


def validate_direct_readback_companions(manifest: dict) -> None:
    companions = manifest.get("current_direct_readback_companions")
    if companions != REQUIRED_DIRECT_READBACK_COMPANIONS:
        raise ValidationError(
            "Phase 6 direct-readback companions mismatch in "
            f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}: expected "
            f"{REQUIRED_DIRECT_READBACK_COMPANIONS}, got {companions}"
        )


def validate_helper_entries(manifest: dict) -> None:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(
            "Phase 6 helper manifest must expose a helpers list in "
            f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}"
        )

    helpers_by_key = {}
    for entry in helpers:
        if not isinstance(entry, dict):
            raise ValidationError(
                "Phase 6 helper manifest contains a non-object helper entry in "
                f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}"
            )
        key = entry.get("key")
        if not isinstance(key, str):
            raise ValidationError(
                "Phase 6 helper manifest contains a helper entry without a string key in "
                f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}"
            )
        helpers_by_key[key] = entry

    if set(helpers_by_key) != set(EXPECTED_HELPERS):
        raise ValidationError(
            "Phase 6 helper manifest helper keys mismatch in "
            f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}: expected "
            f"{sorted(EXPECTED_HELPERS)}, got {sorted(helpers_by_key)}"
        )

    for key, expected in EXPECTED_HELPERS.items():
        entry = helpers_by_key[key]
        if entry.get("zig_helper") != expected["zig_helper"]:
            raise ValidationError(
                "Phase 6 helper manifest zig_helper mismatch for "
                f"{key} in {HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}: expected "
                f'{expected["zig_helper"]}, got {entry.get("zig_helper")}'
            )
        if entry.get("slice_note") != expected["slice_note"]:
            raise ValidationError(
                "Phase 6 helper manifest slice_note mismatch for "
                f"{key} in {HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}: expected "
                f'{expected["slice_note"]}, got {entry.get("slice_note")}'
            )
        if entry.get("current_review_posture") != expected["review_posture"]:
            raise ValidationError(
                "Phase 6 helper manifest review posture mismatch for "
                f"{key} in {HELPER_EVIDENCE_MANIFEST_PATH.as_posix()}: expected "
                f'{expected["review_posture"]}'
            )


def validate(repo_root: Path) -> None:
    catalog_path = repo_root / HELPER_EVIDENCE_CATALOG_PATH
    manifest_path = repo_root / HELPER_EVIDENCE_MANIFEST_PATH
    catalog_content = require_snippets(catalog_path, REQUIRED_CATALOG_SNIPPETS)
    manifest_content = read_text(manifest_path)
    manifest_data = load_manifest_data(manifest_path)
    require_snippets_in_content(
        manifest_path, manifest_content, REQUIRED_MANIFEST_SNIPPETS
    )

    catalog_head = extract_catalog_surveyed_head(catalog_content)
    manifest_head = extract_manifest_surveyed_head(manifest_content)
    if manifest_head != catalog_head:
        raise ValidationError(
            "Phase 6 surveyed-head mismatch between "
            f"{HELPER_EVIDENCE_CATALOG_PATH.as_posix()} ({catalog_head}) and "
            f"{HELPER_EVIDENCE_MANIFEST_PATH.as_posix()} ({manifest_head})"
        )

    validate_direct_readback_companions(manifest_data)
    validate_helper_entries(manifest_data)

    for helper_path in REQUIRED_HELPER_PATHS:
        if not (repo_root / helper_path).is_file():
            raise ValidationError(f"missing required file: {helper_path.as_posix()}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_manifest_json() -> str:
    manifest = {
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
        "helpers": [
            {
                "key": key,
                "roadmap_anchor": anchor,
                "zig_helper": expected["zig_helper"],
                "slice_note": expected["slice_note"],
                "current_review_posture": expected["review_posture"],
            }
            for key, expected, anchor in [
                ("base64", EXPECTED_HELPERS["base64"], "lib/base64.c"),
                ("bsearch", EXPECTED_HELPERS["bsearch"], "lib/bsearch.c"),
                ("checksum", EXPECTED_HELPERS["checksum"], "lib/checksum.c"),
                ("hexdump", EXPECTED_HELPERS["hexdump"], "lib/hexdump.c"),
            ]
        ],
        "current_repo_reality_gaps": [
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "zigux/tests/phase6_helper_parity_manifest.json",
        ],
        "last_known_shared_replay_inventory": [
            "make -C zigux phase6-base64-perf",
            "make -C zigux phase6-hexdump-perf",
        ],
    }
    return json.dumps(manifest, indent=2) + "\n"


def scaffold_repo(root: Path) -> None:
    catalog_content = "\n".join(
        [
            "# Phase 6 Helper Evidence Catalog",
            "",
            "- surveyed head: `840f388`",
            *REQUIRED_CATALOG_SNIPPETS,
            "",
        ]
    )
    write(root / HELPER_EVIDENCE_CATALOG_PATH, catalog_content)
    write(root / HELPER_EVIDENCE_MANIFEST_PATH, scaffold_manifest_json())
    for helper_path in REQUIRED_HELPER_PATHS:
        write(root / helper_path, "// stub\n")


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        message = str(exc)
        if expected not in message:
            raise AssertionError(
                f"expected {expected!r} in validation error, got {message!r}"
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

        for snippet in REQUIRED_CATALOG_SNIPPETS:
            write(catalog_path, read_text(catalog_path).replace(snippet + "\n", "", 1))
            expect_failure(root, snippet)
            cases_run += 1
            scaffold_repo(root)

        write(
            catalog_path,
            read_text(catalog_path).replace('- surveyed head: `840f388`\n', "", 1),
        )
        expect_failure(root, "- surveyed head: `<sha>`")
        cases_run += 1
        scaffold_repo(root)

        manifest = load_manifest_data(manifest_path)
        manifest["current_direct_readback_companions"] = manifest[
            "current_direct_readback_companions"
        ][:-1]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "Phase 6 direct-readback companions mismatch")
        cases_run += 1
        scaffold_repo(root)

        manifest = load_manifest_data(manifest_path)
        manifest["helpers"][0]["current_review_posture"] = "direct-readback-limited"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "Phase 6 helper manifest review posture mismatch for base64")
        cases_run += 1
        scaffold_repo(root)

        manifest = load_manifest_data(manifest_path)
        manifest["helpers"][0]["slice_note"] = "Documentation/zigux/wrong.md"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "Phase 6 helper manifest slice_note mismatch for base64")
        cases_run += 1
        scaffold_repo(root)

        write(
            manifest_path,
            read_text(manifest_path).replace('"surveyed_head": "840f388"', '"surveyed_head": "deadbee"'),
        )
        expect_failure(root, "Phase 6 surveyed-head mismatch")
        cases_run += 1
        scaffold_repo(root)

        write(manifest_path, "{\n")
        expect_failure(root, "invalid JSON")
        cases_run += 1
        scaffold_repo(root)

        (root / HELPER_EVIDENCE_MANIFEST_PATH).unlink()
        expect_failure(root, HELPER_EVIDENCE_MANIFEST_PATH.as_posix())
        cases_run += 1
        scaffold_repo(root)

        for helper_path in REQUIRED_HELPER_PATHS:
            (root / helper_path).unlink()
            expect_failure(root, helper_path.as_posix())
            cases_run += 1
            scaffold_repo(root)

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

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
    except ValidationError as exc:
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1

    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
