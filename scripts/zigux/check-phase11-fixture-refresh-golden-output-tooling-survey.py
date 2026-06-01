#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 11 deterministic tooling gap note."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()

NOTE_PATH = Path("Documentation/zigux/phase11-fixture-refresh-golden-output-tooling-survey.md")
CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
MATRIX_SURVEY_PATH = Path("Documentation/zigux/phase11-validation-matrix-gap-survey.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_NOTE_MARKERS = (
    "`PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_STATUS=deterministic_gap_open`",
    "`make -C zigux phase11-validate` is the surviving shared Makefile route on",
    "`zigux/tests/fixtures/phase11_build_inventory.json` truthfully records the",
    "No shared Phase 11 fixture-refresh manifest currently records which simple",
    "No shared Phase 11 golden-output checker or expectation catalog currently",
    "Current `master` does not materialize `make -C zigux phase11`,",
)

REQUIRED_CONTRACT_MARKERS = (
    "`zigux/Makefile` now materializes `make -C zigux phase11-validate`",
    "`zigux/tests/phase11_build.zig` is not part of the current shared packet",
    "no shared `zigux/tests/phase11_build.zig` replay route on current `master`",
)

REQUIRED_MATRIX_MARKERS = (
    "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
    "That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap on current `master`",
)

EXPECTED_COUNTS = {
    "build_test_names": 3,
    "shared_test_depend_steps": 0,
    "dedicated_survey_replays": 0,
    "shared_adjunct_build_replays": 3,
    "exact_current_checks": 11,
}


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {path}")
    return payload


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    return list(value)


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = read_text(path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {path}: {marker}")


def require_makefile_routes(path: Path) -> None:
    lines = read_text(path).splitlines()
    stripped = {line.strip() for line in lines}
    if "phase11-validate:" not in stripped:
        raise CheckError("missing phase11-validate route in zigux/Makefile")
    if "phase11:" in stripped:
        raise CheckError("unexpected aggregate phase11 route in zigux/Makefile")
    if "phase11-contract:" in stripped:
        raise CheckError("unexpected phase11-contract route in zigux/Makefile")


def run_check(root: Path) -> None:
    require_markers(root / NOTE_PATH, REQUIRED_NOTE_MARKERS)
    require_markers(root / CONTRACT_PATH, REQUIRED_CONTRACT_MARKERS)
    require_markers(root / MATRIX_SURVEY_PATH, REQUIRED_MATRIX_MARKERS)
    require_makefile_routes(root / MAKEFILE_PATH)

    inventory = read_json(root / INVENTORY_PATH)
    for label, expected in EXPECTED_COUNTS.items():
        actual = len(expect_string_list(label, inventory.get(label)))
        if actual != expected:
            raise CheckError(f"{label} count mismatch: expected {expected}, found {actual}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / NOTE_PATH, (Path(__file__).resolve().parents[2] / NOTE_PATH).read_text(encoding="utf-8"))
    write(
        root / CONTRACT_PATH,
        "\n".join(
            [
                "`zigux/Makefile` now materializes `make -C zigux phase11-validate`",
                "`zigux/tests/phase11_build.zig` is not part of the current shared packet",
                "no shared `zigux/tests/phase11_build.zig` replay route on current `master`",
            ]
        )
        + "\n",
    )
    write(
        root / MATRIX_SURVEY_PATH,
        "\n".join(
            [
                "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
                "That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap on current `master`",
            ]
        )
        + "\n",
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "build_test_names": ["a", "b", "c"],
                "shared_test_depend_steps": [],
                "dedicated_survey_replays": [],
                "shared_adjunct_build_replays": ["one", "two", "three"],
                "exact_current_checks": [str(i) for i in range(11)],
            },
            indent=2,
        )
        + "\n",
    )
    write(root / MAKEFILE_PATH, "phase11-validate:\n\t@echo ok\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_fixture_refresh_golden_output_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        inventory = read_json(wrong_inventory / INVENTORY_PATH)
        inventory["exact_current_checks"] = inventory["exact_current_checks"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_inventory, "exact_current_checks count mismatch")
        case_count += 1

        wrong_makefile = tmpdir / "wrong_makefile"
        shutil.copytree(fixture, wrong_makefile, dirs_exist_ok=True)
        write(wrong_makefile / MAKEFILE_PATH, "phase11-validate:\n\t@echo ok\nphase11:\n\t@echo bad\n")
        expect_failure(wrong_makefile, "unexpected aggregate phase11 route")
        case_count += 1

        wrong_note = tmpdir / "wrong_note"
        shutil.copytree(fixture, wrong_note, dirs_exist_ok=True)
        write(
            wrong_note / NOTE_PATH,
            read_text(wrong_note / NOTE_PATH).replace(
                "No shared Phase 11 golden-output checker or expectation catalog currently",
                "No shared Phase 11 output checker currently",
                1,
            ),
        )
        expect_failure(wrong_note, "No shared Phase 11 golden-output checker or expectation catalog")
        case_count += 1

        print("PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_SURVEY_SELF_TEST=pass")
        print(f"PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_fixture(args.write_sample_root.resolve())
        print(f"PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_SURVEY_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_SURVEY=fail: {exc}")
        return 1

    print("PHASE11_FIXTURE_REFRESH_GOLDEN_OUTPUT_TOOLING_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())