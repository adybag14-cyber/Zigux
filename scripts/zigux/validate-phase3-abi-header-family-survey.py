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

FAMILY_ENTRIES = (
    {
        "slug": "delivery_window",
        "header_status_symbol": "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
        "binding_status_symbol": "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED",
        "status_expected": 6,
        "header_budget_symbol": "ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED",
        "binding_budget_symbol": "CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED",
        "budget_expected": 1,
        "header_view_symbol": "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {",
        "binding_view_symbol": "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {",
        "header_summary_symbol": "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {",
        "binding_summary_symbol": "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {",
    },
    {
        "slug": "delivery_budget_guard",
        "header_status_symbol": "ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_HELD",
        "binding_status_symbol": "CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_HELD",
        "status_expected": 7,
        "header_budget_symbol": "ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_BUDGET_FLAG_BUDGET_APPLIED",
        "binding_budget_symbol": "CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_BUDGET_FLAG_BUDGET_APPLIED",
        "budget_expected": 1,
        "header_view_symbol": "struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_view {",
        "binding_view_symbol": "pub const ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView = extern struct {",
        "header_summary_symbol": "struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_summary {",
        "binding_summary_symbol": "pub const ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary = extern struct {",
    },
)

SELF_TEST_CASE_COUNT = 9

HEADER_DEFINE_RE = re.compile(r"^#define\s+(?P<name>[A-Z0-9_]+)\s+(?P<value>[0-9xa-fA-F]+)U?$")
BINDING_CONST_RE = re.compile(r"^pub const (?P<name>[A-Z0-9_]+): [^=]+ = (?P<value>[0-9xa-fA-F]+);$")

