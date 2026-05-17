#!/usr/bin/env python3
"""Validate the Phase 12 build-only release surfaces stay aligned."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

PHASE12_ROOT = Path("Documentation/zigux")
PHASE12_RELEASE_MATRIX_PATH = PHASE12_ROOT / "phase12-release-coordination-matrix.md"
PHASE12_RELEASE_READINESS_PATH = PHASE12_ROOT / "phase12-release-readiness-survey.md"
PHASE12_RELEASE_SEQUENCING_PATH = PHASE12_ROOT / "phase12-release-sequencing.md"
PHASE12_RAW_GITHUB_SURVEY_PATH = PHASE12_ROOT / "phase12-raw-github-coverage-survey.md"
PHASE12_LIBBPF_SEQUENCE_PATH = PHASE12_ROOT / "phase12-libbpf-heavy-consumer-lane-sequencing.md"
PHASE12_COMPLEX_DRIVER_SEQUENCE_PATH = PHASE12_ROOT / "phase12-complex-driver-lane-sequencing.md"
SCRIPTS_ROOT = Path("scripts/zigux")
SCRIPTS_README_PATH = SCRIPTS_ROOT / "README.md"
CHECK_PHASE12_SURFACE_PATH = SCRIPTS_ROOT / "check-build-only-phase12-surface.py"
TESTS_ROOT = Path("zigux/tests")
TESTS_README_PATH = TESTS_ROOT / "README.md"
PHASE12_LIBBPF_SNAPSHOT_PATH = TESTS_ROOT / "fixtures/phase12_libbpf_snapshot.json"
PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH = TESTS_ROOT / "fixtures/phase12_libbpf_snapshot_determinism.json"
REVIEW_CHECKLIST_PATH = PHASE12_ROOT / "review-checklist.md"

REQUIRED_FILES = (
    PHASE12_RELEASE_MATRIX_PATH,
    PHASE12_RELEASE_READINESS_PATH,
    PHASE12_RELEASE_SEQUENCING_PATH,
    PHASE12_RAW_GITHUB_SURVEY_PATH,
    PHASE12_LIBBPF_SEQUENCE_PATH,
    PHASE12_COMPLEX_DRIVER_SEQUENCE_PATH,
    SCRIPTS_README_PATH,
    CHECK_PHASE12_SURFACE_PATH,
    TESTS_README_PATH,
    PHASE12_LIBBPF_SNAPSHOT_PATH,
    PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH,
    REVIEW_CHECKLIST_PATH,
)

REQUIRED_MATRIX_MARKERS = (
    "scope: keep the active shared Phase 12 packet reviewable without implying a broader validator-first or deep-core delivery claim",
    "the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard",
    "the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor",
    "starter-present direct `virtio_net` packet",
    "bounded driver-local NVMe starter-plus-verifier-plus-direct-replay-plus-slice-plus-survey packet",
    "one-catalog plus one-gap-note plus two-anchor split explicit in PMO release wording",
    "Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs",
)

REQUIRED_READINESS_MARKERS = (
    "The build-only release packet stays inside segmented preparation and bounded delivery only.",
    "Drivers with DMA queues, recovery loops, or throughput ownership remain blocked from runtime claims until later phases.",
    "Shared review is limited to docs, build-only helper slices, validator scripts, and deterministic fixtures.",
    "`scripts/zigux/check-build-only-phase12-surface.py` and the support-checker plus validate wording in the adjacent shared surfaces are aligned and required for every Phase 12 release-packet rerun.",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain the only approved libbpf-heavy snapshot fixtures under this packet.",
)

REQUIRED_SEQUENCING_MARKERS = (
    "bounded direct-build shards only",
    "keep `virtio_net_transmit_recycle` and `virtio_net_queue_resume` parked as follow-up review targets rather than folding them into the direct build-only shard list",
    "queue ownership, DMA routing, recovery, and throughput semantics stay deferred even when helper or fixture surfaces expand",
    "tests-root fixture updates must preserve both the snapshot fixture and the determinism fixture before any shared release packet is considered complete",
)

REQUIRED_RAW_GITHUB_MARKERS = (
    "raw GitHub coverage stays documentation-first and build-only",
    "reviewers must not infer runtime queueing, DMA ownership, recovery, or throughput readiness from raw file presence alone",
    "the snapshot fixture and the determinism fixture are both part of the required direct-read packet for libbpf-heavy consumers",
)

REQUIRED_LIBBPF_SEQUENCE_MARKERS = (
    "phase12_libbpf_snapshot.json",
    "phase12_libbpf_snapshot_determinism.json",
    "determinism fixture stays mandatory for any replay-route or helper-survey refresh",
    "throughput, recovery, DMA, and queue semantics remain blocked behind later delivery work even when the fixture packet changes",
)

REQUIRED_COMPLEX_DRIVER_MARKERS = (
    "complex-driver preparation stays bounded to build-only helper evidence, deterministic fixtures, and segmented release coordination",
    "do not claim queue ownership, DMA wiring, recovery loops, or throughput behavior from these surfaces",
    "virtio, nvme, and mlx5 helper consumers stay in the same parked packet until later delivery phases reopen runtime work",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`check-build-only-phase12-surface.py` validates the segmented Phase 12 release packet for the release coordination matrix, readiness survey, sequencing note, raw-GitHub survey, complex-driver lane note, libbpf-heavy lane note, tests guide, review checklist, and both libbpf snapshot fixtures",
    "keeps the Phase 12 packet limited to build-only helper evidence for complex drivers and other heavy helper consumers without reopening queue ownership, DMA routing, recovery, or throughput semantics",
)

REQUIRED_TESTS_README_MARKERS = (
    "`fixtures/phase12_libbpf_snapshot.json` and `fixtures/phase12_libbpf_snapshot_determinism.json` are the locked libbpf-heavy replay fixtures for the segmented Phase 12 build-only packet",
    "Phase 12 tests remain build-only and may not be cited as runtime queue, DMA, recovery, or throughput evidence",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "Phase 12 release packet reruns `scripts/zigux/check-build-only-phase12-surface.py` and confirms both libbpf-heavy fixtures stay present before citing complex-driver build-only readiness",
    "No review note may treat Phase 12 helper, fixture, or survey changes as proof of runtime queue, DMA, recovery, or throughput behavior.",
)


def load_text(root: Path, relative: Path) -> str:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing_file:{relative.as_posix()}") from exc



def require_markers(name: str, text: str, markers: tuple[str, ...]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(
            f"missing_markers:{name}:{json.dumps(missing, ensure_ascii=True)}"
        )



def validate(root: Path) -> None:
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            raise SystemExit(f"missing_file:{relative.as_posix()}")

    require_markers(
        "phase12-release-coordination-matrix",
        load_text(root, PHASE12_RELEASE_MATRIX_PATH),
        REQUIRED_MATRIX_MARKERS,
    )
    require_markers(
        "phase12-release-readiness-survey",
        load_text(root, PHASE12_RELEASE_READINESS_PATH),
        REQUIRED_READINESS_MARKERS,
    )
    require_markers(
        "phase12-release-sequencing",
        load_text(root, PHASE12_RELEASE_SEQUENCING_PATH),
        REQUIRED_SEQUENCING_MARKERS,
    )
    require_markers(
        "phase12-raw-github-coverage-survey",
        load_text(root, PHASE12_RAW_GITHUB_SURVEY_PATH),
        REQUIRED_RAW_GITHUB_MARKERS,
    )
    require_markers(
        "phase12-libbpf-heavy-consumer-lane-sequencing",
        load_text(root, PHASE12_LIBBPF_SEQUENCE_PATH),
        REQUIRED_LIBBPF_SEQUENCE_MARKERS,
    )
    require_markers(
        "phase12-complex-driver-lane-sequencing",
        load_text(root, PHASE12_COMPLEX_DRIVER_SEQUENCE_PATH),
        REQUIRED_COMPLEX_DRIVER_MARKERS,
    )
    require_markers(
        "scripts-readme",
        load_text(root, SCRIPTS_README_PATH),
        REQUIRED_SCRIPTS_README_MARKERS,
    )
    require_markers(
        "tests-readme",
        load_text(root, TESTS_README_PATH),
        REQUIRED_TESTS_README_MARKERS,
    )
    require_markers(
        "review-checklist",
        load_text(root, REVIEW_CHECKLIST_PATH),
        REQUIRED_REVIEW_CHECKLIST_MARKERS,
    )



def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except SystemExit as exc:
        actual = str(exc)
        if actual != expected:
            raise SystemExit(
                f"unexpected_failure:{actual}:expected:{expected}"
            ) from exc
    else:
        raise SystemExit(f"missing_expected_failure:{expected}")



def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")



def run_self_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix="phase12_build_only_surface_") as tmp_dir:
        root = Path(tmp_dir)
        shutil.copytree(repo_root / "Documentation", root / "Documentation")
        shutil.copytree(repo_root / "scripts", root / "scripts")
        shutil.copytree(repo_root / "zigux", root / "zigux")

        validate(root)

        matrix_path = root / PHASE12_RELEASE_MATRIX_PATH
        original_matrix = matrix_path.read_text(encoding="utf-8")
        write_text(
            matrix_path,
            original_matrix.replace(
                "scope: keep the active shared Phase 12 packet reviewable without implying a broader validator-first or deep-core delivery claim",
                "scope: drift the active shared Phase 12 packet beyond the current validator-first and deep-core delivery boundary",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-release-coordination-matrix:"
            + json.dumps(
                [
                    "scope: keep the active shared Phase 12 packet reviewable without implying a broader validator-first or deep-core delivery claim",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(matrix_path, original_matrix)

        readiness_path = root / PHASE12_RELEASE_READINESS_PATH
        original_readiness = readiness_path.read_text(encoding="utf-8")
        write_text(
            readiness_path,
            original_readiness.replace(
                "The build-only release packet stays inside segmented preparation and bounded delivery only.",
                "The build-only release packet drifts outside segmented preparation and bounded delivery only.",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-release-readiness-survey:"
            + json.dumps(
                [
                    "The build-only release packet stays inside segmented preparation and bounded delivery only.",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(readiness_path, original_readiness)

        sequencing_path = root / PHASE12_RELEASE_SEQUENCING_PATH
        original_sequencing = sequencing_path.read_text(encoding="utf-8")
        write_text(
            sequencing_path,
            original_sequencing.replace(
                "bounded direct-build shards only",
                "bounded direct-build shard drift only",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-release-sequencing:"
            + json.dumps(["bounded direct-build shards only"], ensure_ascii=True),
        )
        write_text(sequencing_path, original_sequencing)

        raw_survey_path = root / PHASE12_RAW_GITHUB_SURVEY_PATH
        original_raw_survey = raw_survey_path.read_text(encoding="utf-8")
        write_text(
            raw_survey_path,
            original_raw_survey.replace(
                "raw GitHub coverage stays documentation-first and build-only",
                "raw GitHub coverage drifts documentation-first and build-only",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-raw-github-coverage-survey:"
            + json.dumps(
                ["raw GitHub coverage stays documentation-first and build-only"],
                ensure_ascii=True,
            ),
        )
        write_text(raw_survey_path, original_raw_survey)

        libbpf_sequence_path = root / PHASE12_LIBBPF_SEQUENCE_PATH
        original_libbpf_sequence = libbpf_sequence_path.read_text(encoding="utf-8")
        write_text(
            libbpf_sequence_path,
            original_libbpf_sequence.replace(
                "phase12_libbpf_snapshot_determinism.json",
                "phase12_libbpf_snapshot_determinism_missing.json",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-libbpf-heavy-consumer-lane-sequencing:"
            + json.dumps(["phase12_libbpf_snapshot_determinism.json"], ensure_ascii=True),
        )
        write_text(libbpf_sequence_path, original_libbpf_sequence)

        complex_driver_path = root / PHASE12_COMPLEX_DRIVER_SEQUENCE_PATH
        original_complex_driver = complex_driver_path.read_text(encoding="utf-8")
        write_text(
            complex_driver_path,
            original_complex_driver.replace(
                "complex-driver preparation stays bounded to build-only helper evidence, deterministic fixtures, and segmented release coordination",
                "complex-driver preparation drifts to build-only helper evidence, deterministic fixtures, and segmented release coordination",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-complex-driver-lane-sequencing:"
            + json.dumps(
                [
                    "complex-driver preparation stays bounded to build-only helper evidence, deterministic fixtures, and segmented release coordination",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(complex_driver_path, original_complex_driver)

        scripts_readme_path = root / SCRIPTS_README_PATH
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        write_text(
            scripts_readme_path,
            original_scripts_readme.replace(
                "`check-build-only-phase12-surface.py` validates the segmented Phase 12 release packet for the release coordination matrix, readiness survey, sequencing note, raw-GitHub survey, complex-driver lane note, libbpf-heavy lane note, tests guide, review checklist, and both libbpf snapshot fixtures",
                "`check-build-only-phase12-surface.py` validates only part of the segmented Phase 12 release packet",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:scripts-readme:"
            + json.dumps(
                [
                    "`check-build-only-phase12-surface.py` validates the segmented Phase 12 release packet for the release coordination matrix, readiness survey, sequencing note, raw-GitHub survey, complex-driver lane note, libbpf-heavy lane note, tests guide, review checklist, and both libbpf snapshot fixtures",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(scripts_readme_path, original_scripts_readme)

        tests_readme_path = root / TESTS_README_PATH
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        write_text(
            tests_readme_path,
            original_tests_readme.replace(
                "`fixtures/phase12_libbpf_snapshot.json` and `fixtures/phase12_libbpf_snapshot_determinism.json` are the locked libbpf-heavy replay fixtures for the segmented Phase 12 build-only packet",
                "`fixtures/phase12_libbpf_snapshot.json` is the only locked libbpf-heavy replay fixture for the segmented Phase 12 build-only packet",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:tests-readme:"
            + json.dumps(
                [
                    "`fixtures/phase12_libbpf_snapshot.json` and `fixtures/phase12_libbpf_snapshot_determinism.json` are the locked libbpf-heavy replay fixtures for the segmented Phase 12 build-only packet",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(tests_readme_path, original_tests_readme)

        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        write_text(
            review_checklist_path,
            original_review_checklist.replace(
                "Phase 12 release packet reruns `scripts/zigux/check-build-only-phase12-surface.py` and confirms both libbpf-heavy fixtures stay present before citing complex-driver build-only readiness",
                "Phase 12 release packet reruns only part of the build-only checker before citing complex-driver build-only readiness",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:review-checklist:"
            + json.dumps(
                [
                    "Phase 12 release packet reruns `scripts/zigux/check-build-only-phase12-surface.py` and confirms both libbpf-heavy fixtures stay present before citing complex-driver build-only readiness",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(review_checklist_path, original_review_checklist)

        snapshot_path = root / PHASE12_LIBBPF_SNAPSHOT_PATH
        snapshot_path.unlink()
        expect_failure(
            root,
            f"missing_file:{PHASE12_LIBBPF_SNAPSHOT_PATH.as_posix()}",
        )
        shutil.copy2(repo_root / PHASE12_LIBBPF_SNAPSHOT_PATH, snapshot_path)

        determinism_path = root / PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH
        determinism_path.unlink()
        expect_failure(
            root,
            f"missing_file:{PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH.as_posix()}",
        )
        shutil.copy2(
            repo_root / PHASE12_LIBBPF_SNAPSHOT_DETERMINISM_PATH,
            determinism_path,
        )

        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
        print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=55")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Zigux Phase 12 build-only release surfaces."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to validate (defaults to current working directory).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in self-test suite.",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return
    validate(args.root)
    print("PHASE12_BUILD_ONLY_SURFACE=pass")


if __name__ == "__main__":
    main()
