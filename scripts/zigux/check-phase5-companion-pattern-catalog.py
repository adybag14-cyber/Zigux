#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CATALOG_PATH = Path("Documentation/zigux/phase5-companion-pattern-catalog.md")

REQUIRED_MARKERS = (
    "Phase 5 still stays inside these roadmap-backed anchors:",
    "Current `master` ships these bounded Phase 5 companion files:",
    "`samples/zigux/bytestream_fifo_window_contract.zig`",
    "`samples/zigux/kobject_example_attr_group_contract.zig`",
    "`samples/zigux/kretprobe_example_instance_budget_contract.zig`",
    "`samples/zigux/trace_events_string_formatting_sample.zig`",
    "`samples/zigux/trace_events_callback_focus_contract.zig`",
    "Keep `zigux/tests/phase5_build.zig` framed as the shared rerun companion for the wider Phase 5 packet rather than as sample-local proof.",
    "Keep `samples/zigux/runtime_*.zig` in the separate Phase 9 lane rather than using runtime files as extra Phase 5 evidence.",
)

REQUIRED_PATHS = (
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md",
    "samples/zigux/README.md",
    "samples/zigux/bytestream_fifo_window_contract.zig",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "samples/zigux/kretprobe_example_instance_budget_contract.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "samples/zigux/trace_events_callback_focus_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract.zig",
    "zigux/tests/phase5_kobject_attr_group_contract_survey.zig",
    "zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig",
    "zigux/tests/phase5_build.zig",
)

FORBIDDEN_TEXT = (
    "a fifth approved Phase 5 sample family",
    "runtime files are extra Phase 5 evidence",
)


def read_text(root: Path, path: Path) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, path: Path, text: str) -> None:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def placeholder() -> str:
    lines = ["# phase5-companion-pattern-catalog.md"]
    lines.extend(REQUIRED_MARKERS)
    lines.extend(f"`{path}`" for path in REQUIRED_PATHS)
    return "\n\n".join(lines) + "\n"


def seed(root: Path) -> None:
    write_text(root, CATALOG_PATH, placeholder())
    for rel in REQUIRED_PATHS:
        rel_path = Path(rel)
        if rel_path == CATALOG_PATH:
            continue
        write_text(root, rel_path, "present\n")


def collect_failures(root: Path) -> list[str]:
    text = read_text(root, CATALOG_PATH)
    failures: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_text:{marker}")
    for rel in REQUIRED_PATHS:
        if f"`{rel}`" not in text and rel not in text:
            failures.append(f"missing_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo_missing_path:{rel}")
    for forbidden in FORBIDDEN_TEXT:
        if forbidden in text:
            failures.append(f"forbidden_text:{forbidden}")
    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="phase5_companion_catalog_") as tmpdir:
        root = Path(tmpdir)
        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_marker"
        seed(mutated)
        write_text(mutated, CATALOG_PATH, placeholder().replace(REQUIRED_MARKERS[7], ""))
        expect_exact("missing marker", collect_failures(mutated), [f"missing_text:{REQUIRED_MARKERS[7]}"])
        checks_run += 1

        mutated = root / "missing_path_reference"
        seed(mutated)
        write_text(mutated, CATALOG_PATH, placeholder().replace("`samples/zigux/kretprobe_example_instance_budget_contract.zig`", ""))
        expect_exact(
            "missing path reference",
            collect_failures(mutated),
            ["missing_text:`samples/zigux/kretprobe_example_instance_budget_contract.zig`", "missing_path:samples/zigux/kretprobe_example_instance_budget_contract.zig"],
        )
        checks_run += 1

        mutated = root / "missing_repo_path"
        seed(mutated)
        (mutated / "zigux/tests/phase5_build.zig").unlink()
        expect_exact("missing repo path", collect_failures(mutated), ["repo_missing_path:zigux/tests/phase5_build.zig"])
        checks_run += 1

        mutated = root / "forbidden_text"
        seed(mutated)
        write_text(mutated, CATALOG_PATH, placeholder() + "\n" + FORBIDDEN_TEXT[0] + "\n")
        expect_exact("forbidden text", collect_failures(mutated), [f"forbidden_text:{FORBIDDEN_TEXT[0]}"])
        checks_run += 1

    print("PHASE5_COMPANION_PATTERN_CATALOG_SELF_TEST=pass")
    print(f"PHASE5_COMPANION_PATTERN_CATALOG_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT.parent.parent, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_COMPANION_PATTERN_CATALOG=fail")
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_COMPANION_PATTERN_CATALOG=pass")
    print(f"PHASE5_COMPANION_PATTERN_CATALOG_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
