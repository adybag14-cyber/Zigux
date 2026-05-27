#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE8_HEADING = "## Phase 8: Userspace-Adjacent Tooling Expansion"
PHASE9_HEADING = "## Phase 9: Runtime Pilot Modules"
PHASE10_HEADING = "## Phase 10: Virtio and Lab Drivers"

REQUIRED_LINES = (
    PHASE9_HEADING,
    "Primary product goal:",
    "- enter runtime kernels through tests and samples, not production pressure",
    "Primary Linux anchors:",
    "- `lib/atomic64_test.c`",
    "- `lib/test_bitmap.c`",
    "- `samples/trace_events/trace-events-sample.c`",
    "- `samples/kprobes/kretprobe_example.c`",
    "Required Zigux features:",
    "- first loadable Zigux runtime modules",
    "- selftest hooks",
    "- runtime module lifecycle parity",
    "Recommended Zigux destinations:",
    "- `zigux/tests/runtime_*`",
    "- `samples/zigux/runtime_*`",
)


def collect_phase9_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            errors.append(f"missing:{line}")

    positions = []
    for heading in (PHASE8_HEADING, PHASE9_HEADING, PHASE10_HEADING):
        idx = roadmap.find(heading)
        if idx == -1:
            errors.append(f"missing-heading:{heading}")
        positions.append(idx)

    if all(idx != -1 for idx in positions) and not (positions[0] < positions[1] < positions[2]):
        errors.append(
            f"heading-order:{PHASE8_HEADING} -> {PHASE9_HEADING} -> {PHASE10_HEADING}"
        )

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """## Phase 8: Userspace-Adjacent Tooling Expansion

Primary product goal:
- prove Zigux inside serious repo-hosted tooling, not just tiny helpers

Primary Linux anchors:
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`
- `tools/lib/symbol/kallsyms.c`
- `tools/lib/bpf/libbpf.c`

Required Zigux features:
- helper-first expansion
- segmented plan for large consumers like libbpf
- output-stable tooling behavior

Recommended Zigux destinations:
- `tools/lib/subcmd/*.zig`
- `tools/lib/symbol/*.zig`
- `tools/lib/bpf/zigux_segments/`

## Phase 9: Runtime Pilot Modules

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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase9_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase9_errors(root):
            raise AssertionError("baseline Phase 9 fixture should pass")
        case_count += 1

        cases = (
            (
                "heading",
                _sample_roadmap().replace(PHASE9_HEADING + "\n\n", "", 1),
                [f"missing:{PHASE9_HEADING}", f"missing-heading:{PHASE9_HEADING}"],
            ),
            (
                "anchor",
                _sample_roadmap().replace("- `lib/test_bitmap.c`\n", "", 1),
                ["missing:- `lib/test_bitmap.c`"],
            ),
            (
                "feature",
                _sample_roadmap().replace("- selftest hooks\n", "", 1),
                ["missing:- selftest hooks"],
            ),
            (
                "destination",
                _sample_roadmap().replace("- `samples/zigux/runtime_*`\n", "", 1),
                ["missing:- `samples/zigux/runtime_*`"],
            ),
            (
                "phase8",
                _sample_roadmap().replace(PHASE8_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE8_HEADING}"],
            ),
            (
                "phase10",
                _sample_roadmap().replace(PHASE10_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE10_HEADING}"],
            ),
            (
                "order",
                _sample_roadmap().replace(
                    PHASE9_HEADING
                    + "\n\nPrimary product goal:\n- enter runtime kernels through tests and samples, not production pressure\n\nPrimary Linux anchors:\n- `lib/atomic64_test.c`\n- `lib/test_bitmap.c`\n- `samples/trace_events/trace-events-sample.c`\n- `samples/kprobes/kretprobe_example.c`\n\nRequired Zigux features:\n- first loadable Zigux runtime modules\n- selftest hooks\n- runtime module lifecycle parity\n\nRecommended Zigux destinations:\n- `zigux/tests/runtime_*`\n- `samples/zigux/runtime_*`\n\n"
                    + PHASE10_HEADING,
                    PHASE10_HEADING
                    + "\n\n"
                    + PHASE9_HEADING
                    + "\n\nPrimary product goal:\n- enter runtime kernels through tests and samples, not production pressure\n\nPrimary Linux anchors:\n- `lib/atomic64_test.c`\n- `lib/test_bitmap.c`\n- `samples/trace_events/trace-events-sample.c`\n- `samples/kprobes/kretprobe_example.c`\n\nRequired Zigux features:\n- first loadable Zigux runtime modules\n- selftest hooks\n- runtime module lifecycle parity\n\nRecommended Zigux destinations:\n- `zigux/tests/runtime_*`\n- `samples/zigux/runtime_*`\n",
                    1,
                ),
                [
                    f"heading-order:{PHASE8_HEADING} -> {PHASE9_HEADING} -> {PHASE10_HEADING}"
                ],
            ),
        )

        for _, content, expected in cases:
            _write(root / ROADMAP_PATH, content)
            errors = collect_phase9_errors(root)
            if errors != expected:
                raise AssertionError(f"unexpected errors: {errors} != {expected}")
            case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE9_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE9_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 9 packet remains aligned."
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
        help="exercise the checker against synthetic Phase 9 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase9_errors(args.root)
    if errors:
        for entry in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE9_ERROR={entry}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE9=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE9_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
