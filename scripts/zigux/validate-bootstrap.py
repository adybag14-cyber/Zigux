#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
TOOLCHAIN_POLICY = "scripts/zigux/zig-toolchain-policy.json"

DEFAULT_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)

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
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/validate-bootstrap.py",
    TOOLCHAIN_POLICY,
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


def read_json_dict(root: Path, rel: str) -> dict:
    path = root / rel
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def load_required_make_routes(root: Path) -> tuple[str, ...]:
    payload = read_json_dict(root, TOOLCHAIN_POLICY)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {root / TOOLCHAIN_POLICY}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {root / TOOLCHAIN_POLICY}")

    normalized: list[str] = []
    seen: set[str] = set()
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes entry in required file: {root / TOOLCHAIN_POLICY}")
        normalized_route = route.strip()
        if normalized_route in seen:
            raise SystemExit(
                f"duplicate required_make_routes entry in required file: {root / TOOLCHAIN_POLICY}: {normalized_route}"
            )
        seen.add(normalized_route)
        normalized.append(normalized_route)
    return tuple(normalized)


def format_workflow_route_line(route: str) -> str:
    return f"run: make -C zigux {route}"


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

    readme = read_text(root, "zigux-alpha/README.md")
    roadmap = read_text(root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
    ledger = read_text(root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md")
    docs_readme = read_text(root, "Documentation/zigux/README.md")
    freeze_map = read_text(root, "Documentation/zigux/freeze-map.md")
    scripts_readme = read_text(root, "scripts/zigux/README.md")
    workflow = read_text(root, WORKFLOW)
    required_make_routes = load_required_make_routes(root)

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

    for route in required_make_routes:
        marker = format_workflow_route_line(route)
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_POLICY_ROUTE_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_POLICY_ROUTE_WORKFLOW_LINE", f"{marker}:count={count}"))

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


def policy_payload(required_make_routes: tuple[str, ...] = DEFAULT_REQUIRED_MAKE_ROUTES) -> str:
    payload = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {"x86_64-linux": "3" * 64},
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": ["x86_64-linux"],
            "required_make_routes": list(required_make_routes),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


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
    write_text(root, "scripts/zigux/check-phase1-route-summary-counts.py", "present\n")
    write_text(root, "scripts/zigux/install-zig.py", "present\n")
    write_text(root, "scripts/zigux/validate-bootstrap.py", "present\n")
    write_text(root, TOOLCHAIN_POLICY, policy_payload())
    write_text(root, "zigux/tests/README.md", "present\n")
    route_lines = tuple(format_workflow_route_line(route) for route in DEFAULT_REQUIRED_MAKE_ROUTES)
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES, *route_lines)) + "\n")


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
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
                "run: python3 scripts/zigux/other.py",
            ),
        )
        assert (
            "MISSING_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
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
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), REQUIRED_WORKFLOW_LINES[-1]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[-1]}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        route_line = format_workflow_route_line(DEFAULT_REQUIRED_MAKE_ROUTES[-1])
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(read_text(root, WORKFLOW), route_line, "run: make -C zigux phase2-other"),
        )
        assert ("MISSING_POLICY_ROUTE_WORKFLOW_LINE", route_line) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        route_line = format_workflow_route_line(DEFAULT_REQUIRED_MAKE_ROUTES[0])
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), route_line))
        assert ("DUPLICATE_POLICY_ROUTE_WORKFLOW_LINE", f"{route_line}:count=2") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-zig-toolchain.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/check-zig-toolchain.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-phase1-route-summary-counts.py").unlink()
        assert (
            "MISSING_REQUIRED_PATH",
            "scripts/zigux/check-phase1-route-summary-counts.py",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/stage-pinned-zig-archive.py").unlink()
        assert (
            "MISSING_REQUIRED_PATH",
            "scripts/zigux/stage-pinned-zig-archive.py",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/check-lane05-stage-helper-selftest.py").unlink()
        assert (
            "MISSING_REQUIRED_PATH",
            "scripts/zigux/check-lane05-stage-helper-selftest.py",
        ) in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / "scripts/zigux/install-zig.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/install-zig.py") in collect_issues(root)
        checks += 1

        build_self_test_root(root)
        (root / TOOLCHAIN_POLICY).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert f"required file missing: {root / TOOLCHAIN_POLICY}" == str(exc)
            checks += 1
        else:
            raise AssertionError("missing toolchain policy did not abort")

        build_self_test_root(root)
        write_text(root, TOOLCHAIN_POLICY, "{broken\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid toolchain policy json did not abort")

        build_self_test_root(root)
        write_text(root, TOOLCHAIN_POLICY, json.dumps({"phase": "Phase 2"}, indent=2) + "\n")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid upgrade_policy" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing upgrade_policy did not abort")

        build_self_test_root(root)
        write_text(
            root,
            TOOLCHAIN_POLICY,
            json.dumps({"phase": "Phase 2", "upgrade_policy": {"required_make_routes": []}}, indent=2) + "\n",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks += 1
        else:
            raise AssertionError("empty required_make_routes did not abort")

        build_self_test_root(root)
        write_text(
            root,
            TOOLCHAIN_POLICY,
            policy_payload(DEFAULT_REQUIRED_MAKE_ROUTES[:-1] + ("phase2-cross",)),
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate required_make_routes entry" in str(exc)
            checks += 1
        else:
            raise AssertionError("duplicate required_make_routes did not abort")

        build_self_test_root(root)
        write_text(
            root,
            TOOLCHAIN_POLICY,
            json.dumps(
                {
                    "phase": "Phase 2",
                    "upgrade_policy": {"required_make_routes": ["phase2-toolchain", "  "]},
                },
                indent=2,
            )
            + "\n",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes entry" in str(exc)
            checks += 1
        else:
            raise AssertionError("blank required_make_routes entry did not abort")

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

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    required_make_routes = load_required_make_routes(root)
    print("BOOTSTRAP_VALIDATION=pass")
    print(f"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"BOOTSTRAP_POLICY_REQUIRED_ROUTE_COUNT={len(required_make_routes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())