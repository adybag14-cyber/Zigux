#!/usr/bin/env python3
"""Check that the Phase 2 scripts README keeps the live toolchain action path explicit."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

SCRIPTS_README = "scripts/zigux/README.md"
REQUIRED_PATHS = (
    ".github/workflows/zigux-bootstrap.yml",
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/install-zig.py",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)

PHASE2_ANCHOR = (
    "Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker"
)
ACTION_PATH_PREFIX = "- `.github/workflows/zigux-bootstrap.yml`"
ACTION_PATH_MARKERS = (
    "`.github/workflows/zigux-bootstrap.yml`",
    "`python3 scripts/zigux/check-zig-toolchain.py --self-test`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path",
)
CHECKER_LIST_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py`",
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _find_action_path_line(readme: str) -> str | None:
    for line in readme.splitlines():
        if line.startswith(ACTION_PATH_PREFIX):
            return line
    return None


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / SCRIPTS_README
    if not readme_path.is_file():
        return [f"missing_file:{SCRIPTS_README}"]

    readme = _read(readme_path)
    if PHASE2_ANCHOR not in readme:
        errors.append("missing_marker:scripts_readme:phase2_anchor")

    for marker in CHECKER_LIST_MARKERS:
        if marker not in readme:
            errors.append(f"missing_marker:scripts_readme:checker_list:{marker}")

    action_path_line = _find_action_path_line(readme)
    if action_path_line is None:
        errors.append("missing_marker:scripts_readme:action_path_line")
    else:
        for marker in ACTION_PATH_MARKERS:
            if marker not in action_path_line:
                errors.append(f"missing_marker:scripts_readme:action_path:{marker}")

    for rel in REQUIRED_PATHS:
        if not (root / rel).is_file():
            errors.append(f"missing_file:{rel}")

    return errors


def write_sample_root(root: Path) -> None:
    readme = (
        "# scripts/zigux\n\n"
        "## Phase 2\n\n"
        "- Phase 2 flow - the current scripts-root bridge packet stays reviewable through the live toolchain checker, installer helper, direct cross-route packet, `conf_bridge` and `confdata_bridge` helper surfaces, the restored closure-side validator packet, the manifest-backed kconfig fixture roster, the shipped make-wrapper packet, and the surviving Phase 2 alignment guards instead of replaying older missing-route assumptions inside that now-rematerialized toolchain packet\n"
        "- `scripts/zigux/check-zig-toolchain.py`, `scripts/zigux/check-phase2-kbuild-routes.py`, `scripts/zigux/check-phase2-cross.py`, and `scripts/zigux/check-phase2-toolchain-pinning.py` remain the shipped Phase 2 toolchain, reminder, alignment, artifact-support, fixdep, genksyms-bridge, and required-make-route guards that survive on current `master`\n"
        "- `.github/workflows/zigux-bootstrap.yml`, `python3 scripts/zigux/check-zig-toolchain.py --self-test`, `python3 scripts/zigux/check-zig-toolchain.py --policy-only`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing` keep the shipped pinned Zig toolchain guard explicit in the live bootstrap action path before the surviving Phase 2 bridge and pinning checks\n"
    )
    _write(root / SCRIPTS_README, readme)
    for rel in REQUIRED_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2-scripts-action-path-") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)
        assert validate(root) == []
        case_count += 1

        _write(root / SCRIPTS_README, "# scripts/zigux\n")
        errors = validate(root)
        assert "missing_marker:scripts_readme:phase2_anchor" in errors
        assert "missing_marker:scripts_readme:action_path_line" in errors
        case_count += 1

        for marker in ACTION_PATH_MARKERS:
            write_sample_root(root)
            path = root / SCRIPTS_README
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            errors = validate(root)
            if marker == ACTION_PATH_MARKERS[0]:
                assert "missing_marker:scripts_readme:action_path_line" in errors
            else:
                assert f"missing_marker:scripts_readme:action_path:{marker}" in errors
            case_count += 1

        for marker in CHECKER_LIST_MARKERS:
            write_sample_root(root)
            path = root / SCRIPTS_README
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            errors = validate(root)
            assert f"missing_marker:scripts_readme:checker_list:{marker}" in errors
            case_count += 1

        for rel in REQUIRED_PATHS:
            write_sample_root(root)
            (root / rel).unlink()
            errors = validate(root)
            assert f"missing_file:{rel}" in errors
            case_count += 1

    print("PHASE2_SCRIPTS_ACTION_PATH_SELF_TEST=pass")
    print(f"PHASE2_SCRIPTS_ACTION_PATH_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 scripts README keeps the live toolchain action path explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    errors = validate(args.root)
    if errors:
        print("PHASE2_SCRIPTS_ACTION_PATH=fail")
        print("PHASE2_SCRIPTS_ACTION_PATH_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE2_SCRIPTS_ACTION_PATH_ISSUES_END")
        return 1

    print("PHASE2_SCRIPTS_ACTION_PATH=pass")
    print(f"PHASE2_SCRIPTS_ACTION_PATH_MARKER_COUNT={len(ACTION_PATH_MARKERS) + len(CHECKER_LIST_MARKERS) + 1}")
    print(f"PHASE2_SCRIPTS_ACTION_PATH_REQUIRED_FILE_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
