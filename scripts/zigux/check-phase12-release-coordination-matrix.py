#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase12-release-coordination-matrix.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

COORDINATION_MATRIX_PATH = "Documentation/zigux/phase12-release-coordination-matrix.md"
RELEASE_SEQUENCING_PATH = "Documentation/zigux/phase12-release-sequencing.md"
RELEASE_READINESS_PATH = "Documentation/zigux/phase12-release-readiness-survey.md"
RELEASE_CLOSURE_PATH = "Documentation/zigux/phase12-release-closure-checklist.md"
RAW_GITHUB_COVERAGE_PATH = "Documentation/zigux/phase12-raw-github-coverage-survey.md"
COMPLEX_DRIVER_LANE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
LIBBPF_LANE_PATH = "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
BUILD_ONLY_CHECKER_PATH = "scripts/zigux/check-build-only-phase12-surface.py"
READINESS_CHECKER_PATH = "scripts/zigux/check-phase12-release-readiness-packet.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase12.py"
MAKEFILE_PATH = "zigux/Makefile"
PHASE12_BUILD_PATH = "zigux/tests/phase12_build.zig"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [
    COORDINATION_MATRIX_PATH,
    RELEASE_SEQUENCING_PATH,
    RELEASE_READINESS_PATH,
    RELEASE_CLOSURE_PATH,
    RAW_GITHUB_COVERAGE_PATH,
    COMPLEX_DRIVER_LANE_PATH,
    LIBBPF_LANE_PATH,
    FREEZE_MAP_PATH,
    BUILD_ONLY_CHECKER_PATH,
    READINESS_CHECKER_PATH,
    VALIDATOR_PATH,
    MAKEFILE_PATH,
    PHASE12_BUILD_PATH,
    WORKFLOW_PATH,
]

REQUIRED_MARKERS = {
    COORDINATION_MATRIX_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "validator-first support bundle: `scripts/zigux/validate-phase12.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
        "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
        "The active shared build packet is the returned five-file `virtio_net` quintet only:",
        "`zigux/tests/phase12_virtio_net_queue_resume.zig`",
        "`zigux/tests/phase12_virtio_net_receive_refill_replay.zig`",
        "`zigux/tests/phase12_virtio_net_transmit_recycle.zig`",
        "`zigux/tests/phase12_virtio_net_post_reset_replay.zig`",
        "`zigux/tests/phase12_virtio_net_throughput_parity.zig`",
        "commit-pinned direct replay catalog:",
        "driver-local current-master gap inventory companion:",
        "shared-tree-only anchors:",
        "If `zig` is unavailable on `PATH`, keep the shipped degraded-workflow bundle plus that same validator-first then smoke-first order explicit, first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    ],
    RELEASE_SEQUENCING_PATH: [
        "Current repo-reality override: `zigux/Makefile` still omits `phase12-validate` on current `master`, but it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again.",
        "readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
    ],
    RELEASE_READINESS_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
    ],
    RELEASE_CLOSURE_PATH: [
        "support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`",
        "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence and still omits `phase12-validate`.",
    ],
    RAW_GITHUB_COVERAGE_PATH: [
        "It is a compact fallback overview, not a new replay surface and not a commit-pinned artifact itself.",
        "the raw-URL-backed direct replay catalog, the current-master NVMe gap-note companion, the contents-bridge-backed build-only anchor pair, and the contents-bridge-backed shared support bundle are distinct evidence states in this runtime",
    ],
    COMPLEX_DRIVER_LANE_PATH: [
        "Keep the shared validator-first then smoke-first packet wording explicit: current `zigux/Makefile` now ships `phase12-smoke`, `phase12-test`, and `phase12` again, while `phase12-validate` is still absent",
    ],
    LIBBPF_LANE_PATH: [
        "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-smoke`, `phase12-test`, and `phase12` on current `master` while still omitting `phase12-validate`",
    ],
    FREEZE_MAP_PATH: [
        "- `net/core/skbuff.c`",
        "- `kernel/workqueue.c`",
        "- `kernel/trace/ring_buffer.c`",
    ],
    MAKEFILE_PATH: [
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-smoke phase12-test",
    ],
    PHASE12_BUILD_PATH: [
        "\"phase12_virtio_net_queue_resume.zig\"",
        "\"phase12_virtio_net_receive_refill_replay.zig\"",
        "\"phase12_virtio_net_transmit_recycle.zig\"",
        "\"phase12_virtio_net_post_reset_replay.zig\"",
        "\"phase12_virtio_net_throughput_parity.zig\"",
    ],
    WORKFLOW_PATH: [
        "- name: Self-test current Phase 12 build-only surface checker",
        "run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
        "- name: Self-test current Phase 12 release-readiness packet checker",
        "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
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
        "phase12-validate:",
        "phase12: phase12-validate phase12-smoke phase12-test",
    ],
}

