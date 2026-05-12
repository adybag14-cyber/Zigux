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
        "* `scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "* direct GitHub contents reads do not materialize `zigux/tests/phase11_build.zig`",
        "* direct GitHub contents reads also do not materialize the previously referenced direct replay files `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
        "* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, but treat them as reminder-only configuration markers until the missing Phase 11 build file and direct replay files land again",
        "* no shared `validate-phase11.py`",
        "* no shared `make -C zigux phase11-validate` target on `master`",
        "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* no materialized shared build-backed replay route on current `master`",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "* direct GitHub contents reads do not materialize `zigux/tests/phase11_build.zig`",
        "* direct GitHub contents reads also do not materialize the previously referenced direct replay files `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
        "* the `phase11` and `phase11-hvc-survey` routes still exist in `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml`, but until the missing build file returns those routes are reminder markers rather than direct replay evidence",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
        "* no landed shared build-backed replay route",
        "* no landed direct watchdog or HVC replay packet on current `master`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "* shared sequencing lane `P11-Y06` owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, and `scripts/zigux/check-phase11-shared-summary-surfaces.py`, plus the shared Phase 11 route markers in `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml`",
        "* DesignWare lane `P11-L10` owns DesignWare reminder-note and checker follow-through; treat direct DesignWare Zig replay files as repo-reality gaps until they are materialized again on `master`",
        "* HVC archival packet lane `P11-L16` owns HVC reminder-note and checker follow-through; treat direct HVC Zig replay files plus `drivers/tty/hvc/hvc_console_verify.zig` as repo-reality gaps until they are materialized again on `master`",
        "Direct GitHub contents reads do not currently materialize `zigux/tests/phase11_build.zig` or the previously referenced direct watchdog and HVC replay files, so the shared sequencing lane must keep treating those paths as repo-reality gaps rather than as shipped replay evidence.",
        "4. Keep the current validator posture explicit: there is no shared `validate-phase11.py`, no shared `zigux/tests/fixtures/phase11_build_inventory.json`, and no materialized shared `zigux/tests/phase11_build.zig` on current `master`, so reminder-surface edits should stay aligned with the surviving reminder packet instead of reviving an unshipped build-backed replay story.",
    ],
}

FORBIDDEN_MARKERS = {
    "note": [
        "The active shared Phase 11 packet is currently reviewable through these shared surfaces:",
        "These shared surfaces keep the build-backed replay route explicit without implying a broader validator stack than the current shipped checkers and surveys.",
        "the shared `zigux/tests/phase11_build.zig` replay currently runs exactly",
        "Treat `Documentation/zigux/phase11-hvc-console-teardown-note.md` together with `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`",
    ],
    "closure_note": [
        "These surfaces are the shared Phase 11 closure packet this note treats as fail-closed today.",
        "* shared replay route: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
        "* shared make route: `make -C zigux phase11`",
        "* the dedicated archival HVC route remains separate so the shared packet does not overclaim notifier, khvcd, sysrq, or host-backed execution coverage",
    ],
    "lane_note": [
        "- HVC archival packet lane `P11-L16` owns `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`",
        "8. Keep the HVC split honest: on current `master` the landed HVC archival packet is the teardown note, validation matrix, survey note, direct `zigux/tests/phase11_hvc_console.zig` plus `zigux/tests/phase11_hvc_cleanup.zig` replays",
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


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, MARKERS[label])
        expect_forbidden_markers_absent(label, text)


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
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        cases = [
            (FILES["note"], MARKERS["note"][3]),
            (FILES["note"], MARKERS["note"][5]),
            (FILES["note"], MARKERS["note"][9]),
            (FILES["closure_note"], MARKERS["closure_note"][3]),
            (FILES["closure_note"], MARKERS["closure_note"][6]),
            (FILES["lane_note"], MARKERS["lane_note"][1]),
            (FILES["lane_note"], MARKERS["lane_note"][3]),
            (FILES["lane_note"], MARKERS["lane_note"][4]),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            ("note", FORBIDDEN_MARKERS["note"][2]),
            ("closure_note", FORBIDDEN_MARKERS["closure_note"][1]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][1]),
        ]

        for label, marker in forbidden_cases:
            case_root = tmpdir / f"forbidden_{label}_{abs(hash(marker))}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT=11")
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
