#!/usr/bin/env python3
"""PHASE12_CHECK_PACKET=complex_driver_lane_sequencing

Fail-closed checker for the shared Phase 12 complex-driver lane-sequencing note.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE12_CHECK_PACKET=complex_driver_lane_sequencing"
NOTE_PATH = "Documentation/zigux/phase12-complex-driver-lane-sequencing.md"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_FILES = [
    NOTE_PATH,
    MAKEFILE_PATH,
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
    "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-slice.md",
    "Documentation/zigux/phase12-virtio-scsi-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-nvme-pci-reopen-governance.md",
    "Documentation/zigux/phase12-nvme-pci-slice.md",
    "Documentation/zigux/phase12-nvme-pci-survey.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-build-only-phase12-surface.py",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "zigux/tests/README.md",
    "zigux/tests/phase12_virtio_net_manifest.json",
    "zigux/tests/phase12_virtio_net_survey.zig",
    "zigux/tests/phase12_virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_scsi_manifest.json",
    "zigux/tests/phase12_virtio_scsi_survey.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    "zigux/tests/phase12_nvme_pci_manifest.json",
    "zigux/tests/phase12_nvme_pci_survey.zig",
    "zigux/tests/phase12_nvme_pci.zig",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "drivers/nvme/host/pci_verify.zig",
]

NOTE_MARKERS = [
    "scope: shared release-planning, review-surface truthfulness, smoke-first replay reminders, fallback wording, and anti-overlap guidance for the bounded `nvme_pci`, `virtio_net`, and `virtio_scsi` families",
    "drivers/net/virtio_net_transmit_recycle.zig",
    "zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig",
    "drivers/nvme/host/pci_verify.zig",
    "The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history",
    "`python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
    "`python3 scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test`",
    "`python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`",
    "Current `master` now ships the smaller validator-first bundle through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-sequencing.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but there is still no focused-libbpf-only replay or cross-build replay.",
    "If this lane reopens soon, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-complex-driver-lane-sequencing.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, and `make -C zigux phase12-validate`",
]

MAKEFILE_MARKERS = [
    "phase12-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py",
    "phase12: phase12-validate phase12-smoke phase12-test",
]


def repo_root() -> Path:
    resolved = Path(__file__).resolve()
    return resolved.parents[2] if len(resolved.parents) >= 3 else resolved.parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_exact_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def require_exact_line_count(errors: list[str], rel_path: str, text: str, markers: list[str]) -> None:
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line == marker)
        if count != 1:
            errors.append(
                f"marker count drift in {rel_path}: {marker} (expected 1, found {count})"
            )


def check(root: Path, source_text: str | None = None) -> list[str]:
    errors: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            errors.append(f"missing file: {rel_path}")
    if errors:
        return errors

    checker_source = source_text if source_text is not None else read_text(Path(__file__))
    if MARKER not in checker_source:
        errors.append("checker marker missing from checker source")

    require_exact_count(errors, NOTE_PATH, read_text(root / NOTE_PATH), NOTE_MARKERS)
    require_exact_line_count(
        errors, MAKEFILE_PATH, read_text(root / MAKEFILE_PATH), MAKEFILE_MARKERS
    )
    return errors


def good_note_text() -> str:
    return "\n".join(
        [
            "# Phase 12 Complex-Driver Lane Sequencing",
            "",
            "This note is the anti-overlap companion for the shared Phase 12 complex-driver packet.",
            "",
            "## Status",
            "- `PHASE12_STATUS=active`",
            "- scope: shared release-planning, review-surface truthfulness, smoke-first replay reminders, fallback wording, and anti-overlap guidance for the bounded `nvme_pci`, `virtio_net`, and `virtio_scsi` families",
            "",
            "## Lane Scope",
            "- `drivers/net/virtio_net_transmit_recycle.zig` stays part of the bounded `virtio_net` follow-up packet.",
            "- `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` stays explicit beside the shipped `virtio_scsi` rollback-lab packet.",
            "- `drivers/nvme/host/pci_verify.zig` stays explicit beside the bounded NVMe starter packet.",
            "",
            "## Anti-Overlap Rules",
            "- The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history.",
            "",
            "## Boundaries",
            "- Current `master` now ships the smaller validator-first bundle through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-sequencing.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but there is still no focused-libbpf-only replay or cross-build replay.",
            "- Keep the degraded-workflow validation quartet explicit beside that same order too:",
            "  - `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`",
            "  - `python3 scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test`",
            "  - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`",
            "  - `make -C zigux phase12-validate`",
            "",
            "## Next Bounded Step",
            "If this lane reopens soon, rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-complex-driver-lane-sequencing.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, and `make -C zigux phase12-validate` before rereading the shared Phase 12 reminder packet.",
            "",
        ]
    )


def good_makefile_text() -> str:
    return "\n".join(
        [
            "phase12-validate:",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-build-only-phase12-surface.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-release-readiness-packet.py",
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase12.py",
            "",
            "phase12: phase12-validate phase12-smoke phase12-test",
            "",
        ]
    )


def write_fixture_root(tmp_root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        path = tmp_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if rel_path == NOTE_PATH:
            path.write_text(good_note_text(), encoding="utf-8")
        elif rel_path == MAKEFILE_PATH:
            path.write_text(good_makefile_text(), encoding="utf-8")
        else:
            path.write_text("fixture\n", encoding="utf-8")


def expect_contains(errors: list[str], needle: str, label: str) -> None:
    if not any(needle in error for error in errors):
        raise SystemExit(f"{label}: {errors!r}")


def run_self_test() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="phase12-complex-driver-lane-"))
    case_count = 0
    try:
        write_fixture_root(tmp_root)
        if errors := check(tmp_root, source_text=MARKER):
            raise SystemExit(f"self-test expected success but failed: {errors!r}")

        (tmp_root / "drivers/nvme/host/pci_verify.zig").unlink()
        case_count += 1
        expect_contains(check(tmp_root, source_text=MARKER), "missing file: drivers/nvme/host/pci_verify.zig", "missing nvme verifier not detected")
        write_fixture_root(tmp_root)

        write_text(
            tmp_root / NOTE_PATH,
            good_note_text().replace(
                "`python3 scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test`",
                "`python3 scripts/zigux/check-phase12-complex-driver-lane-sequencing-missing.py --self-test`",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test",
            "missing lane-checker self-test marker not detected",
        )
        write_fixture_root(tmp_root)

        write_text(
            tmp_root / NOTE_PATH,
            good_note_text().replace(
                "The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history.",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "The separate `p12-complex-drivers-nvme-pci-history` lane remains the home for bounded nvme recovery replay history",
            "missing nvme history lane marker not detected",
        )
        write_fixture_root(tmp_root)

        write_text(
            tmp_root / NOTE_PATH,
            good_note_text().replace(
                "Current `master` now ships the smaller validator-first bundle through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-sequencing.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but there is still no focused-libbpf-only replay or cross-build replay.",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "Current `master` now ships the smaller validator-first bundle through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-complex-driver-lane-sequencing.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but there is still no focused-libbpf-only replay or cross-build replay.",
            "missing validator bundle boundary marker not detected",
        )
        write_fixture_root(tmp_root)

        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test\n",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "scripts/zigux/check-phase12-complex-driver-lane-sequencing.py --self-test",
            "missing Makefile lane-checker self-test not detected",
        )
        write_fixture_root(tmp_root)

        write_text(
            tmp_root / MAKEFILE_PATH,
            good_makefile_text().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py\n",
                "",
                1,
            ),
        )
        case_count += 1
        expect_contains(
            check(tmp_root, source_text=MARKER),
            "marker count drift in zigux/Makefile: \tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-complex-driver-lane-sequencing.py (expected 1, found 0)",
            "missing Makefile lane-checker run not detected",
        )
        write_fixture_root(tmp_root)

        case_count += 1
        expect_contains(
            check(tmp_root, source_text="PHASE12_CHECK_PACKET=broken"),
            "checker marker missing from checker source",
            "missing checker marker not detected",
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("PHASE12_COMPLEX_DRIVER_LANE_SELF_TEST=pass")
    print(f"PHASE12_COMPLEX_DRIVER_LANE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="repository root to validate (defaults to the checker directory)",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("phase12 complex-driver lane sequencing validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
