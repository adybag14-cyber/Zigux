#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
MAKEFILE_REL = "zigux/Makefile"

PATH_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_PATH": "zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_PATH": "zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_PATH": "zigux/helpers/allocator_policy.zig",
    "PHASE3_MMIO_PATH": "zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_PATH": "zigux/unsafe/narrow.zig",
    "PHASE3_ABI_TEST_PATH": "zigux/tests/phase3_abi.zig",
    "PHASE3_ABI_DUMP_PATH": "zigux/tests/phase3_abi_dump.zig",
}

STATIC_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_SCOPE=canonical-bindings",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-only",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
)

BLOB_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": "zigux/helpers/layout_assert.zig",
    "PHASE3_PANIC_POLICY_BLOB_SHA": "zigux/helpers/panic_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": "zigux/helpers/allocator_policy.zig",
    "PHASE3_MMIO_BLOB_SHA": "zigux/helpers/mmio.zig",
    "PHASE3_UNSAFE_BLOB_SHA": "zigux/unsafe/narrow.zig",
    "PHASE3_ABI_TEST_BLOB_SHA": "zigux/tests/phase3_abi.zig",
    "PHASE3_ABI_DUMP_BLOB_SHA": "zigux/tests/phase3_abi_dump.zig",
    "PHASE3_ABI_MANIFEST_BLOB_SHA": "zigux/tests/fixtures/phase3_abi_manifest.json",
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": "Documentation/zigux/phase3-abi-slice.md",
}

MAKEFILE_REQUIRED_LINES = (
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test",
)


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey_path = root / SURVEY_REL
    makefile_path = root / MAKEFILE_REL

    try:
        survey = survey_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_survey:{SURVEY_REL}"]

    for marker, rel in PATH_MARKERS.items():
        expected = f"{marker}={rel}"
        if expected not in survey:
            issues.append(f"missing_marker:{expected}")
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")

    for marker in STATIC_MARKERS:
        if marker not in survey:
            issues.append(f"missing_marker:{marker}")

    for marker, rel in BLOB_MARKERS.items():
        path = root / rel
        if not path.exists():
            issues.append(f"missing_file:{rel}")
            continue
        expected = f"{marker}={git_blob_sha(path)}"
        if expected not in survey:
            issues.append(f"stale_blob_marker:{marker}")

    try:
        makefile = makefile_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_makefile:{MAKEFILE_REL}")
        return issues

    for line in MAKEFILE_REQUIRED_LINES:
        if line not in makefile:
            issues.append(f"missing_makefile_line:{line.strip()}")

    return issues


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    content_by_rel = {
        "zigux/helpers/layout_assert.zig": "// layout\n",
        "zigux/helpers/panic_policy.zig": "// panic\n",
        "zigux/helpers/allocator_policy.zig": "// allocator\n",
        "zigux/helpers/mmio.zig": "// mmio\n",
        "zigux/unsafe/narrow.zig": "// narrow\n",
        "zigux/tests/phase3_abi.zig": "// abi test\n",
        "zigux/tests/phase3_abi_dump.zig": "// abi dump\n",
        "zigux/tests/fixtures/phase3_abi_manifest.json": "{\n  \"phase\": \"Phase 3\"\n}\n",
        "Documentation/zigux/phase3-abi-slice.md": "# abi\n",
    }
    for rel, content in content_by_rel.items():
        write_file(root / rel, content)

    survey_lines = [
        "# Phase 3 Policy and Unsafe Boundary Survey",
        "",
    ]
    for marker, rel in PATH_MARKERS.items():
        survey_lines.append(f"- `{marker}={rel}`")
    for marker in STATIC_MARKERS:
        survey_lines.append(f"- `{marker}`")
    for marker, rel in BLOB_MARKERS.items():
        survey_lines.append(f"- `{marker}={git_blob_sha(root / rel)}`")
    write_file(root / SURVEY_REL, "\n".join(survey_lines) + "\n")

    write_file(
        root / MAKEFILE_REL,
        "\n".join(
            [
                "phase3-validate:",
                MAKEFILE_REQUIRED_LINES[0],
                MAKEFILE_REQUIRED_LINES[1],
                "",
            ]
        ),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_validator_") as tmp_dir:
        root = Path(tmp_dir)
        build_valid_workspace(root)
        assert validate(root) == []

        broken_note = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "PHASE3_MMIO_BLOB_SHA=",
            "PHASE3_MMIO_BLOB_SHA=stale-",
            1,
        )
        write_file(root / SURVEY_REL, broken_note)
        issues = validate(root)
        assert "stale_blob_marker:PHASE3_MMIO_BLOB_SHA" in issues

        build_valid_workspace(root)
        broken_makefile = (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
            MAKEFILE_REQUIRED_LINES[1] + "\n",
            "",
            1,
        )
        write_file(root / MAKEFILE_REL, broken_makefile)
        issues = validate(root)
        assert (
            "missing_makefile_line:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase3-policy-unsafe-survey.py --self-test"
            in issues
        )

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 policy and unsafe survey note against the current ABI packet.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage in a temporary workspace.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_SURVEY_VALIDATION=fail")
        print("PHASE3_POLICY_UNSAFE_SURVEY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_POLICY_UNSAFE_SURVEY_ISSUES_END")
        return 1

    print("PHASE3_POLICY_UNSAFE_SURVEY_VALIDATION=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
