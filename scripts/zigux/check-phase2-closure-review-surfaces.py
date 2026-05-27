#!/usr/bin/env python3
"""Keep the Phase 2 closure packet aligned on scripts-root review surfaces."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
REQUIRED_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_manifest(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(resolve(root, PHASE2_CLOSURE))
    read_text(resolve(root, SCRIPTS_README))
    manifest = read_manifest(resolve(root, TOOL_MANIFEST))

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues
    review_surfaces = surfaces.get("review_surfaces")
    if not isinstance(review_surfaces, list) or not all(isinstance(item, str) for item in review_surfaces):
        issues.append(("INVALID_MANIFEST_SHAPE", "review_surfaces"))
        return issues

    for marker in REQUIRED_REVIEW_SURFACES:
        if marker not in review_surfaces:
            issues.append(("MISSING_MANIFEST_REVIEW_SURFACE", marker))
        if f"`{marker}`" not in closure_text:
            issues.append(("MISSING_CLOSURE_REVIEW_SURFACE", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CLOSURE_REVIEW_SURFACES=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve(root, PHASE2_CLOSURE),
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                *[f"- `{marker}`" for marker in REQUIRED_REVIEW_SURFACES],
                "",
            )
        ),
    )
    write_text(resolve(root, SCRIPTS_README), "# scripts/zigux\n")
    write_text(
        resolve(root, TOOL_MANIFEST),
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {
                    "review_surfaces": list(REQUIRED_REVIEW_SURFACES),
                },
                "repo_reality_gaps": [],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_p2_closure_review_surfaces_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        manifest_path = resolve(root, TOOL_MANIFEST)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["review_surfaces"].remove("scripts/zigux/README.md")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_REVIEW_SURFACE", "scripts/zigux/README.md") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve(root, PHASE2_CLOSURE)
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace("`scripts/zigux/README.md`", "", 1),
            encoding="utf-8",
        )
        assert ("MISSING_CLOSURE_REVIEW_SURFACE", "scripts/zigux/README.md") in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_REVIEW_SURFACES=self-test-pass")
    print(f"PHASE2_CLOSURE_REVIEW_SURFACES_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic regression checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_REVIEW_SURFACES=pass")
    print("PHASE2_CLOSURE_REVIEW_SURFACES_REQUIRED_COUNT=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
