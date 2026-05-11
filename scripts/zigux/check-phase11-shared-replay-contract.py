#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-shared-replay-contract.py"

FILES = {
    "note": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
}

MARKERS = {
    "note": [
        "# Phase 11 Shared Replay Contract",
        "* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
        "* `zigux/tests/phase11_build.zig`",
        "* `make -C zigux phase11`",
        "* no shared `validate-phase11.py`",
        "* no shared `make -C zigux phase11-validate` target on `master`",
        "The dedicated archival HVC evidence still stays explicit beside that shared route:",
        "* `scripts/zigux/check-phase11-header-boundary-packet.py`",
        "* `zigux/tests/phase11_uapi_header_parity_survey.zig`",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "* `zigux/tests/phase11_build.zig`",
        "* `make -C zigux phase11`",
        "* there is no shared `validate-phase11.py`",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
        "* shared header boundary continuity stays with `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, and `zigux/tests/phase11_uapi_header_parity_survey.zig`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "- header-boundary lane `P11-L18` owns `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, and `scripts/zigux/check-phase11-header-boundary-packet.py`",
        "The shared packet surfaces still living together on current `master` are `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `zigux/tests/phase11_build.zig`, and `make -C zigux phase11`.",
        "Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the shared notes, the shared contract checker, the shared `phase11_build.zig` route, and `make -C zigux phase11`, while the driver-local evidence stays with the owning lane.",
        "Keep the current validator posture explicit: there is a shared `zigux/tests/phase11_build.zig` route and a shared `make -C zigux phase11` wrapper on current `master`, but there is no shared `validate-phase11.py`, no shared `zigux/tests/fixtures/phase11_build_inventory.json`, and no shared `make -C zigux phase11-validate` target, so reminder-surface edits should stay aligned with the surviving build-backed packet instead of reviving the older inventory-driven validator story.",
        "Keep the HVC lane honest: on current `master` the landed HVC archival packet is the survey gate, modem-control split, poll-retry split, sysrq helper, teardown note, validation matrix, and dedicated `phase11-hvc-survey` route rather than a missing or purely reminder-only packet.",
    ],
}

SELF_TEST_CASE_COUNT = 6


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


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        expect_markers(label, read_text(root, relative_path), MARKERS[label])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    for label, relative_path in FILES.items():
        write(root / relative_path, "\n".join(MARKERS[label]) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_contract_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        cases = [
            (FILES["note"], MARKERS["note"][2]),
            (FILES["note"], MARKERS["note"][5]),
            (FILES["closure_note"], MARKERS["closure_note"][2]),
            (FILES["closure_note"], MARKERS["closure_note"][6]),
            (FILES["lane_note"], MARKERS["lane_note"][2]),
            (FILES["lane_note"], MARKERS["lane_note"][3]),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(tmpdir, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(path.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_SHARED_REPLAY_CONTRACT=fail: {exc}")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
