#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
PHASE12_SEQUENCE_PATH = "Documentation/zigux/phase12-release-sequencing.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

FORBIDDEN_LITERAL_COUNTS = {
    "validate-phase12.py": 6,
    "check-phase12-*.py": 6,
    "phase12-validate": 5,
}

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 12 flow",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`",
    "`zigux/tests/phase12_build.zig`",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "`check-build-only-phase12-surface.py --self-test` and `check-build-only-phase12-surface.py` keep the docs-root, scripts-root, tests-root, and Makefile build-only contract fail-closed while `.github/workflows/zigux-bootstrap.yml` reruns that same self-test plus the live checker in CI.",
    "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`",
]

REQUIRED_DOCS_README_MARKERS = [
    "Phase 12 notes",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, and `make -C zigux phase12` now keep the current nvme pci, virtio_net, virtio_scsi, and libbpf survey-backed complex-driver bundle reviewable through the shipped Phase 12 release packet instead of implying removed validator or PMO checker surfaces.",
    "`scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`",
    "there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "- if the change touches the shared Phase 12 complex-driver packet, do `Documentation/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `Documentation/zigux/phase12-release-sequencing.md`",
    "`make -C zigux phase12` still agree on the same shipped nvme, virtio_net, virtio_scsi, and libbpf survey packet plus the active release-order note without implying removed `validate-phase12.py`, `check-phase12-*.py`, raw-coverage, or focused-libbpf-only replay surfaces that are not on `master`?",
]

REQUIRED_SEQUENCE_MARKERS = [
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py` must continue to keep that build-only contract fail-closed rather than implying an unshipped validator stack.",
    "current public fallback split: two commit-pinned artifacts (`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)",
    "`scripts/zigux/check-build-only-phase12-surface.py` is a shipped build-only contract checker, not a broader validator-first release gate",
    "there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`",
]

