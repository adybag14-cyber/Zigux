#!/usr/bin/env python3
"""Check that the Phase 9 runtime build surface only references committed files."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT_SOURCE_RE = re.compile(r'\.root_source_file\s*=\s*=b\.path\("([^"]+)"\)')


def extract_runtime_paths(build_text: str) -> list[str]:
    return sorted(dict.fromkeys(ROOT_SOURCE_RE.findall(build_text)))


def resolve_runtime_paths(repo_root: pathlib.Path, build_relpath: str) -> list[tuple[str, pathlib.Path]]:
    build_path = repo_root / build_relpath
    build_text = build_path.read_text(encoding="utf-8")
    return [(entry, (build_path.parent / entry).resolve()) for entry in extract_runtime_paths(build_text)]


def check_runtime_build_surface(repo_root: pathlib.Path, build_relpath: str) -> dict[str, object]:
    resolved = resolve_runtime_paths(repo_root, build_relpath)
    present: list[str] = []
    missing: list[str] = []
    for _, abs_path in resolved:
        rel_abs = abs_path.relative_to(repo_root.resolve())
        rel_str = rel_abs.as_posix()
        if abs_path.is_file():
            present.append(rel_str)
        else:
            missing.append(rel_str)

    return {
        "build_file": build_relpath,
        "checked_paths": len(resolved),
        "present": present,
        "missing": missing,
    }


def run_self_test() -> int:
    fixture = """
    const runtime_a = b.createModule(.{
        .root_source_file = b.path("../helpers/runtime_a.zig"),
    });
    const runtime_b = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_b.zig"),
    });
    const runtime_a_dupe = b.createModule(.{
        .root_source_file = b.path("../helpers/runtime_a.zig"),
    });
    """.strip()
    extracted = extract_runtime_paths(fixture)
    expected = ["../../samples/zigux/runtime_b.zig", "../helpers/runtime_a.zig"]
    if extracted != expected:
        raise AssertionError(f"unexpected extraction result: {extracted!r}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 9 runtime build surface for missing file references.",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument(
        "--build-file",
        default="zigux/tests/phase9_build.zig",
        help="Path to the Phase 9 build file relative to the repo root.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--self-test", action="store_true", help="Run parser self-tests and exit.")
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    repo_root = pathlib.Path(args.repo_root).resolve()
    report = check_runtime_build_surface(repo_root, args.build_file)

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(f"Phase 9 build file: {report['build_file']}")
        print(f"Checked runtime paths: {report['checked_paths']}")
        if report["missing"]:
            print("Missing runtime paths:")
            for path in report["missing"]:
                print(f"  - {path}")
        else:
            print("Missing runtime paths: none")
        if report["present"]:
            print("Present runtime paths:")
            for path in report["present"]:
                print(f"  - {path}")

    return 1 if report["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
