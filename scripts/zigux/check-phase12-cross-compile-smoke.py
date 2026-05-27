#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 12 cross-compile smoke note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


CHECK_NAME = "PHASE12_CROSS_COMPILE_SMOKE"

NOTE_PATH = Path("Documentation/zigux/phase12-cross-compile-smoke.md")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = (
    NOTE_PATH,
    MAKEFILE_PATH,
)

NOTE_MARKERS = (
    "- support checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`",
    "the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`",
    "current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, `make -C zigux phase12-virtio-net-syntax-lab-test`, and `make -C zigux phase12-virtio-net-throughput-parity-test`",
    "the isolated syntax-lab rerun handles are `zig build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all` and `make -C zigux phase12-virtio-net-syntax-lab-test`, so the companion stays reviewable without joining the shared packet",
    "the dedicated throughput-parity rerun handles are `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-virtio-net-throughput-parity-test`, so the perf-focused replay stays reviewable without widening the shared packet",
    "the shipped cross-compile checker now keeps that returned wrapper wording plus the isolated syntax-lab rerun hook and the dedicated throughput-parity rerun hook fail-closed across this note and `zigux/Makefile`",
    "If only the isolated syntax-lab rerun hook or the dedicated throughput-parity rerun hook drifts, repair just that narrower rerun handle around `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and this note instead of widening the shared packet.",
)

MAKEFILE_MARKERS = (
    "phase12-virtio-net-syntax-lab-test:",
    "$(ZIG) build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all",
    "phase12-virtio-net-throughput-parity-test:",
    "$(ZIG) build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-validate phase12-smoke phase12-test",
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
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS, str(MAKEFILE_PATH))


def write_fixture(root: Path) -> None:
    files = {
        NOTE_PATH: "\n".join((
            "# Phase 12 Cross Compile Smoke",
            "",
            *NOTE_MARKERS,
            "",
        )),
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
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
        (root / MAKEFILE_PATH).write_text("broken\n", encoding="utf-8")
        try:
            check(root)
        except CheckFailure as exc:
            if "zigux/Makefile" not in str(exc):
                raise
            cases += 1
        else:
            raise AssertionError("expected makefile marker failure")

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
