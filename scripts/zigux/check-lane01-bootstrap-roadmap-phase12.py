#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE11_HEADING = "## Phase 11: Simple Production Drivers"
PHASE12_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"
PHASE13_HEADING = "## Phase 13: Shared Subsystem Helpers"

REQUIRED_LINES = (
    PHASE12_HEADING,
    "Primary product goal:",
    "- take on high-value, high-risk drivers only after earlier proof",
    "Primary Linux anchors:",
    "- `drivers/net/virtio_net.c`",
    "- `drivers/nvme/host/pci.c`",
    "- `drivers/scsi/virtio_scsi.c`",
    "- `tools/lib/bpf/libbpf.c`",
    "Required Zigux features:",
    "- DMA-safe abstractions",
    "- queueing correctness",
    "- throughput and recovery parity",
    "- segmented rollout",
    "Recommended Zigux destinations:",
    "- `drivers/net/virtio_net.zig`",
    "- `drivers/nvme/host/pci.zig`",
    "- `drivers/scsi/virtio_scsi.zig`",
    "- `tools/lib/bpf/zigux_segments/`",
)


def collect_phase12_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            errors.append(f"missing:{line}")

    positions = []
    for heading in (PHASE11_HEADING, PHASE12_HEADING, PHASE13_HEADING):
        idx = roadmap.find(heading)
        if idx == -1:
            errors.append(f"missing-heading:{heading}")
        positions.append(idx)

    if all(idx != -1 for idx in positions) and not (positions[0] < positions[1] < positions[2]):
        errors.append(
            f"heading-order:{PHASE11_HEADING} -> {PHASE12_HEADING} -> {PHASE13_HEADING}"
        )

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """## Phase 11: Simple Production Drivers

Primary product goal:
- move from lab drivers to bounded real hardware drivers with straightforward lifecycles

Primary Linux anchors:
- `drivers/watchdog/gpio_wdt.c`
- `drivers/watchdog/bcm2835_wdt.c`
- `drivers/watchdog/dw_wdt.c`
- `drivers/tty/hvc/hvc_console.c`

Required Zigux features:
- direct-port or dual-impl driver templates
- hardware validation matrix
- teardown and failure-mode parity

Recommended Zigux destinations:
- `drivers/watchdog/*.zig`
- `drivers/tty/hvc/*.zig`

## Phase 12: Complex Production Drivers and Heavy Helper Consumers

Primary product goal:
- take on high-value, high-risk drivers only after earlier proof

Primary Linux anchors:
- `drivers/net/virtio_net.c`
- `drivers/nvme/host/pci.c`
- `drivers/scsi/virtio_scsi.c`
- `tools/lib/bpf/libbpf.c`

Required Zigux features:
- DMA-safe abstractions
- queueing correctness
- throughput and recovery parity
- segmented rollout

Recommended Zigux destinations:
- `drivers/net/virtio_net.zig`
- `drivers/nvme/host/pci.zig`
- `drivers/scsi/virtio_scsi.zig`
- `tools/lib/bpf/zigux_segments/`

## Phase 13: Shared Subsystem Helpers

Primary product goal:
- port bounded helper layers shared across multiple runtime consumers
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase12_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase12_errors(root):
            raise AssertionError("baseline Phase 12 fixture should pass")
        case_count += 1

        cases = (
            (
                "heading",
                _sample_roadmap().replace(PHASE12_HEADING + "\n\n", "", 1),
                [f"missing:{PHASE12_HEADING}", f"missing-heading:{PHASE12_HEADING}"],
            ),
            (
                "anchor",
                _sample_roadmap().replace("- `drivers/scsi/virtio_scsi.c`\n", "", 1),
                ["missing:- `drivers/scsi/virtio_scsi.c`"],
            ),
            (
                "feature",
                _sample_roadmap().replace("- queueing correctness\n", "", 1),
                ["missing:- queueing correctness"],
            ),
            (
                "destination",
                _sample_roadmap().replace("- `tools/lib/bpf/zigux_segments/`\n", "", 1),
                ["missing:- `tools/lib/bpf/zigux_segments/`"],
            ),
            (
                "phase11",
                _sample_roadmap().replace(PHASE11_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE11_HEADING}"],
            ),
            (
                "phase13",
                _sample_roadmap().replace(PHASE13_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE13_HEADING}"],
            ),
            (
                "order",
                _sample_roadmap().replace(
                    PHASE12_HEADING
                    + "\n\nPrimary product goal:\n- take on high-value, high-risk drivers only after earlier proof\n\nPrimary Linux anchors:\n- `drivers/net/virtio_net.c`\n- `drivers/nvme/host/pci.c`\n- `drivers/scsi/virtio_scsi.c`\n- `tools/lib/bpf/libbpf.c`\n\nRequired Zigux features:\n- DMA-safe abstractions\n- queueing correctness\n- throughput and recovery parity\n- segmented rollout\n\nRecommended Zigux destinations:\n- `drivers/net/virtio_net.zig`\n- `drivers/nvme/host/pci.zig`\n- `drivers/scsi/virtio_scsi.zig`\n- `tools/lib/bpf/zigux_segments/`\n\n"
                    + PHASE13_HEADING,
                    PHASE13_HEADING
                    + "\n\n"
                    + PHASE12_HEADING
                    + "\n\nPrimary product goal:\n- take on high-value, high-risk drivers only after earlier proof\n\nPrimary Linux anchors:\n- `drivers/net/virtio_net.c`\n- `drivers/nvme/host/pci.c`\n- `drivers/scsi/virtio_scsi.c`\n- `tools/lib/bpf/libbpf.c`\n\nRequired Zigux features:\n- DMA-safe abstractions\n- queueing correctness\n- throughput and recovery parity\n- segmented rollout\n\nRecommended Zigux destinations:\n- `drivers/net/virtio_net.zig`\n- `drivers/nvme/host/pci.zig`\n- `drivers/scsi/virtio_scsi.zig`\n- `tools/lib/bpf/zigux_segments/`\n\n",
                    1,
                ),
                [
                    f"heading-order:{PHASE11_HEADING} -> {PHASE12_HEADING} -> {PHASE13_HEADING}"
                ],
            ),
        )

        for _, content, expected in cases:
            _write(root / ROADMAP_PATH, content)
            errors = collect_phase12_errors(root)
            if errors != expected:
                raise AssertionError(f"unexpected errors: {errors} != {expected}")
            case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE12_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE12_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 12 packet remains aligned."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Phase 12 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase12_errors(args.root)
    if errors:
        for entry in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE12_ERROR={entry}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE12=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE12_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
