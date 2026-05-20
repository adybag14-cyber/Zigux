#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"

DOCS_README_MARKERS = (
    "Phase 2 notes",
    "`Documentation/zigux/phase2-closure.md`",
    "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "selected kconfig bridge helpers",
    "the current docs-root Phase 2 reminder packet should stay parked on",
    "the current kconfig bridge manifests",
    "`make -C zigux phase2-kconfig`",
)

DOCS_README_FORBIDDEN_MARKERS = (
    "repeated authenticated reads on current `master` still return missing for `scripts/zigux/check-kconfig-bridge.py`",
    "repeated authenticated reads on current `master` still return missing for `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "repeated authenticated reads on current `master` still return missing for `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "repeated authenticated reads on current `master` still return missing for `zigux/tests/fixtures/kconfig_bridge/cases.json`",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_forbidden_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker in text]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    text = read_text(resolve_path(root, DOCS_README))
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            text,
            DOCS_README_MARKERS,
            "MISSING_DOCS_README_MARKERS",
        )
    )
    issues.extend(
        collect_forbidden_markers(
            text,
            DOCS_README_FORBIDDEN_MARKERS,
            "FORBIDDEN_DOCS_README_MARKERS",
        )
    )
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_DOCS_README_KCONFIG_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, DOCS_README), "\n".join(DOCS_README_MARKERS) + "\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 1 + len(DOCS_README_MARKERS) + len(DOCS_README_FORBIDDEN_MARKERS) + 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_docs_readme_kconfig_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in DOCS_README_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            issues = collect_issues(root)
            assert ("MISSING_DOCS_README_MARKERS", marker) in issues
            checks_run += 1

        for marker in DOCS_README_FORBIDDEN_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, DOCS_README)
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            issues = collect_issues(root)
            assert ("FORBIDDEN_DOCS_README_MARKERS", marker) in issues
            checks_run += 1

        build_self_test_root(root)
        resolve_path(root, DOCS_README).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            assert str(resolve_path(root, DOCS_README)) in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing docs README did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_DOCS_README_KCONFIG_PACKET_SELF_TEST=pass")
    print(f"PHASE2_DOCS_README_KCONFIG_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 docs-root kconfig bridge packet explicit in Documentation/zigux/README.md."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_DOCS_README_KCONFIG_PACKET=pass")
    print(f"PHASE2_DOCS_README_KCONFIG_PACKET_MARKER_COUNT={len(DOCS_README_MARKERS)}")
    print(
        "PHASE2_DOCS_README_KCONFIG_PACKET_FORBIDDEN_MARKER_COUNT="
        f"{len(DOCS_README_FORBIDDEN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
