#!/usr/bin/env python3
"""Fail-close the direct Phase 3 ABI header-to-binding parity surface."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

ABI_HEADER = Path("include/zigux/abi.h")
ABI_BINDING = Path("zigux/bindings/abi.zig")

DEFINE_RE = re.compile(
    r"^\s*#define\s+(ZIGUX_[A-Z0-9_]+)\s+([0-9]+)U?\s*$",
    re.MULTILINE,
)
C_STRUCT_RE = re.compile(
    r"(?:typedef\s+)?struct\s+(?P<tag>[A-Za-z0-9_]+)\s*\{(?P<body>.*?)\}\s*(?P<alias>[A-Za-z0-9_]+)?\s*;",
    re.DOTALL,
)
C_FIELD_RE = re.compile(
    r"^\s*(?P<type>uint32_t|uint16_t|uint8_t|int32_t|uintptr_t|size_t)\s+(?P<name>[A-Za-z0-9_]+)\s*;\s*$",
    re.MULTILINE,
)
ZIG_CONST_RE = re.compile(
    r"^\s*pub const\s+(?P<name>[A-Z0-9_]+)\s*:\s*[A-Za-z0-9_]+\s*=\s*(?P<value>[0-9]+)\s*;",
    re.MULTILINE,
)
ZIG_EXTERN_STRUCT_RE = re.compile(
    r"^\s*pub const\s+(?P<name>[A-Za-z0-9_]+)\s*=\s*extern struct\s*\{(?P<body>.*?)^\s*\};",
    re.MULTILINE | re.DOTALL,
)
ZIG_FIELD_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_]+)\s*:\s*(?P<type>u32|u16|u8|i32|usize)\s*,\s*$",
    re.MULTILINE,
)
C_INLINE_HELPER_RE = re.compile(
    r"^\s*static\s+inline\b[^\n(]*\b(?P<name>zigux_[A-Za-z0-9_]+)\s*\(",
    re.MULTILINE,
)
ZIG_FUNCTION_RE = re.compile(
    r"^\s*pub fn\s+(?P<name>[A-Za-z][A-Za-z0-9_]*)\s*\(",
    re.MULTILINE,
)

C_TO_ZIG_TYPE = {
    "uint32_t": "u32",
    "uint16_t": "u16",
    "uint8_t": "u8",
    "int32_t": "i32",
    "uintptr_t": "usize",
    "size_t": "usize",
}

STRUCT_NAME_MAP = {
    "zigux_boundary_header": "BoundaryHeader",
    "zigux_export_status": "ExportStatus",
    "zigux_interop_policy": "InteropPolicy",
    "zigux_notifier_chain_priority_increase": "ChainPriorityIncrease",
    "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view": "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView",
    "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary": "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary",
    "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view": "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView",
    "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary": "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary",
    "zigux_notifier_block": "NotifierBlock",
    "zigux_list_head": "ListHead",
    "zigux_hlist_head": "HListHead",
    "zigux_hlist_node": "HListNode",
    "zigux_list_backlink_break": "ListBackLinkBreak",
    "zigux_hlist_prev_link_break": "HListPrevLinkBreak",
}

HELPER_NAME_MAP = {
    "zigux_default_header": "defaultHeader",
    "zigux_compatible_header": "compatibleHeader",
    "zigux_abi_version_is_current": "headerHasCurrentAbiVersion",
    "zigux_header_is_canonical": "headerIsCanonical",
    "zigux_header_is_compatible": "headerIsCompatible",
    "zigux_header_extends_boundary": "extendsBoundary",
    "zigux_header_requested_extra_bytes": "requestedExtraBytes",
    "zigux_header_canonicalize": "canonicalizeHeader",
    "zigux_default_interop_policy": "defaultInteropPolicy",
    "zigux_make_status": "makeStatus",
    "zigux_ok_status": "okStatus",
    "zigux_export_status_ok": "statusIsOk",
    "zigux_notifier_chain_has_nonincreasing_priority": "chainHasNonincreasingPriority",
    "zigux_notifier_first_chain_priority_increase": "firstChainPriorityIncrease",
    "zigux_list_has_consistent_backlinks": "listHasConsistentBacklinks",
    "zigux_hlist_has_consistent_prev_links": "hlistHasConsistentPrevLinks",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_header_defines(text: str) -> dict[str, int]:
    return {match.group(1): int(match.group(2)) for match in DEFINE_RE.finditer(text)}


def parse_binding_consts(text: str) -> dict[str, int]:
    return {match.group("name"): int(match.group("value")) for match in ZIG_CONST_RE.finditer(text)}


def parse_c_structs(text: str) -> dict[str, list[tuple[str, str]]]:
    structs: dict[str, list[tuple[str, str]]] = {}
    for match in C_STRUCT_RE.finditer(text):
        name = match.group("alias") or match.group("tag")
        fields = [
            (field.group("name"), C_TO_ZIG_TYPE[field.group("type")])
            for field in C_FIELD_RE.finditer(match.group("body"))
        ]
        if fields:
            structs[name] = fields
    return structs


def parse_zig_structs(text: str) -> dict[str, list[tuple[str, str]]]:
    structs: dict[str, list[tuple[str, str]]] = {}
    for match in ZIG_EXTERN_STRUCT_RE.finditer(text):
        structs[match.group("name")] = [
            (field.group("name"), field.group("type"))
            for field in ZIG_FIELD_RE.finditer(match.group("body"))
        ]
    return structs


def parse_header_helpers(text: str) -> set[str]:
    return {match.group("name") for match in C_INLINE_HELPER_RE.finditer(text)}


def parse_binding_functions(text: str) -> set[str]:
    return {match.group("name") for match in ZIG_FUNCTION_RE.finditer(text)}


def validate_pair(header_text: str, binding_text: str) -> list[str]:
    issues: list[str] = []

    header_defines = parse_header_defines(header_text)
    binding_consts = parse_binding_consts(binding_text)
    for name, value in sorted(header_defines.items()):
        binding_name = name.removeprefix("ZIGUX_")
        if binding_name not in binding_consts:
            issues.append(f"missing binding constant for header define: {name}")
            continue
        if binding_consts[binding_name] != value:
            issues.append(
                f"constant value mismatch for {name}: header={value} binding={binding_consts[binding_name]}"
            )

    c_structs = parse_c_structs(header_text)
    zig_structs = parse_zig_structs(binding_text)
    for c_name, zig_name in STRUCT_NAME_MAP.items():
        c_fields = c_structs.get(c_name)
        if c_fields is None:
            issues.append(f"missing header struct: {c_name}")
            continue
        zig_fields = zig_structs.get(zig_name)
        if zig_fields is None:
            issues.append(f"missing binding extern struct: {zig_name}")
            continue
        if c_fields != zig_fields:
            issues.append(
                f"struct field parity mismatch for {c_name} -> {zig_name}: "
                f"header={c_fields!r} binding={zig_fields!r}"
            )

    header_helpers = parse_header_helpers(header_text)
    binding_functions = parse_binding_functions(binding_text)
    for header_name, binding_name in sorted(HELPER_NAME_MAP.items()):
        if header_name not in header_helpers:
            issues.append(f"missing header helper: {header_name}")
            continue
        if binding_name not in binding_functions:
            issues.append(
                f"missing binding helper for header helper: {header_name} -> {binding_name}"
            )

    return issues


def validate_repo(repo_root: Path) -> list[str]:
    header_path = repo_root / ABI_HEADER
    binding_path = repo_root / ABI_BINDING
    issues: list[str] = []
    if not header_path.is_file():
        issues.append(f"missing repo file: {ABI_HEADER.as_posix()}")
    if not binding_path.is_file():
        issues.append(f"missing repo file: {ABI_BINDING.as_posix()}")
    if issues:
        return issues
    return validate_pair(_read(header_path), _read(binding_path))


def run_self_test() -> None:
    good_header = """\
