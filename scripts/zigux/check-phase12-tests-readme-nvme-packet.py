#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

TESTS_README_PATH = Path("zigux/tests/README.md")

NVME_PACKET_MARKERS = [
    "`Documentation/zigux/phase12-nvme-pci-slice.md`",
    "`Documentation/zigux/phase12-nvme-pci-survey.md`",
    "`zigux/tests/phase12_nvme_pci.zig`",
    "`zigux/tests/phase12_nvme_pci_survey.zig`",
    "`zigux/tests/phase12_nvme_pci_manifest.json`",
]

NVME_PACKET_PATHS = [
    Path("Documentation/zigux/phase12-nvme-pci-slice.md"),
    Path("Documentation/zigux/phase12-nvme-pci-survey.md"),
    Path("zigux/tests/phase12_nvme_pci.zig"),
    Path("zigux/tests/phase12_nvme_pci_survey.zig"),
    Path("zigux/tests/phase12_nvme_pci_manifest.json"),
]

PARKED_LIBBPF_CLAUSE = (
    "the direct `phase12_libbpf_*` replay files stay recorded only through the "
    "shared survey, fallback, parked, or anti-overlap notes until they actually "
    "land on `master`"
)


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    return path.read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    readme_path = root / TESTS_README_PATH
    if not readme_path.exists():
        return [f"missing_file:{TESTS_README_PATH.as_posix()}"]

    tests_readme = read_text(root, TESTS_README_PATH)

    for marker in NVME_PACKET_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:{marker}")

    if PARKED_LIBBPF_CLAUSE not in tests_readme:
        failures.append(f"tests_readme:{PARKED_LIBBPF_CLAUSE}")

    for relative_path in NVME_PACKET_PATHS:
        if not (root / relative_path).exists():
            failures.append(f"missing_packet_file:{relative_path.as_posix()}")

    return failures


def write_fixture_tree(root: Path) -> None:
    for relative_path in NVME_PACKET_PATHS:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture for {relative_path.as_posix()}\n", encoding="utf-8")

    readme_path = root / TESTS_README_PATH
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(
        "\n".join(
            [
                "# zigux/tests",
                "",
                "Phase 12 packet reminder:",
                (
                    "  * keep the shared Phase 12 complex-driver packet explicit in "
                    "the tests root too: "
                    "`Documentation/zigux/phase12-nvme-pci-slice.md`, "
                    "`Documentation/zigux/phase12-nvme-pci-survey.md`, "
                    "`zigux/tests/phase12_nvme_pci.zig`, "
                    "`zigux/tests/phase12_nvme_pci_survey.zig`, and "
                    "`zigux/tests/phase12_nvme_pci_manifest.json` stay explicit as "
                    "the bounded NVMe driver-local packet while the direct "
                    "`phase12_libbpf_*` replay files stay recorded only through the "
                    "shared survey, fallback, parked, or anti-overlap notes until "
                    "they actually land on `master`."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = collect_failures(root)
    if expected not in failures:
        raise SystemExit(
            f"expected failure {expected!r}, got {failures!r}"
        )


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase12-nvme-tests-readme-check-"))
    try:
        write_fixture_tree(base)
        failures = collect_failures(base)
        if failures:
            raise SystemExit(f"unexpected failures for valid fixture: {failures!r}")

        write_fixture_tree(base)
        broken_readme = (base / TESTS_README_PATH).read_text(encoding="utf-8").replace(
            NVME_PACKET_MARKERS[2], "", 1
        )
        (base / TESTS_README_PATH).write_text(broken_readme, encoding="utf-8")
        expect_failure(base, f"tests_readme:{NVME_PACKET_MARKERS[2]}")

        write_fixture_tree(base)
        broken_readme = (base / TESTS_README_PATH).read_text(encoding="utf-8").replace(
            PARKED_LIBBPF_CLAUSE, "libbpf replay wording drifted", 1
        )
        (base / TESTS_README_PATH).write_text(broken_readme, encoding="utf-8")
        expect_failure(base, f"tests_readme:{PARKED_LIBBPF_CLAUSE}")

        write_fixture_tree(base)
        (base / NVME_PACKET_PATHS[0]).unlink()
        expect_failure(base, f"missing_packet_file:{NVME_PACKET_PATHS[0].as_posix()}")

        print("PHASE12_TESTS_README_NVME_PACKET_CHECK_SELF_TEST=pass")
        print("PHASE12_TESTS_README_NVME_PACKET_CHECK_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed on the Phase 12 tests-root NVMe packet wording and its "
            "bounded file anchors."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root containing zigux/tests/README.md.",
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

    print("PHASE12_TESTS_README_NVME_PACKET_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
