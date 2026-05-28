#!/usr/bin/env python3
"""Guard the current standalone Phase 2 genksyms proof routes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
PHASE2_CLOSURE = Path("Documentation/zigux/phase2-closure.md")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

STANDALONE_PROOF_PATHS = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)

WORKFLOW_LINES = tuple(f"run: zig test {path}" for path in STANDALONE_PROOF_PATHS)
MAKEFILE_LINES = tuple(
    f"cd $(ZIGUX_ROOT) && $(ZIG) test {path}" for path in STANDALONE_PROOF_PATHS
)

CLOSURE_MARKERS = (
    "- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig` and `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig` remain the standalone version-side-effect proofs carried by the shipped bridge packet.",
)

BOOTSTRAP_MARKERS = (
    "- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, and the restored `zigux/tests/fixtures/genksyms_bridge/` expected plus process-output fixture roster keep the bounded genksyms bridge helper packet explicit beside the reminder guards, and `make -C zigux phase2-genksyms` keeps its wrapper route inside the same returned make-wrapper packet.",
)

EXPECTED_SELF_TEST_CASE_COUNT = 9


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def load_manifest(root: Path) -> dict[str, object]:
    path = root / TOOL_MANIFEST
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    workflow_text = read_text(root / WORKFLOW)
    makefile_text = read_text(root / MAKEFILE)
    closure_text = read_text(root / PHASE2_CLOSURE)
    bootstrap_notes_text = read_text(root / BOOTSTRAP_NOTES)
    manifest = load_manifest(root)

    for marker in CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in BOOTSTRAP_MARKERS:
        if marker not in bootstrap_notes_text:
            issues.append(("MISSING_BOOTSTRAP_NOTE_MARKER", marker))

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return issues

    bridge_helpers = present_surfaces.get("bridge_helpers")
    if not isinstance(bridge_helpers, list) or not all(
        isinstance(item, str) for item in bridge_helpers
    ):
        issues.append(("INVALID_MANIFEST_SHAPE", "bridge_helpers"))
        return issues

    for path in STANDALONE_PROOF_PATHS:
        if path not in bridge_helpers:
            issues.append(("MISSING_MANIFEST_PROOF", path))

    return issues


def build_sample_root(root: Path) -> None:
    write_text(root / WORKFLOW, "\n".join(("name: zigux-bootstrap", *WORKFLOW_LINES)) + "\n")
    write_text(root / MAKEFILE, "\n".join(("phase2-genksyms: phase2-toolchain", *MAKEFILE_LINES)) + "\n")
    write_text(root / PHASE2_CLOSURE, "\n".join(("# Phase 2 Closure", "", *CLOSURE_MARKERS)) + "\n")
    write_text(root / BOOTSTRAP_NOTES, "\n".join(("# Phase 2 Toolchain Bootstrap Notes", "", *BOOTSTRAP_MARKERS)) + "\n")
    write_text(
        root / TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "present_surfaces": {
                    "bridge_helpers": list(STANDALONE_PROOF_PATHS),
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_genksyms_proof_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        path = root / PHASE2_CLOSURE
        path.write_text(path.read_text(encoding="utf-8").replace(CLOSURE_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_CLOSURE_MARKER", CLOSURE_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        path = root / BOOTSTRAP_NOTES
        path.write_text(path.read_text(encoding="utf-8").replace(BOOTSTRAP_MARKERS[0], "", 1), encoding="utf-8")
        assert ("MISSING_BOOTSTRAP_NOTE_MARKER", BOOTSTRAP_MARKERS[0]) in collect_issues(root)
        checks += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            path = root / WORKFLOW
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        for marker in MAKEFILE_LINES:
            build_sample_root(root)
            path = root / MAKEFILE
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        manifest = json.loads((root / TOOL_MANIFEST).read_text(encoding="utf-8"))
        manifest["present_surfaces"]["bridge_helpers"].remove(STANDALONE_PROOF_PATHS[0])
        (root / TOOL_MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_PROOF", STANDALONE_PROOF_PATHS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        (root / TOOL_MANIFEST).write_text("{not-json}\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks += 1
        else:
            raise AssertionError("invalid manifest json did not abort")

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a compact sample root for replay validation")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES=pass")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTE_COUNT={len(STANDALONE_PROOF_PATHS)}")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
