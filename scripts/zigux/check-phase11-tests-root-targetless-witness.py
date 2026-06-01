#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 11 tests-root targetless witness reminder."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 3 else Path.cwd()

COMPANION_PATH = Path(
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
)
TESTS_README_PATH = Path("zigux/tests/README.md")

WITNESS_CHECKER = "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`"
WITNESS_REPLAY = "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`"
WITNESS_BUILD = "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`"
CLEANUP_CHECKER = "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`"

REQUIRED_MARKERS = {
    COMPANION_PATH: (
        WITNESS_CHECKER,
        WITNESS_REPLAY,
        WITNESS_BUILD,
        CLEANUP_CHECKER,
        "targetless-unregister witness",
    ),
    TESTS_README_PATH: (
        WITNESS_CHECKER,
        WITNESS_REPLAY,
        WITNESS_BUILD,
        CLEANUP_CHECKER,
        "targetless-unregister witness",
    ),
}


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise ValidationError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            if marker not in text:
                raise ValidationError(
                    f"{relative_path} is missing required marker: {marker}"
                )


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_repo(root: Path) -> None:
    write_text(
        root,
        COMPANION_PATH,
        "\n".join(
            (
                "# companion",
                "Keep the current bounded simple-driver packet explicit.",
                CLEANUP_CHECKER,
                WITNESS_CHECKER,
                WITNESS_REPLAY,
                WITNESS_BUILD,
                "Keep the targetless-unregister witness packet explicit.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        TESTS_README_PATH,
        "\n".join(
            (
                "# tests",
                "Phase 11 reminder packet",
                CLEANUP_CHECKER,
                WITNESS_CHECKER,
                WITNESS_REPLAY,
                WITNESS_BUILD,
                "The targetless-unregister witness stays explicit in the shared packet.",
            )
        )
        + "\n",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase11_tests_root_targetless_") as tmpdir:
        root = Path(tmpdir)
        populate_repo(root)
        validate(root)

        companion_path = root / COMPANION_PATH
        companion_path.write_text(
            companion_path.read_text(encoding="utf-8").replace(WITNESS_CHECKER + "\n", ""),
            encoding="utf-8",
        )
        try:
            validate(root)
        except ValidationError:
            pass
        else:
            raise AssertionError("expected missing witness checker marker to fail")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed when the shared Phase 11 tests-root reminder surfaces stop "
            "naming the HVC targetless-unregister witness checker."
        )
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.self_test:
        run_self_test()
        print("PHASE11_TESTS_ROOT_TARGETLESS_WITNESS_SELF_TEST=pass")
        print("PHASE11_TESTS_ROOT_TARGETLESS_WITNESS_SELF_TEST_CASE_COUNT=2")
        return 0

    if args.write_sample_root is not None:
        sample_root = args.write_sample_root.resolve()
        if sample_root.exists():
            shutil.rmtree(sample_root)
        populate_repo(sample_root)
        print(sample_root)
        return 0

    try:
        validate(args.root.resolve())
    except ValidationError as exc:
        print(f"PHASE11_TESTS_ROOT_TARGETLESS_WITNESS=fail: {exc}")
        return 1

    print("PHASE11_TESTS_ROOT_TARGETLESS_WITNESS=pass")
    print(f"PHASE11_TESTS_ROOT_TARGETLESS_WITNESS_REQUIRED_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE11_TESTS_ROOT_TARGETLESS_WITNESS_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