#define ZIGUX_ABI_VERSION 1U
#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_STATUS_FLAG_ERROR 1U

typedef struct zigux_boundary_header {
    uint32_t size;
    uint16_t abi_version;
    uint16_t flags;
} zigux_boundary_header;

struct zigux_export_status {
    int32_t code;
    uint16_t facility;
    uint16_t flags;
};

struct zigux_interop_policy {
    uint8_t panic_mode;
    uint8_t allocator_mode;
    uint8_t unsafe_scope;
    uint8_t reserved;
};

struct zigux_notifier_block {
    uintptr_t notifier_call;
    uintptr_t next;
    int32_t priority;
};

typedef struct zigux_notifier_chain_priority_increase {
    size_t previous_index;
    size_t current_index;
    int32_t previous_priority;
    int32_t current_priority;
} zigux_notifier_chain_priority_increase;

struct zigux_list_head {
    uintptr_t next;
    uintptr_t prev;
};

struct zigux_hlist_head {
    uintptr_t first;
};

struct zigux_hlist_node {
    uintptr_t next;
    uintptr_t pprev;
};

typedef struct zigux_list_backlink_break {
    size_t current_index;
    uintptr_t expected_prev;
    uintptr_t actual_prev;
} zigux_list_backlink_break;

typedef struct zigux_hlist_prev_link_break {
    size_t current_index;
    uintptr_t expected_pprev;
    uintptr_t actual_pprev;
} zigux_hlist_prev_link_break;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
    uint32_t ack_window;
    uint32_t delivery_window;
    uint32_t status;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
    uint32_t applied;
    uint32_t skipped;
    uint32_t delivered;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
    uint32_t budget;
    uint32_t window;
    uint32_t flags;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
    uint32_t attempted;
    uint32_t applied;
    uint32_t skipped;
};

