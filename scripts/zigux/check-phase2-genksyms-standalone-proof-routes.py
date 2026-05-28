#!/usr/bin/env python3
"""Guard the Phase 2 genksyms standalone-proof route packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")

PROOF_TESTS = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)
WORKFLOW_LINES = tuple(f"run: zig test {path}" for path in PROOF_TESTS)
MAKEFILE_LINES = tuple(
    f"cd $(ZIGUX_ROOT) && $(ZIG) test {path}" for path in PROOF_TESTS
)
CLOSURE_MARKERS = (*PROOF_TESTS, "make -C zigux phase2-genksyms")
VALIDATE_PHASE2_MARKERS = tuple(
    f'{name} = "{path}"'
    for name, path in (
        ("GENKSYMS_VERSION_SIDE_EFFECT_TEST", PROOF_TESTS[0]),
        ("GENKSYMS_VERSION_SIDE_EFFECT_AMBIGUOUS_TEST", PROOF_TESTS[1]),
    )
)


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


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_manifest_surface(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str]:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return []
    values = present_surfaces.get(key)
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return []
    return list(values)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    required_files = (
        WORKFLOW_REL,
        MAKEFILE_REL,
        PHASE2_VALIDATE_REL,
        PHASE2_CLOSURE_REL,
        PHASE2_BOOTSTRAP_NOTES_REL,
        PHASE2_TOOL_MANIFEST_REL,
        GENKSYMS_MANIFEST_REL,
        *(Path(path) for path in PROOF_TESTS),
    )
    for rel in required_files:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(root / WORKFLOW_REL)
    makefile_text = read_text(root / MAKEFILE_REL)
    validate_text = read_text(root / PHASE2_VALIDATE_REL)
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    notes_text = read_text(root / PHASE2_BOOTSTRAP_NOTES_REL)
    phase2_manifest = read_json_dict(root / PHASE2_TOOL_MANIFEST_REL)
    genksyms_manifest = read_json_dict(root / GENKSYMS_MANIFEST_REL)

    bridge_helpers = collect_manifest_surface(issues, phase2_manifest, "bridge_helpers")
    if issues:
        return issues

    standalone_proof_packet = genksyms_manifest.get("standalone_proof_packet")
    if not isinstance(standalone_proof_packet, list) or not all(
        isinstance(item, str) for item in standalone_proof_packet
    ):
        issues.append(("INVALID_GENKSYMS_MANIFEST_SHAPE", "standalone_proof_packet"))
        return issues

    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    phase2_genksyms_make_line = "run: make -C zigux phase2-genksyms"
    count = count_exact_lines(workflow_text, phase2_genksyms_make_line)
    if count == 0:
        issues.append(("MISSING_WORKFLOW_LINE", phase2_genksyms_make_line))
    elif count != 1:
        issues.append(("DUPLICATE_WORKFLOW_LINE", f"{phase2_genksyms_make_line}:count={count}"))

    phase2_genksyms_target = "phase2-genksyms: phase2-toolchain"
    count = count_exact_lines(makefile_text, phase2_genksyms_target)
    if count == 0:
        issues.append(("MISSING_MAKEFILE_LINE", phase2_genksyms_target))
    elif count != 1:
        issues.append(("DUPLICATE_MAKEFILE_LINE", f"{phase2_genksyms_target}:count={count}"))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in VALIDATE_PHASE2_MARKERS:
        count = count_exact_lines(validate_text, marker)
        if count == 0:
            issues.append(("MISSING_VALIDATE_PHASE2_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATE_PHASE2_MARKER", f"{marker}:count={count}"))

    for marker in CLOSURE_MARKERS:
        quoted = f"`{marker}`"
        if quoted not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
        if quoted not in notes_text:
            issues.append(("MISSING_NOTES_MARKER", marker))

    for path in PROOF_TESTS:
        if path not in bridge_helpers:
            issues.append(("MISSING_BRIDGE_HELPER_SURFACE", path))
        if path not in standalone_proof_packet:
            issues.append(("MISSING_STANDALONE_PROOF_PACKET", path))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


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


def build_sample_root(root: Path) -> None:
    if root.exists():
        for child in root.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        root.mkdir(parents=True)

    write_text(
        root / WORKFLOW_REL,
        "\n".join(
            (
                "name: zigux-bootstrap",
                *WORKFLOW_LINES,
                "run: make -C zigux phase2-genksyms",
            )
        )
        + "\n",
    )
    write_text(
        root / MAKEFILE_REL,
        "\n".join(
            (
                ".PHONY: phase2-genksyms",
                "phase2-genksyms: phase2-toolchain",
                *("\t" + line for line in MAKEFILE_LINES),
            )
        )
        + "\n",
    )
    write_text(
        root / PHASE2_VALIDATE_REL,
        "\n".join(VALIDATE_PHASE2_MARKERS) + "\n",
    )
    write_text(
        root / PHASE2_CLOSURE_REL,
        "\n".join(f"- `{marker}`" for marker in CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / PHASE2_BOOTSTRAP_NOTES_REL,
        "\n".join(f"- `{marker}`" for marker in CLOSURE_MARKERS) + "\n",
    )
    write_text(
        root / PHASE2_TOOL_MANIFEST_REL,
        json.dumps(
            {
                "present_surfaces": {
                    "bridge_helpers": list(PROOF_TESTS),
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / GENKSYMS_MANIFEST_REL,
        json.dumps(
            {
                "standalone_proof_packet": list(PROOF_TESTS),
            },
            indent=2,
        )
        + "\n",
    )
    for path in PROOF_TESTS:
        write_text(root / path, "test {}\n")


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane24_genksyms_routes_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in WORKFLOW_LINES:
            build_sample_root(root)
            write_text(root / WORKFLOW_REL, replace_exact_line(read_text(root / WORKFLOW_REL), marker, "run: zig test scripts/zigux/other.zig"))
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks += 1

        build_sample_root(root)
        write_text(root / WORKFLOW_REL, duplicate_exact_line(read_text(root / WORKFLOW_REL), WORKFLOW_LINES[0]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / MAKEFILE_REL, replace_exact_line(read_text(root / MAKEFILE_REL), MAKEFILE_LINES[0], "\tcd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/other.zig"))
        assert ("MISSING_MAKEFILE_LINE", MAKEFILE_LINES[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / MAKEFILE_REL, duplicate_exact_line(read_text(root / MAKEFILE_REL), MAKEFILE_LINES[1]))
        assert ("DUPLICATE_MAKEFILE_LINE", f"{MAKEFILE_LINES[1]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / PHASE2_VALIDATE_REL, read_text(root / PHASE2_VALIDATE_REL).replace(VALIDATE_PHASE2_MARKERS[0], "# removed", 1))
        assert ("MISSING_VALIDATE_PHASE2_MARKER", VALIDATE_PHASE2_MARKERS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / PHASE2_CLOSURE_REL, read_text(root / PHASE2_CLOSURE_REL).replace(f"`{PROOF_TESTS[0]}`", "`scripts/zigux/other.zig`", 1))
        assert ("MISSING_CLOSURE_MARKER", PROOF_TESTS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root / PHASE2_BOOTSTRAP_NOTES_REL, read_text(root / PHASE2_BOOTSTRAP_NOTES_REL).replace("`make -C zigux phase2-genksyms`", "`make -C zigux phase2-other`", 1))
        assert ("MISSING_NOTES_MARKER", "make -C zigux phase2-genksyms") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest = read_json_dict(root / PHASE2_TOOL_MANIFEST_REL)
        manifest["present_surfaces"]["bridge_helpers"] = [PROOF_TESTS[0]]
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_BRIDGE_HELPER_SURFACE", PROOF_TESTS[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        manifest = read_json_dict(root / GENKSYMS_MANIFEST_REL)
        manifest["standalone_proof_packet"] = [PROOF_TESTS[1]]
        write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_STANDALONE_PROOF_PACKET", PROOF_TESTS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        (root / PROOF_TESTS[0]).unlink()
        assert ("MISSING_REQUIRED_FILE", PROOF_TESTS[0]) in collect_issues(root)
        checks += 1

    print("PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the Phase 2 genksyms standalone-proof route packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree to the given root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTES=pass")
    print(f"PHASE2_GENKSYMS_STANDALONE_PROOF_ROUTE_COUNT={len(PROOF_TESTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
