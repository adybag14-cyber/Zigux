#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"

REQUIRED_FILES = [
    DOCS_README_PATH,
    SCRIPTS_README_PATH,
]

REQUIRED_MARKERS = {
    DOCS_README_PATH: [
        "keep the bounded Phase 12 docs-root packet explicit through the shared release-order, readiness, closure, coordination, fallback, and driver-local reminder notes plus the shipped validator-side support bundle instead of letting the docs root drift away from the active-not-closed release packet on current `master`.",
        "`scripts/zigux/validate-phase12.py`, `scripts/zigux/check-build-only-phase12-surface.py`, and `scripts/zigux/check-phase12-release-readiness-packet.py` keep the directly readable validator-side support bundle explicit from the docs root while current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again, and `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns on current `master`.",
        "keep the bounded packet split explicit here too: `virtio_net` stays starter-present reviewability, `virtio_scsi` stays the smoke-first and rollback-lab packet, `nvme_pci` stays driver-local outside the shared smoke-and-test route, and the Phase 12 libbpf packet stays parked behind survey, snapshot, and verify-shard reminder surfaces instead of widening the docs root into deeper DMA, queueing, throughput, or transport claims.",
    ],
    SCRIPTS_README_PATH: [
        "Phase 12 flow - the current shared release packet stays reviewable through the release-order and readiness companions, the scripts-side support checker pair, the shipped validator body, the returned shared Makefile routes, the shared build gate, and the bounded driver-family split instead of reviving a missing validate wrapper or widening into driver-local DMA, queueing, throughput, or segmented-rollout claims",
        "`Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` keep the shipped shared Phase 12 reminder packet explicit from the scripts root",
        "`zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and the shared checker pair keep the current smoke-first build gate explicit, while `virtio_net` stays starter-present reviewability, `virtio_scsi` stays the smoke-first and rollback-lab packet, and `nvme_pci` stays driver-local outside the shared smoke-and-test route",
    ],
}


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")
    if missing:
        return missing, []

    drift: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        text = (root / rel_path).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                drift.append(f"missing_marker:{rel_path}:{marker}")
    return [], drift


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def marker_fixture(title: str, markers: list[str]) -> str:
    body = "\n".join(f"- {marker}" for marker in markers)
    return f"{title}\n\n{body}\n"


FIXTURE_TEXT = {
    DOCS_README_PATH: marker_fixture(
        "# Zigux Documentation",
        REQUIRED_MARKERS[DOCS_README_PATH],
    ),
    SCRIPTS_README_PATH: marker_fixture(
        "# scripts/zigux",
        REQUIRED_MARKERS[SCRIPTS_README_PATH],
    ),
}


def write_fixture_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        write_text(root / rel_path, FIXTURE_TEXT[rel_path])


def expect_failure(root: Path, expected: str) -> None:
    missing, drift = validate(root)
    failures = missing + drift
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(f"- {marker}\n", "")
    updated = updated.replace(marker, "")
    if updated == text:
        raise SystemExit(f"marker not removable: {marker}")
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-shared-rollback-summary-"))
    try:
        write_fixture_root(base)
        missing, drift = validate(base)
        if missing or drift:
            raise SystemExit(f"fixture tree should pass but failed: {(missing + drift)!r}")

        for rel_path in REQUIRED_FILES:
            write_fixture_root(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                write_fixture_root(base)
                remove_marker(base / rel_path, marker)
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        case_count = len(REQUIRED_FILES) + sum(
            len(markers) for markers in REQUIRED_MARKERS.values()
        )
        print("PHASE12_SHARED_ROLLBACK_SUMMARY_SELF_TEST=pass")
        print(f"PHASE12_SHARED_ROLLBACK_SUMMARY_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the current Phase 12 shared reminder summaries so the "
            "docs-root and scripts-root rollback packet does not drift away "
            "from the shipped smoke-first and rollback-lab evidence."
        )
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test without reading repo files.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the inferred repository root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing, drift = validate(args.root)
    if missing:
        print("PHASE12_SHARED_ROLLBACK_SUMMARY=fail")
        print("PHASE12_SHARED_ROLLBACK_SUMMARY_MISSING_FILES_START")
        for item in missing:
            print(item)
        print("PHASE12_SHARED_ROLLBACK_SUMMARY_MISSING_FILES_END")
        return 1
    if drift:
        print("PHASE12_SHARED_ROLLBACK_SUMMARY=fail")
        print("PHASE12_SHARED_ROLLBACK_SUMMARY_DRIFT_START")
        for item in drift:
            print(item)
        print("PHASE12_SHARED_ROLLBACK_SUMMARY_DRIFT_END")
        return 1

    print("PHASE12_SHARED_ROLLBACK_SUMMARY=pass")
    print(f"PHASE12_SHARED_ROLLBACK_SUMMARY_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE12_SHARED_ROLLBACK_SUMMARY_MARKER_COUNT="
        f"{sum(len(v) for v in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