static inline zigux_boundary_header zigux_default_header(uint16_t flags) { return (zigux_boundary_header){0}; }
static inline zigux_boundary_header zigux_compatible_header(uint32_t size, uint16_t flags) { return zigux_default_header(flags); }
static inline int zigux_abi_version_is_current(uint16_t abi_version) { return abi_version == 1; }
static inline int zigux_header_is_canonical(zigux_boundary_header header) { return header.size == 0; }
static inline int zigux_header_is_compatible(zigux_boundary_header header) { return header.size == 0; }
static inline int zigux_header_extends_boundary(zigux_boundary_header header) { return header.size == 0; }
static inline uint32_t zigux_header_requested_extra_bytes(zigux_boundary_header header) { return header.size; }
static inline zigux_boundary_header zigux_header_canonicalize(zigux_boundary_header header) { return header; }
static inline struct zigux_interop_policy zigux_default_interop_policy(void) { return (struct zigux_interop_policy){0}; }
static inline struct zigux_export_status zigux_make_status(int32_t code, uint16_t facility) { return (struct zigux_export_status){0}; }
static inline struct zigux_export_status zigux_ok_status(uint16_t facility) { return (struct zigux_export_status){0}; }
static inline int zigux_export_status_ok(struct zigux_export_status status) { return status.flags == 0; }
static inline int zigux_notifier_chain_has_nonincreasing_priority(const struct zigux_notifier_block *head) { return head != 0; }
static inline int zigux_notifier_first_chain_priority_increase(const struct zigux_notifier_block *head, zigux_notifier_chain_priority_increase *out) { return out != 0 || head != 0; }
static inline int zigux_list_has_consistent_backlinks(const struct zigux_list_head *head) { return head != 0; }
static inline int zigux_hlist_has_consistent_prev_links(const struct zigux_hlist_head *head) { return head != 0; }
"""

    good_binding = """\
pub const ABI_VERSION: u16 = 1;
pub const FACILITY_KERNEL: u16 = 1;
pub const STATUS_FLAG_ERROR: u16 = 1;

pub const BoundaryHeader = extern struct {
    size: u32,
    abi_version: u16,
    flags: u16,
};

pub const ExportStatus = extern struct {
    code: i32,
    facility: u16,
    flags: u16,
};

pub const InteropPolicy = extern struct {
    panic_mode: u8,
    allocator_mode: u8,
    unsafe_scope: u8,
    reserved: u8,
};

pub const NotifierBlock = extern struct {
    notifier_call: usize,
    next: usize,
    priority: i32,
};

pub const ChainPriorityIncrease = extern struct {
    previous_index: usize,
    current_index: usize,
    previous_priority: i32,
    current_priority: i32,
};

pub const ListHead = extern struct {
    next: usize,
    prev: usize,
};

pub const HListHead = extern struct {
    first: usize,
};

pub const HListNode = extern struct {
    next: usize,
    pprev: usize,
};

pub const ListBackLinkBreak = extern struct {
    current_index: usize,
    expected_prev: usize,
    actual_prev: usize,
};

