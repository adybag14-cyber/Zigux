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
    "the shipped `python3 scripts/zigux/check-phase12-cross.py --self-test` companion",
    "the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor",
    "starter-present direct `virtio_net` packet",
    "bounded driver-local NVMe starter-plus-verifier-plus-direct-replay-plus-slice-plus-survey packet",
    "one-catalog plus one-gap-note plus two-anchor split explicit in PMO release wording",
    "Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs",
)

REQUIRED_READINESS_MARKERS = (
    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
    "`scripts/zigux/check-build-only-phase12-surface.py` now matches that shipped support-checker-plus-validate-route reminder too.",
    "Keep the same degraded-workflow validation quartet explicit too:",
    "The public fallback split must stay explicit:",
    "During degraded GitHub contents reads, keep the intended shared-tree anchor pair `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` explicit",
)

REQUIRED_SEQUENCING_MARKERS = (
    "Keep the degraded-workflow validation quartet explicit beside that same order too:",
    "The active smoke-first direct shard set is `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, because those are the files the current `smoke` step actually runs.",
    "Current `master` now also ships the degraded-workflow `make -C zigux phase12-validate` route together with `scripts/zigux/validate-phase12.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
)

REQUIRED_RAW_GITHUB_MARKERS = (
    "rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in shared PMO wording",
    "exact coverage evidence checked on `2026-05-17`: direct contents reads now succeed for `scripts/zigux/check-build-only-phase12-surface.py`",
    "exact runtime-reality evidence checked on `2026-05-17`: treat the directly readable checker, workflow, and scripts-root README trio as bounded reminder evidence only",
    "keep the current validator-first then smoke-first order explicit through `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`",
)

REQUIRED_LIBBPF_SEQUENCE_MARKERS = (
    "scope: shared release-planning truthfulness, fallback wording, smoke-first replay reminders, and anti-overlap guidance for the bounded libbpf survey packet plus the parked verify-shard boundary already documented on current `master`",
    "Keep the degraded-workflow support bundle explicit beside that same order too:",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "Keep the shared fallback split explicit here too:",
)

REQUIRED_COMPLEX_DRIVER_MARKERS = (
    "scope: shared release-planning truthfulness, build-only contract reminders, and anti-overlap guidance for the starter-present `virtio_net` packet, the bounded `virtio_scsi` rollback-lab packet, and the published-but-still-unwired NVMe foothold",
    "Keep the degraded-workflow support bundle explicit beside that same order too:",
    "Keep the current partial direct-read bridge explicit too:",
    "Keep the shared fallback split explicit:",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned",
    "`scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate` keep the degraded-workflow support bundle explicit",
    "the current starter-present `virtio_net` plus smoke-first `virtio_scsi` release packet and the parked verify-shard-backed libbpf survey packet reviewable from the scripts root",
    "If `zig` is unavailable on `PATH`, rerun only the shipped Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-smoke ZIG=<attached-zig-path>` and `make -C zigux phase12 ZIG=<attached-zig-path>`, while `make -C zigux phase12-validate` stays the shipped support-bundle route.",
)

REQUIRED_TESTS_README_MARKERS = (
    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
    "`zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`",
    "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
    "`make -C zigux phase12`",
)

REQUIRED_REVIEW_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 12 complex-driver packet",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`scripts/zigux/check-phase12-release-readiness-packet.py` checker plus the shipped `make -C zigux phase12-validate` route explicit as support-bundle evidence rather than as a second direct replay route",
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
                "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
                "shared build-only contract drift: `scripts/zigux/check-build-only-phase12-surface.py`",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-release-readiness-survey:"
            + json.dumps(
                [
                    "shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`",
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
                "Keep the degraded-workflow validation quartet explicit beside that same order too:",
                "Keep the degraded-workflow validation quartet drift beside that same order too:",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-release-sequencing:"
            + json.dumps(
                [
                    "Keep the degraded-workflow validation quartet explicit beside that same order too:",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(sequencing_path, original_sequencing)

        raw_survey_path = root / PHASE12_RAW_GITHUB_SURVEY_PATH
        original_raw_survey = raw_survey_path.read_text(encoding="utf-8")
        write_text(
            raw_survey_path,
            original_raw_survey.replace(
                "rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in shared PMO wording",
                "rule: keep this one-catalog plus one-gap-note plus two-anchor split drift in shared PMO wording",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-raw-github-coverage-survey:"
            + json.dumps(
                [
                    "rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in shared PMO wording",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(raw_survey_path, original_raw_survey)

        libbpf_sequence_path = root / PHASE12_LIBBPF_SEQUENCE_PATH
        original_libbpf_sequence = libbpf_sequence_path.read_text(encoding="utf-8")
        write_text(
            libbpf_sequence_path,
            original_libbpf_sequence.replace(
                "scope: shared release-planning truthfulness, fallback wording, smoke-first replay reminders, and anti-overlap guidance for the bounded libbpf survey packet plus the parked verify-shard boundary already documented on current `master`",
                "scope: drift the shared release-planning truthfulness, fallback wording, smoke-first replay reminders, and anti-overlap guidance for the bounded libbpf survey packet",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-libbpf-heavy-consumer-lane-sequencing:"
            + json.dumps(
                [
                    "scope: shared release-planning truthfulness, fallback wording, smoke-first replay reminders, and anti-overlap guidance for the bounded libbpf survey packet plus the parked verify-shard boundary already documented on current `master`",
                ],
                ensure_ascii=True,
            ),
        )
        write_text(libbpf_sequence_path, original_libbpf_sequence)

        complex_driver_path = root / PHASE12_COMPLEX_DRIVER_SEQUENCE_PATH
        original_complex_driver = complex_driver_path.read_text(encoding="utf-8")
        write_text(
            complex_driver_path,
            original_complex_driver.replace(
                "scope: shared release-planning truthfulness, build-only contract reminders, and anti-overlap guidance for the starter-present `virtio_net` packet, the bounded `virtio_scsi` rollback-lab packet, and the published-but-still-unwired NVMe foothold",
                "scope: drift the shared release-planning truthfulness and build-only contract reminders for the starter-present driver packet",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:phase12-complex-driver-lane-sequencing:"
            + json.dumps(
                [
                    "scope: shared release-planning truthfulness, build-only contract reminders, and anti-overlap guidance for the starter-present `virtio_net` packet, the bounded `virtio_scsi` rollback-lab packet, and the published-but-still-unwired NVMe foothold",
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
                "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned",
                "Phase 12 flow - `validate-phase12.py` drifts away from the current complex-driver packet",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:scripts-readme:"
            + json.dumps(
                [
                    "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned",
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
                "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
                "`zigux/tests/fixtures/phase12_libbpf_snapshot_missing.json`",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:tests-readme:"
            + json.dumps(
                [
                    "`zigux/tests/fixtures/phase12_libbpf_snapshot.json`",
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
                "if the change touches the shared Phase 12 complex-driver packet",
                "if the change drifts away from the shared Phase 12 complex-driver packet",
                1,
            ),
        )
        expect_failure(
            root,
            "missing_markers:review-checklist:"
            + json.dumps(
                [
                    "if the change touches the shared Phase 12 complex-driver packet",
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
