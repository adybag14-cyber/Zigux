#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
README = "scripts/zigux/README.md"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    README,
    WORKFLOW,
    MAKEFILE,
    POLICY,
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
)

README_REQUIRED_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2-cross`",
)

WORKFLOW_REQUIRED_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
)

MAKEFILE_REQUIRED_HEADERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-cross:",
    "phase2-validate:",
)

EXPECTED_POLICY_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-validate",
    "phase2-cross",
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


def count_occurrences(text: str, marker: str) -> int:
    return text.count(marker)


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    readme_text = read_text(root, README)
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)
    policy_text = read_text(root, POLICY)

    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
        return issues

    required_make_routes = policy.get("upgrade_policy", {}).get("required_make_routes")
    if required_make_routes != list(EXPECTED_POLICY_ROUTES):
        issues.append(
            (
                "POLICY_ROUTE_MISMATCH",
                ",".join(required_make_routes) if isinstance(required_make_routes, list) else repr(required_make_routes),
            )
        )

    for marker in README_REQUIRED_MARKERS:
        count = count_occurrences(readme_text, marker)
        if count == 0:
            issues.append(("MISSING_README_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_README_MARKER", f"{marker}:count={count}"))

    for line in WORKFLOW_REQUIRED_LINES:
        count = sum(1 for workflow_line in workflow_text.splitlines() if workflow_line.strip() == line)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", line))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{line}:count={count}"))

    for header in MAKEFILE_REQUIRED_HEADERS:
        count = sum(1 for make_line in makefile_text.splitlines() if make_line.startswith(header))
        if count == 0:
            issues.append(("MISSING_MAKEFILE_HEADER", header))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_HEADER", f"{header}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_PHASE2_TOOLCHAIN_README=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        if rel in {README, WORKFLOW, MAKEFILE, POLICY}:
            continue
        write_text(root, rel, "present\n")

    write_text(
        root,
        README,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "## Phase 2",
                "",
                "- current toolchain packet keeps "
                + ", ".join(README_REQUIRED_MARKERS[:5])
                + " explicit beside "
                + ", ".join(README_REQUIRED_MARKERS[5:]),
            )
        )
        + "\n",
    )
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Zig toolchain checker",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
                "      - name: Check current Zig toolchain policy packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "      - name: Check current pinned Zig archive packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "      - name: Run current Phase 2 toolchain make route",
                "        run: make -C zigux phase2-toolchain",
                "      - name: Run current Phase 2 tools make route",
                "        run: make -C zigux phase2-tools",
                "      - name: Run current Phase 2 cross make route",
                "        run: make -C zigux phase2-cross",
                "      - name: Run current Phase 2 validate make route",
                "        run: make -C zigux phase2-validate",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "phase2-toolchain:",
                "\t@true",
                "",
                "phase2-tools:",
                "\t@true",
                "",
                "phase2-cross:",
                "\t@true",
                "",
                "phase2-validate:",
                "\t@true",
            )
        )
        + "\n",
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_POLICY_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="zigux_lane03_phase2_toolchain_readme_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            README,
            replace_once(
                read_text(root, README),
                "`make -C zigux phase2-tools`",
                "`make -C zigux phase2-tools-missing`",
            ),
        )
        assert ("MISSING_README_MARKER", "`make -C zigux phase2-tools`") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            README,
            read_text(root, README) + "\n`make -C zigux phase2-tools`\n",
        )
        assert (
            "DUPLICATE_README_MARKER",
            "`make -C zigux phase2-tools`:count=2",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_once(
                read_text(root, WORKFLOW),
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only-missing",
            ),
        )
        assert (
            "MISSING_WORKFLOW_LINE",
            "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["required_make_routes"] = [
            "phase2-toolchain",
            "phase2-validate",
            "phase2-cross",
        ]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert (
            "POLICY_ROUTE_MISMATCH",
            "phase2-toolchain,phase2-validate,phase2-cross",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_once(read_text(root, MAKEFILE), "phase2-tools:", "phase2-tools-disabled:"),
        )
        assert ("MISSING_MAKEFILE_HEADER", "phase2-tools:") in collect_issues(root)
        checks += 1

    print("LANE03_PHASE2_TOOLCHAIN_README_SELF_TEST=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_README_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 2 toolchain reminder packet from the Lane 03 scripts root."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a focused current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("LANE03_PHASE2_TOOLCHAIN_README_SAMPLE_ROOT=pass")
        print(f"LANE03_PHASE2_TOOLCHAIN_README_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PHASE2_TOOLCHAIN_README=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_README_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_PHASE2_TOOLCHAIN_README_MARKER_COUNT={len(README_REQUIRED_MARKERS)}")
    print(f"LANE03_PHASE2_TOOLCHAIN_README_WORKFLOW_LINE_COUNT={len(WORKFLOW_REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
