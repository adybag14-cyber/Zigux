#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_REL = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_ROUTE_MARKERS = (
    ("make -C zigux phase14-validate", "phase14-validate:"),
    ("make -C zigux phase14-smoke", "phase14-smoke:"),
    ("make -C zigux phase14-test", "phase14-test:"),
)
REQUIRED_AGGREGATE_COMMAND = "make -C zigux phase14"
REQUIRED_AGGREGATE_TARGET = "phase14: phase14-validate phase14-smoke phase14-test"


def default_doc_path(root: Path) -> Path:
    return root / DOC_REL


def default_makefile_path(root: Path) -> Path:
    return root / MAKEFILE_REL


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_issues(doc_text: str, makefile_text: str) -> list[str]:
    issues: list[str] = []

    for command_marker, target_marker in REQUIRED_ROUTE_MARKERS:
        if command_marker in doc_text and target_marker not in makefile_text:
            issues.append(f"missing_makefile_target_for_doc_command:{target_marker[:-1]}")

    if REQUIRED_AGGREGATE_COMMAND in doc_text and REQUIRED_AGGREGATE_TARGET not in makefile_text:
        issues.append("missing_makefile_aggregate_for_doc_command:phase14")

    return issues


def run_check(doc_path: Path, makefile_path: Path) -> int:
    missing_paths: list[str] = []
    if not doc_path.exists():
        missing_paths.append(str(doc_path))
    if not makefile_path.exists():
        missing_paths.append(str(makefile_path))

    if missing_paths:
        print("PHASE14_MAKEFILE_ROUTE_DRIFT=fail")
        print("PHASE14_MAKEFILE_ROUTE_DRIFT_ISSUES_START")
        for path in missing_paths:
            print(f"missing_required_path:{path}")
        print("PHASE14_MAKEFILE_ROUTE_DRIFT_ISSUES_END")
        return 1

    issues = collect_issues(load_text(doc_path), load_text(makefile_path))
    if issues:
        print("PHASE14_MAKEFILE_ROUTE_DRIFT=fail")
        print("PHASE14_MAKEFILE_ROUTE_DRIFT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE14_MAKEFILE_ROUTE_DRIFT_ISSUES_END")
        return 1

    print("PHASE14_MAKEFILE_ROUTE_DRIFT=pass")
    print(f"PHASE14_MAKEFILE_ROUTE_DRIFT_ROUTE_COUNT={len(REQUIRED_ROUTE_MARKERS)}")
    print("PHASE14_MAKEFILE_ROUTE_DRIFT_AGGREGATE=phase14")
    return 0


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_doc(*commands: str) -> str:
    body = ["# Phase 14", "## Packet-Local Rerun Vocabulary"]
    body.extend(f"* `{command}`" for command in commands)
    return "\n".join(body) + "\n"


def build_makefile(*targets: str) -> str:
    return "\n".join(targets) + "\n"


def assert_case(tmp_root: Path, *, doc_text: str, makefile_text: str, expected: list[str]) -> None:
    doc_path = tmp_root / DOC_REL
    makefile_path = tmp_root / MAKEFILE_REL
    write_text(doc_path, doc_text)
    write_text(makefile_path, makefile_text)
    actual = collect_issues(doc_text, makefile_text)
    assert actual == expected, (actual, expected)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase14_makefile_route_drift_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        full_doc = build_doc(
            "make -C zigux phase14-validate",
            "make -C zigux phase14-smoke",
            "make -C zigux phase14-test",
            "make -C zigux phase14",
        )
        full_makefile = build_makefile(
            "phase14-validate:",
            "phase14-smoke:",
            "phase14-test:",
            "phase14: phase14-validate phase14-smoke phase14-test",
        )
        assert_case(tmp_root, doc_text=full_doc, makefile_text=full_makefile, expected=[])
        case_count += 1

        assert_case(
            tmp_root,
            doc_text=full_doc,
            makefile_text=build_makefile(
                "phase14-smoke:",
                "phase14-test:",
                "phase14: phase14-validate phase14-smoke phase14-test",
            ),
            expected=["missing_makefile_target_for_doc_command:phase14-validate"],
        )
        case_count += 1

        assert_case(
            tmp_root,
            doc_text=full_doc,
            makefile_text=build_makefile(
                "phase14-validate:",
                "phase14-test:",
                "phase14: phase14-validate phase14-smoke phase14-test",
            ),
            expected=["missing_makefile_target_for_doc_command:phase14-smoke"],
        )
        case_count += 1

        assert_case(
            tmp_root,
            doc_text=full_doc,
            makefile_text=build_makefile(
                "phase14-validate:",
                "phase14-smoke:",
                "phase14-test:",
                "phase14: phase14-validate phase14-test",
            ),
            expected=["missing_makefile_aggregate_for_doc_command:phase14"],
        )
        case_count += 1

        assert_case(
            tmp_root,
            doc_text=build_doc("make -C zigux phase12-test"),
            makefile_text=build_makefile(),
            expected=[],
        )
        case_count += 1

    print("PHASE14_MAKEFILE_ROUTE_DRIFT_SELF_TEST=pass")
    print(f"PHASE14_MAKEFILE_ROUTE_DRIFT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when Phase 14 shared smoke notes advertise Makefile routes that are no longer shipped."
    )
    parser.add_argument("--root", help="Override the repository root.")
    parser.add_argument("--doc-path", help="Override the Phase 14 shared smoke survey path.")
    parser.add_argument("--makefile-path", help="Override the Zigux Makefile path.")
    parser.add_argument("--self-test", action="store_true", help="Run embedded self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = Path(args.root).resolve() if args.root else ROOT.resolve()
    doc_path = Path(args.doc_path).resolve() if args.doc_path else default_doc_path(root)
    makefile_path = Path(args.makefile_path).resolve() if args.makefile_path else default_makefile_path(root)
    return run_check(doc_path, makefile_path)


if __name__ == "__main__":
    raise SystemExit(main())
