#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
DOCS_README = Path("Documentation/zigux/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
SURVEY_DOC = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
SURVEY_CHECKER = "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json_dict(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    docs_readme_text = read_text(root / DOCS_README)
    scripts_readme_text = read_text(root / SCRIPTS_README)
    tests_readme_text = read_text(root / TESTS_README)
    phase2_tool_manifest = read_json_dict(root / PHASE2_TOOL_MANIFEST)
    read_text(root / SURVEY_DOC)
    read_text(root / SURVEY_CHECKER)

    issues: list[tuple[str, str]] = []

    survey_doc_marker = f"`{SURVEY_DOC.as_posix()}`"
    survey_checker_marker = f"`{SURVEY_CHECKER}`"

    for code, text in (
        ("MISSING_DOCS_README_MARKER", docs_readme_text),
        ("MISSING_SCRIPTS_README_MARKER", scripts_readme_text),
        ("MISSING_TESTS_README_MARKER", tests_readme_text),
    ):
        if survey_doc_marker not in text:
            issues.append((code, SURVEY_DOC.as_posix()))
        if survey_checker_marker not in text:
            issues.append((code, SURVEY_CHECKER))

    notes = phase2_tool_manifest.get("notes")
    if not isinstance(notes, list) or not all(isinstance(item, str) for item in notes):
        raise SystemExit(f"invalid notes in required file: {root / PHASE2_TOOL_MANIFEST}")
    if not any("dedicated genksyms dual-implementation survey guard" in note for note in notes):
        issues.append(("MISSING_TOOL_MANIFEST_NOTE", "dedicated genksyms dual-implementation survey guard"))

    surfaces = phase2_tool_manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        raise SystemExit(f"invalid present_surfaces in required file: {root / PHASE2_TOOL_MANIFEST}")
    checkers = surfaces.get("checkers")
    if not isinstance(checkers, list) or not all(isinstance(item, str) for item in checkers):
        raise SystemExit(f"invalid checkers in required file: {root / PHASE2_TOOL_MANIFEST}")
    if SURVEY_CHECKER not in checkers:
        issues.append(("MISSING_TOOL_MANIFEST_CHECKER", SURVEY_CHECKER))
    elif checkers.count(SURVEY_CHECKER) != 1:
        issues.append(("DUPLICATE_TOOL_MANIFEST_CHECKER", SURVEY_CHECKER))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_SURVEY_REMINDER_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / DOCS_README,
        "\n".join(
            (
                "# docs",
                "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
                "",
            )
        ),
    )
    write_text(
        root / SCRIPTS_README,
        "\n".join(
            (
                "# scripts",
                "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
                "",
            )
        ),
    )
    write_text(
        root / TESTS_README,
        "\n".join(
            (
                "# tests",
                "- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
                "",
            )
        ),
    )
    write_text(
        root / PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "notes": [
                    "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker."
                ],
                "present_surfaces": {
                    "checkers": [
                        "scripts/zigux/check-phase2-tool-manifest.py",
                        "scripts/zigux/check-genksyms-bridge.py",
                    ]
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / SURVEY_DOC, "# survey\n")
    write_text(root / SURVEY_CHECKER, "#!/usr/bin/env python3\n")


def build_passing_root(root: Path) -> None:
    lines = (
        f"- `{SURVEY_DOC.as_posix()}`",
        f"- `{SURVEY_CHECKER}`",
    )
    write_text(root / DOCS_README, "# docs\n" + "\n".join(lines) + "\n")
    write_text(root / SCRIPTS_README, "# scripts\n" + "\n".join(lines) + "\n")
    write_text(root / TESTS_README, "# tests\n" + "\n".join(lines) + "\n")
    write_text(
        root / PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "notes": [
                    "Keep the dedicated genksyms dual-implementation survey guard explicit beside the shared Phase 2 closure packet."
                ],
                "present_surfaces": {
                    "checkers": [
                        "scripts/zigux/check-phase2-tool-manifest.py",
                        "scripts/zigux/check-genksyms-bridge.py",
                        SURVEY_CHECKER,
                    ]
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / SURVEY_DOC, "# survey\n")
    write_text(root / SURVEY_CHECKER, "#!/usr/bin/env python3\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_survey_reminder_") as tmp_dir:
        root = Path(tmp_dir)

        build_passing_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        issues = collect_issues(root)
        assert ("MISSING_DOCS_README_MARKER", SURVEY_CHECKER) in issues
        assert ("MISSING_SCRIPTS_README_MARKER", SURVEY_CHECKER) in issues
        assert ("MISSING_TESTS_README_MARKER", SURVEY_CHECKER) in issues
        assert ("MISSING_TOOL_MANIFEST_NOTE", "dedicated genksyms dual-implementation survey guard") in issues
        assert ("MISSING_TOOL_MANIFEST_CHECKER", SURVEY_CHECKER) in issues
        checks_run += 1

        build_passing_root(root)
        manifest_path = root / PHASE2_TOOL_MANIFEST
        manifest = read_json_dict(manifest_path)
        manifest["present_surfaces"]["checkers"].append(SURVEY_CHECKER)
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = collect_issues(root)
        assert ("DUPLICATE_TOOL_MANIFEST_CHECKER", SURVEY_CHECKER) in issues
        checks_run += 1

        build_passing_root(root)
        (root / SURVEY_CHECKER).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing survey checker did not abort")

    print("PHASE2_GENKSYMS_SURVEY_REMINDER_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_SURVEY_REMINDER_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the shared Phase 2 reminder surfaces aligned with the genksyms dual-implementation survey checker."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="Write a minimal current-like failing root to this path",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_GENKSYMS_SURVEY_REMINDER_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_SURVEY_REMINDER_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
