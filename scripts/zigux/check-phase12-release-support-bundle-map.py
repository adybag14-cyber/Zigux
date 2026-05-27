#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 12 release support-bundle map."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

CHECK_NAME = "PHASE12_RELEASE_SUPPORT_BUNDLE_MAP"

NOTE_PATH = Path("Documentation/zigux/phase12-release-support-bundle-map.md")
BUILD_ONLY_CHECKER_PATH = Path("scripts/zigux/check-build-only-phase12-surface.py")
BUILD_INVENTORY_CHECKER_PATH = Path("scripts/zigux/check-phase12-build-inventory.py")
READINESS_CHECKER_PATH = Path("scripts/zigux/check-phase12-release-readiness-packet.py")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase12.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
BUILD_PATH = Path("zigux/tests/phase12_build.zig")

REQUIRED_FILES = (
    NOTE_PATH,
    BUILD_ONLY_CHECKER_PATH,
    BUILD_INVENTORY_CHECKER_PATH,
    READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    BUILD_PATH,
)

NOTE_MARKERS = (
    "- lane owner: `pmo-release`",
    "- `scripts/zigux/check-build-only-phase12-surface.py`",
    "- `scripts/zigux/check-phase12-build-inventory.py`",
    "- `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "- `make -C zigux phase12-validate`",
    "- `make -C zigux phase12-smoke`",
    "- `make -C zigux phase12-test`",
    "- `make -C zigux phase12`",
    "- the shared smoke-and-test route is still the six-file `virtio_net` packet wired through `zigux/tests/phase12_build.zig`",
)

WORKFLOW_MARKERS = (
    "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "run: python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
    "run: python3 scripts/zigux/check-phase12-build-inventory.py",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "run: python3 scripts/zigux/validate-phase12.py",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: make -C zigux phase12",
)

MAKEFILE_MARKERS = (
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

BUILD_MARKERS = (
    "phase12_virtio_net_queue_resume.zig",
    "phase12_virtio_net_receive_refill_replay.zig",
    "phase12_virtio_net_transmit_recycle.zig",
    "phase12_virtio_net_post_reset_replay.zig",
    "phase12_virtio_net_throughput_parity.zig",
    "phase12_virtio_net_survey.zig",
)


class CheckFailure(RuntimeError):
    pass


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CheckFailure(f"missing file: {path}") from exc


def require_markers(text: str, markers: tuple[str, ...], label: Path) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckFailure(f"{label} missing marker: {marker}")


def check(root: Path) -> None:
    for path in REQUIRED_FILES:
        if not (root / path).is_file():
            raise CheckFailure(f"missing required file: {path}")

    require_markers(read_text(root, NOTE_PATH), NOTE_MARKERS, NOTE_PATH)
    require_markers(read_text(root, WORKFLOW_PATH), WORKFLOW_MARKERS, WORKFLOW_PATH)
    require_markers(read_text(root, MAKEFILE_PATH), MAKEFILE_MARKERS, MAKEFILE_PATH)
    require_markers(read_text(root, BUILD_PATH), BUILD_MARKERS, BUILD_PATH)


def write_fixture(root: Path) -> None:
    fixtures = {
        NOTE_PATH: "\n".join(
            [
                "# Phase 12 Release Support Bundle Map",
                "",
                *NOTE_MARKERS,
                "",
            ]
        ),
        BUILD_ONLY_CHECKER_PATH: "#!/usr/bin/env python3\n",
        BUILD_INVENTORY_CHECKER_PATH: "#!/usr/bin/env python3\n",
        READINESS_CHECKER_PATH: "#!/usr/bin/env python3\n",
        VALIDATOR_PATH: "#!/usr/bin/env python3\n",
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
        BUILD_PATH: "\n".join(BUILD_MARKERS) + "\n",
    }
    for path, text in fixtures.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        check(root)
    except CheckFailure as exc:
        if expected_fragment not in str(exc):
            raise
        return
    raise AssertionError(f"expected failure containing: {expected_fragment}")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="phase12-release-support-bundle-map-") as tmp:
        root = Path(tmp)

        write_fixture(root)
        check(root)
        cases += 1

        write_fixture(root)
        (root / NOTE_PATH).write_text("# broken\n", encoding="utf-8")
        expect_failure(root, str(NOTE_PATH))
        cases += 1

        write_fixture(root)
        (root / BUILD_INVENTORY_CHECKER_PATH).unlink()
        expect_failure(root, str(BUILD_INVENTORY_CHECKER_PATH))
        cases += 1

        write_fixture(root)
        (root / WORKFLOW_PATH).write_text("run: python3 scripts/zigux/validate-phase12.py\n", encoding="utf-8")
        expect_failure(root, str(WORKFLOW_PATH))
        cases += 1

        write_fixture(root)
        (root / MAKEFILE_PATH).write_text("phase12-smoke:\n", encoding="utf-8")
        expect_failure(root, str(MAKEFILE_PATH))
        cases += 1

        write_fixture(root)
        (root / BUILD_PATH).write_text("phase12_virtio_net_queue_resume.zig\n", encoding="utf-8")
        expect_failure(root, str(BUILD_PATH))
        cases += 1

    print(f"{CHECK_NAME}_SELF_TEST=pass")
    print(f"{CHECK_NAME}_SELF_TEST_CASES={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run fixture-backed self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        check(args.root)
    except CheckFailure as exc:
        print(f"{CHECK_NAME}=fail:{exc}")
        return 1

    print(f"{CHECK_NAME}=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
