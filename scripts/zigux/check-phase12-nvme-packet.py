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
        if (candidate / "Documentation/zigux").exists() and (candidate / "zigux/tests").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SURVEY_NOTE_PATH = "Documentation/zigux/phase12-nvme-pci-survey.md"
FALLBACK_MAP_PATH = "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
REOPEN_GOVERNANCE_PATH = "Documentation/zigux/phase12-nvme-pci-reopen-governance.md"
MANIFEST_PATH = "zigux/tests/phase12_nvme_pci_manifest.json"
DIRECT_TEST_PATH = "zigux/tests/phase12_nvme_pci.zig"
DRIVER_PATH = "drivers/nvme/host/pci.zig"
VERIFY_PATH = "drivers/nvme/host/pci_verify.zig"

REQUIRED_FILES = [
    SURVEY_NOTE_PATH,
    FALLBACK_MAP_PATH,
    REOPEN_GOVERNANCE_PATH,
    MANIFEST_PATH,
    DIRECT_TEST_PATH,
    DRIVER_PATH,
    VERIFY_PATH,
]

SURVEY_NOTE_MARKERS = [
    "`PHASE12_STATUS=starter-present-direct-replay-and-survey-note`",
    "`PHASE12_LANE=P12-L08`",
    "`drivers/nvme/host/pci.zig`",
    "`drivers/nvme/host/pci_verify.zig`",
    "`zigux/tests/phase12_nvme_pci.zig`",
    "`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
    "`Documentation/zigux/phase12-nvme-pci-reopen-governance.md`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
    "current `master` still does not carry `Documentation/zigux/phase12-nvme-pci-slice.md` or `zigux/tests/phase12_nvme_pci_survey.zig`",
    "current `master` still does not wire the bounded NVMe direct replay into `zigux/tests/phase12_build.zig` or the shared `phase12-smoke` and `phase12` routes",
]

FALLBACK_MAP_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_direct_replay_survey_note_and_manifest_present_survey_packet_incomplete`",
    "driver-local owner-map companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`",
    "starter, verifier, direct replay, survey note, manifest, and shared replay companions that remain shipped today: `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`",
    "- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`",
    "- survey replay: `zigux/tests/phase12_nvme_pci_survey.zig`",
    "this NVMe PCI note now records the starter, verifier, direct replay, survey note, and manifest anchor as present and the still-missing slice and survey-gate packet as absent on current `master`",
]

REOPEN_GOVERNANCE_MARKERS = [
    "`PHASE12_STATUS=active`",
    "`PHASE12_LANE_KEY=P12-L08`",
    "later reopen alias: `P12-Y02`",
    "`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
    "- `Documentation/zigux/phase12-nvme-pci-slice.md`",
    "- `zigux/tests/phase12_nvme_pci_survey.zig`",
    "- `P12-L08` owns the shipped direct packet:",
    "- `P12-Y02` owns only a later same-driver reopen",
]

MANIFEST_MARKERS = [
    '"lane_key": "P12-L08"',
    '"preexisting_nvme_pci_verifier_present": true',
    '"preexisting_phase12_direct_test_present": true',
    '"preexisting_phase12_survey_note_present": true',
    '"preexisting_phase12_survey_gate_present": false',
]

DIRECT_TEST_MARKERS = [
    'test "phase12 nvme pci queue planner keeps host DMA budget smaller when IO queues use CMB"',
    'test "phase12 nvme pci prp shape reports multi-page throughput fanout"',
    'test "phase12 nvme pci recovery restore summary keeps admin-first replay and DMA budget reviewable"',
    'test "phase12 nvme pci dropped backlog retirement stays blocked until recovery plans are rebuilt"',
]


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    ensure_contains(
        failures,
        "nvme_survey_note",
        (root / SURVEY_NOTE_PATH).read_text(encoding="utf-8"),
        SURVEY_NOTE_MARKERS,
    )
    ensure_contains(
        failures,
        "nvme_fallback_map",
        (root / FALLBACK_MAP_PATH).read_text(encoding="utf-8"),
        FALLBACK_MAP_MARKERS,
    )
    ensure_contains(
        failures,
        "nvme_reopen_governance",
        (root / REOPEN_GOVERNANCE_PATH).read_text(encoding="utf-8"),
        REOPEN_GOVERNANCE_MARKERS,
    )
    ensure_contains(
        failures,
        "nvme_manifest",
        (root / MANIFEST_PATH).read_text(encoding="utf-8"),
        MANIFEST_MARKERS,
    )
    ensure_contains(
        failures,
        "nvme_direct_test",
        (root / DIRECT_TEST_PATH).read_text(encoding="utf-8"),
        DIRECT_TEST_MARKERS,
    )
    return failures