pub const HListPrevLinkBreak = extern struct {
    current_index: usize,
    expected_pprev: usize,
    actual_pprev: usize,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {
    ack_window: u32,
    delivery_window: u32,
    status: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {
    applied: u32,
    skipped: u32,
    delivered: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView = extern struct {
    budget: u32,
    window: u32,
    flags: u32,
};

pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary = extern struct {
    attempted: u32,
    applied: u32,
    skipped: u32,
};

pub fn defaultHeader(flags: u16) BoundaryHeader { _ = flags; return undefined; }
pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader { _ = .{ size, flags }; return undefined; }
pub fn headerHasCurrentAbiVersion(abi_version: u16) bool { return abi_version == 1; }
pub fn headerIsCanonical(header: BoundaryHeader) bool { _ = header; return true; }
pub fn headerIsCompatible(header: BoundaryHeader) bool { _ = header; return true; }
pub fn extendsBoundary(header: BoundaryHeader) bool { _ = header; return false; }
pub fn requestedExtraBytes(header: BoundaryHeader) u32 { _ = header; return 0; }
pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader { return header; }
pub fn defaultInteropPolicy() InteropPolicy { return undefined; }
pub fn makeStatus(code: i32, facility: u16) ExportStatus { _ = .{ code, facility }; return undefined; }
pub fn okStatus(facility: u16) ExportStatus { _ = facility; return undefined; }
pub fn statusIsOk(status: ExportStatus) bool { _ = status; return true; }
pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool { _ = head; return true; }
pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease { _ = head; return null; }
pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool { _ = head; return true; }
pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool { _ = head; return true; }
"""

    mismatch_constant_binding = good_binding.replace(
        "pub const STATUS_FLAG_ERROR: u16 = 1;",
        "pub const STATUS_FLAG_ERROR: u16 = 2;",
    )
    mismatch_struct_binding = good_binding.replace(
        "allocator_mode: u8,\n    unsafe_scope: u8,",
        "unsafe_scope: u8,\n    allocator_mode: u8,",
    )
    missing_helper_binding = good_binding.replace(
        "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader { return header; }\n",
        "",
    )

    cases = (
        (good_header, good_binding, []),
        (
            good_header,
            mismatch_constant_binding,
            ["constant value mismatch for ZIGUX_STATUS_FLAG_ERROR: header=1 binding=2"],
        ),
        (
            good_header,
            mismatch_struct_binding,
            ["struct field parity mismatch for zigux_interop_policy -> InteropPolicy:"],
        ),
        (
            good_header,
            missing_helper_binding,
            ["missing binding helper for header helper: zigux_header_canonicalize -> canonicalizeHeader"],
        ),
    )

    for header_text, binding_text, expected_substrings in cases:
        issues = validate_pair(header_text, binding_text)
        if not expected_substrings:
            if issues:
                raise SystemExit(f"unexpected self-test issues: {issues}")
            continue
        if not issues:
            raise SystemExit(f"expected self-test issues for case: {expected_substrings}")
        for needle in expected_substrings:
            if not any(needle in issue for issue in issues):
                raise SystemExit(
                    f"self-test expected issue containing {needle!r}, got: {issues!r}"
                )

    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_root = Path(tmp_dir)
        _write(repo_root / ABI_HEADER, good_header)
        _write(repo_root / ABI_BINDING, good_binding)
        repo_issues = validate_repo(repo_root)
        if repo_issues:
            raise SystemExit(f"unexpected repo self-test issues: {repo_issues}")

    print("PHASE3_ABI_HEADER_BINDING_PARITY_SELF_TEST=pass")
    print(f"PHASE3_ABI_HEADER_BINDING_PARITY_SELF_TEST_CASE_COUNT={len(cases) + 1}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    issues = validate_repo(args.repo_root)
    if issues:
        for issue in issues:
            print(f"PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE={issue}")
        print("PHASE3_ABI_HEADER_BINDING_PARITY=fail")
        print(f"PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE_COUNT={len(issues)}")
        return 1

    print("PHASE3_ABI_HEADER_BINDING_PARITY=pass")
    print(f"PHASE3_ABI_HEADER_BINDING_PARITY_HEADER_DEFINE_COUNT={len(parse_header_defines(_read(args.repo_root / ABI_HEADER)))}")
    print(f"PHASE3_ABI_HEADER_BINDING_PARITY_STRUCT_COUNT={len(STRUCT_NAME_MAP)}")
    print(f"PHASE3_ABI_HEADER_BINDING_PARITY_HELPER_COUNT={len(HELPER_NAME_MAP)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
