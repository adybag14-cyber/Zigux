#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-readiness-survey.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_READINESS_SURVEY_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_CLOSURE_CHECKLIST_PATH = (
    "Documentation/zigux/phase12-release-closure-checklist.md"
)
RELEASE_COORDINATION_MATRIX_PATH = (
    "Documentation/zigux/phase12-release-coordination-matrix.md"
)
RAW_GITHUB_COVERAGE_SURVEY_PATH = (
    "Documentation/zigux/phase12-raw-github-coverage-survey.md"
)
PHASE12_COMPLEX_DRIVER_LANE_PATH = (
    "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
)
PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH = (
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
)
SCRIPTS_README_PATH = "scripts/zigux/README.md"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    DOCS_README_PATH,
    FREEZE_MAP_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_READINESS_SURVEY_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_CLOSURE_CHECKLIST_PATH,
    RELEASE_COORDINATION_MATRIX_PATH,
    RAW_GITHUB_COVERAGE_SURVEY_PATH,
    PHASE12_COMPLEX_DRIVER_LANE_PATH,
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH,
    SCRIPTS_README_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, so keep `make -C zigux phase12-validate` explicit as shipped wrapper evidence on current `master`.",
        "the shared route stays the six-file `virtio_net` smoke-and-test sextet in `zigux/tests/phase12_build.zig`",
    ],
    FREEZE_MAP_PATH: [
        "- `net/core/skbuff.c`",
        "- `kernel/workqueue.c`",
        "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree that current `zigux/Makefile` ships `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again while `make -C zigux phase12-validate` remains reminder-only vocabulary",
        "keep the repo-local `.zig-toolchain` fallback before the attached-Zig degraded rerun order explicit",
    ],
    RELEASE_READINESS_SURVEY_PATH: [
        "The route story on current `master` is now fully returned rather than split: the directly readable scripts-side support packet is still present through `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `.github/workflows/zigux-bootstrap.yml`, and current `zigux/Makefile` now provides shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrapper routes again.",
        "The active shared build route on current `master` is the six-file `virtio_net` smoke-and-test packet in `zigux/tests/phase12_build.zig`: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` are the directly wired shared reruns",
        "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: the route story on current `master` is now fully returned rather than split. `zigux/Makefile` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
        "The active smoke-first direct shard set on current `master` is `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`",
        "keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns",
    ],
    RELEASE_CLOSURE_CHECKLIST_PATH: [
        "keep `make -C zigux phase12-validate` explicit here as shipped wrapper evidence again on current `master`.",
        "The active shared build packet on current `master` is the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`",
        "The deterministic libbpf fixture pair stays explicit: `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` remain required",
    ],
    RELEASE_COORDINATION_MATRIX_PATH: [
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the shipped wrapper name `make -C zigux phase12-validate`",
        "The active shared build packet is the returned six-file `virtio_net` sextet only:",
        "Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs",
    ],
    RAW_GITHUB_COVERAGE_SURVEY_PATH: [
        "  * current contents-bridge shared support bundle during degraded contents reads:",
        "- exact coverage evidence checked on `2026-05-23`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` at blob `b34900db85b8872b5981b63839ab35583d340f0a`, `scripts/zigux/validate-phase12.py` at blob `de1e248f6688adf89b9f9edb3abd824ece6ddae5`, `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `f6343d3b1dd6c4c6e0a16fb86d888dcf68186d74`, `.github/workflows/zigux-bootstrap.yml` at blob `5d07f69d341f667c96f59a26cd6957870c54997f`, `scripts/zigux/README.md` at blob `82636ad6f5befd3b0fc4eb8f6ac875475d9119a9`, `zigux/Makefile` at blob `ad34a7346eac978fc6bb824778e408084d6af909`, and `zigux/tests/phase12_build.zig` at blob `c338d24f4d12317c6a58d25708bbc14a5006852c`",
        "exact runtime-reality evidence checked on `2026-05-23`: the directly readable `zigux/Makefile` blob `ad34a7346eac978fc6bb824778e408084d6af909` now exposes shared `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` again",
    ],
    PHASE12_COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12`",
        "The directly readable rerun and support surfaces in this lane are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`",
        "The readable build file currently wires `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` through the shared `smoke` and `test` steps",
    ],
    PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: [
        "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase12` on current `master`",
        "The shipped heavy-consumer guard now sits beside that same support bundle too: `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test` and `python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the parked helper-first packet fail-closed beside the snapshot checker and shared validator entrypoint",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/check-phase12-libbpf-snapshot.py`, and `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py` keep the directly readable validator-side support bundle explicit from the scripts root while `make -C zigux phase12-validate` stays reminder-only vocabulary until the wrapper returns on current `master`",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    ],
    VALIDATOR_PATH: [
        "BUILD_ONLY_CHECKER_PATH = \"scripts/zigux/check-build-only-phase12-surface.py\"",
        "RELEASE_READINESS_CHECKER_PATH = (",
        "make -C zigux phase12-validate",
        "scripts-side support packet",
        "PHASE12_VALIDATION=pass",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "Keep `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py` explicit as the shipped shared support bundle so the tests-root summary does not undercount the dedicated release-readiness checker.",
        "Current `master` keeps the shared Phase 12 rerun story split rather than absent: `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
        "Keep `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` explicit as the shared heavy-helper anti-overlap companion so the tests-root reminder stays aligned with the same parked libbpf boundary already named by the release-order, closure, readiness, coordination, fallback, and complex-driver notes.",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "- name: Validate current Phase 12 support bundle",
        "run: python3 scripts/zigux/validate-phase12.py",
        "- name: Run current Phase 12 aggregate route",
        "run: make -C zigux phase12",
    ],
}

