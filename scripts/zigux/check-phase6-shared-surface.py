#!/usr/bin/env python3
"""Guard the current Phase 6 shared reminder surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
HELPER_EVIDENCE_CATALOG_PATH = Path(
    "Documentation/zigux/phase6-helper-evidence-catalog.md"
)
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")

REQUIRED_DOCS_SNIPPETS = [
    "Phase 6 notes",
    "- `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "- `zigux/tests/phase6_helper_evidence_manifest.json`",
    "- `scripts/zigux/check-phase6-shared-surface.py`",
    "- `scripts/zigux/check-phase6-present-entrypoints.py`",
    "now keep the current Phase 6 docs-root reminder packet explicit from the documentation root so current helper parity and perf follow-through stays bounded to the directly readable shared evidence packet without widening into new helper semantics.",
    "  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`, so treat those broader parity and perf reminder paths as historical packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` docs-root evidence.",
    "  * keep the docs-root Phase 6 summary aligned with `Documentation/zigux/phase6-helper-evidence-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, and `scripts/zigux/check-phase6-present-entrypoints.py`, so the shared helper packet keeps the bounded base64, bsearch, checksum, and hexdump evidence rows truthful without widening into missing helper-local parity or perf surfaces.",
    "  * keep the roadmap-backed leaf-helper anchors explicit here too: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` stay the Phase 6 scope, and follow-through should remain limited to reminder-surface truthfulness, helper-local parity, or perf-gate drift inside that bounded packet rather than runtime-core or freeze-map targets.",
]

REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "- Phase 6 flow - the current shared helper-evidence packet keeps the bounded base64, bsearch, checksum, and hexdump lane truthful from the scripts root without widening into new helper semantics",
    "- `python3 scripts/zigux/check-phase6-shared-surface.py --self-test` and `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test` replay the shipped shared-surface and present-entrypoint guards",
    "- `scripts/zigux/check-phase6-shared-surface.py` and `scripts/zigux/check-phase6-present-entrypoints.py` keep the direct-readback warning, the helper-evidence catalog packet, and the shared replay inventory explicit from the scripts root",
    "- `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, and this scripts-root reminder remain the current directly readable shared companions for that packet",
    "- repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so treat those broader parity and perf reminder paths as historical packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` scripts-root evidence",
    "- the shared replay inventory now treats `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-base64-perf`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-checksum-perf` as committed rerun routes beside the existing bsearch and hexdump reminders, so keep those wrappers out of the older inventory-only bucket",
    "- keep the current partially blocked helper packet tied to those shared surfaces instead of reconstructing broader helper-local proof from older route names alone until fresh direct reads recover the missing helper-local replay files again",
]

REQUIRED_TESTS_SNIPPETS = [
    "* current direct-readback Phase 6 shared packet: `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/tests/phase6_helper_evidence_manifest.json`",
    "* repo-reality warning for the broader Phase 6 helper parity and perf packet: repeated authenticated contents reads on current `master` now return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`",
    "* keep current Phase 6 follow-through tied to those directly readable shared reminder surfaces plus the restored shared build and machine-readable evidence footholds instead of reconstructing the broader helper-local parity and perf packet from older route names alone",
]

REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "- `zigux/tests/phase6_helper_parity_manifest.json`",
    "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
    "## Last-known shared replay inventory",
    "- `make -C zigux phase6-hexdump-perf`",
]

REQUIRED_MANIFEST_SNIPPETS = [
    '"packet": "phase6-helper-evidence"',
    '"phase": "Phase 6"',
    '"lane_scope": "shared helper-evidence rows and machine-readable manifest only"',
    '"Documentation/zigux/phase6-helper-evidence-catalog.md"',
    '"zigux/tests/phase6_build.zig"',
    '"scripts/zigux/check-phase6-shared-surface.py"',
    '"scripts/zigux/check-phase6-present-entrypoints.py"',
    '"key": "base64"',
    '"key": "bsearch"',
    '"key": "checksum"',
    '"key": "hexdump"',
    '"current_review_posture": "direct-helper-readback-restored"',
    '"current_review_posture": "direct-readback-limited"',
    '"Documentation/zigux/phase6-helper-parity-catalog.md"',
    '"Documentation/zigux/phase6-perf-gate-survey.md"',
    '"zigux/tests/phase6_helper_parity_manifest.json"',
    '"make -C zigux phase6-hexdump-perf"',
]

SELF_TEST_CASE_COUNT = 35


class ValidationError(RuntimeError):
    """Raised when a required shared-surface marker is missing."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 shared-surface marker in {path.as_posix()}: {snippet}"
            )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / DOCS_README_PATH, REQUIRED_DOCS_SNIPPETS)
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / TESTS_README_PATH, REQUIRED_TESTS_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_MANIFEST_PATH, REQUIRED_MANIFEST_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / DOCS_README_PATH, "\n".join(REQUIRED_DOCS_SNIPPETS) + "\n")
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write(root / TESTS_README_PATH, "\n".join(REQUIRED_TESTS_SNIPPETS) + "\n")
    write(
        root / HELPER_EVIDENCE_CATALOG_PATH,
        "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n",
    )
    write(
        root / HELPER_EVIDENCE_MANIFEST_PATH,
        "\n".join(REQUIRED_MANIFEST_SNIPPETS) + "\n",
    )