EXACT_LINE_MARKER_PATHS = {WORKFLOW_PATH}


def has_required_marker(rel_path: str, text: str, marker: str) -> bool:
    if rel_path in EXACT_LINE_MARKER_PATHS:
        return marker in [line.lstrip() for line in text.splitlines()]
    return marker in text


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
            if not has_required_marker(rel_path, text, marker):
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    return f"{title}\n\n" + "\n".join(f"- {marker}" for marker in markers) + "\n"


def fixture_text(rel_path: str) -> str:
    if rel_path in REQUIRED_MARKERS:
        title = {
            COORDINATION_MATRIX_PATH: "# Phase 12 Release Coordination Matrix",
            RELEASE_SEQUENCING_PATH: "# Phase 12 Release Sequencing",
            RELEASE_READINESS_PATH: "# Phase 12 Release Readiness Survey",
            RELEASE_CLOSURE_PATH: "# Phase 12 Release Closure Checklist",
            RAW_GITHUB_COVERAGE_PATH: "# Phase 12 Raw GitHub Coverage Survey",
            COMPLEX_DRIVER_LANE_PATH: "# Phase 12 Complex Driver Lane Sequencing",
            LIBBPF_LANE_PATH: "# Phase 12 Libbpf Heavy Consumer Lane Sequencing",
            FREEZE_MAP_PATH: "# Zigux Freeze Map",
            MAKEFILE_PATH: "# Makefile",
            PHASE12_BUILD_PATH: "# phase12_build",
            WORKFLOW_PATH: "name: zigux-bootstrap",
        }.get(rel_path, "# Fixture")
        if rel_path == WORKFLOW_PATH:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        if rel_path == MAKEFILE_PATH:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        if rel_path == PHASE12_BUILD_PATH:
            return "\n".join(REQUIRED_MARKERS[rel_path]) + "\n"
        return marker_fixture(title, REQUIRED_MARKERS[rel_path])
    if rel_path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    return "# Fixture\n"


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
    if updated == text:
        updated = text.replace(marker, "", 1)
    if updated == text:
        raise SystemExit(f"unable to remove marker: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-release-coordination-matrix-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path in REQUIRED_FILES:
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

        forbidden_cases = [
            (rel_path, marker)
            for rel_path, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
        ]
        for rel_path, marker in forbidden_cases:
            write_fixture_tree(base)
            write_text(
                base / rel_path,
                (base / rel_path).read_text(encoding="utf-8") + f"{marker}\n",
            )
            expect_failure(base, f"forbidden_marker:{rel_path}:{marker}")

        case_count = len(REQUIRED_FILES) + len(marker_cases) + len(forbidden_cases)
        print("PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass")
        print(
            "PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST_CASE_COUNT="
            f"{case_count}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 release coordination matrix against the "
            "shared PMO packet, shipped smoke-and-test wrapper split, and bounded "
            "driver-family coordination wording."
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
            print(f"PHASE12_RELEASE_COORDINATION_MATRIX=fail:{failure}")
        return 1

    print("PHASE12_RELEASE_COORDINATION_MATRIX=pass")
    print(
        "PHASE12_RELEASE_COORDINATION_MATRIX_REQUIRED_FILE_COUNT="
        f"{len(REQUIRED_FILES)}"
    )
    print(
        "PHASE12_RELEASE_COORDINATION_MATRIX_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE12_RELEASE_COORDINATION_MATRIX_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
