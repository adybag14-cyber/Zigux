#!/usr/bin/env python3
"""Guard the current Phase 6 helper evidence packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HELPER_EVIDENCE_CATALOG_PATH = Path(
    "Documentation/zigux/phase6-helper-evidence-catalog.md"
)

REQUIRED_CATALOG_SNIPPETS = [
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "- `zigux/tests/phase6_build.zig`",
    "- `zigux/tests/phase6_helper_parity_manifest.json`",
    "- `zigux/tests/phase6_base64.zig`",
    "- `zigux/tests/phase6_bsearch.zig`",
    "- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
    "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
    "- `zigux/tests/phase6_checksum.zig`",
    "- `zigux/tests/phase6_hexdump.zig`",
    "- `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- `scripts/zigux/check-phase6-hexdump-packet.py`",
    "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
    "### base64",
    "### bsearch",
    "### checksum",
    "### hexdump",
    "- current review posture: the roadmap-backed base64 packet remains the intended bounded helper surface, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again",
    "- current review posture: the roadmap-backed bsearch packet still names the right parity and comparison-budget surfaces, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replays and corpus checker again",
    "- current review posture: the roadmap-backed checksum packet remains intentionally bounded, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again",
    "- current review posture: the roadmap-backed hexdump packet still points at the right formatting and slowdown surfaces, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay, checker, and perf companions again",
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

SELF_TEST_CASE_COUNT = 11


class ValidationError(RuntimeError):
    """Raised when a required Phase 6 marker is missing."""


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
                f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}"
            )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / HELPER_EVIDENCE_CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / HELPER_EVIDENCE_CATALOG_PATH,
        "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n",
    )


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

        for snippet in [
            "## Current direct-readback warning",
            "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
            "- `Documentation/zigux/phase6-perf-gate-survey.md`",
            "- `zigux/tests/phase6_helper_parity_manifest.json`",
            "- `scripts/zigux/check-phase6-base64-c-parity.py`",
            "- `scripts/zigux/check-phase6-hexdump-packet.py`",
            "### hexdump",
            "- current review posture: the roadmap-backed checksum packet remains intentionally bounded, but current direct evidence is limited to this shared catalog and the directly readable scripts-root plus tests-root reminders until fresh direct reads confirm the helper-local replay and parity members again",
            "## Last-known shared replay inventory",
            "- `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
            "- `make -C zigux phase6-hexdump-perf`",
        ]:
            write(catalog_path, read_text(catalog_path).replace(snippet + "\n", "", 1))
            expect_failure(root, snippet)
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
