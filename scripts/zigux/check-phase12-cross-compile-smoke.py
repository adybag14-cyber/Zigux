#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 12 cross-compile smoke note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_CROSS_COMPILE_SMOKE"

NOTE_PATH = Path("Documentation/zigux/phase12-cross-compile-smoke.md")
VIRTIO_NET_SURVEY_PATH = Path("Documentation/zigux/phase12-virtio-net-survey.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase12.py")
SYNTAX_LAB_PATH = Path("zigux/tests/phase12_virtio_net_syntax_lab.zig")
SYNTAX_LAB_BUILD_PATH = Path("zigux/tests/phase12_virtio_net_syntax_lab_build.zig")

REQUIRED_FILES = (
    NOTE_PATH,
    VIRTIO_NET_SURVEY_PATH,
    WORKFLOW_PATH,
    BUILD_PATH,
    MAKEFILE_PATH,
    VALIDATOR_PATH,
    SYNTAX_LAB_PATH,
    SYNTAX_LAB_BUILD_PATH,
)

SYNTAX_LAB_NOTE_MARKER = (
    "that same survey note also keeps `zigux/tests/phase12_virtio_net_syntax_lab.zig` "
    "and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` explicit as "
    "surviving standalone compile-smoke companions outside the shared six-file "
    "`phase12-validate` / `phase12-smoke` / `phase12-test` route"
)

NOTE_MARKERS = (
    "- support checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`",
    "the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`",
    "current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
    "current `.github/workflows/zigux-bootstrap.yml` keeps the same shared packet explicit through the build-only checker, the complex-driver lane checker, the cross-compile smoke checker, the release-readiness checker, `scripts/zigux/validate-phase12.py`, the `phase12-smoke` and `phase12-test` wrappers, the aggregate `phase12` route, and the adjacent throughput-parity anchor",
    "current `Documentation/zigux/phase12-virtio-net-survey.md` confirms the older monolithic syntax-lab packet has been replaced by the split helper family and the shared survey gate",
    SYNTAX_LAB_NOTE_MARKER,
    "current `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` also keeps the older `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` vocabulary out of the live packet on `master`",
    "substantive same-family lab progress has therefore landed since the earlier cross-note packet: the shared route is now the six-file split-helper smoke-and-test sextet with returned wrapper evidence rather than the older syntax-lab-era shape",
    "the shipped cross-compile checker now keeps that returned wrapper wording fail-closed across this note, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/phase12_build.zig`",
    "leave the next same-lane follow-through note-local and rerun `scripts/zigux/check-phase12-cross-compile-smoke.py` before widening compile-smoke claims again",
)

SURVEY_MARKERS = (
    "`PHASE12_STATUS=split-helper-packet-present-shared-build-sextet-throughput-review-only`",
    "current `master` now keeps `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper proof for that sextet",
    "current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab.zig`",
    "current `master` now carries `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`",
    "the standalone syntax-lab companion remains compile-smoke evidence beside that sextet, but `zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` are not wired into the shared Phase 12 validate, smoke, or test routes",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
    "run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "phase12-virtio-net-queue-resume-tests",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12-virtio-net-receive-refill-replay-tests",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12-virtio-net-transmit-recycle-tests",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12-virtio-net-post-reset-replay-tests",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12-virtio-net-throughput-parity-tests",
    "phase12_virtio_net_survey.zig",
    "phase12-virtio-net-survey-tests",
)

