#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/install-zig.py",
    POLICY,
    "third_party/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    WORKFLOW,
)

NOTES_MARKERS = (
    "`scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download, SHA-256 verification, and install-root replay path explicit beside the reminder guards.",
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`third_party/README.md` is directly readable on current `master` and keeps the repo-local pinned archive filename, digest, size, duplicate-copy boundary, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` replay contract explicit beside the policy-driven toolchain packet.",
)

CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 2 toolchain packet",
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
)

SCRIPTS_README_MARKERS = (
    "- `check-zig-toolchain.py` verifies that the selected Zig binary exists and satisfies the configured minimum version.",
    "- `check-zig-toolchain.py --self-test` runs built-in parser and version-ordering coverage without needing a local Zig install.",
    "- `check-zig-toolchain.py`, `install-zig.py`, `validate-phase2.py`, `validate-phase2-closure.py`, `check-phase2-toolchain-pin-scope.py`",
)

TESTS_README_MARKERS = (
    "Keep the current toolchain self-check and replay surface explicit through `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`, `python3 scripts/zigux/install-zig.py --self-test`, and `python3 scripts/zigux/check-phase2-cross.py --self-test`.",
    "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and the local-first `third_party`, mirror, then direct-download bootstrap order reused by `.github/workflows/zigux-bootstrap.yml` and the two Lane 05 archive checkers",
)

THIRD_PARTY_MARKERS = (
    "- target: `x86_64-linux`",
    "- channel: `0.17.0-dev.87+9b177a7d2`",
    "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/install-zig.py --self-test",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def maybe_read_text(root: Path, rel: str) -> str:
    path = root / rel
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.rstrip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.rstrip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    notes = maybe_read_text(root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
    checklist = maybe_read_text(root, "Documentation/zigux/review-checklist.md")
    scripts_readme = maybe_read_text(root, "scripts/zigux/README.md")
    tests_readme = maybe_read_text(root, "zigux/tests/README.md")
    third_party = maybe_read_text(root, "third_party/README.md")
    workflow = maybe_read_text(root, WORKFLOW)
    makefile = maybe_read_text(root, "zigux/Makefile")

    policy_path = root / POLICY
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
        payload = None

    if payload is not None:
        channel = payload.get("channel")
        minimum_version = payload.get("minimum_version")
        archive_sha256 = payload.get("archive_sha256")
        upgrade_policy = payload.get("upgrade_policy")
        if channel != "0.17.0-dev.87+9b177a7d2":
            issues.append(("UNEXPECTED_POLICY_CHANNEL", str(channel)))
        if minimum_version != "0.17.0-dev.87+9b177a7d2":
            issues.append(("UNEXPECTED_POLICY_MIN_VERSION", str(minimum_version)))
        if not isinstance(archive_sha256, dict) or archive_sha256.get("x86_64-linux") != "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77":
            issues.append(("UNEXPECTED_POLICY_ARCHIVE_SHA", "x86_64-linux"))
        if not isinstance(upgrade_policy, dict) or upgrade_policy.get("archive_target_scope") != ["x86_64-linux"]:
            issues.append(("UNEXPECTED_POLICY_ARCHIVE_SCOPE", str(None if not isinstance(upgrade_policy, dict) else upgrade_policy.get("archive_target_scope"))))
        if not isinstance(upgrade_policy, dict) or upgrade_policy.get("required_make_routes") != [
            "phase2-toolchain",
            "phase2-validate",
            "phase2-cross",
        ]:
            issues.append(("UNEXPECTED_POLICY_REQUIRED_ROUTES", str(None if not isinstance(upgrade_policy, dict) else upgrade_policy.get("required_make_routes"))))

    for marker in NOTES_MARKERS:
        if marker not in notes:
            issues.append(("MISSING_NOTES_MARKER", marker))
    for marker in CHECKLIST_MARKERS:
        if marker not in checklist:
            issues.append(("MISSING_CHECKLIST_MARKER", marker))
    for marker in SCRIPTS_README_MARKERS:
        if marker not in scripts_readme:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))
    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme:
            issues.append(("MISSING_TESTS_README_MARKER", marker))
    for marker in THIRD_PARTY_MARKERS:
        if marker not in third_party:
            issues.append(("MISSING_THIRD_PARTY_MARKER", marker))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_PINNED_TOOLCHAIN_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.",
                "",
                "## Current direct packet",
                "",
                NOTES_MARKERS[0],
                NOTES_MARKERS[1],
                NOTES_MARKERS[2],
            )
        )
        + "\n",
    )
    write_text(
        root,
        "Documentation/zigux/review-checklist.md",
        "\n".join(
            (
                "# Zigux Review Checklist",
                "",
                "## Validation",
                "",
                "  * if the change touches the shared Phase 2 toolchain packet, do "
                + ", ".join(CHECKLIST_MARKERS[1:]),
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
                SCRIPTS_README_MARKERS[0],
                SCRIPTS_README_MARKERS[1],
                SCRIPTS_README_MARKERS[2],
            )
        )
        + "\n",
    )
    write_text(root, "scripts/zigux/check-zig-toolchain.py", "present\n")
    write_text(root, "scripts/zigux/install-zig.py", "present\n")
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
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root,
        "third_party/README.md",
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                "## Current pinned Zig archive contract",
                "",
                *THIRD_PARTY_MARKERS,
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux/tests/README.md",
        "\n".join(
            (
                "# zigux/tests",
                "",
                "## Phase 2 review packet",
                "",
                TESTS_README_MARKERS[0],
                "",
                TESTS_README_MARKERS[1],
            )
        )
        + "\n",
    )
    write_text(
        root,
        "zigux/Makefile",
        "\n".join(
            (
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                *MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_pinned_toolchain_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            read_text(root, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md").replace(NOTES_MARKERS[2] + "\n", "", 1),
        )
        assert ("MISSING_NOTES_MARKER", NOTES_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            "Documentation/zigux/review-checklist.md",
            read_text(root, "Documentation/zigux/review-checklist.md").replace("`python3 scripts/zigux/install-zig.py --self-test`", "`python3 scripts/zigux/install-zig.py`", 1),
        )
        assert ("MISSING_CHECKLIST_MARKER", "`python3 scripts/zigux/install-zig.py --self-test`") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
                "run: python3 scripts/zigux/check-zig-toolchain.py",
            ),
        )
        assert ("MISSING_WORKFLOW_LINE", "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            "zigux/Makefile",
            replace_exact_line(
                read_text(root, "zigux/Makefile"),
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only",
            ),
        )
        assert (
            "MISSING_MAKEFILE_LINE",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            POLICY,
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": "0.17.0-dev.87+9b177a7d2",
                    "minimum_version": "0.17.0-dev.87+9b177a7d2",
                    "archive_sha256": {"x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": True,
                        "archive_target_scope": ["x86_64-linux"],
                        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                    },
                },
                indent=2,
            )
            + "\n",
        )
        assert ("UNEXPECTED_POLICY_REQUIRED_ROUTES", "['phase2-toolchain', 'phase2-validate']") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        (root / "third_party/README.md").unlink()
        assert ("MISSING_REQUIRED_PATH", "third_party/README.md") in collect_issues(root)
        checks += 1

    print("PHASE2_PINNED_TOOLCHAIN_PACKET_SELF_TEST=pass")
    print(f"PHASE2_PINNED_TOOLCHAIN_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current pinned Phase 2 Zig toolchain packet stays explicit across docs, scripts, tests, workflow, and Makefile surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in packet checks")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing current-like sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_PINNED_TOOLCHAIN_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_PINNED_TOOLCHAIN_PACKET=pass")
    print(f"PHASE2_PINNED_TOOLCHAIN_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_PINNED_TOOLCHAIN_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_PINNED_TOOLCHAIN_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
