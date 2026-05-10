#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-abi-header-family-survey.md"
HEADER_REL = "include/zigux/abi.h"
BINDINGS_REL = "zigux/bindings/abi.zig"
SCRIPT_REL = "scripts/zigux/validate-phase3-abi-header-family-survey.py"

HEADER_STATUS_SYMBOL = "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED"
BINDING_STATUS_SYMBOL = "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED"
STATUS_EXPECTED = 6

HEADER_BUDGET_SYMBOL = "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED"
BINDING_BUDGET_SYMBOL = "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED"
BUDGET_EXPECTED = 1

HEADER_VIEW_SYMBOL = "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {"
BINDING_VIEW_SYMBOL = "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {"
HEADER_SUMMARY_SYMBOL = "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {"
BINDING_SUMMARY_SYMBOL = "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {"

SELF_TEST_CASE_COUNT = 7

HEADER_DEFINE_RE = re.compile(r"^#define\s+(?P<name>[A-Z0-9_]+)\s+(?P<value>[0-9xa-fA-F]+)U?$")
BINDING_CONST_RE = re.compile(r"^pub const (?P<name>[A-Z0-9_]+): [^=]+ = (?P<value>[0-9xa-fA-F]+);$")

SURVEY_MARKERS = (
    "PHASE3_ABI_HEADER_FAMILY=chrdev_notify_ack_window_policy_budget_window_delivery_window",
    f"PHASE3_ABI_HEADER_PATH={HEADER_REL}",
    f"PHASE3_ABI_BINDINGS_PATH={BINDINGS_REL}",
    f"PHASE3_ABI_HEADER_FAMILY_SURVEY_PATH={SCRIPT_REL}",
    "PHASE3_ABI_HEADER_FAMILY_SURVEY_SCOPE=one bounded chrdev notify ack window policy budget window delivery window family survey",
    f"PHASE3_ABI_HEADER_STATUS_SYMBOL={HEADER_STATUS_SYMBOL}",
    f"PHASE3_ABI_BINDING_STATUS_SYMBOL={BINDING_STATUS_SYMBOL}",
    f"PHASE3_ABI_HEADER_BUDGET_SYMBOL={HEADER_BUDGET_SYMBOL}",
    f"PHASE3_ABI_BINDING_BUDGET_SYMBOL={BINDING_BUDGET_SYMBOL}",
    f"PHASE3_ABI_HEADER_VIEW_SYMBOL={HEADER_VIEW_SYMBOL}",
    f"PHASE3_ABI_BINDING_VIEW_SYMBOL={BINDING_VIEW_SYMBOL}",
    f"PHASE3_ABI_HEADER_SUMMARY_SYMBOL={HEADER_SUMMARY_SYMBOL}",
    f"PHASE3_ABI_BINDING_SUMMARY_SYMBOL={BINDING_SUMMARY_SYMBOL}",
    "PHASE3_ABI_HEADER_FAMILY_GATE=python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "PHASE3_ABI_HEADER_FAMILY_NEXT_STEP=extend-the-same-family-survey-one-foothold-at-a-time-before-widening-the-phase3-abi-surface",
)

BLOB_MARKERS = (
    ("PHASE3_ABI_HEADER_BLOB_SHA", HEADER_REL),
    ("PHASE3_ABI_BINDINGS_BLOB_SHA", BINDINGS_REL),
    ("PHASE3_ABI_HEADER_FAMILY_SURVEY_BLOB_SHA", SCRIPT_REL),
)


def parse_int(text: str) -> int:
    return int(text, 0)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def normalized_line(raw: str) -> str:
    line = raw.strip()
    if line.startswith("- "):
        line = line[2:].strip()
    if line.startswith("* "):
        line = line[2:].strip()
    if line.startswith("`") and line.endswith("`") and len(line) >= 2:
        line = line[1:-1]
    return line


def normalized_lines(text: str) -> list[str]:
    return [normalized_line(line) for line in text.splitlines()]


