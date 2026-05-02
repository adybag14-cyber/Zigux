#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
MMIO_REL = "zigux/helpers/mmio.zig"
POLICY_TEST_REL = "zigux/tests/phase3_policy_unsafe.zig"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig",
    "PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay",
    "PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet",
    "the current tree does not yet ship a third Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly beyond the focused replay and the scoped MMIO helper",
)

REQUIRED_MMIO_SNIPPETS = (
    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
    "pub fn readScopedWithPolicy(",
    "pub fn writeScopedWithPolicy(",
    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
    "pub fn write32Policy(",
    'test "phase3 mmio wrapper consumes decoded interop policy"',
)

REQUIRED_POLICY_TEST_SNIPPETS = (
    'test "phase3 policy gate reaches a second boundary helper through decoded policy"',
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));",
    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    mmio = _read_text(root, MMIO_REL, issues)
    policy_test = _read_text(root, POLICY_TEST_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
    if mmio:
        _check_snippets(mmio, REQUIRED_MMIO_SNIPPETS, "missing_mmio_snippet", issues)
    if policy_test:
        _check_snippets(policy_test, REQUIRED_POLICY_TEST_SNIPPETS, "missing_policy_test_snippet", issues)

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_mmio_consumer_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        _write(
            root,
            SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                    "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                    "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                    "",
                    "`zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet.",
                    "the current tree does not yet ship a third Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly beyond the focused replay and the scoped MMIO helper.",
                    "",
                )
            ),
        )
        _write(
            root,
            MMIO_REL,
            "\n".join(
                (
                    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
                    "    _ = policy;",
                    "}",
                    "pub fn readScopedWithPolicy(",
                    "pub fn writeScopedWithPolicy(",
                    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
                    "    _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn write32Policy(",
                    'test "phase3 mmio wrapper consumes decoded interop policy"',
                    "",
                )
            ),
        )
        _write(
            root,
            POLICY_TEST_REL,
            "\n".join(
                (
                    'test "phase3 policy gate reaches a second boundary helper through decoded policy"',
                    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));",
                    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.read32Policy(raw_pointer_policy, base32, 0));",
                    "",
                )
            ),
        )

        assert validate(root) == []

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                    "",
                )
            ),
        )
        issues = validate(root)
        assert "missing_survey_marker:PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig" in issues

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                (
                    "# Phase 3 Policy and Unsafe Boundary Survey",
                    "",
                    "- `PHASE3_MMIO_TYPED_POLICY_CONSUMER=zigux/helpers/mmio.zig`",
                    "- `PHASE3_BOUNDARY_GAP=typed-policy-mmio-consumer-landed-no-third-boundary-helper-beyond-focused-replay`",
                    "- `PHASE3_NEXT_BOUNDED_STEP=keep-the-policy-and-unsafe-surface-narrow-until-one-roadmap-backed-helper-beyond-mmio-needs-a-typed-interop-policy-consumer`",
                    "",
                    "`zigux/helpers/mmio.zig` is now the shipped second boundary helper that consumes `DecodedInteropPolicy` directly outside the focused `phase3_policy_unsafe` test packet.",
                    "the current tree does not yet ship a third Phase 3 boundary helper that consumes `DecodedInteropPolicy` directly beyond the focused replay and the scoped MMIO helper.",
                    "",
                )
            ),
        )
        _write(
            root,
            MMIO_REL,
            "\n".join(
                (
                    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
                    "    _ = policy;",
                    "}",
                    "pub fn readScopedWithPolicy(",
                    "pub fn writeScopedWithPolicy(",
                    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
                    "    _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn write32Policy(",
                    "",
                )
            ),
        )
        issues = validate(root)
        assert 'missing_mmio_snippet:test "phase3 mmio wrapper consumes decoded interop policy"' in issues

        _write(
            root,
            MMIO_REL,
            "\n".join(
                (
                    "fn scopeFromPolicy(policy: interop_policy.DecodedInteropPolicy) narrow.ScopeError!narrow.UnsafeScopeTag {",
                    "    _ = policy;",
                    "}",
                    "pub fn readScopedWithPolicy(",
                    "pub fn writeScopedWithPolicy(",
                    "pub fn read32Policy(policy: interop_policy.DecodedInteropPolicy, base_addr: usize, offset: usize) narrow.ScopeError!u32 {",
                    "    _ = policy; _ = base_addr; _ = offset; }",
                    "pub fn write32Policy(",
                    'test "phase3 mmio wrapper consumes decoded interop policy"',
                    "",
                )
            ),
        )
        _write(
            root,
            POLICY_TEST_REL,
            "\n".join(
                (
                    "try std.testing.expectError(error.UnsafeScopeDenied, mmio.write32Policy(raw_pointer_policy, base32, 0, 1));",
                    "",
                )
            ),
        )
        issues = validate(root)
        assert 'missing_policy_test_snippet:test "phase3 policy gate reaches a second boundary helper through decoded policy"' in issues

    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Phase 3 policy/unsafe packet still records and tests the typed-policy MMIO consumer."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated validator coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(Path(args.root).resolve() if args.root else ROOT)
    if issues:
        print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_POLICY_UNSAFE_MMIO_CONSUMER=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())