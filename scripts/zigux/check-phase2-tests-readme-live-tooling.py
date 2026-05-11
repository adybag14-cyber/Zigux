#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_MARKERS = (
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-kconfig-readme-alignment.py",
    "scripts/zigux/check-phase2-tool-manifest-packets.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "zig test scripts/zigux/fixdep.zig",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
)

FORBIDDEN_LIVE_TOOL_PATHS = (
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/mk_elfconfig.zig",
)

FORBIDDEN_README_MARKERS = (
    "scripts/zigux/check-phase2-genksyms-bridge-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "scripts/zigux/check-mk-elfconfig-diff.py",
    "zig test scripts/zigux/genksyms.zig",
    "zig test scripts/zigux/genksyms_crc.zig",
    "zig test scripts/zigux/kconfig/conf_bridge.zig",
    "zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "zig test scripts/zigux/mk_elfconfig.zig",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path, readme_rel_path: str) -> list[str]:
    issues: list[str] = []
    readme_path = root / readme_rel_path
    if not readme_path.is_file():
        return [f"missing_file:{readme_rel_path}"]

    readme_text = read_text(readme_path)
    for marker in REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing_required_marker:{marker}")

    for marker in FORBIDDEN_README_MARKERS:
        count = readme_text.count(marker)
        if count != 0:
            issues.append(f"forbidden_readme_marker:{marker}:count={count}:expected=0")

    for rel_path in FORBIDDEN_LIVE_TOOL_PATHS:
        if (root / rel_path).exists():
            issues.append(f"unexpected_live_tool:{rel_path}")

    return issues


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "zigux-tests-README.md",
        "\n".join(REQUIRED_MARKERS) + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_tests_readme_live_tooling_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root, "zigux-tests-README.md") == []
        case_count += 1

        build_self_test_root(root)
        readme_path = root / "zigux-tests-README.md"
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8").replace(REQUIRED_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        issues = collect_issues(root, "zigux-tests-README.md")
        assert f"missing_required_marker:{REQUIRED_MARKERS[0]}" in issues
        case_count += 1

        build_self_test_root(root)
        readme_path = root / "zigux-tests-README.md"
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8") + FORBIDDEN_README_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        issues = collect_issues(root, "zigux-tests-README.md")
        assert (
            f"forbidden_readme_marker:{FORBIDDEN_README_MARKERS[0]}:count=1:expected=0" in issues
        )
        case_count += 1

        build_self_test_root(root)
        write_text(root / FORBIDDEN_LIVE_TOOL_PATHS[0], "placeholder\n")
        issues = collect_issues(root, "zigux-tests-README.md")
        assert f"unexpected_live_tool:{FORBIDDEN_LIVE_TOOL_PATHS[0]}" in issues
        case_count += 1

        issues = collect_issues(root, "missing.md")
        assert "missing_file:missing.md" in issues
        case_count += 1

    print("PHASE2_TESTS_README_LIVE_TOOLING_SELF_TEST=pass")
    print(f"PHASE2_TESTS_README_LIVE_TOOLING_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 2 tests-root reminder stays anchored to the live "
            "current-master toolchain packet instead of naming missing direct bridge tooling."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--readme-rel-path",
        default="zigux/tests/README.md",
        help="Tests-root README path relative to --root",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root, args.readme_rel_path)
    if issues:
        print("PHASE2_TESTS_README_LIVE_TOOLING=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_TESTS_README_LIVE_TOOLING=pass")
    print(f"PHASE2_TESTS_README_LIVE_TOOLING_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(f"PHASE2_TESTS_README_LIVE_TOOLING_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_README_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
