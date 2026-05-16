#!/usr/bin/env python3
"""Validate the Phase 3 policy and unsafe boundary survey against live packet files."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
SUPPORT_NOTE_REL = "Documentation/zigux/phase3-validator-support-surface.md"
MAKEFILE_REL = "zigux/Makefile"
VALIDATE_PHASE3_REL = "scripts/zigux/validate-phase3.py"
VALIDATOR_SUPPORT_REL = "scripts/zigux/validate-phase3-validator-support-surface.py"
POLICY_BYTE_GUARD_REL = "scripts/zigux/check-phase3-policy-byte-guards.py"
LAYOUT_ASSERT_REL = "zigux/helpers/layout_assert.zig"
PANIC_POLICY_REL = "zigux/helpers/panic_policy.zig"
ALLOCATOR_POLICY_REL = "zigux/helpers/allocator_policy.zig"
MMIO_REL = "zigux/helpers/mmio.zig"
UNSAFE_NARROW_REL = "zigux/unsafe/narrow.zig"
ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"
ABI_SLICE_DOC_REL = "Documentation/zigux/phase3-abi-slice.md"

SELF_PATH = "scripts/zigux/validate-phase3-policy-unsafe-survey.py"

REQUIRED_FILES = (
    SURVEY_REL,
    SUPPORT_NOTE_REL,
    MAKEFILE_REL,
    VALIDATE_PHASE3_REL,
    VALIDATOR_SUPPORT_REL,
    POLICY_BYTE_GUARD_REL,
    LAYOUT_ASSERT_REL,
    PANIC_POLICY_REL,
    ALLOCATOR_POLICY_REL,
    MMIO_REL,
    UNSAFE_NARROW_REL,
    ABI_TEST_REL,
    ABI_DUMP_REL,
    ABI_MANIFEST_REL,
    ABI_SLICE_DOC_REL,
)

PATH_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_PATH": LAYOUT_ASSERT_REL,
    "PHASE3_PANIC_POLICY_PATH": PANIC_POLICY_REL,
    "PHASE3_ALLOCATOR_POLICY_PATH": ALLOCATOR_POLICY_REL,
    "PHASE3_MMIO_PATH": MMIO_REL,
    "PHASE3_UNSAFE_PATH": UNSAFE_NARROW_REL,
    "PHASE3_ABI_TEST_PATH": ABI_TEST_REL,
    "PHASE3_ABI_DUMP_PATH": ABI_DUMP_REL,
}

STATIC_MARKERS = (
    "PHASE3_LAYOUT_ASSERT_SCOPE=generic-layout-helper-plus-canonical-abi-byte-and-field-asserts-consumed-by-shared-abi-replays",
    "PHASE3_PANIC_POLICY=explicit-modes-only",
    "PHASE3_ALLOCATOR_POLICY=explicit-modes-plus-init-flow",
    "PHASE3_UNSAFE_SCOPE=narrow-mmio-and-raw-pointer-bridge",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
    "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    "PHASE3_DUMP_GATE=zig build phase3-dump --build-file zigux/tests/build.zig",
    "PHASE3_POLICY_BYTE_GUARD=python3 scripts/zigux/check-phase3-policy-byte-guards.py",
    "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-shared-abi-packet",
    "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-the-shared-abi-manifest-or-shared-abi-slice-drifts-again",
)

SURVEY_SNIPPETS = (
    "`zigux/helpers/layout_assert.zig` is still a small generic helper, but it now centralizes compile-time layout checks for `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` plus the current panic, allocator, and unsafe-scope byte values, and it now also keeps the current chrdev notify ack-window policy budget-window delivery-window view, summary, budget-view, and budget-summary layouts explicit so those ABI structs no longer live only in the shared replays.",
    "`zigux/helpers/panic_policy.zig` keeps panic action explicit both through the typed enum path and through `modeFromInteropPolicyBytes`, `actionForInteropPolicyBytes`, and `canReturnInteropPolicyBytes` so unknown panic modes and nonzero reserved bytes fail closed before raw-byte callers infer behavior elsewhere in the packet.",
    "`zigux/helpers/allocator_policy.zig` keeps allocator mode, init ownership, and global-fallback policy explicit through `InitFlow`, `initFlowFor`, `modeFromInteropPolicyBytes`, `requiresExplicitCallerPolicyBytes`, `permitsGlobalFallbackPolicyBytes`, `initializesOwnedStatePolicyBytes`, and `requiresResetOnInitPolicyBytes` so unknown allocator modes, helper-owned initialization, arena reset requirements, and nonzero reserved bytes fail closed before raw-byte or typed shared callers infer behavior elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` still keeps the raw-pointer bridge deliberately small, but it also decodes `InteropPolicy` unsafe-scope bytes explicitly through `scopeFromInteropPolicyBytes`, `recognizesInteropPolicyBytes`, `permitsVolatileMmioPolicyBytes`, and `permitsRawPointerBridgePolicyBytes` so unknown scopes and reserved-byte drift do not have to be inferred elsewhere in the packet.",
    "`zigux/unsafe/narrow.zig` also mirrors the panic and allocator helper style with typed `InteropPolicy` entry points through `scopeFromInteropPolicy`, `recognizesInteropPolicy`, `permitsNoUnsafeInteropPolicy`, `permitsVolatileMmioInteropPolicy`, and `permitsRawPointerBridgeInteropPolicy`, while keeping the direct raw-pointer bridge relays narrowed to the `sliceAt*`, `constSliceAt*`, `constPointerAt*`, `pointerAt*`, and `writeValueAt*` helper family instead of widening into a broader unsafe facade.",
    "`zigux/helpers/mmio.zig` consumes that same narrow layer for direct `range()`, `read8()`, `write8()`, `read16()`, `write16()`, `read32()`, `write32()`, `read64()`, and `write64()` access while also routing policy-aware MMIO through `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*` relays so volatile-MMIO callers stay inside the bounded unsafe contract.",
    "`scripts/zigux/check-phase3-policy-byte-guards.py` gives the shared policy-and-unsafe survey validator a dedicated reserved-byte and typed-wrapper guard across the policy helpers, this survey note, the paired `scripts/zigux/check-phase3-policy-unsafe-focused-replay.py` and `scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py` packet checks, and the explicit shared dump gate, so the existing `phase3-validate` path can fail closed on policy-byte drift instead of leaving that contract implicit.",
    "`zigux/tests/phase3_abi.zig` is the live shared Zig proof packet for this family today, and it now proves the `BoundaryHeader`, `ExportStatus`, and `InteropPolicy` layouts, exported constants, `export_shim` compatibility rules, and direct panic-policy, allocator-policy, and unsafe-scope decoding alignment by importing the shared policy helpers themselves.",
    "`zigux/tests/phase3_abi_dump.zig` keeps the current shared dump path explicit by emitting ABI constants plus the `InteropPolicy` and chrdev budget-window struct layouts; it no longer claims a dedicated policy/unsafe dump family or helper-local `MmioRange` layout packet of its own.",
)

BLOB_MARKERS = {
    "PHASE3_LAYOUT_ASSERT_BLOB_SHA": LAYOUT_ASSERT_REL,
    "PHASE3_PANIC_POLICY_BLOB_SHA": PANIC_POLICY_REL,
    "PHASE3_ALLOCATOR_POLICY_BLOB_SHA": ALLOCATOR_POLICY_REL,
    "PHASE3_MMIO_BLOB_SHA": MMIO_REL,
    "PHASE3_UNSAFE_BLOB_SHA": UNSAFE_NARROW_REL,
    "PHASE3_ABI_TEST_BLOB_SHA": ABI_TEST_REL,
    "PHASE3_ABI_DUMP_BLOB_SHA": ABI_DUMP_REL,
    "PHASE3_ABI_MANIFEST_BLOB_SHA": ABI_MANIFEST_REL,
    "PHASE3_ABI_SLICE_DOC_BLOB_SHA": ABI_SLICE_DOC_REL,
}

REFERENCE_TARGETS = {
    SUPPORT_NOTE_REL: (SELF_PATH,),
    VALIDATOR_SUPPORT_REL: (SELF_PATH,),
    MAKEFILE_REL: (SELF_PATH,),
    VALIDATE_PHASE3_REL: (SELF_PATH,),
}


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("`") and line.endswith("`"):
            line = line[1:-1]
        lines.append(line)
    return lines


def require_exact_line(
    issues: list[str],
    text: str,
    line: str,
    *,
    prefix: str,
    normalized: bool = False,
) -> None:
    lines = normalized_lines(text) if normalized else text.splitlines()
    count = lines.count(line)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_{prefix}:{line}")
        return
    issues.append(f"duplicate_{prefix}:{line}:{count}")


def require_prefix_once(
    issues: list[str],
    text: str,
    prefix: str,
    *,
    normalized: bool = False,
    label: str,
) -> None:
    lines = normalized_lines(text) if normalized else text.splitlines()
    matches = [line for line in lines if line.startswith(prefix)]
    if len(matches) == 1:
        return
    if not matches:
        issues.append(f"missing_{label}:{prefix}<value>")
        return
    issues.append(f"duplicate_{label}:{prefix}<value>:{len(matches)}")


def require_snippets(issues: list[str], text: str, prefix: str, snippets: tuple[str, ...]) -> None:
    for snippet in snippets:
        count = text.count(snippet)
        if count == 1:
            continue
        if count == 0:
            issues.append(f"missing_{prefix}_snippet:{snippet}")
            continue
        issues.append(f"duplicate_{prefix}_snippet:{snippet}:{count}")


def validate(root: Path) -> list[str]:
    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing_files:
        return [f"missing_file:{rel}" for rel in missing_files]

    issues: list[str] = []

    survey = (root / SURVEY_REL).read_text(encoding="utf-8")

    for marker, rel in PATH_MARKERS.items():
        require_exact_line(
            issues,
            survey,
            f"{marker}={rel}",
            prefix="marker",
            normalized=True,
        )

    for marker in STATIC_MARKERS:
        require_exact_line(issues, survey, marker, prefix="marker", normalized=True)

    require_prefix_once(
        issues,
        survey,
        "PHASE3_SURVEY_PROVENANCE=",
        normalized=True,
        label="marker",
    )

    require_snippets(issues, survey, "survey", SURVEY_SNIPPETS)

    survey_lines = normalized_lines(survey)
    for marker, rel in BLOB_MARKERS.items():
        prefix = f"{marker}="
        matches = [line for line in survey_lines if line.startswith(prefix)]
        if not matches:
            issues.append(f"missing_blob_marker:{marker}=<sha>")
            continue
        if len(matches) != 1:
            issues.append(f"duplicate_blob_marker:{marker}=<sha>:{len(matches)}")
            continue
        actual = matches[0].split(prefix, 1)[1]
        expected = git_blob_sha(root / rel)
        if actual != expected:
            issues.append(f"stale_blob_marker:{marker}:{actual}!={expected}")

    for rel, required_tokens in REFERENCE_TARGETS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for token in required_tokens:
            if token not in text:
                issues.append(f"missing_reference:{rel}:{token}")

    checker = subprocess.run(
        [sys.executable, root / POLICY_BYTE_GUARD_REL],
        capture_output=True,
        text=True,
        check=False,
    )
    if checker.returncode != 0:
        issues.append(f"policy_byte_guard_exit:{checker.returncode}")
        for line in checker.stdout.splitlines():
            issues.append(f"policy_byte_guard_stdout:{line}")
        for line in checker.stderr.splitlines():
            issues.append(f"policy_byte_guard_stderr:{line}")

    return issues


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    for rel in (
        LAYOUT_ASSERT_REL,
        PANIC_POLICY_REL,
        ALLOCATOR_POLICY_REL,
        MMIO_REL,
        UNSAFE_NARROW_REL,
        ABI_TEST_REL,
        ABI_DUMP_REL,
        ABI_MANIFEST_REL,
        ABI_SLICE_DOC_REL,
    ):
        write_file(root / rel, f"{rel}\n")

    write_file(root / POLICY_BYTE_GUARD_REL, "#!/usr/bin/env python3\nprint(\"PHASE3_POLICY_BYTE_GUARDS=pass\")\n")

    survey_lines = [
        "# Phase 3 Policy and Unsafe Boundary Survey",
        "",
        "- `PHASE3_SURVEY_PROVENANCE=connector-current-head-sha-unavailable-in-run`",
    ]
    for marker, rel in PATH_MARKERS.items():
        survey_lines.append(f"- `{marker}={rel}`")
    for marker in STATIC_MARKERS:
        survey_lines.append(f"- `{marker}`")
    for marker, rel in BLOB_MARKERS.items():
        survey_lines.append(f"- `{marker}={git_blob_sha(root / rel)}`")
    for snippet in SURVEY_SNIPPETS:
        survey_lines.append(f"- {snippet}")
    write_file(root / SURVEY_REL, "\n".join(survey_lines) + "\n")

    for rel in REFERENCE_TARGETS:
        write_file(root / rel, f"{SELF_PATH}\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_validator_") as tmp_dir:
        root = Path(tmp_dir)

        build_valid_workspace(root)
        assert validate(root) == []

        build_valid_workspace(root)
        stale_survey = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "PHASE3_MMIO_BLOB_SHA=",
            "PHASE3_MMIO_BLOB_SHA=stale-",
            1,
        )
        write_file(root / SURVEY_REL, stale_survey)
        issues = validate(root)
        expected = git_blob_sha(root / MMIO_REL)
        assert f"stale_blob_marker:PHASE3_MMIO_BLOB_SHA:stale-{expected}!={expected}" in issues

        build_valid_workspace(root)
        missing_provenance = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_SURVEY_PROVENANCE=connector-current-head-sha-unavailable-in-run`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_provenance)
        issues = validate(root)
        assert "missing_marker:PHASE3_SURVEY_PROVENANCE=<value>" in issues

        build_valid_workspace(root)
        missing_validate_gate = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_validate_gate)
        issues = validate(root)
        assert "missing_marker:PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py" in issues

        build_valid_workspace(root)
        missing_survey_snippet = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            SURVEY_SNIPPETS[5] + "\n",
            "",
            1,
        )
        write_file(root / SURVEY_REL, missing_survey_snippet)
        issues = validate(root)
        assert f"missing_survey_snippet:{SURVEY_SNIPPETS[5]}" in issues

        build_valid_workspace(root)
        duplicate_survey_snippet = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            SURVEY_SNIPPETS[1] + "\n",
            SURVEY_SNIPPETS[1] + "\n" + SURVEY_SNIPPETS[1] + "\n",
            1,
        )
        write_file(root / SURVEY_REL, duplicate_survey_snippet)
        issues = validate(root)
        assert f"duplicate_survey_snippet:{SURVEY_SNIPPETS[1]}:2" in issues

        build_valid_workspace(root)
        missing_support_reference = (root / SUPPORT_NOTE_REL).read_text(encoding="utf-8").replace(
            SELF_PATH,
            "",
            1,
        )
        write_file(root / SUPPORT_NOTE_REL, missing_support_reference)
        issues = validate(root)
        assert f"missing_reference:{SUPPORT_NOTE_REL}:{SELF_PATH}" in issues

        build_valid_workspace(root)
        missing_makefile_reference = (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
            SELF_PATH,
            "",
            1,
        )
        write_file(root / MAKEFILE_REL, missing_makefile_reference)
        issues = validate(root)
        assert f"missing_reference:{MAKEFILE_REL}:{SELF_PATH}" in issues

        build_valid_workspace(root)
        write_file(
            root / POLICY_BYTE_GUARD_REL,
            "#!/usr/bin/env python3\nimport sys\nprint(\"PHASE3_POLICY_BYTE_GUARDS=fail\")\nsys.exit(1)\n",
        )
        issues = validate(root)
        assert "policy_byte_guard_exit:1" in issues

        build_valid_workspace(root)
        duplicate_path_marker = (root / SURVEY_REL).read_text(encoding="utf-8").replace(
            "- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`\n",
            "- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`\n- `PHASE3_MMIO_PATH=zigux/helpers/mmio.zig`\n",
            1,
        )
        write_file(root / SURVEY_REL, duplicate_path_marker)
        issues = validate(root)
        assert "duplicate_marker:PHASE3_MMIO_PATH=zigux/helpers/mmio.zig:2" in issues

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT=9")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 3 policy and unsafe boundary survey against the current shared ABI packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run isolated validator coverage in a temporary workspace",
    )
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
