#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 tests-root summary packet.

This checker is intentionally narrow: it compares the tests-root Phase 6
summary against the shared manifest and the known blocked base64/checksum
surfaces called out by the shared Phase 6 packet. It is useful even before
the paired README refresh lands because it gives that remaining shared-surface
drift a focused, self-tested checker instead of leaving it only in run memory.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
README_PATH = Path("zigux/tests/README.md")

EXPECTED_PRESENT = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "zigux/tests/phase6_bsearch.zig",
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
    "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "zigux/tests/phase6_hexdump.zig",
    "zigux/tests/phase6_hexdump_perf.zig",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
]

EXPECTED_GAPS = [
    "zigux/tests/phase6_base64.zig",
    "zigux/tests/phase6_base64_perf.zig",
    "zigux/tests/fixtures/phase6_base64_vectors.zig",
    "lib/checksum.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
]

REQUIRED_README_SNIPPETS = [
    "current partially blocked base64, bsearch, checksum, and hexdump helper bundle",
    "stay explicit as current public-tree gaps rather than shipped replay evidence",
    "`tests_root_present_entrypoints` should keep the current live tests-root evidence packet explicit",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"expected object in {path}")
    return data


def validate_manifest(manifest: dict[str, object]) -> None:
    present = manifest.get("tests_root_present_entrypoints")
    if present != EXPECTED_PRESENT:
        raise ValidationError(
            "phase6 manifest present-entrypoint packet drifted away from the "
            "current shared tests-root evidence set"
        )

    gaps = manifest.get("tests_root_public_tree_gaps")
    if gaps != EXPECTED_GAPS:
        raise ValidationError(
            "phase6 manifest public-tree gap packet drifted away from the "
            "current blocked base64/checksum surface set"
        )

    note = manifest.get("tests_root_truthfulness_note")
    if not isinstance(note, str) or "tests_root_present_entrypoints" not in note:
        raise ValidationError("phase6 manifest lost the tests-root truthfulness note")


def validate_readme(content: str) -> None:
    for path in EXPECTED_PRESENT:
        if path not in content:
            raise ValidationError(f"tests README missing current Phase 6 evidence marker: {path}")

    for path in EXPECTED_GAPS:
        if path not in content:
            raise ValidationError(f"tests README missing blocked Phase 6 gap marker: {path}")

    for snippet in REQUIRED_README_SNIPPETS:
        if snippet not in content:
            raise ValidationError(f"tests README missing shared Phase 6 summary marker: {snippet}")



def run_checks(repo_root: Path) -> None:
    manifest = read_manifest(repo_root / MANIFEST_PATH)
    validate_manifest(manifest)
    validate_readme(read_text(repo_root / README_PATH))



def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def scaffold(root: Path) -> None:
    write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "tests_root_present_entrypoints": EXPECTED_PRESENT,
                "tests_root_public_tree_gaps": EXPECTED_GAPS,
                "tests_root_truthfulness_note": (
                    "zigux/tests/README.md should keep tests_root_present_entrypoints "
                    "as the current live tests-root evidence packet explicit and keep "
                    "tests_root_public_tree_gaps explicit as missing public-tree files."
                ),
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / README_PATH,
        "\n".join(
            [
                "# zigux/tests",
                "",
                "Phase 6 packet",
                "- the current partially blocked base64, bsearch, checksum, and hexdump helper bundle stays reviewable through the shared surface checker, the direct base64 and checksum C parity scaffolding, the live bsearch comparison-budget replays, the dedicated hexdump replay and perf packet, and the Linux-style shared lane together, while "
                + ", ".join(f"`{path}`" for path in EXPECTED_GAPS[:-1])
                + f", and `{EXPECTED_GAPS[-1]}` stay explicit as current public-tree gaps rather than shipped replay evidence.",
                "- `tests_root_present_entrypoints` should keep the current live tests-root evidence packet explicit, and `tests_root_public_tree_gaps` should keep the missing base64 and checksum helper-owned files explicit until those helper packets return.",
            ]
            + [f"- `{path}`" for path in EXPECTED_PRESENT]
            + [f"- gap `{path}`" for path in EXPECTED_GAPS]
        )
        + "\n",
    )



def assert_failure(root: Path, rel_path: Path, old: str, new: str, marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path}: {old}")
    path.write_text(original.replace(old, new), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if marker not in str(exc):
            raise AssertionError(f"unexpected failure for {rel_path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")



def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold(root)
        run_checks(root)

        assert_failure(
            root,
            MANIFEST_PATH,
            '"zigux/tests/phase6_checksum_c_parity.zig"',
            '"zigux/tests/phase6_checksum.zig"',
            "present-entrypoint packet drifted",
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"zigux/tests/phase6_checksum_perf.zig"',
            '"zigux/tests/phase6_checksum_c_parity.zig"',
            "public-tree gap packet drifted",
        )
        assert_failure(
            root,
            README_PATH,
            "- `zigux/tests/phase6_checksum_c_parity.zig`",
            "- `zigux/tests/phase6_checksum.zig`",
            "tests README missing current Phase 6 evidence marker",
        )
        assert_failure(
            root,
            README_PATH,
            "zigux/tests/phase6_checksum_perf.zig",
            "zigux/tests/phase6_checksum_c_parity.zig",
            "tests README missing blocked Phase 6 gap marker",
        )
        assert_failure(
            root,
            README_PATH,
            "`tests_root_present_entrypoints` should keep the current live tests-root evidence packet explicit",
            "the tests-root packet may summarize any broader helper story it wants",
            "tests README missing shared Phase 6 summary marker",
        )

    print("PHASE6_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE6_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT=6")



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    run_checks(Path(args.repo_root).resolve())
    print("PHASE6_TESTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