EXACT_COUNT_MARKERS = {
    RAW_GITHUB_COVERAGE_SURVEY_PATH: {
        "- exact coverage evidence checked on `2026-05-23`: the current GitHub contents bridge directly reads `scripts/zigux/check-build-only-phase12-surface.py` at blob `b34900db85b8872b5981b63839ab35583d340f0a`, `scripts/zigux/validate-phase12.py` at blob `de1e248f6688adf89b9f9edb3abd824ece6ddae5`, `scripts/zigux/check-phase12-release-readiness-packet.py` at blob `f6343d3b1dd6c4c6e0a16fb86d888dcf68186d74`, `.github/workflows/zigux-bootstrap.yml` at blob `5d07f69d341f667c96f59a26cd6957870c54997f`, `scripts/zigux/README.md` at blob `82636ad6f5befd3b0fc4eb8f6ac875475d9119a9`, `zigux/Makefile` at blob `ad34a7346eac978fc6bb824778e408084d6af909`, and `zigux/tests/phase12_build.zig` at blob `c338d24f4d12317c6a58d25708bbc14a5006852c`": 1,
    },
}


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker, expected_count in markers.items():
            actual_count = text.count(marker)
            if actual_count != expected_count:
                failures.append(
                    "wrong_count:"
                    f"{rel_path}:{marker}:expected={expected_count}:actual={actual_count}"
                )

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            DOCS_README_PATH: "# Zigux Documentation",
            FREEZE_MAP_PATH: "# Zigux Freeze Map",
            REVIEW_CHECKLIST_PATH: "# Zigux Review Checklist",
            RELEASE_READINESS_SURVEY_PATH: "# Phase 12 Release Readiness Survey",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_CLOSURE_CHECKLIST_PATH: "# Phase 12 Release Closure Checklist",
            RELEASE_COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            RAW_GITHUB_COVERAGE_SURVEY_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            PHASE12_COMPLEX_DRIVER_LANE_PATH: "# Phase 12 Complex-Driver Lane Sequencing",
            PHASE12_LIBBPF_HEAVY_CONSUMER_LANE_PATH: "# Phase 12 Libbpf Heavy-Consumer Lane Sequencing",
            SCRIPTS_README_PATH: "# scripts/zigux",
            TESTS_README_PATH: "# zigux/tests",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path in {VALIDATOR_PATH, MAKEFILE_PATH, WORKFLOW_PATH}:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if rel_path.endswith(".md"):
        return "# Fixture\n"
    if rel_path.endswith(".zig"):
        return "// fixture\n"
    if rel_path.endswith(".yml"):
        return "name: zigux-bootstrap\n"
    return ""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, fixture_text(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "", 1)
    if updated == text:
        updated = text.replace(f"{marker}\n", "", 1)
    if marker in updated:
        updated = updated.replace(marker, "__REMOVED_PHASE12_MARKER__", 1)
    if updated == text:
        raise SystemExit(f"unable to mutate marker in fixture: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-readiness-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        missing_file_cases = REQUIRED_FILES[:]
        for rel_path in missing_file_cases:
            write_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        marker_cases = [
            (rel_path, marker)
            for rel_path, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in marker_cases:
            write_fixture_tree(base)
            remove_marker(base / rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        exact_count_cases = [
            (rel_path, marker, expected_count)
            for rel_path, markers in EXACT_COUNT_MARKERS.items()
            for marker, expected_count in markers.items()
        ]
        for rel_path, marker, expected_count in exact_count_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + marker + "\n",
            )
            expect_failure(
                base,
                "wrong_count:"
                f"{rel_path}:{marker}:expected={expected_count}:actual={expected_count + 1}"
            )

        case_count = (
            len(missing_file_cases)
            + len(marker_cases)
            + len(exact_count_cases)
        )
        print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
        print(f"PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current narrow Phase 12 release-readiness support bundle "
            "around the shared release notes, fallback split, and returned wrapper "
            "state."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_RELEASE_READINESS_PACKET=fail:{failure}", file=sys.stderr)
        return 1

    print("PHASE12_RELEASE_READINESS_PACKET=pass")
    print(f"PHASE12_RELEASE_READINESS_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_RELEASE_READINESS_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print("PHASE12_RELEASE_READINESS_PACKET_FORBIDDEN_MARKER_COUNT=0")
    print(
        "PHASE12_RELEASE_READINESS_PACKET_EXACT_COUNT_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_COUNT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
