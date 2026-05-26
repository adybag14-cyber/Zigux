#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
RELEASE_COORDINATION_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
READINESS_CHECKER_PATH = "scripts/zigux/check-phase12-release-readiness-packet.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    DOCS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_PATH,
    RELEASE_CLOSURE_PATH,
    RELEASE_COORDINATION_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    SCRIPTS_README_PATH,
    BUILD_ONLY_CHECKER_PATH,
    READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "Phase 12 notes",
        "`Documentation/zigux/phase12-release-sequencing.md`",
        "`Documentation/zigux/phase12-release-readiness-survey.md`",
        "`Documentation/zigux/phase12-release-closure-checklist.md`",
        "`Documentation/zigux/phase12-release-coordination-matrix.md`",
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`",
        "`zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again",
    ],
    RELEASE_SEQUENCING_PATH: [
        "shared-summary lane owner: `pmo-release`",
        "Current repo-reality override: the route story on current `master` is now fully returned rather than split.",
        "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
        "2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`",
        "5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
        "6. shipped wrapper evidence on current `master`: `make -C zigux phase12`",
    ],
    RELEASE_READINESS_PATH: [
        "shared-summary lane owner: `pmo-release`",
        "The active shared build route on current `master` is the six-file `virtio_net` smoke-and-test packet in `zigux/tests/phase12_build.zig`",
        "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again",
    ],
    RELEASE_CLOSURE_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    ],
    RELEASE_COORDINATION_PATH: [
        "shared-summary lane owner: `pmo-release`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
        "The active shared build packet is the returned six-file `virtio_net` sextet only:",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "- exact current support-bundle reread checked on `2026-05-26`:",
        "`scripts/zigux/check-phase12-release-readiness-packet.py` `4a10382b6d897afccad318bdeccbb959a6373087`",
        "`zigux/Makefile` `4d572bfda15dc6ae7cd419cc4c7f858d973cda26`",
        "`zigux/tests/phase12_build.zig` `c338d24f4d12317c6a58d25708bbc14a5006852c`",
    ],
    SCRIPTS_README_PATH: [
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit",
        "`make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` are shipped wrapper evidence again on current `master`",
    ],
    VALIDATOR_PATH: [
        'BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"',
        'RELEASE_READINESS_CHECKER_PATH = (',
        "PHASE12_VALIDATION=pass",
    ],
    MAKEFILE_PATH: [
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
    TESTS_README_PATH: [
        "Keep the directly readable validator-first support bundle explicit too: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the current shared build gate explicit",
        "Keep the active shared build packet explicit too: `zigux/tests/phase12_build.zig` keeps `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig` wired through the shared `smoke` and `test` route.",
    ],
    PHASE12_BUILD_PATH: [
        "phase12_virtio_net_queue_resume",
        "phase12_virtio_net_receive_refill_replay",
        "phase12_virtio_net_transmit_recycle",
        "phase12_virtio_net_post_reset_replay",
        "phase12_virtio_net_throughput_parity",
        "phase12_virtio_net_survey",
    ],
    WORKFLOW_PATH: [
        "Self-test current Phase 12 release-readiness packet checker",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "Validate current Phase 12 support bundle",
        "python3 scripts/zigux/validate-phase12.py",
        "Run current Phase 12 aggregate route",
        "make -C zigux phase12",
    ],
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
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        markers = REQUIRED_MARKERS.get(rel_path, [])
        content = "\n".join(markers) + "\n" if markers else "# fixture\n"
        if rel_path.endswith(".py") and not content.startswith("#!/usr/bin/env python3"):
            content = "#!/usr/bin/env python3\n" + content
        write_text(root / rel_path, content)


def run_self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="phase12_pmo_shared_") as tmpdir:
        root = Path(tmpdir)
        build_fixture(root)
        base_failures = validate(root)
        if base_failures:
            failures.append(f"fixture_validation_failed:{base_failures}")

        broken_root = root / "broken"
        build_fixture(broken_root)
        broken_readme = broken_root / RELEASE_READINESS_PATH
        broken_readme.write_text(
            broken_readme.read_text(encoding="utf-8").replace(
                "make -C zigux phase12-test", "make -C zigux phase12-test-missing"
            ),
            encoding="utf-8",
        )
        negative_failures = validate(broken_root)
        expected_fragment = "missing_marker:Documentation/zigux/phase12-release-readiness-survey.md:That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again"
        if expected_fragment not in negative_failures:
            failures.append("negative_case_missing_expected_marker_failure")

    if failures:
        for failure in failures:
            print(f"PHASE12_PMO_SHARED_SURFACE_SELF_TEST_FAILURE={failure}")
        print("PHASE12_PMO_SHARED_SURFACE_SELF_TEST=fail")
        return 1

    print("PHASE12_PMO_SHARED_SURFACE_SELF_TEST=pass")
    print("PHASE12_PMO_SHARED_SURFACE_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Phase 12 PMO release-planning surface."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE12_PMO_SHARED_SURFACE_FAILURE={failure}")
        print("PHASE12_PMO_SHARED_SURFACE=fail")
        return 1

    print("PHASE12_PMO_SHARED_SURFACE=pass")
    print(f"PHASE12_PMO_SHARED_SURFACE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE12_PMO_SHARED_SURFACE_REQUIRED_MARKER_COUNT={sum(len(v) for v in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
