#!/usr/bin/env python3
"""Guard the Phase 1 direct-anchor helper split against reminder-surface drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]
EXPECTED_DIRECT_ANCHOR_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

SCRIPTS_README_LINE = (
    "- the current direct-anchor tie-breakers stay helper-local: bitmap, "
    "find_bit, rbtree, and string reopen only inside their existing helper-local "
    "anchors or already-committed shared fixture keys, while the other nine "
    "closed helpers stay parked unless the shared replay or reminder packet drifts"
)
LANE_NOTE_LINE = (
    "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,"
    "tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`"
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    if actual != expected:
        return [f"{label}:expected={expected!r}:actual={actual!r}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (SCRIPTS_README_REL, LANE_NOTE_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    failures.extend(
        require_exact_line(
            load_text(root, SCRIPTS_README_REL),
            "scripts_readme:direct_anchor_tie_breakers",
            SCRIPTS_README_LINE,
        )
    )
    failures.extend(
        require_exact_line(
            load_text(root, LANE_NOTE_REL),
            "lane_note:direct_anchor_followup_helpers",
            LANE_NOTE_LINE,
        )
    )

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    lane_sequencing = manifest.get("lane_sequencing")
    if not isinstance(lane_sequencing, dict):
        return [
            f"{MANIFEST_REL.as_posix()}:lane_sequencing:expected=dict:actual={type(lane_sequencing).__name__}"
        ]

    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.shared_replay_parked_helpers",
            lane_sequencing.get("shared_replay_parked_helpers"),
            EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
        )
    )
    failures.extend(
        require_exact_value(
            f"{MANIFEST_REL.as_posix()}:lane_sequencing.direct_anchor_followup_helpers",
            lane_sequencing.get("direct_anchor_followup_helpers"),
            EXPECTED_DIRECT_ANCHOR_HELPERS,
        )
    )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, SCRIPTS_README_REL, "# sample\n\n" + SCRIPTS_README_LINE + "\n")
    write_file(root, LANE_NOTE_REL, "# sample\n\n" + LANE_NOTE_LINE + "\n")
    write_file(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_HELPERS,
                }
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    cases: list[tuple[str, str]] = [
        ("scripts_remove", "scripts_remove"),
        ("scripts_duplicate", "scripts_duplicate"),
        ("lane_remove", "lane_remove"),
        ("lane_duplicate", "lane_duplicate"),
        ("manifest_shared", "manifest_shared"),
        ("manifest_direct", "manifest_direct"),
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-direct-anchor-split-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-direct-anchor-split-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation == "scripts_remove":
                path = root / SCRIPTS_README_REL
                path.write_text(path.read_text(encoding="utf-8").replace(SCRIPTS_README_LINE + "\n", "", 1), encoding="utf-8")
            elif mutation == "scripts_duplicate":
                path = root / SCRIPTS_README_REL
                path.write_text(
                    path.read_text(encoding="utf-8").replace(
                        SCRIPTS_README_LINE,
                        SCRIPTS_README_LINE + "\n" + SCRIPTS_README_LINE,
                        1,
                    ),
                    encoding="utf-8",
                )
            elif mutation == "lane_remove":
                path = root / LANE_NOTE_REL
                path.write_text(path.read_text(encoding="utf-8").replace(LANE_NOTE_LINE + "\n", "", 1), encoding="utf-8")
            elif mutation == "lane_duplicate":
                path = root / LANE_NOTE_REL
                path.write_text(
                    path.read_text(encoding="utf-8").replace(
                        LANE_NOTE_LINE,
                        LANE_NOTE_LINE + "\n" + LANE_NOTE_LINE,
                        1,
                    ),
                    encoding="utf-8",
                )
            else:
                path = root / MANIFEST_REL
                manifest = json.loads(path.read_text(encoding="utf-8"))
                lane_sequencing = manifest["lane_sequencing"]
                if mutation == "manifest_shared":
                    lane_sequencing["shared_replay_parked_helpers"] = lane_sequencing["shared_replay_parked_helpers"][1:]
                else:
                    lane_sequencing["direct_anchor_followup_helpers"] = lane_sequencing["direct_anchor_followup_helpers"][1:]
                path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    print("PHASE1_DIRECT_ANCHOR_SPLIT_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-direct-anchor-split:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