def expect_failure(root: Path, path: Path, snippet: str) -> None:
    original = read_text(path)
    write(path, original.replace(snippet + "\n", "", 1))
    try:
        validate(root)
    except ValidationError as exc:
        message = str(exc)
        if snippet not in message:
            raise AssertionError(
                f"expected {snippet!r} in validation error, got {message!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0
        for path, snippet in [
            (root / DOCS_README_PATH, "Phase 6 notes"),
            (
                root / DOCS_README_PATH,
                "- `Documentation/zigux/phase6-helper-evidence-catalog.md`",
            ),
            (
                root / DOCS_README_PATH,
                "- `zigux/tests/phase6_helper_evidence_manifest.json`",
            ),
            (
                root / DOCS_README_PATH,
                "- `scripts/zigux/check-phase6-shared-surface.py`",
            ),
            (
                root / DOCS_README_PATH,
                "- `scripts/zigux/check-phase6-present-entrypoints.py`",
            ),
            (
                root / DOCS_README_PATH,
                "now keep the current Phase 6 docs-root reminder packet explicit from the documentation root so current helper parity and perf follow-through stays bounded to the directly readable shared evidence packet without widening into new helper semantics.",
            ),
            (
                root / DOCS_README_PATH,
                "  * repeated authenticated reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`, so treat those broader parity and perf reminder paths as historical packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` docs-root evidence.",
            ),
            (
                root / DOCS_README_PATH,
                "  * keep the docs-root Phase 6 summary aligned with `Documentation/zigux/phase6-helper-evidence-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, and `scripts/zigux/check-phase6-present-entrypoints.py`, so the shared helper packet keeps the bounded base64, bsearch, checksum, and hexdump evidence rows truthful without widening into missing helper-local parity or perf surfaces.",
            ),
            (
                root / DOCS_README_PATH,
                "  * keep the roadmap-backed leaf-helper anchors explicit here too: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` stay the Phase 6 scope, and follow-through should remain limited to reminder-surface truthfulness, helper-local parity, or perf-gate drift inside that bounded packet rather than runtime-core or freeze-map targets.",
            ),
            (root / SCRIPTS_README_PATH, "## Phase 6"),
            (
                root / SCRIPTS_README_PATH,
                "- `python3 scripts/zigux/check-phase6-shared-surface.py --self-test` and `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test` replay the shipped shared-surface and present-entrypoint guards",
            ),
            (
                root / SCRIPTS_README_PATH,
                "- `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, and this scripts-root reminder remain the current directly readable shared companions for that packet",
            ),
            (
                root / SCRIPTS_README_PATH,
                "- repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`, so treat those broader parity and perf reminder paths as historical packet members that need fresh reread or re-materialization before they are reused here as direct current-`master` scripts-root evidence",
            ),
            (
                root / SCRIPTS_README_PATH,
                "- `scripts/zigux/check-phase6-shared-surface.py` and `scripts/zigux/check-phase6-present-entrypoints.py` keep the direct-readback warning, the helper-evidence catalog packet, and the shared replay inventory explicit from the scripts root",
            ),
            (
                root / SCRIPTS_README_PATH,
                "- the shared replay inventory now treats `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-base64-perf`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-checksum-perf` as committed rerun routes beside the existing bsearch and hexdump reminders, so keep those wrappers out of the older inventory-only bucket",
            ),
            (
                root / SCRIPTS_README_PATH,
                "- keep the current partially blocked helper packet tied to those shared surfaces instead of reconstructing broader helper-local proof from older route names alone until fresh direct reads recover the missing helper-local replay files again",
            ),
            (
                root / TESTS_README_PATH,
                "* current direct-readback Phase 6 shared packet: `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/phase6_build.zig`, and `zigux/tests/phase6_helper_evidence_manifest.json`",
            ),
            (
                root / TESTS_README_PATH,
                "* repo-reality warning for the broader Phase 6 helper parity and perf packet: repeated authenticated contents reads on current `master` now return missing for `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, and `zigux/tests/phase6_helper_parity_manifest.json`",
            ),
            (
                root / TESTS_README_PATH,
                "* keep current Phase 6 follow-through tied to those directly readable shared reminder surfaces plus the restored shared build and machine-readable evidence footholds instead of reconstructing the broader helper-local parity and perf packet from older route names alone",
            ),
            (root / HELPER_EVIDENCE_CATALOG_PATH, "## Current direct-readback warning"),
            (
                root / HELPER_EVIDENCE_CATALOG_PATH,
                "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
            ),
            (
                root / HELPER_EVIDENCE_CATALOG_PATH,
                "- `Documentation/zigux/phase6-perf-gate-survey.md`",
            ),
            (
                root / HELPER_EVIDENCE_CATALOG_PATH,
                "- `zigux/tests/phase6_helper_parity_manifest.json`",
            ),
            (
                root / HELPER_EVIDENCE_CATALOG_PATH,
                "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
            ),
            (root / HELPER_EVIDENCE_CATALOG_PATH, "## Last-known shared replay inventory"),
            (
                root / HELPER_EVIDENCE_CATALOG_PATH,
                "- `make -C zigux phase6-hexdump-perf`",
            ),
            (root / HELPER_EVIDENCE_MANIFEST_PATH, '"packet": "phase6-helper-evidence"'),
            (
                root / HELPER_EVIDENCE_MANIFEST_PATH,
                '"lane_scope": "shared helper-evidence rows and machine-readable manifest only"',
            ),
            (
                root / HELPER_EVIDENCE_MANIFEST_PATH,
                '"Documentation/zigux/phase6-helper-evidence-catalog.md"',
            ),
            (
                root / HELPER_EVIDENCE_MANIFEST_PATH,
                '"scripts/zigux/check-phase6-shared-surface.py"',
            ),
            (
                root / HELPER_EVIDENCE_MANIFEST_PATH,
                '"scripts/zigux/check-phase6-present-entrypoints.py"',
            ),
            (root / HELPER_EVIDENCE_MANIFEST_PATH, '"key": "base64"'),
            (root / HELPER_EVIDENCE_MANIFEST_PATH, '"key": "hexdump"'),
            (
                root / HELPER_EVIDENCE_MANIFEST_PATH,
                '"zigux/tests/phase6_helper_parity_manifest.json"',
            ),
            (
                root / HELPER_EVIDENCE_MANIFEST_PATH,
                '"make -C zigux phase6-hexdump-perf"',
            ),
        ]:
            expect_failure(root, path, snippet)
            cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE6_SHARED_SURFACE_SELF_TEST=pass")
    print(f"PHASE6_SHARED_SURFACE_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE6_SHARED_SURFACE=fail: {exc}")
        return 1

    print("PHASE6_SHARED_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
