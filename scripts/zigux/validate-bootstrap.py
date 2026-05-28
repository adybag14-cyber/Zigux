#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
SPLIT_HELPER_WORKFLOW = ".github/workflows/zigux-bootstrap-split-helper.yml"
ARCHIVE_PARTS_WORKFLOW = ".github/workflows/zigux-bootstrap-archive-parts-packet.yml"

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
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/split-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-split-helper-selftest.py",
    "scripts/zigux/check-lane05-split-helper-workflow.py",
    "scripts/zigux/check-lane05-archive-parts-packet.py",
    "scripts/zigux/check-lane05-archive-parts-workflow.py",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-bootstrap.py",
    "scripts/zigux/zig-toolchain-policy.json",
    "zigux/tests/README.md",
    "third_party/README.md",
    WORKFLOW,
    SPLIT_HELPER_WORKFLOW,
    ARCHIVE_PARTS_WORKFLOW,
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

THIRD_PARTY_README_MARKERS = (
    "# Zigux third-party archives",
    "Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
    "`scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
)

SPLIT_HELPER_WORKFLOW_LINES = (
    "name: zigux-bootstrap-split-helper",
    "- 'scripts/zigux/**'",
    "- 'third_party/**'",
    "run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-split-helper-workflow.py",
)

ARCHIVE_PARTS_WORKFLOW_LINES = (
    "name: zigux-bootstrap-archive-parts-packet",
    "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'",
    "- 'scripts/zigux/check-lane05-archive-parts-packet.py'",
    "- 'scripts/zigux/zig-toolchain-policy.json'",
    "- 'third_party/**'",
    "run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py",
    "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test",
    "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing",
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


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    def maybe_read(rel: str) -> str:
        path = root / rel
        return path.read_text(encoding="utf-8") if path.exists() else ""

    readme = maybe_read("zigux-alpha/README.md")
    roadmap = maybe_read("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
    ledger = maybe_read("zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    docs_readme = maybe_read("Documentation/zigux/README.md")
    freeze_map = maybe_read("Documentation/zigux/freeze-map.md")
    scripts_readme = maybe_read("scripts/zigux/README.md")
    third_party_readme = maybe_read("third_party/README.md")
    workflow = maybe_read(WORKFLOW)
    split_helper_workflow = maybe_read(SPLIT_HELPER_WORKFLOW)
    archive_parts_workflow = maybe_read(ARCHIVE_PARTS_WORKFLOW)

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
    for marker in THIRD_PARTY_README_MARKERS:
        if marker not in third_party_readme:
            issues.append(("MISSING_THIRD_PARTY_README_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in SPLIT_HELPER_WORKFLOW_LINES:
        count = count_exact_lines(split_helper_workflow, marker)
        if count == 0:
            issues.append(("MISSING_SPLIT_HELPER_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_SPLIT_HELPER_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in ARCHIVE_PARTS_WORKFLOW_LINES:
        count = count_exact_lines(archive_parts_workflow, marker)
        if count == 0:
            issues.append(("MISSING_ARCHIVE_PARTS_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_ARCHIVE_PARTS_WORKFLOW_LINE", f"{marker}:count={count}"))

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
    write_text(root, "scripts/zigux/check-lane05-local-first-archive-workflow.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-local-archive-readme.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-install-zig-archive-verification.py", "present\n")
    write_text(root, "scripts/zigux/stage-pinned-zig-archive.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-stage-helper-contract.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-stage-helper-selftest.py", "present\n")
    write_text(root, "scripts/zigux/split-pinned-zig-archive.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-split-helper-selftest.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-split-helper-workflow.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-archive-parts-packet.py", "present\n")
    write_text(root, "scripts/zigux/check-lane05-archive-parts-workflow.py", "present\n")
    write_text(root, "scripts/zigux/check-phase1-route-summary-counts.py", "present\n")
    write_text(root, "scripts/zigux/install-zig.py", "present\n")
    write_text(root, "scripts/zigux/validate-bootstrap.py", "present\n")
    write_text(root, "scripts/zigux/zig-toolchain-policy.json", "{}\n")
    write_text(root, "zigux/tests/README.md", "present\n")
    write_text(
        root,
        "third_party/README.md",
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                "Lane 05 bootstrap first reuses and validates `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz` when that pinned archive is present.",
                "",
                "`scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the archive-verification, staged-helper contract, and staged-helper self-test packet explicit beside that same local-first archive path.",
            )
        )
        + "\n",
    )
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n")
    write_text(
        root,
        SPLIT_HELPER_WORKFLOW,
        "\n".join(("name: zigux-bootstrap-split-helper", *SPLIT_HELPER_WORKFLOW_LINES[1:])) + "\n",
    )
    write_text(
        root,
        ARCHIVE_PARTS_WORKFLOW,
        "\n".join(("name: zigux-bootstrap-archive-parts-packet", *ARCHIVE_PARTS_WORKFLOW_LINES[1:])) + "\n",
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
            "third_party/README.md",
            read_text(root, "third_party/README.md").replace(THIRD_PARTY_README_MARKERS[1] + "\n", "", 1),
        )
        assert ("MISSING_THIRD_PARTY_README_MARKER", THIRD_PARTY_README_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/install-zig.py --self-test",
                "run: python3 scripts/zigux/other.py",
            ),
        )
        assert (
            "MISSING_WORKFLOW_LINE",
            "run: python3 scripts/zigux/install-zig.py --self-test",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            SPLIT_HELPER_WORKFLOW,
            replace_exact_line(
                read_text(root, SPLIT_HELPER_WORKFLOW),
                "run: python3 scripts/zigux/check-lane05-split-helper-workflow.py",
                "run: python3 scripts/zigux/other.py",
            ),
        )
        assert (
            "MISSING_SPLIT_HELPER_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-split-helper-workflow.py",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            ARCHIVE_PARTS_WORKFLOW,
            replace_exact_line(
                read_text(root, ARCHIVE_PARTS_WORKFLOW),
                "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing",
                "run: python3 scripts/zigux/other.py",
            ),
        )
        assert (
            "MISSING_ARCHIVE_PARTS_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            WORKFLOW,
            duplicate_exact_line(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
            ),
        )
        assert (
            "DUPLICATE_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing:count=2",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            SPLIT_HELPER_WORKFLOW,
            duplicate_exact_line(
                read_text(root, SPLIT_HELPER_WORKFLOW),
                "run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test",
            ),
        )
        assert (
            "DUPLICATE_SPLIT_HELPER_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test:count=2",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        write_text(
            root,
            ARCHIVE_PARTS_WORKFLOW,
            duplicate_exact_line(
                read_text(root, ARCHIVE_PARTS_WORKFLOW),
                "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test",
            ),
        )
        assert (
            "DUPLICATE_ARCHIVE_PARTS_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test:count=2",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-zig-toolchain.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/check-zig-toolchain.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-lane05-split-helper-workflow.py").unlink()
        assert (
            "MISSING_REQUIRED_PATH",
            "scripts/zigux/check-lane05-split-helper-workflow.py",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-lane05-archive-parts-workflow.py").unlink()
        assert (
            "MISSING_REQUIRED_PATH",
            "scripts/zigux/check-lane05-archive-parts-workflow.py",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "third_party/README.md").unlink()
        assert ("MISSING_REQUIRED_PATH", "third_party/README.md") in collect_issues(root)
        checks += 1

    print("BOOTSTRAP_VALIDATION_SELF_TEST=pass")
    print(f"BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the current Zigux bootstrap packet still exposes its charter, docs, toolchain, workflow, and Lane 05 companion workflow surfaces."
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
    print(f"BOOTSTRAP_SPLIT_HELPER_WORKFLOW_LINE_COUNT={len(SPLIT_HELPER_WORKFLOW_LINES)}")
    print(f"BOOTSTRAP_ARCHIVE_PARTS_WORKFLOW_LINE_COUNT={len(ARCHIVE_PARTS_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())