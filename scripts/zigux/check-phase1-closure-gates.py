#!/usr/bin/env python3
"""Guard the shipped Phase 1 closure-gate packet against cross-surface drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    LANE_NOTE_REL,
    WORKFLOW_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    MANIFEST_REL,
)

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
EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

REQUIRED_EXACT_LINES = {
    PHASE1_CLOSURE_REL: {
        "bench_checker_listed": "- `scripts/zigux/check-phase1-bench.py`",
        "closure_validator": "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "shared_tests_route": "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "closure_validator_state": "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
        "tests_build_listed": "- `zigux/tests/build.zig`",
        "tests_smoke_listed": "- `zigux/tests/phase1_host_tools_smoke.zig`",
    },
    LANE_NOTE_REL: {
        "shared_reminder_active_packet": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py`",
        "shared_reminder_route_split": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
    },
    WORKFLOW_REL: {
        "bench_self_test_name": "- name: Self-test current Phase 1 bench checker",
        "bench_self_test_run": "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "closure_gates_self_test_name": "- name: Self-test current Phase 1 closure-gates checker",
        "closure_gates_self_test_run": "run: python3 scripts/zigux/check-phase1-closure-gates.py --self-test",
        "closure_gates_live_name": "- name: Check current Phase 1 closure-gates packet",
        "closure_gates_live_run": "run: python3 scripts/zigux/check-phase1-closure-gates.py",
        "shared_reminder_self_test_name": "- name: Self-test current Phase 1 shared reminder checker",
        "shared_reminder_self_test_run": "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "shared_reminder_live_name": "- name: Check current Phase 1 shared reminder packet",
        "shared_reminder_live_run": "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "shared_smoke_name": "- name: Run current Phase 1 shared tests-root smoke",
        "shared_smoke_run": "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
    TESTS_BUILD_REL: {
        "phase1_step_decl": '        "phase1-host-tools-smoke",',
        "phase1_step_help": '        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    },
    PHASE1_SMOKE_REL: {
        "imports_test": 'test "phase1 host-tools smoke imports the live helper modules" {',
        "behavior_test": 'test "phase1 host-tools smoke exercises live helper behavior" {',
        "find_bit_import": 'pub const find_bit = @import("find_bit");',
    },
}

MANIFEST_EXPECTATIONS = {
    ("phase",): "Phase 1",
    ("status",): "closed",
    ("helper_count",): 13,
    ("lane_sequencing", "shared_replay_parked_helpers"): EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
    ("lane_sequencing", "direct_anchor_followup_helpers"): EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for label, line in labels.items():
            failures.extend(require_exact_line(text, f"{relative_path.as_posix()}:{label}", line))

    manifest = load_json(root, MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]
    for path, expected in MANIFEST_EXPECTATIONS.items():
        failures.extend(
            require_exact_value(
                f"{MANIFEST_REL.as_posix()}:{'.'.join(path)}",
                nested_value(manifest, path),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_text(relative_path: Path) -> str:
    labels = REQUIRED_EXACT_LINES.get(relative_path, {})
    return "# sample\n\n" + "\n".join(labels.values()) + "\n"


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "phase": "Phase 1",
                "status": "closed",
                "helper_count": 13,
                "lane_sequencing": {
                    "shared_replay_parked_helpers": EXPECTED_SHARED_REPLAY_PARKED_HELPERS,
                    "direct_anchor_followup_helpers": EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS,
                },
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        if relative_path == MANIFEST_REL:
            write_file(root, relative_path, sample_manifest())
        else:
            write_file(root, relative_path, sample_text(relative_path))


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, Path | None, str | tuple[str, ...] | None, str]] = [
        ("success", None, None, "none")
    ]
    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        for _, line in labels.items():
            cases.append((f"missing_{relative_path.name}", relative_path, line, "remove"))
            cases.append((f"duplicate_{relative_path.name}", relative_path, line, "duplicate"))
    for path in MANIFEST_EXPECTATIONS:
        cases.append((f"manifest_{'_'.join(path)}", MANIFEST_REL, path, "manifest"))
    cases.extend(
        [
            ("missing_workflow", WORKFLOW_REL, None, "missing_file"),
            ("missing_closure_note", PHASE1_CLOSURE_REL, None, "missing_file"),
        ]
    )

    for name, relative_path, needle, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-closure-gates-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if relative_path:
                target = root / relative_path
                if operation == "missing_file":
                    target.unlink()
                elif operation in {"remove", "duplicate"} and isinstance(needle, str):
                    text = target.read_text(encoding="utf-8")
                    if operation == "remove":
                        target.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")
                    else:
                        target.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")
                elif operation == "manifest" and isinstance(needle, tuple):
                    mutate_manifest(root, needle)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
                continue
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_GATES_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_GATES_SELF_TEST_CASE_COUNT={len(cases)}")
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
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_GATES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())