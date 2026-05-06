#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "scripts/zigux/install-zig.py",
    ".github/workflows/zigux-bootstrap.yml",
]

DOCS_ROOT_MARKERS = [
    "`scripts/zigux/install-zig.py`",
    "workflow-viability installer",
]

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the closed Phase 1 host-tools packet",
    "`scripts/zigux/install-zig.py`",
]

CLOSURE_MARKERS = [
    "- `scripts/zigux/install-zig.py`",
    "Zig installation through an in-repo official-download step instead of a Node 20-bound action",
]

SCRIPTS_README_MARKERS = [
    "- `install-zig.py`",
]

WORKFLOW_MARKERS = [
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain",
]

INSTALLER_MARKERS = [
    "def run_self_test() -> int:",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
    "print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=13')",
]


def repo_root_from_arg(root_arg: str | None) -> Path:
    if root_arg is None:
        return DEFAULT_ROOT
    return Path(root_arg).resolve()


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def collect_presence_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        actual = text.count(marker)
        if actual < 1:
            missing.append(f"{label}:{marker}:expected>=1:actual={actual}")
    return missing


def collect_exact_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        actual = text.count(marker)
        if actual != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={actual}")
    return missing


def collect_missing_markers(root: Path) -> list[str]:
    docs_root = (root / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
    review_checklist = (root / "Documentation" / "zigux" / "review-checklist.md").read_text(
        encoding="utf-8"
    )
    closure = (root / "Documentation" / "zigux" / "phase1-closure.md").read_text(encoding="utf-8")
    scripts_readme = (root / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
    installer = (root / "scripts" / "zigux" / "install-zig.py").read_text(encoding="utf-8")

    missing: list[str] = []
    missing.extend(collect_presence_markers(docs_root, "docs_root", DOCS_ROOT_MARKERS))
    missing.extend(
        collect_presence_markers(review_checklist, "review_checklist", REVIEW_CHECKLIST_MARKERS)
    )
    missing.extend(collect_presence_markers(closure, "closure", CLOSURE_MARKERS))
    missing.extend(collect_presence_markers(scripts_readme, "scripts_readme", SCRIPTS_README_MARKERS))
    missing.extend(collect_exact_markers(workflow, "workflow", WORKFLOW_MARKERS))
    missing.extend(collect_presence_markers(installer, "installer", INSTALLER_MARKERS))
    return missing


def make_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")

    (tmp_root / "Documentation" / "zigux" / "README.md").write_text(
        "\n".join(DOCS_ROOT_MARKERS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / "Documentation" / "zigux" / "review-checklist.md").write_text(
        "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / "Documentation" / "zigux" / "phase1-closure.md").write_text(
        "\n".join(CLOSURE_MARKERS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / "scripts" / "zigux" / "README.md").write_text(
        "\n".join(SCRIPTS_README_MARKERS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml").write_text(
        "\n".join(WORKFLOW_MARKERS) + "\n",
        encoding="utf-8",
    )
    (tmp_root / "scripts" / "zigux" / "install-zig.py").write_text(
        "\n".join(INSTALLER_MARKERS) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_install_zig_surface_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)

        make_fixture_root(tmp_root)
        assert collect_missing_files(tmp_root) == []
        assert collect_missing_markers(tmp_root) == []

        docs_path = tmp_root / "Documentation" / "zigux" / "README.md"
        docs_path.write_text("`scripts/zigux/install-zig.py`\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "docs_root:workflow-viability installer:expected>=1:actual=0" in missing

        make_fixture_root(tmp_root)
        checklist_path = tmp_root / "Documentation" / "zigux" / "review-checklist.md"
        checklist_path.write_text("if the change touches the closed Phase 1 host-tools packet\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "review_checklist:`scripts/zigux/install-zig.py`:expected>=1:actual=0" in missing

        make_fixture_root(tmp_root)
        closure_path = tmp_root / "Documentation" / "zigux" / "phase1-closure.md"
        closure_path.write_text("- `scripts/zigux/install-zig.py`\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert (
            "closure:Zig installation through an in-repo official-download step instead of a Node 20-bound action:expected>=1:actual=0"
            in missing
        )

        make_fixture_root(tmp_root)
        workflow_path = tmp_root / ".github" / "workflows" / "zigux-bootstrap.yml"
        workflow_path.write_text("\n".join(WORKFLOW_MARKERS[:-1]) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert (
            "workflow:run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain:expected=1:actual=0"
            in missing
        )

        make_fixture_root(tmp_root)
        workflow_path.write_text("\n".join(WORKFLOW_MARKERS + [WORKFLOW_MARKERS[1]]) + "\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert (
            "workflow:run: python3 scripts/zigux/install-zig.py --channel 0.17.0-dev.87+9b177a7d2 --dest .zig-toolchain:expected=1:actual=2"
            in missing
        )

        make_fixture_root(tmp_root)
        installer_path = tmp_root / "scripts" / "zigux" / "install-zig.py"
        installer_path.write_text("def run_self_test() -> int:\n", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "installer:print('ZIG_INSTALL_SELF_TEST=pass'):expected>=1:actual=0" in missing

        make_fixture_root(tmp_root)
        scripts_path = tmp_root / "scripts" / "zigux" / "README.md"
        scripts_path.write_text("", encoding="utf-8")
        missing = collect_missing_markers(tmp_root)
        assert "scripts_readme:- `install-zig.py`:expected>=1:actual=0" in missing

        make_fixture_root(tmp_root)
        missing_file = tmp_root / "scripts" / "zigux" / "install-zig.py"
        missing_file.unlink()
        assert collect_missing_files(tmp_root) == ["scripts/zigux/install-zig.py"]

    print("PHASE1_INSTALL_ZIG_SURFACE_SELF_TEST=pass")
    print("PHASE1_INSTALL_ZIG_SURFACE_SELF_TEST_CASE_COUNT=8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shipped Phase 1 install-zig review surface."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root_from_arg(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_INSTALL_ZIG_SURFACE=fail")
        print("MISSING_PHASE1_INSTALL_ZIG_SURFACE_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_INSTALL_ZIG_SURFACE_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_INSTALL_ZIG_SURFACE=fail")
        print("MISSING_PHASE1_INSTALL_ZIG_SURFACE_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_INSTALL_ZIG_SURFACE_MARKERS_END")
        return 1

    print("PHASE1_INSTALL_ZIG_SURFACE=pass")
    print(f"PHASE1_INSTALL_ZIG_SURFACE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_INSTALL_ZIG_SURFACE_REQUIRED_MARKER_COUNT="
        f"{len(DOCS_ROOT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(CLOSURE_MARKERS) + len(SCRIPTS_README_MARKERS) + len(WORKFLOW_MARKERS) + len(INSTALLER_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
