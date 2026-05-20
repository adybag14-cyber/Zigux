#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE9_HEADING = "## Phase 9: Runtime Pilot Modules"
PHASE10_HEADING = "## Phase 10: Virtio and Lab Drivers"
PHASE11_HEADING = "## Phase 11: Simple Production Drivers"

REQUIRED_LINES = (
    PHASE10_HEADING,
    "Primary product goal:",
    "- prove the driver model on VM-friendly transports before touching harder hardware",
    "Primary Linux anchors:",
    "- `drivers/virtio/virtio.c`",
    "- `drivers/virtio/virtio_ring.c`",
    "- `drivers/virtio/virtio_mmio.c`",
    "- `drivers/virtio/virtio_input.c`",
    "Required Zigux features:",
    "- virtqueue wrappers",
    "- MMIO wrappers",
    "- lab-only driver validation",
    "- dual implementations for risky areas",
    "Recommended Zigux destinations:",
    "- `drivers/virtio/*.zig`",
    "- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified",
)


def collect_phase10_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            errors.append(f"missing:{line}")

    positions = []
    for heading in (PHASE9_HEADING, PHASE10_HEADING, PHASE11_HEADING):
        idx = roadmap.find(heading)
        if idx == -1:
            errors.append(f"missing-heading:{heading}")
        positions.append(idx)

    if all(idx != -1 for idx in positions) and not (positions[0] < positions[1] < positions[2]):
        errors.append(
            f"heading-order:{PHASE9_HEADING} -> {PHASE10_HEADING} -> {PHASE11_HEADING}"
        )

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """## Phase 9: Runtime Pilot Modules

Primary product goal:
- enter runtime kernels through tests and samples, not production pressure

Primary Linux anchors:
- `lib/atomic64_test.c`
- `lib/test_bitmap.c`
- `samples/trace_events/trace-events-sample.c`
- `samples/kprobes/kretprobe_example.c`

Required Zigux features:
- first loadable Zigux runtime modules
- selftest hooks
- runtime module lifecycle parity

Recommended Zigux destinations:
- `zigux/tests/runtime_*`
- `samples/zigux/runtime_*`

## Phase 10: Virtio and Lab Drivers

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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase10_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase10_errors(root):
            raise AssertionError("baseline Phase 10 fixture should pass")
        case_count += 1

        cases = (
            (
                "heading",
                _sample_roadmap().replace(PHASE10_HEADING + "\n\n", "", 1),
                [f"missing:{PHASE10_HEADING}", f"missing-heading:{PHASE10_HEADING}"],
            ),
            (
                "anchor",
                _sample_roadmap().replace("- `drivers/virtio/virtio_ring.c`\n", "", 1),
                ["missing:- `drivers/virtio/virtio_ring.c`"],
            ),
            (
                "feature",
                _sample_roadmap().replace("- lab-only driver validation\n", "", 1),
                ["missing:- lab-only driver validation"],
            ),
            (
                "destination",
                _sample_roadmap().replace(
                    "- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified\n",
                    "",
                    1,
                ),
                ["missing:- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified"],
            ),
            (
                "phase9",
                _sample_roadmap().replace(PHASE9_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE9_HEADING}"],
            ),
            (
                "phase11",
                _sample_roadmap().replace(PHASE11_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE11_HEADING}"],
            ),
            (
                "order",
                _sample_roadmap().replace(
                    PHASE10_HEADING
                    + "\n\nPrimary product goal:\n- prove the driver model on VM-friendly transports before touching harder hardware\n\nPrimary Linux anchors:\n- `drivers/virtio/virtio.c`\n- `drivers/virtio/virtio_ring.c`\n- `drivers/virtio/virtio_mmio.c`\n- `drivers/virtio/virtio_input.c`\n\nRequired Zigux features:\n- virtqueue wrappers\n- MMIO wrappers\n- lab-only driver validation\n- dual implementations for risky areas\n\nRecommended Zigux destinations:\n- `drivers/virtio/*.zig`\n- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified\n\n"
                    + PHASE11_HEADING,
                    PHASE11_HEADING
                    + "\n\n"
                    + PHASE10_HEADING
                    + "\n\nPrimary product goal:\n- prove the driver model on VM-friendly transports before touching harder hardware\n\nPrimary Linux anchors:\n- `drivers/virtio/virtio.c`\n- `drivers/virtio/virtio_ring.c`\n- `drivers/virtio/virtio_mmio.c`\n- `drivers/virtio/virtio_input.c`\n\nRequired Zigux features:\n- virtqueue wrappers\n- MMIO wrappers\n- lab-only driver validation\n- dual implementations for risky areas\n\nRecommended Zigux destinations:\n- `drivers/virtio/*.zig`\n- bridging helpers in `zigux/kernel/` or `zigux/helpers/` where justified\n",
                    1,
                ),
                [
                    f"heading-order:{PHASE9_HEADING} -> {PHASE10_HEADING} -> {PHASE11_HEADING}"
                ],
            ),
        )

        for _, content, expected in cases:
            _write(root / ROADMAP_PATH, content)
            errors = collect_phase10_errors(root)
            if errors != expected:
                raise AssertionError(f"unexpected errors: {errors} != {expected}")
            case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE10_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE10_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 10 packet remains aligned."
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
        help="exercise the checker against synthetic Phase 10 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase10_errors(args.root)
    if errors:
        for entry in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE10_ERROR={entry}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE10=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE10_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
