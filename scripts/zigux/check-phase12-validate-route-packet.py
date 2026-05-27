#!/usr/bin/env python3
"""Fail closed on the returned Phase 12 validate-route packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase12-complex-driver-lane-sequencing.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase12.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_MARKERS = {
    DOC_PATH: [
        "make -C zigux phase12-validate",
        "make -C zigux phase12-smoke",
        "make -C zigux phase12-test",
        "make -C zigux phase12",
        "scripts/zigux/validate-phase12.py",
    ],
    VALIDATOR_PATH: [
        "PHASE12_PACKET_CHECKERS = (",
        "VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH",
        "VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH",
        "make -C zigux phase12-validate",
        "scripts-side support packet",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    WORKFLOW_PATH: [
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 smoke packet",
        "run: make -C zigux phase12-smoke",
        "- name: Run current Phase 12 shared test packet",
        "run: make -C zigux phase12-test",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: [
        "phase12: phase12-smoke phase12-test",
    ],
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        if not path.is_file():
            failures.append(f"missing required file: {relative_path.as_posix()}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(
                    f"{relative_path.as_posix()}: missing marker: {marker}"
                )

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        path = root / relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(
                    f"{relative_path.as_posix()}: forbidden stale marker: {marker}"
                )
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_fixture_root(root: Path) -> None:
    write_text(
        root / DOC_PATH,
        "\n".join(
            [
                "# Phase 12 Complex-Driver Lane Sequencing",
                *REQUIRED_MARKERS[DOC_PATH],
            ]
        )
        + "\n",
    )
    write_text(
        root / VALIDATOR_PATH,
        "\n".join(
            [
                "PHASE12_PACKET_CHECKERS = (",
                "    VIRTIO_SCSI_ROLLBACK_COVERAGE_CHECKER_PATH,",
                "    VIRTIO_SCSI_REPEATED_ROLLBACK_PACKET_CHECKER_PATH,",
                ")",
                "make -C zigux phase12-validate",
                "scripts-side support packet",
            ]
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE_PATH,
        "\n".join(REQUIRED_MARKERS[MAKEFILE_PATH]) + "\n",
    )
    write_text(
        root / WORKFLOW_PATH,
        "\n".join(REQUIRED_MARKERS[WORKFLOW_PATH]) + "\n",
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase12-validate-route-packet-") as tmp:
        root = Path(tmp)
        write_fixture_root(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            print("PHASE12_VALIDATE_ROUTE_PACKET_SELF_TEST=fail")
            return 1

        makefile_text = (root / MAKEFILE_PATH).read_text(encoding="utf-8")
        (root / MAKEFILE_PATH).write_text(
            makefile_text.replace(
                "phase12: phase12-validate phase12-smoke phase12-test",
                "phase12: phase12-smoke phase12-test",
            ),
            encoding="utf-8",
        )
        failures = validate(root)
        expected = (
            "zigux/Makefile: missing marker: "
            "phase12: phase12-validate phase12-smoke phase12-test"
        )
        forbidden = (
            "zigux/Makefile: forbidden stale marker: "
            "phase12: phase12-smoke phase12-test"
        )
        if expected not in failures or forbidden not in failures:
            print("self-test did not catch aggregate route drift", file=sys.stderr)
            print("PHASE12_VALIDATE_ROUTE_PACKET_SELF_TEST=fail")
            return 1

    print("PHASE12_VALIDATE_ROUTE_PACKET_SELF_TEST=pass")
    print("PHASE12_VALIDATE_ROUTE_PACKET_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(Path(args.root))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Phase 12 validate-route packet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
