#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parent

README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
RELEASE_READINESS_PATH = Path("Documentation/zigux/phase12-release-readiness-survey.md")

README_MARKERS = [
    "Phase 12 notes - `Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12` keep the shipped validator-first then smoke-first release order visible",
]

REVIEW_MARKERS = [
    "if the change touches the shared Phase 12 complex-driver packet",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared fallback, survey, verify-shard, or anti-overlap notes until they actually land on `master`",
    "avoid implying a broader shared `check-phase12-*.py` family",
    "the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route",
]

RELEASE_READINESS_MARKERS = [
    "support-bundle cross companion: `scripts/zigux/check-phase12-cross.py`",
    "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "`Documentation/zigux/phase12-libbpf-verify-shard-note.md`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "Keep the same degraded-workflow validation quartet explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-cross.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate`",
    "The public fallback split must stay explicit: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact",
]


def read_text(root: Path, rel_path: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files: list[str] = []
    missing_markers: list[str] = []

    for rel_path in (README_PATH, REVIEW_CHECKLIST_PATH, RELEASE_READINESS_PATH):
        if not (root / rel_path).exists():
            missing_files.append(str(rel_path))

    if missing_files:
        return missing_files, missing_markers

    readme_text = read_text(root, README_PATH)
    for marker in README_MARKERS:
        if marker not in readme_text:
            missing_markers.append(f"README.md:{marker}")

    review_text = read_text(root, REVIEW_CHECKLIST_PATH)
    for marker in REVIEW_MARKERS:
        if marker not in review_text:
            missing_markers.append(f"review-checklist.md:{marker}")

    release_readiness_text = read_text(root, RELEASE_READINESS_PATH)
    for marker in RELEASE_READINESS_MARKERS:
        if marker not in release_readiness_text:
            missing_markers.append(f"phase12-release-readiness-survey.md:{marker}")

    return missing_files, missing_markers


def write_fixture(root: Path) -> None:
    (root / README_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / REVIEW_CHECKLIST_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / RELEASE_READINESS_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / README_PATH).write_text("\n".join(README_MARKERS) + "\n", encoding="utf-8")
    (root / REVIEW_CHECKLIST_PATH).write_text("\n".join(REVIEW_MARKERS) + "\n", encoding="utf-8")
    (root / RELEASE_READINESS_PATH).write_text("\n".join(RELEASE_READINESS_MARKERS) + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(old, new, 1)
    if updated == text:
        raise SystemExit(f"failed to mutate fixture: {path}:{old}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_docs_root_routes_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        write_fixture(root)

        missing_files, missing_markers = validate(root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase12-docs-root-routes:self-test:baseline_failed:"
                f"files={','.join(missing_files) or 'none'}:"
                f"markers={','.join(missing_markers) or 'none'}"
            )

        replace_once(
            root / README_PATH,
            "`scripts/zigux/check-phase12-release-readiness-packet.py`",
            "`scripts/zigux/check-phase12-release-readiness-old.py`",
        )
        _, missing_markers = validate(root)
        expected = "README.md:`scripts/zigux/check-phase12-release-readiness-packet.py`"
        if expected not in missing_markers:
            raise SystemExit("phase12-docs-root-routes:self-test:readme_marker_detection")

        write_fixture(root)
        replace_once(
            root / REVIEW_CHECKLIST_PATH,
            "avoid implying a broader shared `check-phase12-*.py` family",
            "allow a broad checker family",
        )
        _, missing_markers = validate(root)
        expected = "review-checklist.md:avoid implying a broader shared `check-phase12-*.py` family"
        if expected not in missing_markers:
            raise SystemExit("phase12-docs-root-routes:self-test:review_marker_detection")

        write_fixture(root)
        replace_once(
            root / RELEASE_READINESS_PATH,
            "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
            "support checker: `scripts/zigux/check-phase12-release-readiness-old.py`",
        )
        _, missing_markers = validate(root)
        expected = "phase12-release-readiness-survey.md:support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`"
        if expected not in missing_markers:
            raise SystemExit("phase12-docs-root-routes:self-test:release_readiness_marker_detection")

        write_fixture(root)
        (root / REVIEW_CHECKLIST_PATH).unlink()
        missing_files, _ = validate(root)
        if str(REVIEW_CHECKLIST_PATH) not in missing_files:
            raise SystemExit("phase12-docs-root-routes:self-test:missing_file_detection")

    print("PHASE12_DOCS_ROOT_ROUTES_SELF_TEST=pass")
    print("PHASE12_DOCS_ROOT_ROUTES_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed if the shared Phase 12 docs-root packet drops the shipped release-route, release-readiness, or parked libbpf boundary markers."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE12_DOCS_ROOT_ROUTES=fail")
        print("PHASE12_DOCS_ROOT_ROUTES_MISSING_FILES_START")
        for item in missing_files:
            print(item)
        print("PHASE12_DOCS_ROOT_ROUTES_MISSING_FILES_END")
        return 1

    if missing_markers:
        print("PHASE12_DOCS_ROOT_ROUTES=fail")
        print("PHASE12_DOCS_ROOT_ROUTES_MISSING_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("PHASE12_DOCS_ROOT_ROUTES_MISSING_MARKERS_END")
        return 1

    print("PHASE12_DOCS_ROOT_ROUTES=pass")
    print(f"PHASE12_DOCS_ROOT_ROUTES_REQUIRED_FILE_COUNT=3")
    print(
        "PHASE12_DOCS_ROOT_ROUTES_REQUIRED_MARKER_COUNT="
        f"{len(README_MARKERS) + len(REVIEW_MARKERS) + len(RELEASE_READINESS_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
