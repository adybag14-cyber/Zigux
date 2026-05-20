#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_PATHS = (
    "zigux-alpha/README.md",
    "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "scripts/zigux/validate-bootstrap.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/tests/README.md",
    WORKFLOW,
)

README_MARKERS = (
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
)

ROADMAP_MARKERS = (
    "## Bootstrap Status Note",
    "## Phase 1: Alpha Host-Side Helpers",
    "- `tools/lib/bitmap.zig`",
)

LEDGER_MARKERS = (
    "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
    "- `scripts/zigux/validate-bootstrap.py`",
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
)

DOCS_README_MARKERS = (
    "# Zigux Documentation This directory is the product documentation root for Zigux.",
    "- review rules",
    "- freeze map",
)

FREEZE_MAP_MARKERS = (
    "## Freeze In C Initially",
    "- `kernel/sched/core.c`",
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
)

SCRIPTS_README_MARKERS = (
    "# scripts/zigux",
    "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
)

REQUIRED_WORKFLOW_STEP_SEQUENCE = (
    "Compile current scripts",
    "Self-test current Zig toolchain checker",
    "Check current Zig toolchain policy packet",
    "Check current pinned Zig archive packet",
    "Self-test current Lane 05 local-first archive checker",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_step_name(text: str, marker: str, replacement: str) -> str:
    return replace_exact_line(text, f"- name: {marker}", f"      - name: {replacement}")


def duplicate_step_name(text: str, marker: str) -> str:
    return duplicate_exact_line(text, f"- name: {marker}")


def swap_step_names(text: str, first: str, second: str) -> str:
    first_marker = f"- name: {first}"
    second_marker = f"- name: {second}"
    lines = text.splitlines()
    first_index: int | None = None
    second_index: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first_marker and first_index is None:
            first_index = index
        elif stripped == second_marker and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError(f"step markers not found: {first}, {second}")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def insert_step_after(text: str, anchor_step: str, new_step_name: str, new_run: str) -> str:
    lines = text.splitlines()
    anchor = f"- name: {anchor_step}"
    for index, line in enumerate(lines):
        if line.strip() != anchor:
            continue
        insert_at = index + 1
        while insert_at < len(lines):
            stripped = lines[insert_at].strip()
            if stripped.startswith("- name: "):
                break
            insert_at += 1
        lines[insert_at:insert_at] = [
            f"      - name: {new_step_name}",
            f"        run: {new_run}",
        ]
        return "\n".join(lines) + "\n"
    raise AssertionError(f"step marker not found: {anchor_step}")


def collect_step_names(text: str) -> list[str]:
    names: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- name: "):
            names.append(stripped.removeprefix("- name: ").strip())
    return names


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    readme = read_text(root, "zigux-alpha/README.md")
    roadmap = read_text(root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
    ledger = read_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    docs_readme = read_text(root, "Documentation/zigux/README.md")
    freeze_map = read_text(root, "Documentation/zigux/freeze-map.md")
    scripts_readme = read_text(root, "scripts/zigux/README.md")
    workflow = read_text(root, WORKFLOW)

    for marker in README_MARKERS:
        if marker not in readme:
            issues.append(("MISSING_README_MARKER", marker))
    for marker in ROADMAP_MARKERS:
        if marker not in roadmap:
            issues.append(("MISSING_ROADMAP_MARKER", marker))
    for marker in LEDGER_MARKERS:
        if marker not in ledger:
            issues.append(("MISSING_LEDGER_MARKER", marker))
    for marker in DOCS_README_MARKERS:
        if marker not in docs_readme:
            issues.append(("MISSING_DOCS_README_MARKER", marker))
    for marker in FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            issues.append(("MISSING_FREEZE_MAP_MARKER", marker))
    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    step_names = collect_step_names(workflow)
    step_indices: list[int] = []
    for marker in REQUIRED_WORKFLOW_STEP_SEQUENCE:
        count = step_names.count(marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_STEP", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_STEP", f"{marker}:count={count}"))
            continue
        step_indices.append(step_names.index(marker))

    if len(step_indices) == len(REQUIRED_WORKFLOW_STEP_SEQUENCE):
        if step_indices != sorted(step_indices):
            issues.append(
                (
                    "MISORDERED_WORKFLOW_STEP_SEQUENCE",
                    " -> ".join(REQUIRED_WORKFLOW_STEP_SEQUENCE),
                )
            )
        elif any(current - previous != 1 for previous, current in zip(step_indices, step_indices[1:])):
            issues.append(
                (
                    "NONCONTIGUOUS_WORKFLOW_STEP_SEQUENCE",
                    " -> ".join(REQUIRED_WORKFLOW_STEP_SEQUENCE),
                )
            )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("BOOTSTRAP_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        root,
        "zigux-alpha/README.md",
        "\n".join(
            (
                "# zigux-alpha",
                "",
                "`zigux-alpha` is the Zigux bootstrap workspace.",
                "",
                "Rules",
                "- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
                "",
                "Active product surfaces",
                "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        "\n".join(
            (
                "# ZAR to Zigux Product Roadmap",
                "",
                "## Bootstrap Status Note",
                "",
                "## Phase 1: Alpha Host-Side Helpers",
                "",
                "- `tools/lib/bitmap.zig`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
        "\n".join(
            (
                "# Zigux Alpha Bootstrap Commit Ledger",
                "",
                "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
                "- `scripts/zigux/validate-bootstrap.py`",
                "",
                "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/README.md",
        "\n".join(
            (
                "# Zigux Documentation This directory is the product documentation root for Zigux.",
                "- review rules",
                "- freeze map",
            )
        )
        + "\n",
    )
    write_text(root, "Documentation/zigux/review-checklist.md", "present\n")
    write_text(
        root,
        "Documentation/zigux/freeze-map.md",
        "\n".join(
            (
                "# Zigux Freeze Map",
                "",
                "## Freeze In C Initially",
                "- `kernel/sched/core.c`",
                "",
                "## Study / Boundary Only",
                "- `kernel/workqueue.c`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        "scripts/zigux/README.md",
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "This directory holds shipped Zigux validation helpers and compact reminder surfaces.",
                "",
                "- `scripts/zigux/check-zig-toolchain.py`",
                "- `scripts/zigux/check-lane01-bootstrap-charter-alignment.py`",
            )
        )
        + "\n",
    )
    write_text(root, "scripts/zigux/check-zig-toolchain.py", "present\n")
    write_text(root, "scripts/zigux/check-lane01-bootstrap-charter-alignment.py", "present\n")
    write_text(root, "scripts/zigux/validate-bootstrap.py", "present\n")
    write_text(root, "scripts/zigux/zig-toolchain-policy.json", "{}\n")
    write_text(root, "zigux/tests/README.md", "present\n")
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Compile current scripts",
                "        run: python3 -m py_compile scripts/zigux/*.py",
                "      - name: Self-test current Zig toolchain checker",
                f"        {REQUIRED_WORKFLOW_LINES[0]}",
                "      - name: Check current Zig toolchain policy packet",
                f"        {REQUIRED_WORKFLOW_LINES[1]}",
                "      - name: Check current pinned Zig archive packet",
                f"        {REQUIRED_WORKFLOW_LINES[2]}",
                "      - name: Self-test current Lane 05 local-first archive checker",
                "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
                "      - name: Self-test current Lane 01 bootstrap charter checker",
                f"        {REQUIRED_WORKFLOW_LINES[3]}",
                "      - name: Check current Lane 01 bootstrap charter packet",
                f"        {REQUIRED_WORKFLOW_LINES[4]}",
                "      - name: Self-test current bootstrap validator",
                f"        {REQUIRED_WORKFLOW_LINES[5]}",
                "      - name: Check current bootstrap validator packet",
                f"        {REQUIRED_WORKFLOW_LINES[6]}",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_validate_bootstrap_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            "zigux-alpha/README.md",
            read_text(root, "zigux-alpha/README.md").replace(README_MARKERS[1] + "\n", "", 1),
        )
        assert ("MISSING_README_MARKER", README_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
            read_text(root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md").replace(ROADMAP_MARKERS[1] + "\n", "", 1),
        )
        assert ("MISSING_ROADMAP_MARKER", ROADMAP_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
            read_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md").replace(LEDGER_MARKERS[1] + "\n", "", 1),
        )
        assert ("MISSING_LEDGER_MARKER", LEDGER_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            "Documentation/zigux/freeze-map.md",
            read_text(root, "Documentation/zigux/freeze-map.md").replace(FREEZE_MAP_MARKERS[3] + "\n", "", 1),
        )
        assert ("MISSING_FREEZE_MAP_MARKER", FREEZE_MAP_MARKERS[3]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                REQUIRED_WORKFLOW_LINES[-1],
                "        run: python3 scripts/zigux/other.py",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[-1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[-1]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-zig-toolchain.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/check-zig-toolchain.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        workflow = swap_step_names(
            read_text(root, WORKFLOW),
            "Check current Zig toolchain policy packet",
            "Check current pinned Zig archive packet",
        )
        write_text(root, WORKFLOW, workflow)
        assert (
            "MISORDERED_WORKFLOW_STEP_SEQUENCE",
            " -> ".join(REQUIRED_WORKFLOW_STEP_SEQUENCE),
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            insert_step_after(
                read_text(root, WORKFLOW),
                "Check current pinned Zig archive packet",
                "Unrelated drift step",
                "python3 scripts/zigux/unrelated.py",
            ),
        )
        assert (
            "NONCONTIGUOUS_WORKFLOW_STEP_SEQUENCE",
            " -> ".join(REQUIRED_WORKFLOW_STEP_SEQUENCE),
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_step_name(
                read_text(root, WORKFLOW),
                "Compile current scripts",
                "Compile some other scripts",
            ),
        )
        assert ("MISSING_WORKFLOW_STEP", "Compile current scripts") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(root, WORKFLOW, duplicate_step_name(read_text(root, WORKFLOW), "Self-test current Lane 05 local-first archive checker"))
        assert (
            "DUPLICATE_WORKFLOW_STEP",
            "Self-test current Lane 05 local-first archive checker:count=2",
        ) in collect_issues(root)
        checks += 1

    print("BOOTSTRAP_VALIDATION_SELF_TEST=pass")
    print(f"BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the current Zigux bootstrap packet still exposes its charter, docs, toolchain, and workflow surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("BOOTSTRAP_VALIDATION=pass")
    print(f"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"BOOTSTRAP_WORKFLOW_STEP_SEQUENCE_COUNT={len(REQUIRED_WORKFLOW_STEP_SEQUENCE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
