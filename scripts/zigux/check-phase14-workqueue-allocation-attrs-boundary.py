#!/usr/bin/env python3
"""Check the bounded Phase 14 workqueue allocation-and-attrs boundary audit."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile


REQUIRED_BRIDGE_SNIPPETS = (
    '.id = "allocation-and-attrs"',
    '.ownership = .boundary_map_only',
    '"__alloc_workqueue"',
    '"devm_alloc_workqueue"',
    "wrapperCandidatePacket",
    "rescuer policy",
    "ordered-workqueue rules",
)

REQUIRED_AUDIT_SNIPPETS = (
    "`PHASE14_LANE_KEY=P14-L02`",
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_SCOPE=allocation-and-attrs`",
    "`__alloc_workqueue()`",
    "`devm_alloc_workqueue()`",
    "`boundary_map_only`",
    "rescuer policy",
    "ordered-workqueue rules",
    "lifetime ownership in C",
    "python3 scripts/zigux/check-phase14-workqueue-allocation-attrs-boundary.py",
)


def require_snippets(label: str, text: str, snippets: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for snippet in snippets:
        if snippet not in text:
            missing.append(f"{label}: missing {snippet!r}")
    return missing


def run_check(root: pathlib.Path) -> list[str]:
    bridge_path = root / "kernel" / "workqueue_bridge.zig"
    audit_path = (
        root
        / "Documentation"
        / "zigux"
        / "phase14-workqueue-allocation-attrs-boundary-audit.md"
    )

    errors: list[str] = []
    if not bridge_path.is_file():
        errors.append(f"missing file: {bridge_path}")
    if not audit_path.is_file():
        errors.append(f"missing file: {audit_path}")
    if errors:
        return errors

    bridge_text = bridge_path.read_text(encoding="utf-8")
    audit_text = audit_path.read_text(encoding="utf-8")

    errors.extend(require_snippets("bridge", bridge_text, REQUIRED_BRIDGE_SNIPPETS))
    errors.extend(require_snippets("audit", audit_text, REQUIRED_AUDIT_SNIPPETS))
    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "kernel").mkdir(parents=True, exist_ok=True)
        (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)

        (root / "kernel" / "workqueue_bridge.zig").write_text(
            """
const wrapper_candidates = [_]WrapperCandidate{
    .{
        .id = "allocation-and-attrs",
        .ownership = .boundary_map_only,
        .anchor_symbols = &[_][]const u8{ "__alloc_workqueue", "devm_alloc_workqueue" },
        .blocked_by = "__alloc_workqueue() and devm_alloc_workqueue() are still coupled to rescuer policy, affinity shaping, ordered-workqueue rules, and lifetime ownership in the current C runtime.",
    },
};

pub fn wrapperCandidatePacket() void {}
""".strip(),
            encoding="utf-8",
        )

        (root / "Documentation" / "zigux" / "phase14-workqueue-allocation-attrs-boundary-audit.md").write_text(
            """
# Phase 14 Workqueue Allocation And Attributes Boundary Audit

- `PHASE14_LANE_KEY=P14-L02`
- `PHASE14_STATUS=blocked_maintenance`
- `PHASE14_SCOPE=allocation-and-attrs`

`__alloc_workqueue()` and `devm_alloc_workqueue()` stay `boundary_map_only`.
This seam keeps rescuer policy, ordered-workqueue rules, and lifetime ownership in C.

- `python3 scripts/zigux/check-phase14-workqueue-allocation-attrs-boundary.py --self-test`
- `python3 scripts/zigux/check-phase14-workqueue-allocation-attrs-boundary.py`
""".strip(),
            encoding="utf-8",
        )

        errors = run_check(root)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to inspect. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = run_check(pathlib.Path(args.root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("phase14 workqueue allocation-and-attrs boundary audit looks aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
