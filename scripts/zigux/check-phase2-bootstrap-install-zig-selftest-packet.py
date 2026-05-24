#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
INSTALL_ZIG = "scripts/zigux/install-zig.py"
BOOTSTRAP_NOTES = "Documentation/zigux/phase2-toolchain-bootstrap-notes.md"
SCRIPTS_README = "scripts/zigux/README.md"
POLICY = "scripts/zigux/zig-toolchain-policy.json"

REQUIRED_PATHS = (
    WORKFLOW,
    MAKEFILE,
    INSTALL_ZIG,
    BOOTSTRAP_NOTES,
    SCRIPTS_README,
    POLICY,
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
)

INSTALL_ZIG_MARKERS = (
    "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "policy_channel = load_policy_channel()",
    "if channel == policy_channel:",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
    "parser.add_argument('--self-test'",
)

BOOTSTRAP_NOTES_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "install-root replay path explicit",
)

SCRIPTS_README_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "installer and direct cross-route surfaces explicit",
)


def resolve(root: Path, rel: str) -> Path:
    return root / rel


def read_text(root: Path, rel: str) -> str:
    path = resolve(root, rel)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = resolve(root, rel)
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


def swap_exact_lines(text: str, first: str, second: str) -> str:
    lines = text.splitlines()
    first_index = None
    second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first and first_index is None:
            first_index = index
        if stripped == second and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError("swap markers not found")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def remove_once(text: str, marker: str) -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, "", 1)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(text: str, markers: tuple[str, ...], missing: str, duplicate: str) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing, marker))
        elif count != 1:
            issues.append((duplicate, f"{marker}:count={count}"))
    return issues


def ensure_order(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    positions: list[int] = []
    for marker in markers:
        position = text.find(marker)
        if position == -1:
            return []
        positions.append(position)
    if positions != sorted(positions):
        return [(code, " -> ".join(markers))]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    workflow = read_text(root, WORKFLOW)
    makefile = read_text(root, MAKEFILE)
    install_zig = read_text(root, INSTALL_ZIG)
    bootstrap_notes = read_text(root, BOOTSTRAP_NOTES)
    scripts_readme = read_text(root, SCRIPTS_README)

    issues.extend(
        collect_exact_line_issues(
            workflow,
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            makefile,
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    issues.extend(ensure_order(workflow, WORKFLOW_LINES, "MISORDERED_WORKFLOW_PACKET"))
    issues.extend(ensure_order(makefile, MAKEFILE_LINES[1:], "MISORDERED_MAKEFILE_PACKET"))
    issues.extend(collect_missing_markers(install_zig, INSTALL_ZIG_MARKERS, "MISSING_INSTALL_ZIG_MARKER"))
    issues.extend(
        collect_missing_markers(
            bootstrap_notes,
            BOOTSTRAP_NOTES_MARKERS,
            "MISSING_BOOTSTRAP_NOTES_MARKER",
        )
    )
    issues.extend(
        collect_missing_markers(
            scripts_readme,
            SCRIPTS_README_MARKERS,
            "MISSING_SCRIPTS_README_MARKER",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                *WORKFLOW_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                *MAKEFILE_LINES,
            )
        )
        + "\n",
    )
    write_text(
        root,
        INSTALL_ZIG,
        "\n".join(
            (
                "#!/usr/bin/env python3",
                *INSTALL_ZIG_MARKERS,
            )
        )
        + "\n",
    )
    write_text(
        root,
        BOOTSTRAP_NOTES,
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                *BOOTSTRAP_NOTES_MARKERS,
            )
        )
        + "\n",
    )
    write_text(
        root,
        SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                *SCRIPTS_README_MARKERS,
            )
        )
        + "\n",
    )
    write_text(
        root,
        POLICY,
        "{\n"
        '  "phase": "Phase 2",\n'
        '  "channel": "0.17.0-dev.87+9b177a7d2"\n'
        "}\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_install_zig_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[2], "run: python3 other.py --self-test"))
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[2]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[2]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), WORKFLOW_LINES[2], WORKFLOW_LINES[3]))
        assert any(code == "MISORDERED_WORKFLOW_PACKET" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[3], "$(PYTHON) other.py"))
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[3]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), MAKEFILE_LINES[3]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[3]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, swap_exact_lines(read_text(root, MAKEFILE), MAKEFILE_LINES[3], MAKEFILE_LINES[4]))
        assert any(code == "MISORDERED_MAKEFILE_PACKET" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        write_text(root, INSTALL_ZIG, remove_once(read_text(root, INSTALL_ZIG), INSTALL_ZIG_MARKERS[4]))
        assert ("MISSING_INSTALL_ZIG_MARKER", INSTALL_ZIG_MARKERS[4]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, BOOTSTRAP_NOTES, remove_once(read_text(root, BOOTSTRAP_NOTES), BOOTSTRAP_NOTES_MARKERS[1]))
        assert ("MISSING_BOOTSTRAP_NOTES_MARKER", BOOTSTRAP_NOTES_MARKERS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, SCRIPTS_README, remove_once(read_text(root, SCRIPTS_README), SCRIPTS_README_MARKERS[2]))
        assert ("MISSING_SCRIPTS_README_MARKER", SCRIPTS_README_MARKERS[2]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        resolve(root, POLICY).unlink()
        assert ("MISSING_REQUIRED_PATH", POLICY) in collect_issues(root)
        checks += 1

    print("PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the bootstrap install-zig self-test helper packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a focused current-like sample root for manual replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET=pass")
    print(f"PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_BOOTSTRAP_INSTALL_ZIG_SELFTEST_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES) - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