FORBIDDEN_BUILD_MARKERS = (
    "../../drivers/net/virtio_net.zig",
    '"phase12_virtio_net.zig"',
    "phase12-virtio-net-tests",
    '"phase12_virtio_net_syntax_lab.zig"',
    "phase12-virtio-net-syntax-lab-tests",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
    "scripts/zigux/check-phase12-cross-compile-smoke.py",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

VALIDATOR_MARKERS = (
    'VIRTIO_NET_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-virtio-net-packet.py"',
    'VIRTIO_SCSI_PACKET_CHECKER_PATH = "scripts/zigux/check-phase12-virtio-scsi-packet.py"',
    "for checker_path in PHASE12_PACKET_CHECKERS:",
    "checker_failures.extend(run_checker(args.root, checker_path))",
)

FORBIDDEN_NOTE_MARKERS = (
    "the remaining same-family note drift is shared wording",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    try:
        return (root / relative_path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {relative_path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def require_absent(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker in text:
            raise CheckFailure(f"{label} stale marker present: {marker}")


def check(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            raise CheckFailure(f"missing required file: {relative_path}")

    note_text = read_text(root, NOTE_PATH)
    require_markers(note_text, NOTE_MARKERS, str(NOTE_PATH))
    require_absent(note_text, FORBIDDEN_NOTE_MARKERS, str(NOTE_PATH))
    require_markers(
        read_text(root, VIRTIO_NET_SURVEY_PATH),
        SURVEY_MARKERS,
        str(VIRTIO_NET_SURVEY_PATH),
    )
    require_markers(read_text(root, WORKFLOW_PATH), WORKFLOW_MARKERS, str(WORKFLOW_PATH))
    build_text = read_text(root, BUILD_PATH)
    require_markers(build_text, BUILD_MARKERS, str(BUILD_PATH))
    require_absent(build_text, FORBIDDEN_BUILD_MARKERS, str(BUILD_PATH))
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS, str(MAKEFILE_PATH))
    require_markers(
        read_text(root, VALIDATOR_PATH),
        VALIDATOR_MARKERS,
        str(VALIDATOR_PATH),
    )


def write_fixture(root: Path) -> None:
    files = {
        NOTE_PATH: "\n".join((
            "# Phase 12 Cross Compile Smoke",
            "",
            *NOTE_MARKERS,
            "",
        )),
        VIRTIO_NET_SURVEY_PATH: "\n".join((
            "# Phase 12 Virtio Net Survey",
            "",
            *SURVEY_MARKERS,
            "",
        )),
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        BUILD_PATH: "\n".join(BUILD_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        VALIDATOR_PATH: "\n".join(VALIDATOR_MARKERS) + "\n",
        SYNTAX_LAB_PATH: "// phase12 syntax-lab fixture\n",
        SYNTAX_LAB_BUILD_PATH: "// phase12 syntax-lab build fixture\n",
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-cross-compile-smoke-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        for relative_path in REQUIRED_FILES:
            write_fixture(root)
            (root / relative_path).unlink()
            try:
                check(root)
            except CheckFailure as exc:
                if f"missing required file: {relative_path}" not in str(exc):
                    raise
                cases += 1
            else:
                raise AssertionError(
                    f"expected missing required file failure for {relative_path}"
                )

        write_fixture(root)
        (root / NOTE_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-cross-compile-smoke.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected note marker failure")

        write_fixture(root)
        path = root / NOTE_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(SYNTAX_LAB_NOTE_MARKER, "", 1),
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-cross-compile-smoke.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected syntax-lab note marker failure")

        write_fixture(root)
        (root / VIRTIO_NET_SURVEY_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "phase12-virtio-net-survey.md" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected survey marker failure")

        write_fixture(root)
        (root / WORKFLOW_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if ".github/workflows/zigux-bootstrap.yml" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected workflow marker failure")

        write_fixture(root)
        (root / BUILD_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/phase12_build.zig" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected build marker failure")

        write_fixture(root)
        path = root / BUILD_PATH
        path.write_text(
            path.read_text(encoding="utf-8") + FORBIDDEN_BUILD_MARKERS[-1] + "\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/tests/phase12_build.zig" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected stale build marker failure")

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text("phase12-smoke:\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected makefile marker failure")

        write_fixture(root)
        (root / VALIDATOR_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "scripts/zigux/validate-phase12.py" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected validator marker failure")

        write_fixture(root)
        path = root / NOTE_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                FORBIDDEN_NOTE_MARKERS[0], "unexpected stale wording"
            )
            + FORBIDDEN_NOTE_MARKERS[0]
            + "\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except CheckFailure as exc:
            if "stale marker present" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected stale note marker failure")

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        check(Path(args.root))
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail")
        print(f"{CHECK_NAME}_ERROR={exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    print(f"{CHECK_NAME}_SCOPE=phase12_cross_compile_smoke_truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