SURVEY_MARKERS = (
    "PHASE3_ABI_HEADER_FAMILY=chrdev_notify_ack_window_policy_budget_window_delivery_window-plus-delivery_budget_guard_window_policy_budget_window_delivery",
    f"PHASE3_ABI_HEADER_PATH={HEADER_REL}",
    f"PHASE3_ABI_BINDINGS_PATH={BINDINGS_REL}",
    f"PHASE3_ABI_HEADER_FAMILY_SURVEY_PATH={SCRIPT_REL}",
    "PHASE3_ABI_HEADER_FAMILY_SURVEY_SCOPE=two bounded adjacent chrdev notify ack header-family footholds inside the shared phase3 abi packet",
    f"PHASE3_ABI_HEADER_PRIMARY_STATUS_SYMBOL={FAMILY_ENTRIES[0]['header_status_symbol']}",
    f"PHASE3_ABI_BINDING_PRIMARY_STATUS_SYMBOL={FAMILY_ENTRIES[0]['binding_status_symbol']}",
    f"PHASE3_ABI_HEADER_PRIMARY_BUDGET_SYMBOL={FAMILY_ENTRIES[0]['header_budget_symbol']}",
    f"PHASE3_ABI_BINDING_PRIMARY_BUDGET_SYMBOL={FAMILY_ENTRIES[0]['binding_budget_symbol']}",
    f"PHASE3_ABI_HEADER_PRIMARY_VIEW_SYMBOL={FAMILY_ENTRIES[0]['header_view_symbol']}",
    f"PHASE3_ABI_BINDING_PRIMARY_VIEW_SYMBOL={FAMILY_ENTRIES[0]['binding_view_symbol']}",
    f"PHASE3_ABI_HEADER_PRIMARY_SUMMARY_SYMBOL={FAMILY_ENTRIES[0]['header_summary_symbol']}",
    f"PHASE3_ABI_BINDING_PRIMARY_SUMMARY_SYMBOL={FAMILY_ENTRIES[0]['binding_summary_symbol']}",
    f"PHASE3_ABI_HEADER_ADJACENT_STATUS_SYMBOL={FAMILY_ENTRIES[1]['header_status_symbol']}",
    f"PHASE3_ABI_BINDING_ADJACENT_STATUS_SYMBOL={FAMILY_ENTRIES[1]['binding_status_symbol']}",
    f"PHASE3_ABI_HEADER_ADJACENT_BUDGET_SYMBOL={FAMILY_ENTRIES[1]['header_budget_symbol']}",
    f"PHASE3_ABI_BINDING_ADJACENT_BUDGET_SYMBOL={FAMILY_ENTRIES[1]['binding_budget_symbol']}",
    f"PHASE3_ABI_HEADER_ADJACENT_VIEW_SYMBOL={FAMILY_ENTRIES[1]['header_view_symbol']}",
    f"PHASE3_ABI_BINDING_ADJACENT_VIEW_SYMBOL={FAMILY_ENTRIES[1]['binding_view_symbol']}",
    f"PHASE3_ABI_HEADER_ADJACENT_SUMMARY_SYMBOL={FAMILY_ENTRIES[1]['header_summary_symbol']}",
    f"PHASE3_ABI_BINDING_ADJACENT_SUMMARY_SYMBOL={FAMILY_ENTRIES[1]['binding_summary_symbol']}",
    "PHASE3_ABI_HEADER_FAMILY_GATE=python3 scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "PHASE3_ABI_HEADER_FAMILY_NEXT_STEP=extend-the-landed-delivery-budget-guard-packet-one-foothold-at-a-time-before-widening-the-phase3-abi-surface",
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

    for entry in FAMILY_ENTRIES:
        header_status = header_constants.get(entry["header_status_symbol"])
        if header_status != entry["status_expected"]:
            issues.append(
                f"header_constant_mismatch:{entry['header_status_symbol']}:{header_status}!={entry['status_expected']}"
            )

        binding_status = binding_constants.get(entry["binding_status_symbol"])
        if binding_status != entry["status_expected"]:
            issues.append(
                f"binding_constant_mismatch:{entry['binding_status_symbol']}:{binding_status}!={entry['status_expected']}"
            )

        header_budget = header_constants.get(entry["header_budget_symbol"])
        if header_budget != entry["budget_expected"]:
            issues.append(
                f"header_constant_mismatch:{entry['header_budget_symbol']}:{header_budget}!={entry['budget_expected']}"
            )

        binding_budget = binding_constants.get(entry["binding_budget_symbol"])
        if binding_budget != entry["budget_expected"]:
            issues.append(
                f"binding_constant_mismatch:{entry['binding_budget_symbol']}:{binding_budget}!={entry['budget_expected']}"
            )

        for marker in (entry["header_view_symbol"], entry["header_summary_symbol"]):
            if marker not in header_source:
                issues.append(f"missing_header_marker:{marker}")
        for marker in (entry["binding_view_symbol"], entry["binding_summary_symbol"]):
            if marker not in bindings_source:
                issues.append(f"missing_binding_marker:{marker}")

    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_valid_workspace(root: Path) -> None:
    header_lines: list[str] = []
    bindings_lines: list[str] = []
    for entry in FAMILY_ENTRIES:
        header_lines.extend(
            (
                f"#define {entry['header_status_symbol']} {entry['status_expected']}U",
                f"#define {entry['header_budget_symbol']} {entry['budget_expected']}U",
                entry["header_view_symbol"],
                entry["header_summary_symbol"],
            )
        )
        bindings_lines.extend(
            (
                f"pub const {entry['binding_status_symbol']}: u32 = {entry['status_expected']};",
                f"pub const {entry['binding_budget_symbol']}: u32 = {entry['budget_expected']};",
                entry["binding_view_symbol"],
                entry["binding_summary_symbol"],
            )
        )

    write_text(root / HEADER_REL, "\n".join([*header_lines, ""]))
    write_text(root / BINDINGS_REL, "\n".join([*bindings_lines, ""]))
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
            "- this dedicated survey stays bounded to two directly adjacent already-landed chrdev families inside the shared Phase 3 ABI packet.",
            "- it fail-closes on one exact status constant pair, one exact budget-flag constant pair, and one exact view-plus-summary type pair for each landed family across the authoritative C header and curated Zig bindings.",
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
                f"#define {FAMILY_ENTRIES[0]['header_status_symbol']} {FAMILY_ENTRIES[0]['status_expected']}U\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"header_constant_mismatch:{FAMILY_ENTRIES[0]['header_status_symbol']}:None!={FAMILY_ENTRIES[0]['status_expected']}" in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / BINDINGS_REL,
            (root / BINDINGS_REL).read_text(encoding="utf-8").replace(
                f"pub const {FAMILY_ENTRIES[1]['binding_budget_symbol']}: u32 = {FAMILY_ENTRIES[1]['budget_expected']};",
                f"pub const {FAMILY_ENTRIES[1]['binding_budget_symbol']}: u32 = 9;",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"binding_constant_mismatch:{FAMILY_ENTRIES[1]['binding_budget_symbol']}:9!={FAMILY_ENTRIES[1]['budget_expected']}" in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                f"- `PHASE3_ABI_HEADER_ADJACENT_SUMMARY_SYMBOL={FAMILY_ENTRIES[1]['header_summary_symbol']}`\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"missing_survey_marker:PHASE3_ABI_HEADER_ADJACENT_SUMMARY_SYMBOL={FAMILY_ENTRIES[1]['header_summary_symbol']}" in issues
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
                FAMILY_ENTRIES[1]["header_view_symbol"] + "\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert f"missing_header_marker:{FAMILY_ENTRIES[1]['header_view_symbol']}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / BINDINGS_REL,
            (root / BINDINGS_REL).read_text(encoding="utf-8").replace(
                FAMILY_ENTRIES[1]["binding_summary_symbol"] + "\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert f"missing_binding_marker:{FAMILY_ENTRIES[1]['binding_summary_symbol']}" in issues, issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / HEADER_REL,
            (root / HEADER_REL).read_text(encoding="utf-8").replace(
                f"#define {FAMILY_ENTRIES[1]['header_budget_symbol']} {FAMILY_ENTRIES[1]['budget_expected']}U\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        assert (
            f"header_constant_mismatch:{FAMILY_ENTRIES[1]['header_budget_symbol']}:None!={FAMILY_ENTRIES[1]['budget_expected']}" in issues
        ), issues
        build_valid_workspace(root)
        case_count += 1

        write_text(
            root / SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8")
            + f"- `PHASE3_ABI_HEADER_PATH={HEADER_REL}`\n",
        )
        issues = validate(root)
        assert f"duplicate_survey_marker:PHASE3_ABI_HEADER_PATH={HEADER_REL}:2" in issues, issues
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