def minimal_join(title: str, markers: list[str]) -> str:
    return title + "\n\n" + "\n".join(markers) + "\n"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder_for(rel_path: str) -> str:
    mapping = {
        SURVEY_NOTE_PATH: minimal_join("# Phase 12 NVMe PCI Survey", SURVEY_NOTE_MARKERS),
        FALLBACK_MAP_PATH: minimal_join(
            "# Phase 12 NVMe PCI Raw GitHub Fallback Map", FALLBACK_MAP_MARKERS
        ),
        REOPEN_GOVERNANCE_PATH: minimal_join(
            "# Phase 12 NVMe PCI Reopen Governance", REOPEN_GOVERNANCE_MARKERS
        ),
        MANIFEST_PATH: "{\n  "
        + ",\n  ".join(MANIFEST_MARKERS)
        + "\n}\n",
        DIRECT_TEST_PATH: "\n".join(DIRECT_TEST_MARKERS) + "\n",
        DRIVER_PATH: "// fixture\n",
        VERIFY_PATH: "// fixture\n",
    }
    return mapping[rel_path]


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, placeholder_for(rel_path))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-nvme-packet-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        (base / SURVEY_NOTE_PATH).unlink()
        expect_failure(base, f"missing_file:{SURVEY_NOTE_PATH}")

        write_fixture_tree(base)
        survey_path = base / SURVEY_NOTE_PATH
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                SURVEY_NOTE_MARKERS[1], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"nvme_survey_note:{SURVEY_NOTE_MARKERS[1]}")

        write_fixture_tree(base)
        survey_path = base / SURVEY_NOTE_PATH
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                SURVEY_NOTE_MARKERS[9], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"nvme_survey_note:{SURVEY_NOTE_MARKERS[9]}")

        write_fixture_tree(base)
        fallback_path = base / FALLBACK_MAP_PATH
        fallback_path.write_text(
            fallback_path.read_text(encoding="utf-8").replace(
                FALLBACK_MAP_MARKERS[3], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"nvme_fallback_map:{FALLBACK_MAP_MARKERS[3]}")

        write_fixture_tree(base)
        fallback_path = base / FALLBACK_MAP_PATH
        fallback_path.write_text(
            fallback_path.read_text(encoding="utf-8").replace(
                FALLBACK_MAP_MARKERS[6], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"nvme_fallback_map:{FALLBACK_MAP_MARKERS[6]}")

        write_fixture_tree(base)
        governance_path = base / REOPEN_GOVERNANCE_PATH
        governance_path.write_text(
            governance_path.read_text(encoding="utf-8").replace(
                REOPEN_GOVERNANCE_MARKERS[7], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"nvme_reopen_governance:{REOPEN_GOVERNANCE_MARKERS[7]}",
        )

        write_fixture_tree(base)
        manifest_path = base / MANIFEST_PATH
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8").replace(
                MANIFEST_MARKERS[3], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"nvme_manifest:{MANIFEST_MARKERS[3]}")

        write_fixture_tree(base)
        direct_test_path = base / DIRECT_TEST_PATH
        direct_test_path.write_text(
            direct_test_path.read_text(encoding="utf-8").replace(
                DIRECT_TEST_MARKERS[2], "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(base, f"nvme_direct_test:{DIRECT_TEST_MARKERS[2]}")

        print("PHASE12_NVME_PACKET_CHECK=pass")
        print("PHASE12_NVME_PACKET_SELF_TEST=pass")
        print("PHASE12_NVME_PACKET_SELF_TEST_CASE_COUNT=8")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current bounded Phase 12 NVMe PCI starter packet so the "
            "survey note, fallback map, reopen-governance note, manifest, and direct "
            "replay stay aligned on the shipped driver-local boundary."
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
        print("PHASE12_NVME_PACKET_CHECK=fail")
        print("PHASE12_NVME_PACKET_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_NVME_PACKET_FAILURES_END")
        return 1

    marker_count = (
        len(REQUIRED_FILES)
        + len(SURVEY_NOTE_MARKERS)
        + len(FALLBACK_MAP_MARKERS)
        + len(REOPEN_GOVERNANCE_MARKERS)
        + len(MANIFEST_MARKERS)
        + len(DIRECT_TEST_MARKERS)
    )
    print("PHASE12_NVME_PACKET_CHECK=pass")
    print(f"PHASE12_NVME_PACKET_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