REQUIRED_TESTS_README_MARKERS = [
    "keep the active Phase 12 survey-backed complex-driver packet explicit in the tests root too:",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-build-only-phase12-surface.py`",
    "`zigux/tests/phase12_build.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase12`",
    "without implying removed `validate-phase12.py`, `check-phase12-*.py`, release-readiness, raw-coverage, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces that are not on `master`",
    "only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors rather than implied fallback maps",
]

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase12-test phase12",
    "phase12-test:",
    "$(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all",
    "phase12: phase12-test",
]

REQUIRED_WORKFLOW_MARKERS = [
    "Self-test Phase 12 build-only surface checker",
    "python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "Check Phase 12 build-only surface",
    "python3 scripts/zigux/check-build-only-phase12-surface.py",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "PHONY += phase12-validate",
    "phase12-validate:",
    "validate-phase12.py",
    "check-phase12-",
]

FORBIDDEN_SCRIPT_FILES = [
    "scripts/zigux/validate-phase12.py",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def expect_exact_count(text: str, marker: str, count: int, label: str, failures: list[str]) -> None:
    actual = text.count(marker)
    if actual != count:
        failures.append(f"{label}:{marker}:count={actual}:expected={count}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        PHASE12_SEQUENCE_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    for rel_path in FORBIDDEN_SCRIPT_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    phase12_wrapper_paths = sorted(
        str(path.relative_to(root))
        for path in (root / "scripts/zigux").glob("check-phase12-*.py")
        if path.is_file()
    )
    for rel_path in phase12_wrapper_paths:
        failures.append(f"unexpected_file:{rel_path}")

    if failures:
        return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    phase12_sequence = read_text(root, PHASE12_SEQUENCE_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

    for marker in REQUIRED_DOCS_README_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist:{marker}")
    for marker in REQUIRED_SEQUENCE_MARKERS:
        if marker not in phase12_sequence:
            failures.append(f"phase12_sequence:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"scripts_readme:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:{marker}")
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile:
            failures.append(f"makefile_forbidden:{marker}")

    combined_claim_surface = "\n".join([
        docs_readme,
        review_checklist,
        phase12_sequence,
        scripts_readme,
        tests_readme,
    ])
    for marker, count in FORBIDDEN_LITERAL_COUNTS.items():
        expect_exact_count(combined_claim_surface, marker, count, "claim_surface", failures)

    return failures


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write(
        root / DOCS_README_PATH,
        """# Zigux Documentation

Phase 12 notes
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, and `make -C zigux phase12` now keep the current nvme pci, virtio_net, virtio_scsi, and libbpf survey-backed complex-driver bundle reviewable through the shipped Phase 12 release packet instead of implying removed validator or PMO checker surfaces.
- the current shared Phase 12 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/README.md`, `zigux/tests/phase12_build.zig`, the bounded Phase 12 nvme, virtio_net, virtio_scsi, and libbpf test modules wired through that build, the committed Phase 12 manifests under `zigux/tests/`, `tools/lib/bpf/zigux_segments/manifest.json`, and `zigux/Makefile`.
- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make surfaces until new validator files actually land.
""",
    )
    write(
        root / REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

## Validation
- if the change touches the shared Phase 12 complex-driver packet, do `Documentation/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/tests/phase12_build.zig`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_libbpf_manifest.json`, `tools/lib/bpf/zigux_segments/manifest.json`, and `make -C zigux phase12` still agree on the same shipped nvme, virtio_net, virtio_scsi, and libbpf survey packet plus the active release-order note without implying removed `validate-phase12.py`, `check-phase12-*.py`, raw-coverage, or focused-libbpf-only replay surfaces that are not on `master`?
""",
    )
    write(
        root / PHASE12_SEQUENCE_PATH,
        """# Phase 12 Release Sequencing

- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-build-only-phase12-surface.py` must continue to keep that build-only contract fail-closed rather than implying an unshipped validator stack.
- current public fallback split: two commit-pinned artifacts (`Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)
- `scripts/zigux/check-build-only-phase12-surface.py` is a shipped build-only contract checker, not a broader validator-first release gate
- there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` release packet, and no `make -C zigux phase12-validate` target on `master`
- future notes should not invent `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` surfaces before they land
""",
    )
    write(
        root / SCRIPTS_README_PATH,
        """# scripts/zigux

Phase 12 flow
- the current shared Phase 12 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, the bounded Phase 12 nvme, virtio_net, virtio_scsi, and libbpf test modules wired through that build, the committed Phase 12 manifests under `zigux/tests/`, and `tools/lib/bpf/zigux_segments/manifest.json`.
- `check-build-only-phase12-surface.py --self-test` and `check-build-only-phase12-surface.py` keep the docs-root, scripts-root, tests-root, and Makefile build-only contract fail-closed while `.github/workflows/zigux-bootstrap.yml` reruns that same self-test plus the live checker in CI.
- `zig build test --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12` rerun that same bounded survey-backed tranche.
- there is no dedicated shared `validate-phase12.py`, `check-phase12-*.py`, or `phase12-validate` target on `master`; future Phase 12 reviewability claims should name only shipped survey, build, and make surfaces until new validator files actually land.
""",
    )
    write(
        root / TESTS_README_PATH,
        """# zigux/tests

- keep the active Phase 12 survey-backed complex-driver packet explicit in the tests root too: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `tools/lib/bpf/zigux_segments/manifest.json`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, and `make -C zigux phase12` should continue to keep the current nvme, virtio_net, virtio_scsi, and libbpf survey packet plus the active release-order note reviewable from the tests root without implying removed `validate-phase12.py`, `check-phase12-*.py`, release-readiness, raw-coverage, focused-libbpf-only replay, cross-build, or `phase12-validate` surfaces that are not on `master`; keep the current public fallback split explicit too: only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors rather than implied fallback maps
""",
    )
    write(
        root / MAKEFILE_PATH,
        """PHONY += phase12-test phase12

phase12-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-test
""",
    )
    write(
        root / WORKFLOW_PATH,
        """jobs:
  bootstrap:
    steps:
      - name: Self-test Phase 12 build-only surface checker
        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test
      - name: Check Phase 12 build-only surface
        run: python3 scripts/zigux/check-build-only-phase12-surface.py
""",
    )


def expect_failure(root: Path, expected: str, label: str) -> None:
    failures = validate(root)
    if expected not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase12_build_only_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)

        baseline = validate(root)
        if baseline:
            raise SystemExit("baseline_failed:" + ",".join(baseline))

        write(root / "scripts/zigux/validate-phase12.py", "print('unexpected')\n")
        expect_failure(
            root,
            "unexpected_file:scripts/zigux/validate-phase12.py",
            "unexpected_validate_script",
        )

    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    print("PHASE12_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=15")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 12 build-only surface without inventing a validator route."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
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
        print("PHASE12_BUILD_ONLY_SURFACE=fail")
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE12_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    print("PHASE12_BUILD_ONLY_SURFACE=pass")
    print(
        "PHASE12_BUILD_ONLY_SURFACE_MARKER_COUNT="
        f"{len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_SEQUENCE_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(FORBIDDEN_LITERAL_COUNTS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
