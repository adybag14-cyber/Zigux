#!/usr/bin/env python3
"""Guard the current Phase 1 helper owner-map packet across docs, tests, manifest, and workflow."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

SHARED_REPLAY_PARKED_HELPERS = (
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
)

DIRECT_ANCHOR_HELPERS = (
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
)

TEXT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- `PHASE1_HELPER_COUNT=13`",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
        "the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche",
    ),
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md": (
        "- `PHASE1_SHARED_REPLAY_PARKED_HELPERS=tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig`",
        "- `PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`",
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`zigux/tests/fixtures/phase1_helper_manifest.json` is the authoritative owner-map split for all thirteen closed Phase 1 helpers",
    ),
    "Documentation/zigux/README.md": (
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
        "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "* keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.",
    ),
    "Documentation/zigux/review-checklist.md": (
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "`zigux/tests/phase1_host_tools_smoke.zig`",
        "`zigux/tests/fixtures/phase1_helper_manifest.json`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
    ),
    "scripts/zigux/README.md": (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
    "zigux/tests/README.md": (
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "- `zigux/tests/phase1_host_tools_smoke.zig`",
        "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'test "phase1 host-tools smoke imports the live helper modules" {',
        'test "phase1 host-tools smoke exercises live helper behavior" {',
        'const argv_split = @import("argv_split");',
        'const rbtree = @import("rbtree");',
        'const string = @import("string");',
    ),
}

LINE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_LINES = {
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/validate-phase1.py --self-test",
        "run: python3 scripts/zigux/validate-phase1.py",
        "run: python3 scripts/zigux/check-phase1-parity.py --self-test",
        "run: python3 scripts/zigux/check-phase1-parity.py",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def require_once(text: str, label: str, marker: str, *, exact_line: bool) -> list[str]:
    count = count_exact_line(text, marker) if exact_line else text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent(text: str, label: str, marker: str, *, exact_line: bool) -> list[str]:
    count = count_exact_line(text, marker) if exact_line else text.count(marker)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_manifest_failures(root: Path) -> list[str]:
    manifest = json.loads(read_text(root, "zigux/tests/fixtures/phase1_helper_manifest.json"))
    failures: list[str] = []

    if manifest.get("phase") != "Phase 1":
        failures.append(f"manifest:phase:expected=Phase 1:actual={manifest.get('phase')}")
    if manifest.get("status") != "closed":
        failures.append(f"manifest:status:expected=closed:actual={manifest.get('status')}")
    if manifest.get("helper_count") != 13:
        failures.append(f"manifest:helper_count:expected=13:actual={manifest.get('helper_count')}")

    helpers = manifest.get("helpers")
    if helpers != list(HELPERS):
        failures.append("manifest:helpers:mismatch")

    lane_sequencing = manifest.get("lane_sequencing", {})
    if lane_sequencing.get("shared_replay_parked_helpers") != list(SHARED_REPLAY_PARKED_HELPERS):
        failures.append("manifest:shared_replay_parked_helpers:mismatch")
    if lane_sequencing.get("direct_anchor_followup_helpers") != list(DIRECT_ANCHOR_HELPERS):
        failures.append("manifest:direct_anchor_followup_helpers:mismatch")

    review_anchors = manifest.get("review_anchors", {})
    expected_anchor_keys = {
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    }
    missing = sorted(expected_anchor_keys.difference(review_anchors))
    if missing:
        failures.append(f"manifest:missing_review_anchors:{','.join(missing)}")

    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in TEXT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_once(text, f"{relative_path}:{marker}", marker, exact_line=False))

    for relative_path, markers in LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_once(text, f"{relative_path}:{marker}", marker, exact_line=True))

    for relative_path, markers in FORBIDDEN_LINES.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_absent(text, f"{relative_path}:{marker}", marker, exact_line=True))

    failures.extend(collect_manifest_failures(root))
    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(
        root,
        "Documentation/zigux/phase1-closure.md",
        "\n".join(TEXT_MARKERS["Documentation/zigux/phase1-closure.md"]) + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        "\n".join(TEXT_MARKERS["Documentation/zigux/phase1-host-helper-lane-sequencing.md"]) + "\n",
    )
    write_text(root, "Documentation/zigux/README.md", "\n".join(TEXT_MARKERS["Documentation/zigux/README.md"]) + "\n")
    write_text(
        root,
        "Documentation/zigux/review-checklist.md",
        "\n".join(TEXT_MARKERS["Documentation/zigux/review-checklist.md"]) + "\n",
    )
    write_text(root, "scripts/zigux/README.md", "\n".join(TEXT_MARKERS["scripts/zigux/README.md"]) + "\n")
    write_text(root, "zigux/tests/README.md", "\n".join(TEXT_MARKERS["zigux/tests/README.md"]) + "\n")
    write_text(
        root,
        "zigux/tests/phase1_host_tools_smoke.zig",
        "\n".join(TEXT_MARKERS["zigux/tests/phase1_host_tools_smoke.zig"]) + "\n",
    )
    workflow_chunks = list(LINE_MARKERS[".github/workflows/zigux-bootstrap.yml"])
    write_text(root, ".github/workflows/zigux-bootstrap.yml", "\n".join(workflow_chunks) + "\n")

    manifest = {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": list(HELPERS),
        "lane_sequencing": {
            "shared_replay_parked_helpers": list(SHARED_REPLAY_PARKED_HELPERS),
            "direct_anchor_followup_helpers": list(DIRECT_ANCHOR_HELPERS),
        },
        "review_anchors": {
            "tools/lib/bitmap.zig": {},
            "tools/lib/find_bit.zig": {},
            "tools/lib/rbtree.zig": {},
            "tools/lib/string.zig": {},
        },
    }
    write_text(
        root,
        "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(manifest, indent=2) + "\n",
    )


def remove_marker(root: Path, relative_path: str, marker: str, *, exact_line: bool) -> None:
    path = root / relative_path
    if exact_line:
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            if line.strip() == marker.strip():
                del lines[idx]
                path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
                return
        raise ValueError(f"missing marker: {relative_path}: {marker}")

    text = path.read_text(encoding="utf-8")
    replacement = marker + "\n"
    if replacement in text:
        path.write_text(text.replace(replacement, "", 1), encoding="utf-8")
        return
    if marker in text:
        path.write_text(text.replace(marker, "", 1), encoding="utf-8")
        return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def duplicate_marker(root: Path, relative_path: str, marker: str, *, exact_line: bool) -> None:
    path = root / relative_path
    if exact_line:
        lines = path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines):
            if line.strip() == marker.strip():
                lines.insert(idx + 1, line)
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return
        raise ValueError(f"missing marker: {relative_path}: {marker}")

    text = path.read_text(encoding="utf-8")
    if marker not in text:
        raise ValueError(f"missing marker: {relative_path}: {marker}")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def add_forbidden_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def write_sample_root(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    build_sample_repo(destination)


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    cases.extend(
        [
            ("missing_marker:phase1_closure_route", ("remove_text", "Documentation/zigux/phase1-closure.md", TEXT_MARKERS["Documentation/zigux/phase1-closure.md"][1])),
            ("duplicate_marker:lane_sequencing_direct_anchor", ("duplicate_text", "Documentation/zigux/phase1-host-helper-lane-sequencing.md", TEXT_MARKERS["Documentation/zigux/phase1-host-helper-lane-sequencing.md"][1])),
            ("missing_marker:review_checklist_smoke", ("remove_text", "Documentation/zigux/review-checklist.md", TEXT_MARKERS["Documentation/zigux/review-checklist.md"][3])),
            ("missing_line:workflow_smoke", ("remove_line", ".github/workflows/zigux-bootstrap.yml", LINE_MARKERS[".github/workflows/zigux-bootstrap.yml"][6])),
            ("duplicate_line:workflow_direct_owner", ("duplicate_line", ".github/workflows/zigux-bootstrap.yml", LINE_MARKERS[".github/workflows/zigux-bootstrap.yml"][0])),
            ("forbidden_line:workflow_validate_phase1", ("forbidden", ".github/workflows/zigux-bootstrap.yml", FORBIDDEN_LINES[".github/workflows/zigux-bootstrap.yml"][1])),
            ("manifest_helper_count", ("manifest_helper_count",)),
            ("manifest_missing_helper", ("manifest_remove_helper", "tools/lib/zalloc.zig")),
            ("manifest_wrong_shared_set", ("manifest_shared_set",)),
            ("manifest_missing_review_anchor", ("manifest_missing_review_anchor", "tools/lib/string.zig")),
        ]
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-helper-owner-map-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove_text":
                    remove_marker(root, mutation[1], mutation[2], exact_line=False)
                elif kind == "duplicate_text":
                    duplicate_marker(root, mutation[1], mutation[2], exact_line=False)
                elif kind == "remove_line":
                    remove_marker(root, mutation[1], mutation[2], exact_line=True)
                elif kind == "duplicate_line":
                    duplicate_marker(root, mutation[1], mutation[2], exact_line=True)
                elif kind == "forbidden":
                    add_forbidden_line(root, mutation[1], mutation[2])
                else:
                    manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    if kind == "manifest_helper_count":
                        manifest["helper_count"] = 12
                    elif kind == "manifest_remove_helper":
                        manifest["helpers"].remove(mutation[1])
                    elif kind == "manifest_shared_set":
                        manifest["lane_sequencing"]["shared_replay_parked_helpers"] = list(SHARED_REPLAY_PARKED_HELPERS[:-1])
                    elif kind == "manifest_missing_review_anchor":
                        del manifest["review_anchors"][mutation[1]]
                    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_HELPER_OWNER_MAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_HELPER_OWNER_MAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument("--write-sample-root", help="write a sample current-like root for validation")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"phase1-helper-owner-map-packet:sample-root-written:{destination}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_HELPER_OWNER_MAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_HELPER_OWNER_MAP_PACKET=pass")
    print(f"PHASE1_HELPER_OWNER_MAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_HELPER_OWNER_MAP_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in TEXT_MARKERS.values()) + sum(len(markers) for markers in LINE_MARKERS.values())}"
    )
    print(
        "PHASE1_HELPER_OWNER_MAP_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{sum(len(markers) for markers in FORBIDDEN_LINES.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
