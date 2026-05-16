#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


FILES = {
    "contract_note": "Documentation/zigux/phase11-shared-replay-contract.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "tests_companion": "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
}

REQUIRED_MARKERS = {
    "contract_note": [
        "# Phase 11 Shared Replay Contract",
        "direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig`",
        "direct GitHub contents reads now materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "`make -C zigux phase11-contract`",
        "`make -C zigux phase11`",
        "`make -C zigux phase11-hvc-survey`",
        "no shared `validate-phase11.py`",
        "no shared `make -C zigux phase11-validate` target on `master`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`make -C zigux phase11-contract`",
        "Current `master` now directly materializes `zigux/tests/phase11_build.zig` and `zigux/tests/fixtures/phase11_build_inventory.json`",
        "there is no shared `validate-phase11.py`",
    ],
    "tests_companion": [
        "## Phase 11 tests-root packet",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "Direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig` and the shared `zigux/tests/fixtures/phase11_build_inventory.json` anchor",
        "`make -C zigux phase11-contract`",
        "`make -C zigux phase11-hvc-survey`",
    ],
    "review_checklist": [
        "if the change touches the shared Phase 11 simple-driver packet",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`zigux/tests/phase11_build.zig`",
        "`make -C zigux phase11-contract`",
        "`make -C zigux phase11`",
        "`make -C zigux phase11-hvc-survey`",
        "without implying removed validators or a shared `make -C zigux phase11-validate` route?",
    ],
}

FORBIDDEN_MARKERS = {
    "contract_note": [
        "can still return 404 for `zigux/tests/phase11_build.zig`",
        "the direct contents bridge still 404s",
        "fallback-only wording",
    ],
    "lane_note": [
        "fallback-only evidence",
    ],
    "tests_companion": [
        "repo-reality gaps",
        "fallback-only wording",
    ],
}


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_forbidden_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, REQUIRED_MARKERS[label])
        expect_forbidden_absent(label, text)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    for label, relative_path in FILES.items():
        lines = REQUIRED_MARKERS[label]
        write(root / relative_path, "\n".join(lines) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_direct_read_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_fixture(fixture_root)
        run_check(fixture_root)

        required_cases = [
            (FILES["contract_note"], REQUIRED_MARKERS["contract_note"][1]),
            (FILES["contract_note"], REQUIRED_MARKERS["contract_note"][2]),
            (FILES["contract_note"], REQUIRED_MARKERS["contract_note"][7]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][3]),
            (FILES["tests_companion"], REQUIRED_MARKERS["tests_companion"][5]),
            (FILES["review_checklist"], REQUIRED_MARKERS["review_checklist"][10]),
        ]
        for idx, (relative_path, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            ("contract_note", FORBIDDEN_MARKERS["contract_note"][0]),
            ("contract_note", FORBIDDEN_MARKERS["contract_note"][1]),
            ("tests_companion", FORBIDDEN_MARKERS["tests_companion"][1]),
        ]
        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST=pass")
        print(
            "PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST_CASE_COUNT="
            f"{len(required_cases) + len(forbidden_cases)}"
        )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_SHARED_DIRECT_READ_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
