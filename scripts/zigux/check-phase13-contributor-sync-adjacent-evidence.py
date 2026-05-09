#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
]

GUIDE_MARKERS = [
    "`scripts/zigux/check-phase13-notifier-packet.py`",
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/bindings/notifier_abi.zig`",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "`include/zigux/abi.h`",
    "`include/zigux/notifier_abi.h`",
    "adjacent shipped release-surface evidence",
]

SYNC_SHARED_SURFACE_MARKERS = [
    "- `scripts/zigux/check-phase13-notifier-packet.py`",
    "- `zigux/tests/phase13_notifier_list_manifest.json`",
    "- `zigux/tests/phase13_notifier_list_reviewability.zig`",
    "- `zigux/bindings/notifier_abi.zig`",
    "- `zigux/helpers/list_view.zig`",
    "- `zigux/helpers/hlist_view.zig`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `include/zigux/abi.h`",
    "- `include/zigux/notifier_abi.h`",
]

SYNC_PHASE13_ANCHOR_MARKERS = [
    "- `scripts/zigux/check-phase13-notifier-packet.py`",
    "- `zigux/tests/phase13_notifier_list_manifest.json`",
    "- `zigux/tests/phase13_notifier_list_reviewability.zig`",
    "- `zigux/bindings/notifier_abi.zig`",
    "- `zigux/helpers/list_view.zig`",
    "- `zigux/helpers/hlist_view.zig`",
    "- `zigux/helpers/notifier_chain_view.zig`",
    "- `include/zigux/abi.h`",
    "- `include/zigux/notifier_abi.h`",
]

SYNC_DRIFT_MARKERS = [
    "adjacent ABI/helper evidence file",
    "or otherwise misstate the notifier evidence?",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def section_between(text: str, start: str, end: str | None = None) -> str:
    start_index = text.index(start) + len(start)
    if end is None:
        return text[start_index:]
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def collect_missing(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def validate(root: Path) -> list[str]:
    issues = [f"missing_file:{rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]
    if issues:
        return issues

    guide_text = read_text(root / "Documentation/zigux/phase13-contributor-workflow-guide.md")
    sync_text = read_text(root / "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md")
    shared_surfaces_text = section_between(sync_text, "## Shared surfaces\n", "\n## Update order\n")
    phase13_anchors_text = section_between(sync_text, "## Phase 13 anchors\n", "\n## Drift checks\n")
    drift_checks_text = section_between(sync_text, "## Drift checks\n")

    issues.extend(collect_missing(guide_text, GUIDE_MARKERS, "phase13-guide"))
    issues.extend(collect_missing(shared_surfaces_text, SYNC_SHARED_SURFACE_MARKERS, "phase13-sync-shared"))
    issues.extend(collect_missing(phase13_anchors_text, SYNC_PHASE13_ANCHOR_MARKERS, "phase13-sync-anchors"))
    issues.extend(collect_missing(drift_checks_text, SYNC_DRIFT_MARKERS, "phase13-sync-drift"))
    return issues


def seed_fixture_tree(root: Path) -> None:
    guide_lines = [
        "# Phase 13 Contributor Workflow Guide",
        "",
        "Adjacent notifier release-surface evidence under "
        + ", ".join(GUIDE_MARKERS[:-1])
        + f" stays in scope for contributor guidance too, but it remains {GUIDE_MARKERS[-1]} rather than a fifth shared-helper anchor or an extra shared replay step.",
        "",
    ]
    sync_lines = [
        "# Phase 10, 11, and 13 Contributor Surface Sync",
        "",
        "## Shared surfaces",
        *SYNC_SHARED_SURFACE_MARKERS,
        "",
        "## Update order",
        "1. Keep the shared workflow bundle aligned when adjacent notifier evidence expands.",
        "",
        "## Phase 13 anchors",
        *SYNC_PHASE13_ANCHOR_MARKERS,
        "",
        "## Drift checks",
        f"- Did docs-root or scripts-root add a new replay, checker, manifest, survey, reviewability shard, or {SYNC_DRIFT_MARKERS[0]} that the shared contributor prompts still compress into older shorthand?",
        f"- Did one shared Phase 13 prompt turn shipped adjacent release-surface evidence into extra replay steps, drop that adjacent notifier checker from the packet, {SYNC_DRIFT_MARKERS[1]}",
        "",
    ]
    write_text(root / REQUIRED_FILES[0], "\n".join(guide_lines))
    write_text(root / REQUIRED_FILES[1], "\n".join(sync_lines))


def assert_only(got: list[str], want: list[str], label: str) -> None:
    if got != want:
        got_text = ",".join(got) or "none"
        want_text = ",".join(want) or "none"
        raise SystemExit(f"phase13-contributor-sync-self-test:{label}:got={got_text}:want={want_text}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_contributor_sync_") as temp_dir:
        root = Path(temp_dir)
        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        write_text(
            root / REQUIRED_FILES[0],
            read_text(root / REQUIRED_FILES[0]).replace("`zigux/helpers/hlist_view.zig`", "", 1),
        )
        assert_only(
            validate(root),
            ["phase13-guide:`zigux/helpers/hlist_view.zig`"],
            "guide_marker_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / REQUIRED_FILES[1],
            read_text(root / REQUIRED_FILES[1]).replace("- `zigux/helpers/list_view.zig`\n", "", 1),
        )
        assert_only(
            validate(root),
            [
                "phase13-sync-shared:- `zigux/helpers/list_view.zig`",
            ],
            "sync_surface_guard_failed",
        )
        seed_fixture_tree(root)
        case_count += 1

        write_text(
            root / REQUIRED_FILES[1],
            read_text(root / REQUIRED_FILES[1]).replace("adjacent ABI/helper evidence file", "adjacent evidence file", 1),
        )
        assert_only(
            validate(root),
            ["phase13-sync-drift:adjacent ABI/helper evidence file"],
            "sync_drift_guard_failed",
        )
        case_count += 1

    print("PHASE13_CONTRIBUTOR_SYNC_ADJACENT_EVIDENCE=pass")
    print(f"PHASE13_CONTRIBUTOR_SYNC_ADJACENT_EVIDENCE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 contributor guide and sync note keep adjacent notifier evidence aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE13_CONTRIBUTOR_SYNC_ADJACENT_EVIDENCE=fail")
        for issue in issues:
            print(f"PHASE13_CONTRIBUTOR_SYNC_ADJACENT_EVIDENCE_ISSUE={issue}")
        return 1

    print("PHASE13_CONTRIBUTOR_SYNC_ADJACENT_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
