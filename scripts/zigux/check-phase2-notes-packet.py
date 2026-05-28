#!/usr/bin/env python3
"""Fail closed when the Phase 2 tool-manifest notes packet drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_NOTES = (
    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, bootstrap workflow-routes checker, kbuild routes checker, the live kconfig bridge checker and fixture roster, the helper-local kconfig allconfig guard, the dedicated genksyms selftest-alignment guard, the dedicated genksyms dual-implementation survey guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
    "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
    "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
    "Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper, the helper-local kconfig allconfig guard, and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-bootstrap-workflow-routes.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py, scripts/zigux/artifact_diff.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
    "Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.",
    "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, the bootstrap workflow-routes guard, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the dedicated genksyms dual-implementation survey checker, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
    "Keep scripts/zigux/README.md explicit as the shipped scripts-root reminder surface for the same current Phase 2 toolchain, kbuild, installer, cross-route, bootstrap workflow-route, and make-wrapper packet that the docs-root, tests-root, and checklist surfaces summarize.",
)


class DuplicateKeyError(ValueError):
    """Raised when a manifest JSON object repeats a key."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateKeyError(f"duplicate json key: {key}")
        payload[key] = value
    return payload


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(notes: list[object] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {},
        "notes": list(EXPECTED_NOTES if notes is None else notes),
    }
    return json.dumps(payload, indent=2) + "\n"


def count_exact_entries(entries: list[str], marker: str) -> int:
    return sum(1 for entry in entries if entry == marker)


def load_manifest(manifest_path: Path) -> dict[str, object]:
    try:
        return json.loads(
            manifest_path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest json: {exc.msg}") from exc
    except DuplicateKeyError as exc:
        raise ValueError(str(exc)) from exc


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = load_manifest(manifest_path)
    except ValueError as exc:
        return [str(exc)]

    if not isinstance(manifest, dict):
        return ["invalid manifest root object"]

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        return ["invalid notes list"]

    issues: list[str] = []
    for index, entry in enumerate(notes):
        if not isinstance(entry, str):
            issues.append(f"invalid notes entry at index {index}: {entry!r}")

    string_entries = [entry for entry in notes if isinstance(entry, str)]
    if len(notes) != len(EXPECTED_NOTES):
        issues.append(
            "notes count drift: "
            f"expected {len(EXPECTED_NOTES)}, found {len(notes)}"
        )

    for expected in EXPECTED_NOTES:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing notes entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate notes entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_NOTES):
        if index >= len(notes):
            continue
        actual = notes[index]
        if actual != expected:
            issues.append(
                f"notes order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_NOTES:
            issues.append(f"unexpected notes entry: {entry}")

    return issues


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_notes_packet_") as temp_dir:
        root = Path(temp_dir)
        _write(root / MANIFEST_PATH, _sample_manifest())

        issues = validate(root)
        if issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase":"Phase 2","phase":"Phase 3"}\n')
        issues = validate(root)
        if "duplicate json key: phase" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected duplicate json key was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "[]\n")
        issues = validate(root)
        if "invalid manifest root object" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected invalid manifest root object was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, '{"phase": "Phase 2", "notes": "bad"}\n')
        issues = validate(root)
        if "invalid notes list" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected invalid notes list was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase":"Phase 2","notes":["a"],"notes":["b"]}\n',
        )
        issues = validate(root)
        if "duplicate json key: notes" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected duplicate nested json key was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_NOTES[:-1])),
        )
        issues = validate(root)
        missing_issue = f"missing notes entry: {EXPECTED_NOTES[-1]}"
        if missing_issue not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected missing notes entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest([EXPECTED_NOTES[0], 7, EXPECTED_NOTES[-1]]),
        )
        issues = validate(root)
        if "invalid notes entry at index 1: 7" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected invalid notes entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_NOTES)
        duplicate_entries[-1] = EXPECTED_NOTES[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = f"duplicate notes entry: {EXPECTED_NOTES[-2]}:count=2"
        if duplicate_issue not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected duplicate notes entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_NOTES)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "notes order drift at index 0: "
            f"expected {EXPECTED_NOTES[0]!r}, found {EXPECTED_NOTES[1]!r}"
        )
        if order_issue not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected notes order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_NOTES) + ["unexpected note"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        issues = validate(root)
        if "unexpected notes entry: unexpected note" not in issues:
            print("PHASE2_NOTES_PACKET_SELF_TEST=fail")
            print("expected unexpected notes entry was not reported")
            return 1
        case_count += 1

    print("PHASE2_NOTES_PACKET_SELF_TEST=pass")
    print(f"PHASE2_NOTES_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 tool-manifest notes packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 2 tool manifest",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"wrote sample root to {args.write_sample_root}")
        return 0

    issues = validate(args.root)
    if issues:
        print("PHASE2_NOTES_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_NOTES_PACKET=pass")
    print(f"PHASE2_NOTES_PACKET_COUNT={len(EXPECTED_NOTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