def parse_header_constants(path: Path) -> dict[str, int]:
    constants: dict[str, int] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = HEADER_DEFINE_RE.match(raw.strip())
        if match:
            constants[match.group("name")] = parse_int(match.group("value"))
    return constants


def parse_binding_constants(path: Path) -> dict[str, int]:
    constants: dict[str, int] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        match = BINDING_CONST_RE.match(raw.strip())
        if match:
            constants[match.group("name")] = parse_int(match.group("value"))
    return constants


def require_marker(issues: list[str], text: str, marker: str) -> None:
    count = normalized_lines(text).count(marker)
    if count == 1:
        return
    if count == 0:
        issues.append(f"missing_survey_marker:{marker}")
    else:
        issues.append(f"duplicate_survey_marker:{marker}:{count}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey_path = root / SURVEY_REL
    header_path = root / HEADER_REL
    bindings_path = root / BINDINGS_REL
    script_path = root / SCRIPT_REL

    for rel in (SURVEY_REL, HEADER_REL, BINDINGS_REL, SCRIPT_REL):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    survey = survey_path.read_text(encoding="utf-8")
    header_source = header_path.read_text(encoding="utf-8")
    bindings_source = bindings_path.read_text(encoding="utf-8")
    header_constants = parse_header_constants(header_path)
    binding_constants = parse_binding_constants(bindings_path)

    for marker in SURVEY_MARKERS:
        require_marker(issues, survey, marker)

    survey_lines = normalized_lines(survey)
    for key, rel in BLOB_MARKERS:
        prefix = f"{key}="
        matches = [line for line in survey_lines if line.startswith(prefix)]
        if not matches:
            issues.append(f"missing_survey_marker:{prefix}<sha>")
            continue
        if len(matches) != 1:
            issues.append(f"duplicate_survey_marker:{prefix}<sha>:{len(matches)}")
            continue
        actual = matches[0].split(prefix, 1)[1]
        expected = git_blob_sha(root / rel)
        if actual != expected:
            issues.append(f"stale_blob_marker:{key}:{actual}!={expected}")

    if header_constants.get(HEADER_STATUS_SYMBOL) != STATUS_EXPECTED:
        issues.append(
            f"header_constant_mismatch:{HEADER_STATUS_SYMBOL}:{header_constants.get(HEADER_STATUS_SYMBOL)}!={STATUS_EXPECTED}"
        )
    if binding_constants.get(BINDING_STATUS_SYMBOL) != STATUS_EXPECTED:
        issues.append(
            f"binding_constant_mismatch:{BINDING_STATUS_SYMBOL}:{binding_constants.get(BINDING_STATUS_SYMBOL)}!={STATUS_EXPECTED}"
        )
    if header_constants.get(HEADER_BUDGET_SYMBOL) != BUDGET_EXPECTED:
        issues.append(
            f"header_constant_mismatch:{HEADER_BUDGET_SYMBOL}:{header_constants.get(HEADER_BUDGET_SYMBOL)}!={BUDGET_EXPECTED}"
        )
    if binding_constants.get(BINDING_BUDGET_SYMBOL) != BUDGET_EXPECTED:
        issues.append(
            f"binding_constant_mismatch:{BINDING_BUDGET_SYMBOL}:{binding_constants.get(BINDING_BUDGET_SYMBOL)}!={BUDGET_EXPECTED}"
        )

    for marker in (HEADER_VIEW_SYMBOL, HEADER_SUMMARY_SYMBOL):
        if marker not in header_source:
            issues.append(f"missing_header_marker:{marker}")
    for marker in (BINDING_VIEW_SYMBOL, BINDING_SUMMARY_SYMBOL):
        if marker not in bindings_source:
            issues.append(f"missing_binding_marker:{marker}")

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    header = "\n".join(
        (
            f"#define {HEADER_STATUS_SYMBOL} {STATUS_EXPECTED}U",
            f"#define {HEADER_BUDGET_SYMBOL} {BUDGET_EXPECTED}U",
            HEADER_VIEW_SYMBOL,
            HEADER_SUMMARY_SYMBOL,
            "",
        )
    )
    bindings = "\n".join(
        (
            f"pub const {BINDING_STATUS_SYMBOL}: u32 = {STATUS_EXPECTED};",
            f"pub const {BINDING_BUDGET_SYMBOL}: u32 = {BUDGET_EXPECTED};",
            BINDING_VIEW_SYMBOL,
            BINDING_SUMMARY_SYMBOL,
            "",
        )
    )
    write_text(root / HEADER_REL, header)
    write_text(root / BINDINGS_REL, bindings)
    write_text(root / SCRIPT_REL, Path(__file__).read_text(encoding="utf-8"))

    survey_lines = [
        "# Phase 3 ABI Header Family Survey",
        "",
        "## Status",
        "",
    ]
    survey_lines.extend(f"- `{marker}`" for marker in SURVEY_MARKERS)
    for key, rel in BLOB_MARKERS:
        survey_lines.append(f"- `{key}={git_blob_sha(root / rel)}`")
    survey_lines.extend(
        (
            "",
            "## Current Repo Evidence",
            "",
            "- this dedicated survey stays bounded to one already-landed chrdev family inside the shared Phase 3 ABI packet.",
            "- it fail-closes on one exact status constant pair, one exact budget-flag constant pair, and the landed view-plus-summary type pair across the authoritative C header and curated Zig bindings.",
            "",
        )
    )
    write_text(root / SURVEY_REL, "\n".join(survey_lines))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_header_family_") as tmp_dir:
        root = Path(tmp_dir)

        build_valid_workspace(root)
        assert validate(root) == []
        case_count += 1

        write_text(
            root / HEADER_REL,
            (root / HEADER_REL).read_text(encoding="utf-8").replace(
                f"#define {HEADER_STATUS_SYMBOL} {STATUS_EXPECTED}U\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"header_constant_mismatch:{HEADER_STATUS_SYMBOL}:None!={STATUS_EXPECTED}" in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / BINDINGS_REL,
            (root / BINDINGS_REL).read_text(encoding="utf-8").replace(
                f"pub const {BINDING_BUDGET_SYMBOL}: u32 = {BUDGET_EXPECTED};",
                f"pub const {BINDING_BUDGET_SYMBOL}: u32 = 9;",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"binding_constant_mismatch:{BINDING_BUDGET_SYMBOL}:9!={BUDGET_EXPECTED}" in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                f"- `PHASE3_ABI_HEADER_STATUS_SYMBOL={HEADER_STATUS_SYMBOL}`\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"missing_survey_marker:PHASE3_ABI_HEADER_STATUS_SYMBOL={HEADER_STATUS_SYMBOL}" in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                "PHASE3_ABI_HEADER_BLOB_SHA=",
                "PHASE3_ABI_HEADER_BLOB_SHA=stale-",
                1,
            ),
        )
        issues = validate(root)
        assert any(issue.startswith("stale_blob_marker:PHASE3_ABI_HEADER_BLOB_SHA:") for issue in issues), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / HEADER_REL,
            (root / HEADER_REL).read_text(encoding="utf-8").replace(
                HEADER_VIEW_SYMBOL + "\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert f"missing_header_marker:{HEADER_VIEW_SYMBOL}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / BINDINGS_REL,
            (root / BINDINGS_REL).read_text(encoding="utf-8").replace(
                BINDING_SUMMARY_SYMBOL + "\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert f"missing_binding_marker:{BINDING_SUMMARY_SYMBOL}" in issues, issues
        case_count += 1

    print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one bounded Phase 3 ABI header-family survey against the current authoritative header and curated bindings."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker coverage.")
    parser.add_argument("root", nargs="?", help="Optional repo root override.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.root).resolve() if args.root else ROOT
    issues = validate(repo_root)
    if issues:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY=fail")
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_ISSUES_END")
        return 1

    print("PHASE3_ABI_HEADER_FAMILY_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
