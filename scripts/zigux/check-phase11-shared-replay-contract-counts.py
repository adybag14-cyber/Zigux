#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 shared replay contract count summary."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

DEFAULT_ROOT = (
    Path(__file__).resolve().parents[3]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")

EXPECTED_COUNTS = {
    "build_test_names": 3,
    "shared_test_depend_steps": 0,
    "dedicated_survey_replays": 0,
    "shared_adjunct_replays": 3,
    "shared_adjunct_build_replays": 3,
    "exact_current_checks": 10,
}

REQUIRED_CONTRACT_MARKERS = (
    "3 build test names",
    "0 shared `test_step.dependOn(...)` edges",
    "0 dedicated survey replays",
    "3 shared adjunct proof replays",
    "3 adjunct build replays",
    "10 HVC current-head exact command markers",
    "eight-route proof fan-out explicit",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {path}")
    return value


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    return list(value)


def run_check(root: Path) -> None:
    inventory = read_json(root / INVENTORY_PATH)
    contract = read_text(root / CONTRACT_PATH)

    for label, expected in EXPECTED_COUNTS.items():
        actual = len(expect_string_list(label, inventory.get(label)))
        if actual != expected:
            raise CheckError(f"{label} count mismatch: expected {expected}, found {actual}")

    for marker in REQUIRED_CONTRACT_MARKERS:
        if marker not in contract:
            raise CheckError(f"missing marker in {CONTRACT_PATH}: {marker}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "build_test_names": ["a", "b", "c"],
                "shared_test_depend_steps": [],
                "dedicated_survey_replays": [],
                "shared_adjunct_replays": ["a", "b", "c"],
                "shared_adjunct_build_replays": ["a", "b", "c"],
                "exact_current_checks": [str(i) for i in range(10)],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / CONTRACT_PATH,
        "\n".join(
            [
                "3 build test names",
                "0 shared `test_step.dependOn(...)` edges",
                "0 dedicated survey replays",
                "3 shared adjunct proof replays",
                "3 adjunct build replays",
                "10 HVC current-head exact command markers",
                "eight-route proof fan-out explicit",
            ]
        )
        + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_replay_counts_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        wrong_contract = tmpdir / "wrong_contract"
        shutil.copytree(fixture, wrong_contract, dirs_exist_ok=True)
        write(
            wrong_contract / CONTRACT_PATH,
            read_text(wrong_contract / CONTRACT_PATH).replace(
                "10 HVC current-head exact command markers",
                "8 HVC current-head exact command markers",
                1,
            ),
        )
        expect_failure(wrong_contract, "10 HVC current-head exact command markers")
        case_count += 1

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        inventory = read_json(wrong_inventory / INVENTORY_PATH)
        inventory["exact_current_checks"] = inventory["exact_current_checks"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_inventory, "exact_current_checks count mismatch")
        case_count += 1

        print("PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST=pass")
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_COUNTS=fail: {exc}")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT_COUNTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
