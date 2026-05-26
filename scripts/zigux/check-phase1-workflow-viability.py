#!/usr/bin/env python3
"""Guard the current-master-safe Lane 17 Phase 1 workflow-viability packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    LANE_NOTE_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    TESTS_BUILD_REL,
    SMOKE_REL,
    MANIFEST_REL,
    DIRECT_OWNER_REL,
    STRING_REVIEW_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
)

WORKFLOW_STEPS = (
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 closure validator", "python3 scripts/zigux/validate-phase1-closure.py --self-test"),
    ("Check current Phase 1 closure packet", "python3 scripts/zigux/validate-phase1-closure.py"),
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
)

ADJACENT_CHAIN = (
    "Check current Phase 1 closure packet",
    "Self-test current Phase 3 interop packet",
)

REQUIRED_CLOSURE_LINES = (
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)

REQUIRED_LANE_NOTE_LINES = (
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`",
)

REQUIRED_README_SNIPPETS = {
    DOCS_README_REL: (
        "Documentation/zigux/phase1-closure.md",
        "scripts/zigux/validate-phase1-closure.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    REVIEW_CHECKLIST_REL: (
        "Documentation/zigux/phase1-closure.md",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "scripts/zigux/validate-phase1-closure.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    SCRIPTS_README_REL: (
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "scripts/zigux/validate-phase1-closure.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
    TESTS_README_REL: (
        "Documentation/zigux/phase1-closure.md",
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "scripts/zigux/validate-phase1-closure.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

FORBIDDEN_WORKFLOW_SNIPPETS = (
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
    "zig build bench --build-file zigux/tests/build.zig",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
)


def repo_root(path: str | None) -> Path:
    return Path(path).resolve() if path else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_line_once(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current == line)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{line}"]


def require_substring(text: str, label: str, snippet: str) -> list[str]:
    return [] if snippet in text else [f"{label}:missing:{snippet}"]


def require_file(root: Path, relative_path: Path) -> list[str]:
    path = root / relative_path
    if not path.exists():
        return [f"missing_file:{relative_path.as_posix()}"]
    if not path.is_file():
        return [f"non_file_path:{relative_path.as_posix()}"]
    return []


def workflow_step_names(workflow_text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in workflow_text.splitlines() if line.startswith(prefix)]


def require_workflow_step(workflow_text: str, step_name: str, run_command: str) -> list[str]:
    failures = require_line_once(workflow_text, f"step:{step_name}", f"      - name: {step_name}")
    failures.extend(require_line_once(workflow_text, f"run:{step_name}", f"        run: {run_command}"))
    return failures


def require_adjacent_chain(workflow_text: str, chain: tuple[str, ...]) -> list[str]:
    names = workflow_step_names(workflow_text)
    want = list(chain)
    for idx in range(len(names) - len(want) + 1):
        if names[idx : idx + len(want)] == want:
            return []
    return [f"workflow_adjacent_chain:missing:{'->'.join(chain)}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        failures.extend(require_file(root, relative_path))
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    closure_text = load_text(root, CLOSURE_REL)
    lane_note_text = load_text(root, LANE_NOTE_REL)

    for line in REQUIRED_CLOSURE_LINES:
        failures.extend(require_line_once(closure_text, "closure", line))
    for line in REQUIRED_LANE_NOTE_LINES:
        failures.extend(require_line_once(lane_note_text, "lane_note", line))

    for relative_path, snippets in REQUIRED_README_SNIPPETS.items():
        text = load_text(root, relative_path)
        for snippet in snippets:
            failures.extend(require_substring(text, relative_path.as_posix(), snippet))

    for step_name, run_command in WORKFLOW_STEPS:
        failures.extend(require_workflow_step(workflow_text, step_name, run_command))
    failures.extend(require_adjacent_chain(workflow_text, ADJACENT_CHAIN))

    for forbidden in FORBIDDEN_WORKFLOW_SNIPPETS:
        if forbidden in workflow_text:
            failures.append(f"workflow_forbidden:unexpected_present:{forbidden}")

    return failures


def sample_workflow_text() -> str:
    lines = ["jobs:", "  bootstrap:", "    runs-on: ubuntu-latest", "    steps:"]
    for step_name, run_command in WORKFLOW_STEPS:
        lines.append(f"      - name: {step_name}")
        lines.append(f"        run: {run_command}")
    return "\n".join(lines) + "\n"


def sample_closure_text() -> str:
    return "\n".join(
        [
            "# Phase 1 Closure",
            "",
            *REQUIRED_CLOSURE_LINES,
            "",
            "The current shared tests-root closure route is narrow on purpose.",
        ]
    ) + "\n"


def sample_lane_note_text() -> str:
    return "\n".join(
        [
            "# Phase 1 Host-Helper Lane Sequencing",
            "",
            *REQUIRED_LANE_NOTE_LINES,
            "",
            "This note is lane-local coordination only.",
        ]
    ) + "\n"


def sample_docs_readme_text() -> str:
    return "\n".join(
        [
            "# Zigux Documentation",
            "",
            "Phase 1 notes",
            "- `Documentation/zigux/phase1-closure.md`",
            "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
            "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
            "- `scripts/zigux/validate-phase1-closure.py`",
            "- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        ]
    ) + "\n"


def sample_review_checklist_text() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            "",
            "- `Documentation/zigux/phase1-closure.md`",
            "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
            "- `scripts/zigux/validate-phase1-closure.py`",
            "- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        ]
    ) + "\n"


def sample_scripts_readme_text() -> str:
    return "\n".join(
        [
            "# scripts/zigux",
            "",
            "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
            "- `scripts/zigux/check-phase1-string-review-packet.py`",
            "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
            "- `scripts/zigux/validate-phase1-closure.py`",
            "- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        ]
    ) + "\n"


def sample_tests_readme_text() -> str:
    return "\n".join(
        [
            "# zigux/tests",
            "",
            "- `Documentation/zigux/phase1-closure.md`",
            "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
            "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
            "- `scripts/zigux/validate-phase1-closure.py`",
            "- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        ]
    ) + "\n"


def write_sample_root(root: Path) -> None:
    write_text(root, WORKFLOW_REL, sample_workflow_text())
    write_text(root, CLOSURE_REL, sample_closure_text())
    write_text(root, LANE_NOTE_REL, sample_lane_note_text())
    write_text(root, DOCS_README_REL, sample_docs_readme_text())
    write_text(root, REVIEW_CHECKLIST_REL, sample_review_checklist_text())
    write_text(root, SCRIPTS_README_REL, sample_scripts_readme_text())
    write_text(root, TESTS_README_REL, sample_tests_readme_text())
    write_text(root, TESTS_BUILD_REL, "// build placeholder\n")
    write_text(root, SMOKE_REL, 'test "phase1 host-tools smoke exercises live helper behavior" {}\n')
    write_text(root, MANIFEST_REL, '{ "phase": "Phase 1", "helper_count": 13 }\n')
    write_text(root, DIRECT_OWNER_REL, "#!/usr/bin/env python3\n")
    write_text(root, STRING_REVIEW_REL, "#!/usr/bin/env python3\n")
    write_text(root, SHARED_REMINDER_REL, "#!/usr/bin/env python3\n")
    write_text(root, CLOSURE_VALIDATOR_REL, "#!/usr/bin/env python3\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane17_workflow_viability_") as temp_dir:
        root = Path(temp_dir)
        write_sample_root(root)

        case_count += 1
        if collect_failures(root):
            print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=fail")
            print("case=baseline_should_pass")
            return 1

        case_count += 1
        bad_root = root / "missing_closure_marker"
        shutil.copytree(root, bad_root)
        write_text(bad_root, CLOSURE_REL, sample_closure_text().replace(REQUIRED_CLOSURE_LINES[0] + "\n", "", 1))
        if not collect_failures(bad_root):
            print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=fail")
            print("case=missing_closure_marker_should_fail")
            return 1

        case_count += 1
        bad_root = root / "missing_readme_snippet"
        shutil.copytree(root, bad_root)
        write_text(bad_root, SCRIPTS_README_REL, "# scripts/zigux\n")
        if not collect_failures(bad_root):
            print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=fail")
            print("case=missing_readme_snippet_should_fail")
            return 1

        case_count += 1
        bad_root = root / "bad_adjacency"
        shutil.copytree(root, bad_root)
        write_text(
            bad_root,
            WORKFLOW_REL,
            sample_workflow_text().replace(
                "      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py\n"
                "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n",
                "      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py\n"
                "      - name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n"
                "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py\n",
                1,
            ),
        )
        if not collect_failures(bad_root):
            print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=fail")
            print("case=bad_adjacency_should_fail")
            return 1

        case_count += 1
        bad_root = root / "forbidden_history"
        shutil.copytree(root, bad_root)
        write_text(bad_root, WORKFLOW_REL, sample_workflow_text() + "        run: python3 scripts/zigux/validate-phase1.py\n")
        if not collect_failures(bad_root):
            print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=fail")
            print("case=forbidden_history_should_fail")
            return 1

        case_count += 1
        bad_root = root / "duplicate_step"
        shutil.copytree(root, bad_root)
        write_text(
            bad_root,
            WORKFLOW_REL,
            sample_workflow_text()
            + "      - name: Self-test current Phase 1 closure validator\n"
            + "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
        )
        if not collect_failures(bad_root):
            print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=fail")
            print("case=duplicate_step_should_fail")
            return 1

    print("PHASE1_WORKFLOW_VIABILITY_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_VIABILITY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--write-sample-root", help="Write a sample current-master-safe root")
    parser.add_argument("--self-test", action="store_true", help="Run builtin self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        write_sample_root(root)
        print(root)
        return 0

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_WORKFLOW_VIABILITY=fail")
        print("PHASE1_WORKFLOW_VIABILITY_MODE=current-master-safe")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_VIABILITY=pass")
    print("PHASE1_WORKFLOW_VIABILITY_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
