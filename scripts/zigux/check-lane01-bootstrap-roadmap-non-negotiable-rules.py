#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

SECTION_ORDER = (
    "## Licensing and Reuse Policy",
    "## Non-Negotiable Product Rules",
    "## How ZAR Should Feed Zigux",
)

RULE_MARKERS = (
    "These rules are consistent across the bundle and should govern every Zigux commit series.",
    "1. No flag-day rewrite.",
    "- Zigux grows through mixed-language coexistence.",
    "- C remains in place until each bounded area proves parity and maintainability.",
    "2. No mirror-tree sprawl.",
    "- Do not build a fake parallel kernel under a generic Zigux namespace.",
    "- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.",
    "3. Co-locate product code with Linux ownership.",
    "- Host-side helper ports belong beside current files such as `tools/lib/*.zig`.",
    "- Runtime helper ports belong beside current files such as `lib/*.zig`.",
    "- Driver pilots belong in current subsystem trees such as `drivers/virtio/*.zig`.",
    "4. Keep the Zigux support root small.",
    "- The support root exists for boundary code, not for duplicating Linux subsystems.",
    "  - `zigux/kernel/`",
    "  - `zigux/helpers/`",
    "  - `zigux/bindings/`",
    "  - `zigux/uapi/`",
    "  - `zigux/tests/`",
    "  - `zigux/unsafe/`",
    "5. Port leaf helpers before shared runtime helpers.",
    "- Port shared runtime helpers before drivers.",
    "- Port simple drivers before high-throughput queueing and DMA-heavy drivers.",
    "6. Validation is mandatory before expansion.",
    "- Every approved target needs parity tests.",
    "- Every sensitive path needs a perf threshold.",
    "- Every migration needs a rollback owner.",
    "7. Wrapper-first or dual-implementation is the default where semantics are risky.",
    "- Build tooling",
    "- ABI/export surfaces",
    "- allocators",
    "- atomics and barriers",
    "- MMIO",
    "- virtio rings",
    "- DMA-sensitive drivers",
    "- tracing and queueing infrastructure",
    "8. Deep-core freeze is real.",
    "- Do not move these into active delivery before the roadmap says so:",
    "  - `kernel/sched/core.c`",
    "  - `mm/page_alloc.c`",
    "  - `kernel/rcu/tree.c`",
    "  - `net/core/skbuff.c`",
    "- Treat `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as boundary-study targets first, not rewrite targets.",
    "9. Human review remains mandatory.",
    "- Follow Linux process expectations.",
    "- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.",
)


