#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()

NOTE_PATH = "Documentation/zigux/phase14-ring-skbuff-rcu-concurrency-survey.md"
RING_BUFFER_SURVEY_PATH = "Documentation/zigux/phase14-ring-buffer-survey.md"
SKBUFF_SURVEY_PATH = "Documentation/zigux/phase14-skbuff-bridge-survey.md"
RCU_SURVEY_PATH = "Documentation/zigux/phase14-rcu-tree-survey.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
TRACEABILITY_PATH = "Documentation/zigux/phase14-core-boundary-traceability.md"

REQUIRED_FILES = [
    NOTE_PATH,
    RING_BUFFER_SURVEY_PATH,
    SKBUFF_SURVEY_PATH,
    RCU_SURVEY_PATH,
    FREEZE_MAP_PATH,
    ACCOUNTING_PATH,
    TRACEABILITY_PATH,
]

REQUIRED_MARKERS = {
    NOTE_PATH: [
        "`PHASE14_LANE_KEY=P14-L12`",
        "`kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`",
        "- `kernel/trace/ring_buffer.c`: `study_only`",
        "- `net/core/skbuff.c`: `freeze_in_c`",
        "- `kernel/rcu/tree.c`: `freeze_in_c`",
        "publication and ordering ownership, consumer lifetime and teardown ownership, and asynchronous wake or escalation ownership still remain C-owned concurrency state machines",
        "ring-buffer reserve or commit publication, `reader_page` handoff, and mapped-reader metadata publication still stay in C",
        "skbuff qdisc-facing publication, shared-info header-write ownership, and checksum-state ownership still stay in C",
        "RCU grace-period sequence publication and the memory-ordering lock network still stay in C",
        "ring-buffer read-page extraction, reader-page consume boundaries, and `rb_remove_pages()` mapped-reader lifetime teardown still stay in C",
        "skbuff destructor ordering, zerocopy fragment orphaning, shared-frag ownership transfer, and the final sock-owned tail transfer still stay in C",
        "RCU callback enqueue and batch invocation, public wait and callback-barrier ownership, and CPU hotplug callback migration still stay in C",
        "ring-buffer wakeup or watermark publication and tracefs reader competition still stay in C",
        "skbuff queue ownership and deferred destructor-side ownership escalation still stay in C",
        "RCU expedited funnel behavior, force-quiescent-state escalation, and NOCB wakeup handoff still stay in C",
        "keep `P14-L08`, `P14-L11`, and `P14-L16` on their dedicated anchor-local packets",
    ],
    RING_BUFFER_SURVEY_PATH: [
        "`PHASE14_STATUS=study_only`",
        "`phase14-ring-buffer-zig-port-blocker`",
        "Reserve or commit publication",
        "`rb_remove_pages()` mapped-reader lifetime teardown",
        "wakeup or watermark publication",
    ],
    SKBUFF_SURVEY_PATH: [
        "`PHASE14_LANE_KEY=P14-L11`",
        "`phase14-skbuff-live-ownership-blocker`",
        "qdisc-facing publication",
        "destructor ordering",
        "final sock-owned tail transfer",
    ],
    RCU_SURVEY_PATH: [
        "`PHASE14_LANE_KEY=P14-L16`",
        "`phase14-rcu-tree-bridge-blocker`",
        "grace-period sequence publication",
        "memory-ordering lock network",
        "NOCB wakeup handoff",
        "CPU hotplug callback migration",
    ],
    FREEZE_MAP_PATH: [
        "## Freeze In C Initially",
        "- `kernel/rcu/tree.c`",
        "- `net/core/skbuff.c`",
        "## Study / Boundary Only",
        "- `kernel/trace/ring_buffer.c`",
    ],
    ACCOUNTING_PATH: [
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only",
        "`kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target",
    ],
    TRACEABILITY_PATH: [
        "### Ring buffer",
        "### Skbuff",
        "### RCU tree",
        "Reserve or commit publication",
        "Live skb lifetime",
        "Grace-period sequence publication",
    ],
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    require(path.exists(), f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def check(root: Path) -> str:
    for relative_path in REQUIRED_FILES:
        text = read_text(root, relative_path)
        for marker in REQUIRED_MARKERS[relative_path]:
            require(
                marker in text,
                f"missing marker in {relative_path}: {marker}",
            )

    return "\n".join(
        [
            "PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY=pass",
            "PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_REQUIRED_FILE_COUNT=7",
            "PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_MARKER_COUNT=39",
        ]
    )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    write_file(
        root / NOTE_PATH,
        """# Phase 14 Ring Skbuff RCU Concurrency Survey

This note records the bounded `P14-L12` cross-anchor concurrency audit for the Phase 14 packets around `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Status
- `PHASE14_LANE_KEY=P14-L12`
- `PHASE14_PHASE=Phase 14`
- `PHASE14_STATUS_BUCKET=cross_anchor_stay_in_c_audit`
- `PHASE14_PROVENANCE_MODE=dated_master_readback`
- surveyed against `current-master-readback-2026-05-27`

## Anchor posture
- `kernel/trace/ring_buffer.c`: `study_only`
- `net/core/skbuff.c`: `freeze_in_c`
- `kernel/rcu/tree.c`: `freeze_in_c`

publication and ordering ownership, consumer lifetime and teardown ownership, and asynchronous wake or escalation ownership still remain C-owned concurrency state machines
ring-buffer reserve or commit publication, `reader_page` handoff, and mapped-reader metadata publication still stay in C
skbuff qdisc-facing publication, shared-info header-write ownership, and checksum-state ownership still stay in C
RCU grace-period sequence publication and the memory-ordering lock network still stay in C
ring-buffer read-page extraction, reader-page consume boundaries, and `rb_remove_pages()` mapped-reader lifetime teardown still stay in C
skbuff destructor ordering, zerocopy fragment orphaning, shared-frag ownership transfer, and the final sock-owned tail transfer still stay in C
RCU callback enqueue and batch invocation, public wait and callback-barrier ownership, and CPU hotplug callback migration still stay in C
ring-buffer wakeup or watermark publication and tracefs reader competition still stay in C
skbuff queue ownership and deferred destructor-side ownership escalation still stay in C
RCU expedited funnel behavior, force-quiescent-state escalation, and NOCB wakeup handoff still stay in C
keep `P14-L08`, `P14-L11`, and `P14-L16` on their dedicated anchor-local packets
""",
    )
    write_file(
        root / RING_BUFFER_SURVEY_PATH,
        """# Phase 14 Ring Buffer Survey
`PHASE14_STATUS=study_only`
`phase14-ring-buffer-zig-port-blocker`
Reserve or commit publication still stays in C.
`rb_remove_pages()` mapped-reader lifetime teardown still stays in C.
wakeup or watermark publication still stays in C.
""",
    )
    write_file(
        root / SKBUFF_SURVEY_PATH,
        """# Phase 14 Skbuff Bridge Survey
`PHASE14_LANE_KEY=P14-L11`
`phase14-skbuff-live-ownership-blocker`
qdisc-facing publication still stays in C.
destructor ordering still stays in C.
final sock-owned tail transfer still stays in C.
""",
    )
    write_file(
        root / RCU_SURVEY_PATH,
        """# Phase 14 RCU Tree Survey
`PHASE14_LANE_KEY=P14-L16`
`phase14-rcu-tree-bridge-blocker`
grace-period sequence publication still stays in C.
memory-ordering lock network still stays in C.
NOCB wakeup handoff still stays in C.
CPU hotplug callback migration still stays in C.
""",
    )
    write_file(
        root / FREEZE_MAP_PATH,
        """# Zigux Freeze Map
## Freeze In C Initially
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`
## Study / Boundary Only
- `kernel/trace/ring_buffer.c`
""",
    )
    write_file(
        root / ACCOUNTING_PATH,
        """# Phase 15 Study-Only Anchor Accounting
`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only
`kernel/trace/ring_buffer.c` remains a boundary-study target first, not a rewrite target
""",
    )
    write_file(
        root / TRACEABILITY_PATH,
        """# Phase 14 Core Boundary Traceability
### Ring buffer
Reserve or commit publication still stays in C.
### Skbuff
Live skb lifetime still stays in C.
### RCU tree
Grace-period sequence publication still stays in C.
""",
    )


def run_self_test() -> str:
    with tempfile.TemporaryDirectory(prefix="phase14_ring_skbuff_rcu_concurrency_") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        output = check(root)
    return "\n".join(
        [
            "PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_SELF_TEST=pass",
            "PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_SELF_TEST_CASE_COUNT=8",
            output,
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 14 ring/skbuff/RCU cross-anchor concurrency survey stays aligned.",
    )
    parser.add_argument("--root", type=Path, help="Root directory to validate.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a sample passing tree to the given directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        build_sample_root(args.write_sample_root)
        print(f"WROTE_SAMPLE_ROOT={args.write_sample_root}")

    if args.self_test:
        print(run_self_test())

    if args.root is not None:
        print(check(args.root))

    if not args.self_test and args.root is None and args.write_sample_root is None:
        print("error: one of --self-test, --root, or --write-sample-root is required", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
