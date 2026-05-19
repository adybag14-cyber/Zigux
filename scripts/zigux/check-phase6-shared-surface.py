#!/usr/bin/env python3
"""Guard the current Phase 6 shared reminder surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
HELPER_EVIDENCE_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

REQUIRED_SCRIPTS_SNIPPETS = [
    "## Phase 6",
    "- Phase 6 flow - the current shared helper-evidence packet keeps the bounded base64, bsearch, checksum, and hexdump lane truthful from the scripts root without widening into new helper semantics",
    "- `python3 scripts/zigux/check-phase6-shared-surface.py --self-test` and `python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test` replay the shipped shared-surface and present-entrypoint guards",
    "- `scripts/zigux/check-phase6-shared-surface.py` and `scripts/zigux/check-phase6-present-entrypoints.py` keep the direct-readback warning, the helper-evidence catalog packet, and the shared replay inventory explicit from the scripts root",
    "- `Documentation/zigux/phase6-helper-evidence-catalog.md`, `Documentation/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-present-entrypoints.py`, and this scripts-root reminder remain the current directly readable shared companions for that packet",
    "- repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase6-helper-parity-catalog.md` and `Documentation/zigux/phase6-perf-gate-survey.md`",
    "- the shared replay inventory now treats `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-base64-perf`, `zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig`, `make -C zigux phase6-bsearch-perf`, `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`, and `make -C zigux phase6-checksum-perf` as committed rerun routes beside the existing hexdump reminders, so keep those wrappers out of the older inventory-only bucket",
    "- keep the current partially blocked helper packet tied to those shared surfaces instead of reconstructing broader helper-local proof from older route names alone until fresh direct reads recover the missing helper-local replay files again",
]

REQUIRED_CATALOG_SNIPPETS = [
    "- lane scope: shared helper-evidence rows and machine-readable manifest only",
    "- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`",
    "- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`",
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "## Current shared replay inventory",
    "- `make -C zigux phase6-bsearch-perf`",
    "- `make -C zigux phase6-hexdump-perf`",
]

REQUIRED_EVIDENCE_MANIFEST_SNIPPETS = [
    '"packet": "phase6-helper-evidence"',
    '"phase": "Phase 6"',
    '"lane_scope": "shared helper-evidence rows and machine-readable manifest only"',
    '"Documentation/zigux/phase6-helper-evidence-catalog.md"',
    '"zigux/tests/phase6_helper_parity_manifest.json"',
    '"scripts/zigux/check-phase6-present-entrypoints.py"',
    '"dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig"',
    '"make -C zigux phase6-bsearch-perf"',
    '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"',
]

REQUIRED_PARITY_MANIFEST_SNIPPETS = [
    '"packet": "phase6-helper-parity"',
    '"phase": "Phase 6"',
    '"lane_scope": "shared helper-parity rows and machine-readable manifest only"',
    '"dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig"',
    '"make -C zigux phase6-bsearch-perf"',
    '"scripts/zigux/check-phase6-shared-surface.py"',
    '"scripts/zigux/check-phase6-present-entrypoints.py"',
]

SELF_TEST_CASE_COUNT = 4


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
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_MANIFEST_PATH, REQUIRED_EVIDENCE_MANIFEST_SNIPPETS)
    require_snippets(repo_root / HELPER_PARITY_MANIFEST_PATH, REQUIRED_PARITY_MANIFEST_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_SNIPPETS) + "\n")
    write(root / HELPER_EVIDENCE_CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_EVIDENCE_MANIFEST_PATH, "\n".join(REQUIRED_EVIDENCE_MANIFEST_SNIPPETS) + "\n")
    write(root / HELPER_PARITY_MANIFEST_PATH, "\n".join(REQUIRED_PARITY_MANIFEST_SNIPPETS) + "\n")


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
            (root / SCRIPTS_README_PATH, "## Phase 6"),
            (root / HELPER_EVIDENCE_CATALOG_PATH, "- `make -C zigux phase6-bsearch-perf`"),
            (root / HELPER_EVIDENCE_MANIFEST_PATH, '"make -C zigux phase6-bsearch-perf"'),
            (root / HELPER_PARITY_MANIFEST_PATH, '"dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig"'),
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
    except ValidationError as exc:
        print(f"PHASE6_SHARED_SURFACE=fail: {exc}")
        return 1

    print("PHASE6_SHARED_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())