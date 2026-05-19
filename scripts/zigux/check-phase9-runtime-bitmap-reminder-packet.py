#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SAMPLES_README_PATH = "samples/zigux/README.md"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / REVIEW_CHECKLIST_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

BITMAP_PACKET_ROSTER_MARKER = (
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, "
    "`samples/zigux/runtime_bitmap.zig`, "
    "`samples/zigux/runtime_bitmap_loader.zig`, "
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`, "
    "`zigux/tests/runtime_bitmap_module.zig`, "
    "`zigux/tests/runtime_bitmap_diff.zig`, "
    "`zigux/tests/runtime_bitmap_manifest.json`, and "
    "`zigux/tests/runtime_bitmap_survey.zig`"
)

CHECKLIST_BITMAP_FAMILY_MARKER = (
    "the returned separate runtime bitmap family stays explicit in "
    "`samples/zigux/README.md`, `Documentation/zigux/README.md`, and "
    "`Documentation/zigux/review-checklist.md` through"
)
CHECKLIST_BITMAP_BOUNDARY_MARKER = (
    "keep that bitmap packet framed as a separate bounded Phase 9 runtime family "
    "rather than proof that the broader shared runtime-loader packet returned or "
    "extra Phase 5 evidence landed"
)

LANE_BITMAP_FAMILY_MARKER = (
    "surviving separate runtime bitmap family from public GitHub fallback rereads:"
)
LANE_BITMAP_BOUNDARY_MARKER = (
    "while still framing that bitmap packet as a separate bounded Phase 9 runtime "
    "family rather than as proof that the broader shared runtime-loader packet "
    "returned or that a fifth approved Phase 5 sample family landed here"
)
LANE_BITMAP_GOVERNANCE_MARKER = (
    "keep the separate runtime bitmap family explicit through "
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, "
    "`samples/zigux/runtime_bitmap.zig`, "
    "`samples/zigux/runtime_bitmap_loader.zig`, "
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`, "
    "`zigux/tests/runtime_bitmap_module.zig`, "
    "`zigux/tests/runtime_bitmap_diff.zig`, "
    "`zigux/tests/runtime_bitmap_manifest.json`, and "
    "`zigux/tests/runtime_bitmap_survey.zig`"
)

SAMPLES_BITMAP_FAMILY_MARKER = "the separate runtime bitmap family on current `master`:"
SAMPLES_BITMAP_BOUNDARY_MARKER = (
    "Keep that returned bitmap packet framed as a separate Phase 9 runtime family "
    "rather than as directly readable neighboring proof that the broader shared "
    "runtime-loader packet returned or as evidence that a fifth approved Phase 5 "
    "sample family landed here."
)
SAMPLES_PHASE5_BITMAP_BOUNDARY_MARKER = (
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample"
)

FILE_MARKERS = {
    REVIEW_CHECKLIST_PATH: [
        CHECKLIST_BITMAP_FAMILY_MARKER,
        BITMAP_PACKET_ROSTER_MARKER,
        CHECKLIST_BITMAP_BOUNDARY_MARKER,
    ],
    LANE_SEQUENCING_PATH: [
        LANE_BITMAP_FAMILY_MARKER,
        BITMAP_PACKET_ROSTER_MARKER,
        LANE_BITMAP_GOVERNANCE_MARKER,
        LANE_BITMAP_BOUNDARY_MARKER,
    ],
    SAMPLES_README_PATH: [
        SAMPLES_BITMAP_FAMILY_MARKER,
        BITMAP_PACKET_ROSTER_MARKER,
        SAMPLES_BITMAP_BOUNDARY_MARKER,
        SAMPLES_PHASE5_BITMAP_BOUNDARY_MARKER,
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text(rel_path: str, markers: list[str]) -> str:
    if rel_path.endswith(".md"):
        return "\n".join(["# fixture", "", *markers, ""])
    return "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(base / rel_path, build_fixture_text(rel_path, markers))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-bitmap-reminder-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                if marker not in current:
                    raise SystemExit(
                        f"fixture missing expected marker before mutation: {rel_path}:{marker}"
                    )
                write_text(base / rel_path, current.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SELF_TEST=pass")
        print(
            "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_CHECKLIST_MARKER_COUNT="
            f"{len(FILE_MARKERS[REVIEW_CHECKLIST_PATH])}"
        )
        print(
            "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_LANE_SEQUENCING_MARKER_COUNT="
            f"{len(FILE_MARKERS[LANE_SEQUENCING_PATH])}"
        )
        print(
            "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SAMPLES_README_MARKER_COUNT="
            f"{len(FILE_MARKERS[SAMPLES_README_PATH])}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_RUNTIME_BITMAP_REMINDER_PACKET=pass")
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_CHECKLIST_MARKER_COUNT="
        f"{len(FILE_MARKERS[REVIEW_CHECKLIST_PATH])}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_LANE_SEQUENCING_MARKER_COUNT="
        f"{len(FILE_MARKERS[LANE_SEQUENCING_PATH])}"
    )
    print(
        "PHASE9_RUNTIME_BITMAP_REMINDER_PACKET_SAMPLES_README_MARKER_COUNT="
        f"{len(FILE_MARKERS[SAMPLES_README_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
