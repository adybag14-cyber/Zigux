#!/usr/bin/env python3
"""Guard the bootstrap Phase 2 required-make-routes packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = "scripts/zigux/README.md"
REQUIRED_ROUTES_CHECKER = "scripts/zigux/check-phase2-required-make-routes.py"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    POLICY,
    BOOTSTRAP_NOTES,
    SCRIPTS_README,
    REQUIRED_ROUTES_CHECKER,
)

WORKFLOW_RUN_LINES = (
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
)

REQUIRED_ROUTE_WORKFLOW_LINES = (
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
)

ORDERED_WORKFLOW_LINES = (
    "- name: Run current Phase 2 cross make route",
    "- name: Self-test current Phase 2 required-make-routes checker",
    "- name: Check current Phase 2 required-make-routes packet",
    "- name: Self-test current Phase 2 shared reminder checker",
)

MAKEFILE_LINES = (
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

NOTES_MARKERS = (
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`make -C zigux phase2-tools`",
    "required Linux-style make routes",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-validate`",
)

EXPECTED_REQUIRED_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_RUN_LINES)
    + len(WORKFLOW_RUN_LINES)
    + 1
    + len(REQUIRED_ROUTE_WORKFLOW_LINES)
    + len(MAKEFILE_LINES)
    + len(MAKEFILE_LINES)
    + 3
    + len(REQUIRED_PATHS)
)


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
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


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_order_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    cursor = -1
    for marker in markers:
        index = text.find(marker)
        if index == -1:
            issues.append((code, marker))
            continue
        if index <= cursor:
            issues.append((code, marker))
        cursor = index
    return issues


def load_required_make_routes(root: Path) -> list[str]:
    policy_path = resolve(root, POLICY)
    payload = json.loads(read_text(policy_path))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid toolchain policy payload in required file: {policy_path}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")
    routes = upgrade_policy.get("required_make_routes")
    if not isinstance(routes, list) or not routes:
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    normalized: list[str] = []
    for route in routes:
        if not isinstance(route, str) or not route.strip():
            raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")
        normalized.append(route.strip())
    return normalized


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).is_file():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow_text = read_text(resolve(root, WORKFLOW))
    for marker in WORKFLOW_RUN_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_RUN_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_RUN_LINE", f"{marker}:count={count}"))
    issues.extend(collect_order_issues(workflow_text, ORDERED_WORKFLOW_LINES, "OUT_OF_ORDER_WORKFLOW_STEP"))
    for marker in REQUIRED_ROUTE_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_REQUIRED_ROUTE_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_REQUIRED_ROUTE_WORKFLOW_LINE", f"{marker}:count={count}"))

    makefile_text = read_text(resolve(root, MAKEFILE))
    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    required_routes = load_required_make_routes(root)
    if required_routes != list(EXPECTED_REQUIRED_ROUTES):
        issues.append(("POLICY_REQUIRED_ROUTES_MISMATCH", ",".join(required_routes)))

    notes_text = read_text(resolve(root, BOOTSTRAP_NOTES))
    issues.extend(collect_missing_markers(notes_text, NOTES_MARKERS, "MISSING_NOTES_MARKER"))

    scripts_readme_text = read_text(resolve(root, SCRIPTS_README))
    issues.extend(
        collect_missing_markers(
            scripts_readme_text,
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKER",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_sample_root(root: Path) -> None:
    write_text(
        resolve(root, WORKFLOW),
        "\n".join(
            (
                "      - name: Run current Phase 2 cross make route",
                "        run: make -C zigux phase2-cross",
                "      - name: Self-test current Phase 2 required-make-routes checker",
                "        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
                "      - name: Check current Phase 2 required-make-routes packet",
                "        run: python3 scripts/zigux/check-phase2-required-make-routes.py",
                "      - name: Self-test current Phase 2 shared reminder checker",
                "        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
                "      - name: Run current Phase 2 toolchain make route",
                "        run: make -C zigux phase2-toolchain",
                "      - name: Run current Phase 2 tools make route",
                "        run: make -C zigux phase2-tools",
                "      - name: Run current Phase 2 validate make route",
                "        run: make -C zigux phase2-validate",
            )
        )
        + "\n",
    )
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, BOOTSTRAP_NOTES),
        "\n".join(
            (
                "`scripts/zigux/check-phase2-required-make-routes.py`",
                "`make -C zigux phase2-tools`",
                "policy note keeps phase2-toolchain, phase2-validate, and phase2-cross as required Linux-style make routes when those routes are rematerialized.",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, SCRIPTS_README),
        "\n".join(
            (
                "`scripts/zigux/check-phase2-required-make-routes.py`",
                "`make -C zigux phase2-tools`",
                "`make -C zigux phase2-validate`",
            )
        )
        + "\n",
    )
    write_text(resolve(root, REQUIRED_ROUTES_CHECKER), "# current required-make-routes checker stub\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_required_make_routes_") as tmp_dir:
        root = Path(tmp_dir)

        write_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_RUN_LINES:
            write_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_RUN_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_RUN_LINES:
            write_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_RUN_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        write_sample_root(root)
        workflow_path = resolve(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(
                workflow_path.read_text(encoding="utf-8"),
                "- name: Self-test current Phase 2 required-make-routes checker",
                "- name: Self-test current Phase 2 shared reminder checker",
            ),
            encoding="utf-8",
        )
        assert ("OUT_OF_ORDER_WORKFLOW_STEP", "- name: Self-test current Phase 2 shared reminder checker") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_ROUTE_WORKFLOW_LINES:
            write_sample_root(root)
            workflow_path = resolve(root, WORKFLOW)
            workflow_path.write_text(
                replace_exact_line(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_REQUIRED_ROUTE_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            write_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            write_sample_root(root)
            makefile_path = resolve(root, MAKEFILE)
            makefile_path.write_text(
                duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        write_sample_root(root)
        policy_path = resolve(root, POLICY)
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_REQUIRED_ROUTES_MISMATCH", "phase2-toolchain,phase2-cross") in collect_issues(root)
        checks_run += 1

        write_sample_root(root)
        notes_path = resolve(root, BOOTSTRAP_NOTES)
        notes_path.write_text("required Linux-style make routes\n", encoding="utf-8")
        assert ("MISSING_NOTES_MARKER", "`scripts/zigux/check-phase2-required-make-routes.py`") in collect_issues(root)
        checks_run += 1

        write_sample_root(root)
        scripts_readme_path = resolve(root, SCRIPTS_README)
        scripts_readme_path.write_text("`scripts/zigux/check-phase2-required-make-routes.py`\n", encoding="utf-8")
        assert ("MISSING_SCRIPTS_README_MARKER", "`make -C zigux phase2-tools`") in collect_issues(root)
        checks_run += 1

        for rel in REQUIRED_PATHS:
            write_sample_root(root)
            resolve(root, rel).unlink()
            try:
                issues = collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                assert ("MISSING_REQUIRED_PATH", rel) in issues
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the bootstrap required-make-routes handoff packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET_WORKFLOW_RUN_LINE_COUNT={len(WORKFLOW_RUN_LINES)}")
    print("PHASE2_BOOTSTRAP_REQUIRED_MAKE_ROUTES_PACKET_REQUIRED_ROUTE_LIST=" + ",".join(EXPECTED_REQUIRED_ROUTES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