def collect_missing_markers(root: Path) -> list[str]:
    roadmap = (root / ROADMAP_PATH).read_text(encoding="utf-8")

    missing: list[str] = []
    positions: list[int] = []
    for heading in SECTION_ORDER:
        position = roadmap.find(heading)
        if position == -1:
            missing.append(f"roadmap-heading:{heading}")
        positions.append(position)

    if all(position != -1 for position in positions) and positions != sorted(positions):
        missing.append(
            "roadmap-section-order:LicensingAndReusePolicy->NonNegotiableProductRules->HowZARShouldFeedZigux"
        )

    for marker in RULE_MARKERS:
        if marker not in roadmap:
            missing.append(f"roadmap-rule:{marker}")

    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    return """# ZAR to Zigux Product Roadmap

## Licensing and Reuse Policy

Legal permission expands the implementation options.

## Non-Negotiable Product Rules

These rules are consistent across the bundle and should govern every Zigux commit series.

1. No flag-day rewrite.
- Zigux grows through mixed-language coexistence.
- C remains in place until each bounded area proves parity and maintainability.

2. No mirror-tree sprawl.
- Do not build a fake parallel kernel under a generic Zigux namespace.
- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.

3. Co-locate product code with Linux ownership.
- Host-side helper ports belong beside current files such as `tools/lib/*.zig`.
- Runtime helper ports belong beside current files such as `lib/*.zig`.
- Driver pilots belong in current subsystem trees such as `drivers/virtio/*.zig`.

4. Keep the Zigux support root small.
- The support root exists for boundary code, not for duplicating Linux subsystems.
- The intended long-term support root is:
  - `zigux/kernel/`
  - `zigux/helpers/`
  - `zigux/bindings/`
  - `zigux/uapi/`
  - `zigux/tests/`
  - `zigux/unsafe/`

5. Port leaf helpers before shared runtime helpers.
- Port shared runtime helpers before drivers.
- Port simple drivers before high-throughput queueing and DMA-heavy drivers.

6. Validation is mandatory before expansion.
- Every approved target needs parity tests.
- Every sensitive path needs a perf threshold.
- Every migration needs a rollback owner.

7. Wrapper-first or dual-implementation is the default where semantics are risky.
- Build tooling
- ABI/export surfaces
- allocators
- atomics and barriers
- MMIO
- virtio rings
- DMA-sensitive drivers
- tracing and queueing infrastructure

8. Deep-core freeze is real.
- Do not move these into active delivery before the roadmap says so:
  - `kernel/sched/core.c`
  - `mm/page_alloc.c`
  - `kernel/rcu/tree.c`
  - `net/core/skbuff.c`
- Treat `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as boundary-study targets first, not rewrite targets.

9. Human review remains mandatory.
- Follow Linux process expectations.
- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.

## How ZAR Should Feed Zigux

ZAR should not try to become Zigux.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_rules_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / ROADMAP_PATH, _sample_roadmap())

        if collect_missing_markers(root):
            raise AssertionError("baseline non-negotiable rules fixture should pass")
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("## Non-Negotiable Product Rules\n\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-heading:## Non-Negotiable Product Rules"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for heading case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        ordered = _sample_roadmap()
        zar_feed_packet = "\n## How ZAR Should Feed Zigux\n\nZAR should not try to become Zigux.\n"
        misordered = ordered.replace(zar_feed_packet, "\n", 1).replace(
            "## Non-Negotiable Product Rules",
            "## How ZAR Should Feed Zigux\n\nZAR should not try to become Zigux.\n\n## Non-Negotiable Product Rules",
            1,
        )
        _write(root / ROADMAP_PATH, misordered)
        missing = collect_missing_markers(root)
        expected = [
            "roadmap-section-order:LicensingAndReusePolicy->NonNegotiableProductRules->HowZARShouldFeedZigux"
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for section-order case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("1. No flag-day rewrite.\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:1. No flag-day rewrite."]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for flag-day case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:- `zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports."]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for bootstrap-workspace case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("  - `zigux/unsafe/`\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:  - `zigux/unsafe/`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for support-root case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- Every approved target needs parity tests.\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:- Every approved target needs parity tests."]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for validation case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- DMA-sensitive drivers\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:- DMA-sensitive drivers"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for wrapper-risk case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("  - `kernel/rcu/tree.c`\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:  - `kernel/rcu/tree.c`"]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for deep-core case: {missing}")
        _write(root / ROADMAP_PATH, _sample_roadmap())
        case_count += 1

        _write(root / ROADMAP_PATH, _sample_roadmap().replace("- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority.\n", "", 1))
        missing = collect_missing_markers(root)
        expected = ["roadmap-rule:- Use AI-assisted work only as a human-reviewed aid, not as an autonomous authority."]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for human-review case: {missing}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_NON_NEGOTIABLE_RULES_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NON_NEGOTIABLE_RULES_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 roadmap Non-Negotiable Product Rules packet."
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
        help="exercise the checker against synthetic roadmap fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_NON_NEGOTIABLE_RULES=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_NON_NEGOTIABLE_RULES_REQUIRED_LINE_COUNT={len(RULE_MARKERS)}")
    print("LANE01_BOOTSTRAP_ROADMAP_NON_NEGOTIABLE_RULES_SECTION_ORDER=Licensing->NonNegotiableRules->ZARFeed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
