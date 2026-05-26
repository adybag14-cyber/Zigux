#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

PHASE7_HEADING = "## Phase 7: In-Kernel Leaf Libraries"
PHASE8_HEADING = "## Phase 8: Userspace-Adjacent Tooling Expansion"
PHASE9_HEADING = "## Phase 9: Runtime Pilot Modules"

REQUIRED_LINES = (
    PHASE8_HEADING,
    "Primary product goal:",
    "- prove Zigux inside serious repo-hosted tooling, not just tiny helpers",
    "Primary Linux anchors:",
    "- `tools/lib/subcmd/exec-cmd.c`",
    "- `tools/lib/subcmd/help.c`",
    "- `tools/lib/symbol/kallsyms.c`",
    "- `tools/lib/bpf/libbpf.c`",
    "Required Zigux features:",
    "- helper-first expansion",
    "- segmented plan for large consumers like libbpf",
    "- output-stable tooling behavior",
    "Recommended Zigux destinations:",
    "- `tools/lib/subcmd/*.zig`",
    "- `tools/lib/symbol/*.zig`",
    "- `tools/lib/bpf/zigux_segments/`",
)


def collect_phase8_errors(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")
    errors: list[str] = []

    for line in REQUIRED_LINES:
        if line not in roadmap:
            errors.append(f"missing:{line}")

    positions = []
    for heading in (PHASE7_HEADING, PHASE8_HEADING, PHASE9_HEADING):
        idx = roadmap.find(heading)
        if idx == -1:
            errors.append(f"missing-heading:{heading}")
        positions.append(idx)

    if all(idx != -1 for idx in positions) and not (positions[0] < positions[1] < positions[2]):
        errors.append(
            f"heading-order:{PHASE7_HEADING} -> {PHASE8_HEADING} -> {PHASE9_HEADING}"
        )

    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """## Phase 7: In-Kernel Leaf Libraries

Primary product goal:
- bring the first reusable runtime helper families into the product path

Primary Linux anchors:
- `lib/string_helpers.c`
- `lib/cmdline.c`
- `lib/argv_split.c`
- `lib/rbtree.c`

Required Zigux features:
- runtime-safe leaf helpers
- stronger ownership and pointer discipline
- integration with validation substrate

Recommended Zigux destinations:
- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

## Phase 8: Userspace-Adjacent Tooling Expansion

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
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_phase8_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_phase8_errors(root):
            raise AssertionError("baseline Phase 8 fixture should pass")
        case_count += 1

        cases = (
            (
                "heading",
                _sample_roadmap().replace(PHASE8_HEADING + "\n\n", "", 1),
                [f"missing:{PHASE8_HEADING}", f"missing-heading:{PHASE8_HEADING}"],
            ),
            (
                "anchor",
                _sample_roadmap().replace("- `tools/lib/subcmd/help.c`\n", "", 1),
                ["missing:- `tools/lib/subcmd/help.c`"],
            ),
            (
                "feature",
                _sample_roadmap().replace(
                    "- segmented plan for large consumers like libbpf\n", "", 1
                ),
                ["missing:- segmented plan for large consumers like libbpf"],
            ),
            (
                "destination",
                _sample_roadmap().replace("- `tools/lib/bpf/zigux_segments/`\n", "", 1),
                ["missing:- `tools/lib/bpf/zigux_segments/`"],
            ),
            (
                "phase7",
                _sample_roadmap().replace(PHASE7_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE7_HEADING}"],
            ),
            (
                "phase9",
                _sample_roadmap().replace(PHASE9_HEADING + "\n\n", "", 1),
                [f"missing-heading:{PHASE9_HEADING}"],
            ),
            (
                "order",
                _sample_roadmap().replace(
                    PHASE8_HEADING
                    + "\n\nPrimary product goal:\n- prove Zigux inside serious repo-hosted tooling, not just tiny helpers\n\nPrimary Linux anchors:\n- `tools/lib/subcmd/exec-cmd.c`\n- `tools/lib/subcmd/help.c`\n- `tools/lib/symbol/kallsyms.c`\n- `tools/lib/bpf/libbpf.c`\n\nRequired Zigux features:\n- helper-first expansion\n- segmented plan for large consumers like libbpf\n- output-stable tooling behavior\n\nRecommended Zigux destinations:\n- `tools/lib/subcmd/*.zig`\n- `tools/lib/symbol/*.zig`\n- `tools/lib/bpf/zigux_segments/`\n\n"
                    + PHASE9_HEADING,
                    PHASE9_HEADING
                    + "\n\n"
                    + PHASE8_HEADING
                    + "\n\nPrimary product goal:\n- prove Zigux inside serious repo-hosted tooling, not just tiny helpers\n\nPrimary Linux anchors:\n- `tools/lib/subcmd/exec-cmd.c`\n- `tools/lib/subcmd/help.c`\n- `tools/lib/symbol/kallsyms.c`\n- `tools/lib/bpf/libbpf.c`\n\nRequired Zigux features:\n- helper-first expansion\n- segmented plan for large consumers like libbpf\n- output-stable tooling behavior\n\nRecommended Zigux destinations:\n- `tools/lib/subcmd/*.zig`\n- `tools/lib/symbol/*.zig`\n- `tools/lib/bpf/zigux_segments/`\n",
                    1,
                ),
                [
                    f"heading-order:{PHASE7_HEADING} -> {PHASE8_HEADING} -> {PHASE9_HEADING}"
                ],
            ),
        )

        for _, content, expected in cases:
            _write(root / ROADMAP_PATH, content)
            errors = collect_phase8_errors(root)
            if errors != expected:
                raise AssertionError(f"unexpected errors: {errors} != {expected}")
            case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE8_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE8_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap Phase 8 packet remains aligned."
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
        help="exercise the checker against synthetic Phase 8 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = collect_phase8_errors(args.root)
    if errors:
        for entry in errors:
            print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE8_ERROR={entry}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_PHASE8=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_PHASE8_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
