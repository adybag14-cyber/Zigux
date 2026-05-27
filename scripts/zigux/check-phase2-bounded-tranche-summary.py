#!/usr/bin/env python3
"""Fail-closed guard for the opening Phase 2 bounded-tranche summary."""

from __future__ import annotations

import argparse
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase2-closure.md")

OPENING_SUMMARY_LINE = (
    "This note keeps the current Phase 2 closure-side packet aligned to the directly readable "
    "toolchain, local-first archive, archive-verification, staged-archive helper, installer, "
    "cross-route, bootstrap-workflow-routes, kconfig-bridge, helper-local allconfig guard, "
    "genksyms bridge, fixdep, make-wrapper, manifest-guard, artifact-diff helper, and "
    "validator surfaces on current `master`."
)

BOUNDED_TRANCHE_LINE = (
    "The bounded Phase 2 tranche remains the directly readable toolchain, local-first archive, "
    "archive-verification, staged repo-local archive helper contract and selftest packet, "
    "installer, direct cross-route, bootstrap workflow-route guard, selected kconfig-bridge "
    "plus helper-local allconfig guard, bounded genksyms bridge, direct standalone genksyms "
    "invalid-long-option and ambiguous-long-option version-side-effect proofs, fixdep, "
    "required-make-route, validator-entrypoint, closure-validator, and fixture-backed "
    "artifact-support packet already present on current `master`."
)

OPENING_REQUIRED_MARKERS = (
    "directly readable toolchain",
    "local-first archive",
    "archive-verification",
    "staged-archive helper",
    "installer",
    "cross-route",
    "bootstrap-workflow-routes",
    "kconfig-bridge",
    "helper-local allconfig guard",
    "genksyms bridge",
    "fixdep",
    "make-wrapper",
    "manifest-guard",
    "artifact-diff helper",
    "validator surfaces",
)

BOUNDED_REQUIRED_MARKERS = (
    "directly readable toolchain",
    "local-first archive",
    "archive-verification",
    "staged repo-local archive helper contract and selftest packet",
    "installer",
    "direct cross-route",
    "bootstrap workflow-route guard",
    "selected kconfig-bridge plus helper-local allconfig guard",
    "bounded genksyms bridge",
    "direct standalone genksyms invalid-long-option and ambiguous-long-option version-side-effect proofs",
    "fixdep",
    "required-make-route",
    "validator-entrypoint",
    "closure-validator",
    "fixture-backed artifact-support packet",
)

SAMPLE_DOC = f"""# Phase 2 Closure

{OPENING_SUMMARY_LINE}

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`

{BOUNDED_TRANCHE_LINE}

## Current Closure Packet
"""


def load_doc(root: Path) -> str:
    doc_path = root / DOC_PATH
    try:
        return doc_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"PHASE2_BOUNDED_TRANCHE_SUMMARY=fail\n"
            f"PHASE2_BOUNDED_TRANCHE_SUMMARY_NOTE=missing:{DOC_PATH.as_posix()}"
        ) from exc


def require_once(text: str, needle: str, label: str) -> None:
    count = text.count(needle)
    if count != 1:
        raise SystemExit(
            "PHASE2_BOUNDED_TRANCHE_SUMMARY=fail\n"
            f"PHASE2_BOUNDED_TRANCHE_SUMMARY_NOTE={label}_count:{count}"
        )


def require_markers(line: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in line]
    if missing:
        raise SystemExit(
            "PHASE2_BOUNDED_TRANCHE_SUMMARY=fail\n"
            f"PHASE2_BOUNDED_TRANCHE_SUMMARY_NOTE={label}_missing:{'|'.join(missing)}"
        )


def check(root: Path) -> None:
    text = load_doc(root)
    require_once(text, OPENING_SUMMARY_LINE, "opening_summary")
    require_once(text, BOUNDED_TRANCHE_LINE, "bounded_tranche")

    opening_index = text.index(OPENING_SUMMARY_LINE)
    bounded_index = text.index(BOUNDED_TRANCHE_LINE)
    current_packet_index = text.index("## Current Closure Packet")
    if not opening_index < bounded_index < current_packet_index:
        raise SystemExit(
            "PHASE2_BOUNDED_TRANCHE_SUMMARY=fail\n"
            "PHASE2_BOUNDED_TRANCHE_SUMMARY_NOTE=section_order_mismatch"
        )

    require_markers(OPENING_SUMMARY_LINE, OPENING_REQUIRED_MARKERS, "opening_summary")
    require_markers(BOUNDED_TRANCHE_LINE, BOUNDED_REQUIRED_MARKERS, "bounded_tranche")

    print("PHASE2_BOUNDED_TRANCHE_SUMMARY=pass")
    print(f"PHASE2_BOUNDED_TRANCHE_SUMMARY_OPENING_MARKER_COUNT={len(OPENING_REQUIRED_MARKERS)}")
    print(f"PHASE2_BOUNDED_TRANCHE_SUMMARY_BOUNDED_MARKER_COUNT={len(BOUNDED_REQUIRED_MARKERS)}")


def run_self_test() -> None:
    cases = 0
    sample_root = Path("/tmp/phase2_bounded_tranche_selftest")
    write_sample_root(sample_root)
    check(sample_root)
    cases += 1

    bad_root = sample_root / "missing_opening"
    write_sample_root(bad_root)
    bad_doc = (bad_root / DOC_PATH).read_text(encoding="utf-8").replace(
        "artifact-diff helper", "artifact helper", 1
    )
    (bad_root / DOC_PATH).write_text(bad_doc, encoding="utf-8")
    try:
        check(bad_root)
    except SystemExit as exc:
        if "opening_summary_count:0" not in str(exc):
            raise
        cases += 1

    bad_root = sample_root / "missing_bounded"
    write_sample_root(bad_root)
    bad_doc = (bad_root / DOC_PATH).read_text(encoding="utf-8").replace(
        "required-make-route", "required make route", 1
    )
    (bad_root / DOC_PATH).write_text(bad_doc, encoding="utf-8")
    try:
        check(bad_root)
    except SystemExit as exc:
        if "bounded_tranche_count:0" not in str(exc):
            raise
        cases += 1

    bad_root = sample_root / "order"
    write_sample_root(bad_root)
    swapped = f"""# Phase 2 Closure

{BOUNDED_TRANCHE_LINE}

## Status

- `PHASE2_STATUS=parked`

{OPENING_SUMMARY_LINE}

## Current Closure Packet
"""
    (bad_root / DOC_PATH).write_text(swapped, encoding="utf-8")
    try:
        check(bad_root)
    except SystemExit as exc:
        if "section_order_mismatch" not in str(exc):
            raise
        cases += 1

    print("PHASE2_BOUNDED_TRANCHE_SUMMARY_SELF_TEST=pass")
    print(f"PHASE2_BOUNDED_TRANCHE_SUMMARY_SELF_TEST_CASE_COUNT={cases}")


def write_sample_root(root: Path) -> None:
    doc_path = root / DOC_PATH
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(SAMPLE_DOC, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return
    if args.self_test:
        run_self_test()
        return
    check(args.root)


if __name__ == "__main__":
    main()
