#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

REQUIRED_FILES = [
    Path("Documentation/zigux/phase12-release-sequencing.md"),
    Path("Documentation/zigux/phase12-release-readiness-survey.md"),
    Path("Documentation/zigux/phase12-release-coordination-matrix.md"),
    Path("Documentation/zigux/phase12-virtio-net-survey.md"),
    Path("Documentation/zigux/phase12-nvme-pci-slice.md"),
    Path("Documentation/zigux/phase12-nvme-pci-survey.md"),
    Path("zigux/tests/phase12_build.zig"),
    Path("zigux/tests/phase12_nvme_pci.zig"),
    Path("zigux/tests/phase12_nvme_pci_survey.zig"),
    Path("zigux/tests/phase12_nvme_pci_manifest.json"),
    Path("scripts/zigux/check-build-only-phase12-surface.py"),
    Path("scripts/zigux/check-phase12-cross.py"),
    Path("scripts/zigux/check-phase12-release-readiness-packet.py"),
    Path("scripts/zigux/validate-phase12.py"),
]

REQUIRED_MARKERS = [
    "Phase 12 flow - `validate-phase12.py` checks that the current complex-driver packet stays aligned across",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase12-virtio-net-survey.md`",
    "`Documentation/zigux/phase12-nvme-pci-slice.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
    "`zigux/tests/phase12_nvme_pci.zig`",
    "`zigux/tests/phase12_nvme_pci_survey.zig`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
    "`scripts/zigux/check-phase12-scripts-readme-release-packet.py`",
    "`python3 scripts/zigux/check-phase12-scripts-readme-release-packet.py --self-test`",
    "`make -C zigux phase12-validate`",
    "`make -C zigux phase12-smoke`",
    "`make -C zigux phase12`",
    "the direct `phase12_libbpf_*` replay files stay recorded only through the shared survey, fallback, parked, or anti-overlap notes until they actually land on `master`",
    "broader shared `check-phase12-*.py` family",
    "make -C zigux phase12-smoke ZIG=<attached-zig-path>",
    "make -C zigux phase12 ZIG=<attached-zig-path>",
]


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    if not (root / SCRIPTS_README_PATH).exists():
        return [f"missing_file:{SCRIPTS_README_PATH.as_posix()}"]

    text = read_text(root, SCRIPTS_README_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"scripts_readme:{marker}")

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_packet_file:{relative_path.as_posix()}")

    return failures


def write_fixture_tree(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {relative_path.as_posix()}\n", encoding="utf-8")

    readme_path = root / SCRIPTS_README_PATH
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(
        "\n".join(
            [
                "# scripts/zigux",
                "",
                (
                    "Phase 12 flow - `validate-phase12.py` checks that the current "
                    "complex-driver packet stays aligned across "
                    "`Documentation/zigux/phase12-release-sequencing.md`, "
                    "`Documentation/zigux/phase12-release-readiness-survey.md`, "
                    "`Documentation/zigux/phase12-release-coordination-matrix.md`, "
                    "`Documentation/zigux/phase12-virtio-net-survey.md`, "
                    "`Documentation/zigux/phase12-nvme-pci-slice.md`, "
                    "`Documentation/zigux/phase12-nvme-pci-survey.md`, "
                    "`scripts/zigux/check-build-only-phase12-surface.py`, "
                    "`scripts/zigux/check-phase12-release-readiness-packet.py`, "
                    "`scripts/zigux/check-phase12-scripts-readme-release-packet.py`, "
                    "`zigux/tests/phase12_build.zig`, `zigux/tests/phase12_nvme_pci.zig`, "
                    "`zigux/tests/phase12_nvme_pci_survey.zig`, and "
                    "`zigux/tests/phase12_nvme_pci_manifest.json` before the shared "
                    "validator-first then smoke-first routes run."
                ),
                (
                    "- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, "
                    "`python3 scripts/zigux/check-phase12-cross.py --self-test`, "
                    "`python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, "
                    "`python3 scripts/zigux/check-phase12-scripts-readme-release-packet.py --self-test`, "
                    "and `make -C zigux phase12-validate` keep the degraded-workflow "
                    "support bundle explicit in this scripts-root summary so the shipped "
                    "validator-first route stays visible as support-bundle evidence rather "
                    "than as a second direct replay route."
                ),
                (
                    "- `make -C zigux phase12-validate`, "
                    "`zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, "
                    "`make -C zigux phase12-smoke`, "
                    "`zig build test --build-file zigux/tests/phase12_build.zig --summary all`, "
                    "and `make -C zigux phase12` keep the active shared complex-driver "
                    "packet reviewable, while the direct `phase12_libbpf_*` replay files "
                    "stay recorded only through the shared survey, fallback, parked, or "
                    "anti-overlap notes until they actually land on `master`, without "
                    "implying a focused libbpf-only replay, a cross-build replay, or a "
                    "broader shared `check-phase12-*.py` family."
                ),
                (
                    "- If `zig` is unavailable on `PATH`, first rely on the repo-local "
                    "`.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local "
                    "fallback is also absent, rerun only the shipped Make routes as "
                    "`make -C zigux phase12-validate`, "
                    "`make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and "
                    "`make -C zigux phase12 ZIG=<attached-zig-path>` instead of "
                    "inventing an unshipped fallback route."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = collect_failures(root)
    if expected not in failures:
        raise SystemExit(f"expected failure {expected!r}, got {failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-scripts-readme-release-packet-"))
    try:
        write_fixture_tree(base)
        failures = collect_failures(base)
        if failures:
            raise SystemExit(f"unexpected failures for valid fixture: {failures!r}")

        write_fixture_tree(base)
        broken_readme = (base / SCRIPTS_README_PATH).read_text(encoding="utf-8").replace(
            "`Documentation/zigux/phase12-release-coordination-matrix.md`", "", 1
        )
        (base / SCRIPTS_README_PATH).write_text(broken_readme, encoding="utf-8")
        expect_failure(
            base,
            "scripts_readme:`Documentation/zigux/phase12-release-coordination-matrix.md`",
        )

        write_fixture_tree(base)
        broken_readme = (base / SCRIPTS_README_PATH).read_text(encoding="utf-8").replace(
            "broader shared `check-phase12-*.py` family",
            "broader checker family",
            1,
        )
        (base / SCRIPTS_README_PATH).write_text(broken_readme, encoding="utf-8")
        expect_failure(base, "scripts_readme:broader shared `check-phase12-*.py` family")

        write_fixture_tree(base)
        broken_readme = (base / SCRIPTS_README_PATH).read_text(encoding="utf-8").replace(
            "make -C zigux phase12-smoke ZIG=<attached-zig-path>",
            "make -C zigux phase12-smoke ZIG=",
            1,
        )
        (base / SCRIPTS_README_PATH).write_text(broken_readme, encoding="utf-8")
        expect_failure(base, "scripts_readme:make -C zigux phase12-smoke ZIG=<attached-zig-path>")

        write_fixture_tree(base)
        (base / REQUIRED_FILES[0]).unlink()
        expect_failure(
            base,
            f"missing_packet_file:{REQUIRED_FILES[0].as_posix()}",
        )

        print("PHASE12_SCRIPTS_README_RELEASE_PACKET_SELF_TEST=pass")
        print("PHASE12_SCRIPTS_README_RELEASE_PACKET_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed on the Phase 12 scripts-root release packet wording and its "
            "bounded release-planning file anchors."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing scripts/zigux/README.md.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run fixture-backed self-tests.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.repo_root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE12_SCRIPTS_README_RELEASE_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
