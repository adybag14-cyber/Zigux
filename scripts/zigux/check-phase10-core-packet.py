#!/usr/bin/env python3
"""Validate the shared Phase 10 virtio core review packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = (
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "Documentation/zigux/phase10-virtio-core-slice.md",
    "Documentation/zigux/phase10-virtio-core-survey.md",
    "Documentation/zigux/phase10-virtio-driver-lane-sequencing.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase10_build.zig",
    "zigux/tests/phase10_closure_manifest.json",
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_verify.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
    "zigux/tests/phase10_virtio_core_manifest.json",
    "zigux/tests/phase10_virtio_core_survey.zig",
    "zigux/tests/phase10_virtio_driver_id.zig",
)

README_MARKERS = (
    "check-phase10-core-packet.py",
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_verify.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
)

TESTS_README_MARKERS = (
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_verify.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
)

CHECKLIST_MARKERS = (
    "drivers/virtio/virtio.zig",
    "drivers/virtio/virtio_driver_id.zig",
    "drivers/virtio/virtio_verify.zig",
    "zigux/tests/phase10_virtio_core.zig",
    "zigux/tests/phase10_virtio_core_reset_queue.zig",
)

MAKEFILE_MARKERS = (
    "scripts/zigux/check-phase10-core-packet.py --self-test",
    "scripts/zigux/check-phase10-core-packet.py",
)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing required file: {path}")


def _require_paths(root: Path) -> None:
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing:
        joined = "\n".join(f"  - {rel}" for rel in missing)
        raise SystemExit(f"missing required Phase 10 core packet files:\n{joined}")


def _require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = _read_text(path)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        joined = "\n".join(f"  - {marker}" for marker in missing)
        raise SystemExit(f"{path} is missing expected Phase 10 core markers:\n{joined}")


def validate(root: Path) -> None:
    _require_paths(root)
    _require_markers(root / "scripts/zigux/README.md", README_MARKERS)
    _require_markers(root / "zigux/tests/README.md", TESTS_README_MARKERS)
    _require_markers(root / "Documentation/zigux/review-checklist.md", CHECKLIST_MARKERS)
    _require_markers(root / "zigux/Makefile", MAKEFILE_MARKERS)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for rel in REQUIRED_FILES:
            _write(root / rel, "placeholder\n")

        _write(
            root / "scripts/zigux/README.md",
            "\n".join(README_MARKERS) + "\n",
        )
        _write(
            root / "zigux/tests/README.md",
            "\n".join(TESTS_README_MARKERS) + "\n",
        )
        _write(
            root / "Documentation/zigux/review-checklist.md",
            "\n".join(CHECKLIST_MARKERS) + "\n",
        )
        _write(
            root / "zigux/Makefile",
            "\n".join(MAKEFILE_MARKERS) + "\n",
        )
        validate(root)

    print("PHASE10_CORE_PACKET_SELF_TEST=pass")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root to validate",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    validate(args.root.resolve())
    print("phase10 core packet ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
