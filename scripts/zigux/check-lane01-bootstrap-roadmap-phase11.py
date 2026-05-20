#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE10_HEADING = "## Phase 10: Virtio and Lab Drivers"
PHASE11_HEADING = "## Phase 11: Simple Production Drivers"
PHASE12_HEADING = "## Phase 12: Complex Production Drivers and Heavy Helper Consumers"

REQUIRED_LINES = (
    PHASE11_HEADING,
    "Primary product goal:",
    "- move from lab drivers to bounded real hardware drivers with straightforward lifecycles",
    "Primary Linux anchors:",
    "- `drivers/watchdog/gpio_wdt.c`",
    "- `drivers/watchdog/bcm2835_wdt.c`",
    "- `drivers/watchdog/dw_wdt.c`",
    "- `drivers/tty/hvc/hvc_console.c`",
    "Required Zigux features:",
    "- direct-port or dual-impl driver templates",
    "- hardware validation matrix",
    "- teardown and failure-mode parity",
    "Recommended Zigux destinations:",
    "- `drivers/watchdog/*.zig`",
    "- `drivers/tty/hvc/*.zig`",
)


def collect_phase11_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            errors.append(f"missing:{line}")

    positions = []
    for heading in (PHASE10_HEADING, PHASE11_HEADING, PHASE12_HEADING):
        idx = roadmap.find(heading)
        if idx == -1:
            errors.append(f"missing-heading:{heading}")
        positions.append(idx)

    if all(idx != -1 for idx in positions) and not (positions[0] < positions[1] < positions[2]):
        errors.append(
            f"heading-order:{PHASE10_HEADING} -> {PHASE11_HEADING} -> {PHASE12_HEADING}"
        )

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """## Phase 10: Virtio and Lab Drivers

Primary product goal:
- prove the driver model on VM-friendly transports before touching harder hardware

Primary Linux anchors:
- `drivers/virtio/virtio.c`
- `drivers/virtio/virtio_ring.c`
- `drivers/virtio/virtio_mmio.c`
- `drivers/virtio/virtio_input.c`

Required Zigux features:
- virtqueue wrappers
- MMIO wrappers
- lab-only driver validation
- dual implementations for risky areas

Recommended Zigux destinations:
- `drivers/virtio/*.zig`
- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified

## Phase 11: Simple Production Drivers

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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase11_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase11_errors(root):
            raise AssertionError("baseline Phase 11 fixture should pass")
        case_count += 1

        cases = (
            (
                "heading",
                _sample_roadmap().replace(PHASE11_HEADING + "\n\n", "", 1),
                [f"missing:{PHASE11_HEADING}", f"missing-heading:{PHASE11_HEADING}"],
            ),
            (
                "anchor",
                _sample_roadmap().replace("- `drivers/watchdog/dw_wdt.c`\n", "", 1),
                ["missing:- `drivers/watchdog/dw_wdt.c`"],
            ),
            (
                "feature",
                _sample_roadmap().replace("- hardware validation matrix\n", "", 1),
                ["missing:- hardware validation matrix"],
            ),
            (
                "destination",
                _sample_roadmap().replace("- `drivers/tty/hvc/*.zig`\n", "", 1),
                ["missing:- `drivers/tty/hvc/*.zig`"],
            ),
            (
                "phase10",
                _sample_roadmap().replace(PHASE10_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE10_HEADING}"],
            ),
            (
                "phase12",
                _sample_roadmap().replace(PHASE12_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE12_HEADING}"],
            ),
            (
                "order",
                _sample_roadmap().replace(
                    PHASE11_HEADING
                    + "\n\nPrimary product goal:\n- move from lab drivers to bounded real hardware drivers with straightforward lifecycles\n\nPrimary Linux anchors:\n- `drivers/watchdog/gpio_wdt.c`\n- `drivers/watchdog/bcm2835_wdt.c`\n- `drivers/watchdog/dw_wdt.c`\n- `drivers/tty/hvc/hvc_console.c`\n\nRequired Zigux features:\n- direct-port or dual-impl driver templates\n- hardware validation matrix\n- teardown and failure-mode parity\n\nRecommended Zigux destinations:\n- `drivers/watchdog/*.zig`\n- `drivers/tty/hvc/*.zig`\n\n"
                    + PHASE12_HEADING,
                    PHASE12_HEADING
                    + "\n\n"
                    + PHASE11_HEADING
                    + "\n\nPrimary product goal:\n- move from lab drivers to bounded real hardware drivers with straightforward lifecycles\n\nPrimary Linux anchors:\n- `drivers/watchdog/gpio_wdt.c`\n- `drivers/watchdog/bcm2835_wdt.c`\n- `drivers/watchdog/dw_wdt.c`\n- `drivers/tty/hvc/hvc_console.c`\n\nRequired Zigux features:\n- direct-port or dual-impl driver templates\n- hardware validation matrix\n- teardown and failure-mode parity\n\nRecommended Zigux destinations:\n- `drivers/watchdog/*.zig`\n- `drivers/tty/hvc/*.zig`\n",
                    1,
                ),
                [
                    f"heading-order:{PHASE10_HEADING} -> {PHASE11_HEADING} -> {PHASE12_HEADING}"
                ],
            ),
        )

        for _, content, expected in cases:
            _write(root / ROADMAP_PATH, content)
            errors = collect_phase11_errors(root)
            if errors != expected:
                raise AssertionError(f"unexpected errors: {errors} != {expected}")
            case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE11_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE11_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 11 packet remains aligned."
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
        help="exercise the checker against synthetic Phase 11 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase11_errors(args.root)
    if errors:
        for entry in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE11_ERROR={entry}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE11=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE11_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
