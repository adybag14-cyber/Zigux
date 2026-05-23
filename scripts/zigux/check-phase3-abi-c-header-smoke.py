#!/usr/bin/env python3
"""Compile and run the current Phase 3 shared ABI C header smoke."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

SMOKE_PATH = Path("zigux/tests/phase3_abi_c_header_smoke.c")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_DUMP_PATH = Path("zigux/tests/phase3_abi_dump_current.zig")

REQUIRED_MARKERS = {
    SMOKE_PATH: (
        "#include <zigux/abi.h>",
        "static int check_header_helpers(void)",
        "zigux_default_header(",
        "zigux_compatible_header(",
        "zigux_header_canonicalize(",
        "static int check_status_and_policy_helpers(void)",
        "zigux_default_interop_policy()",
        "zigux_ok_status(",
        "zigux_make_status(",
        "zigux_export_status_ok(",
        "static int check_notifier_and_list_helpers(void)",
        "zigux_notifier_chain_has_nonincreasing_priority(",
        "zigux_notifier_first_chain_priority_increase(",
        "zigux_list_has_consistent_backlinks(",
        "zigux_hlist_has_consistent_prev_links(",
        "static int check_chrdev_layout_helpers(void)",
        "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view",
        "int main(void)",
    ),
    ABI_HEADER_PATH: (
        "#define ZIGUX_ABI_VERSION 1U",
        "struct zigux_export_status {",
        "struct zigux_interop_policy {",
        "struct zigux_notifier_block {",
        "struct zigux_list_head {",
        "struct zigux_hlist_head {",
        "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {",
        "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
        "static inline struct zigux_interop_policy zigux_default_interop_policy(void)",
        "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
        "static inline int zigux_list_has_consistent_backlinks(",
        "static inline int zigux_hlist_has_consistent_prev_links(",
    ),
    ABI_DUMP_PATH: (
        'const default_header = abi.defaultHeader(0);',
        'const policy = abi.defaultInteropPolicy();',
        '"boundary_header"',
        '"export_status"',
        '"chrdev_budget_window"',
        '"interop_policy"',
        '"facility"',
        '"notifier"',
    ),
}

SELFTEST_ABI_HEADER = """#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

#include <stddef.h>
#include <stdint.h>

#define ZIGUX_ABI_VERSION 1U
#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_FACILITY_HELPERS 2U
#define ZIGUX_FACILITY_DRIVERS 3U
#define ZIGUX_STATUS_FLAG_ERROR 1U
#define ZIGUX_PANIC_ABORT 0U
#define ZIGUX_PANIC_BUG 1U
#define ZIGUX_PANIC_WARN 2U
#define ZIGUX_ALLOC_CALLER_PROVIDED 0U
#define ZIGUX_ALLOC_KERNEL_HEAP 1U
#define ZIGUX_ALLOC_ARENA 2U
#define ZIGUX_UNSAFE_NONE 0U
#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U
#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED 1U

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

typedef struct zigux_notifier_chain_priority_increase {
    size_t previous_index;
    size_t current_index;
    int32_t previous_priority;
    int32_t current_priority;
} zigux_notifier_chain_priority_increase;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
    uint32_t ack_window;
    uint32_t delivery_window;
    uint32_t status;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
    uint32_t applied;
    uint32_t skipped;
    uint32_t delivered;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
    uint32_t budget;
    uint32_t window;
    uint32_t flags;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
    uint32_t attempted;
    uint32_t applied;
    uint32_t skipped;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary
    zigux_chrdev_notify_ack_window_policy_budget_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY;

struct zigux_notifier_block {
    uintptr_t notifier_call;
    uintptr_t next;
    int32_t priority;
};

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

static inline zigux_boundary_header zigux_default_header(uint16_t flags)
{
    zigux_boundary_header header = {
        .size = (uint32_t)sizeof(zigux_boundary_header),
        .abi_version = (uint16_t)ZIGUX_ABI_VERSION,
        .flags = flags,
    };
    return header;
}

static inline zigux_boundary_header zigux_compatible_header(uint32_t size, uint16_t flags)
{
    zigux_boundary_header header = zigux_default_header(flags);
    header.size = size;
    return header;
}

static inline int zigux_abi_version_is_current(uint16_t abi_version)
{
    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;
}

static inline int zigux_header_is_canonical(zigux_boundary_header header)
{
    return header.size == (uint32_t)sizeof(zigux_boundary_header) &&
        zigux_abi_version_is_current(header.abi_version);
}

static inline int zigux_header_is_compatible(zigux_boundary_header header)
{
    return header.size >= (uint32_t)sizeof(zigux_boundary_header) &&
        zigux_abi_version_is_current(header.abi_version);
}

static inline int zigux_header_extends_boundary(zigux_boundary_header header)
{
    return zigux_header_is_compatible(header) &&
        !zigux_header_is_canonical(header);
}

static inline uint32_t zigux_header_requested_extra_bytes(zigux_boundary_header header)
{
    if (!zigux_header_extends_boundary(header))
        return 0;
    return header.size - (uint32_t)sizeof(zigux_boundary_header);
}

static inline zigux_boundary_header zigux_header_canonicalize(zigux_boundary_header header)
{
    header.size = (uint32_t)sizeof(zigux_boundary_header);
    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;
    return header;
}

static inline struct zigux_interop_policy zigux_default_interop_policy(void)
{
    struct zigux_interop_policy policy = {
        .panic_mode = (uint8_t)ZIGUX_PANIC_ABORT,
        .allocator_mode = (uint8_t)ZIGUX_ALLOC_CALLER_PROVIDED,
        .unsafe_scope = (uint8_t)ZIGUX_UNSAFE_NONE,
        .reserved = 0,
    };
    return policy;
}

static inline struct zigux_export_status zigux_make_status(int32_t code, uint16_t facility)
{
    struct zigux_export_status status = {
        .code = code,
        .facility = facility,
        .flags = (uint16_t)(code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0U),
    };
    return status;
}

static inline struct zigux_export_status zigux_ok_status(uint16_t facility)
{
    return zigux_make_status(0, facility);
}

static inline int zigux_export_status_ok(struct zigux_export_status status)
{
    return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0;
}

static inline int zigux_notifier_chain_has_nonincreasing_priority(
    const struct zigux_notifier_block *head)
{
    int32_t previous_priority;
    const struct zigux_notifier_block *node;

    if (!head)
        return 1;

    previous_priority = head->priority;
    while (head->next != (uintptr_t)0) {
        node = (const struct zigux_notifier_block *)(uintptr_t)head->next;
        if (node->priority > previous_priority)
            return 0;
        previous_priority = node->priority;
        head = node;
    }

    return 1;
}

static inline int zigux_notifier_first_chain_priority_increase(
    const struct zigux_notifier_block *head,
    zigux_notifier_chain_priority_increase *out)
{
    size_t previous_index = 0;
    int32_t previous_priority;

    if (!head || head->next == (uintptr_t)0 || !out)
        return 0;

    previous_priority = head->priority;
    while (head->next != (uintptr_t)0) {
        const struct zigux_notifier_block *node =
            (const struct zigux_notifier_block *)(uintptr_t)head->next;
        const size_t current_index = previous_index + 1;
        if (node->priority > previous_priority) {
            out->previous_index = previous_index;
            out->current_index = current_index;
            out->previous_priority = previous_priority;
            out->current_priority = node->priority;
            return 1;
        }
        previous_index = current_index;
        previous_priority = node->priority;
        head = node;
    }

    return 0;
}

static inline int zigux_list_first_broken_backlink(
    const struct zigux_list_head *head,
    zigux_list_backlink_break *out)
{
    uintptr_t expected_prev;
    size_t current_index = 0;
    const struct zigux_list_head *cursor;

    if (!head)
        return 0;

    expected_prev = (uintptr_t)head;
    cursor = (const struct zigux_list_head *)(uintptr_t)head->next;
    while (cursor && cursor != head) {
        if (cursor->prev != expected_prev) {
            if (out) {
                out->current_index = current_index;
                out->expected_prev = expected_prev;
                out->actual_prev = cursor->prev;
            }
            return 1;
        }
        expected_prev = (uintptr_t)cursor;
        current_index += 1;
        cursor = (const struct zigux_list_head *)(uintptr_t)cursor->next;
    }

    if (!cursor) {
        if (out) {
            out->current_index = current_index;
            out->expected_prev = expected_prev;
            out->actual_prev = 0;
        }
        return 1;
    }

    if (head->prev != expected_prev) {
        if (out) {
            out->current_index = current_index;
            out->expected_prev = expected_prev;
            out->actual_prev = head->prev;
        }
        return 1;
    }

    return 0;
}

static inline int zigux_list_has_consistent_backlinks(
    const struct zigux_list_head *head)
{
    return head != NULL && zigux_list_first_broken_backlink(head, NULL) == 0;
}

static inline int zigux_hlist_first_broken_prev_link(
    const struct zigux_hlist_head *head,
    zigux_hlist_prev_link_break *out)
{
    uintptr_t expected_pprev;
    size_t current_index = 0;
    const struct zigux_hlist_node *cursor;

    if (!head)
        return 0;

    expected_pprev = (uintptr_t)&head->first;
    cursor = (const struct zigux_hlist_node *)(uintptr_t)head->first;
    while (cursor) {
        if (cursor->pprev != expected_pprev) {
            if (out) {
                out->current_index = current_index;
                out->expected_pprev = expected_pprev;
                out->actual_pprev = cursor->pprev;
            }
            return 1;
        }
        expected_pprev = (uintptr_t)&cursor->next;
        current_index += 1;
        cursor = (const struct zigux_hlist_node *)(uintptr_t)cursor->next;
    }

    return 0;
}

static inline int zigux_hlist_has_consistent_prev_links(
    const struct zigux_hlist_head *head)
{
    return head != NULL && zigux_hlist_first_broken_prev_link(head, NULL) == 0;
}

#endif
"""

SELFTEST_ABI_DUMP = """const abi = @import("abi_bindings");
const default_header = abi.defaultHeader(0);
const policy = abi.defaultInteropPolicy();
"boundary_header"
"export_status"
"chrdev_budget_window"
"interop_policy"
"facility"
"notifier"
"""

SELFTEST_SMOKE = """#include <stddef.h>
#include <zigux/abi.h>

static int check_header_helpers(void)
{
    zigux_boundary_header canonical = zigux_default_header(0x41u);
    zigux_boundary_header compatible =
        zigux_compatible_header((uint32_t)sizeof(zigux_boundary_header) + 8u, 0x41u);
    zigux_boundary_header stale = canonical;
    zigux_boundary_header canonicalized;

    stale.abi_version += 1u;
    canonicalized = zigux_header_canonicalize(compatible);

    if (!zigux_abi_version_is_current(canonical.abi_version))
        return __LINE__;
    if (!zigux_header_is_canonical(canonical))
        return __LINE__;
    if (!zigux_header_is_compatible(canonical))
        return __LINE__;
    if (zigux_header_extends_boundary(canonical))
        return __LINE__;
    if (zigux_header_requested_extra_bytes(canonical) != 0u)
        return __LINE__;

    if (zigux_header_is_canonical(compatible))
        return __LINE__;
    if (!zigux_header_is_compatible(compatible))
        return __LINE__;
    if (!zigux_header_extends_boundary(compatible))
        return __LINE__;
    if (zigux_header_requested_extra_bytes(compatible) != 8u)
        return __LINE__;

    if (zigux_header_is_compatible(stale))
        return __LINE__;
    if (!zigux_header_is_canonical(canonicalized))
        return __LINE__;
    if (canonicalized.flags != compatible.flags)
        return __LINE__;

    return 0;
}

static int check_status_and_policy_helpers(void)
{
    struct zigux_interop_policy policy = zigux_default_interop_policy();
    struct zigux_export_status ok = zigux_ok_status((uint16_t)ZIGUX_FACILITY_HELPERS);
    struct zigux_export_status err = zigux_make_status(-22, (uint16_t)ZIGUX_FACILITY_KERNEL);

    if (sizeof(struct zigux_interop_policy) != 4u)
        return __LINE__;
    if (offsetof(struct zigux_interop_policy, panic_mode) != 0u)
        return __LINE__;
    if (offsetof(struct zigux_interop_policy, allocator_mode) != 1u)
        return __LINE__;
    if (policy.panic_mode != ZIGUX_PANIC_ABORT)
        return __LINE__;
    if (policy.allocator_mode != ZIGUX_ALLOC_CALLER_PROVIDED)
        return __LINE__;
    if (policy.unsafe_scope != ZIGUX_UNSAFE_NONE)
        return __LINE__;
    if (policy.reserved != 0u)
        return __LINE__;
    if (!zigux_export_status_ok(ok))
        return __LINE__;
    if (zigux_export_status_ok(err))
        return __LINE__;
    if (err.flags != ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;

    return 0;
}

static int check_notifier_and_list_helpers(void)
{
    struct zigux_notifier_block tail = { .notifier_call = 0, .next = 0, .priority = 7 };
    struct zigux_notifier_block head = {
        .notifier_call = 0,
        .next = (uintptr_t)&tail,
        .priority = 3,
    };
    zigux_notifier_chain_priority_increase increase;
    struct zigux_list_head list_head = { .next = 0, .prev = 0 };
    struct zigux_list_head list_first = { .next = 0, .prev = 0 };
    struct zigux_list_head list_second = { .next = 0, .prev = 0 };
    zigux_list_backlink_break list_break;
    struct zigux_hlist_head hlist_head = { .first = 0 };
    struct zigux_hlist_node hlist_first = { .next = 0, .pprev = 0 };
    struct zigux_hlist_node hlist_second = { .next = 0, .pprev = 0 };
    zigux_hlist_prev_link_break hlist_break;

    if (zigux_notifier_chain_has_nonincreasing_priority(&head))
        return __LINE__;
    if (!zigux_notifier_first_chain_priority_increase(&head, &increase))
        return __LINE__;
    if (increase.previous_index != 0u || increase.current_index != 1u)
        return __LINE__;
    if (increase.previous_priority != 3 || increase.current_priority != 7)
        return __LINE__;

    list_head.next = (uintptr_t)&list_first;
    list_head.prev = (uintptr_t)&list_second;
    list_first.next = (uintptr_t)&list_second;
    list_first.prev = (uintptr_t)&list_head;
    list_second.next = (uintptr_t)&list_head;
    list_second.prev = (uintptr_t)&list_head;
    if (zigux_list_has_consistent_backlinks(&list_head))
        return __LINE__;
    if (!zigux_list_first_broken_backlink(&list_head, &list_break))
        return __LINE__;
    if (list_break.current_index != 1u)
        return __LINE__;

    hlist_head.first = (uintptr_t)&hlist_first;
    hlist_first.next = (uintptr_t)&hlist_second;
    hlist_first.pprev = (uintptr_t)&hlist_head.first;
    hlist_second.next = 0;
    hlist_second.pprev = (uintptr_t)&hlist_head.first;
    if (zigux_hlist_has_consistent_prev_links(&hlist_head))
        return __LINE__;
    if (!zigux_hlist_first_broken_prev_link(&hlist_head, &hlist_break))
        return __LINE__;
    if (hlist_break.current_index != 1u)
        return __LINE__;

    return 0;
}

static int check_chrdev_layout_helpers(void)
{
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view view = {
        .ack_window = 7u,
        .delivery_window = 11u,
        .status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };

    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED != 1u)
        return __LINE__;
    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED != 1u)
        return __LINE__;
    if (sizeof(view) != 12u)
        return __LINE__;
    if (offsetof(
            zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view,
            status) != 8u)
        return __LINE__;

    return 0;
}

int main(void)
{
    int rc = check_header_helpers();
    if (rc != 0)
        return rc;

    rc = check_status_and_policy_helpers();
    if (rc != 0)
        return rc;

    rc = check_notifier_and_list_helpers();
    if (rc != 0)
        return rc;

    rc = check_chrdev_layout_helpers();
    if (rc != 0)
        return rc;

    return 0;
}
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _compile_and_run(repo_root: Path, cc: str) -> list[str]:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_c_") as temp_dir:
        exe_path = Path(temp_dir) / "phase3_abi_c_header_smoke"
        compile_result = subprocess.run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                f"-I{(repo_root / 'include').as_posix()}",
                (repo_root / SMOKE_PATH).as_posix(),
                "-o",
                exe_path.as_posix(),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            issues.append(
                "phase3 abi c header smoke failed to compile: "
                + compile_result.stderr.strip()
            )
            return issues

        run_result = subprocess.run(
            [exe_path.as_posix()],
            check=False,
            capture_output=True,
            text=True,
        )
        if run_result.returncode != 0:
            issues.append(
                "phase3 abi c header smoke failed at runtime: "
                + f"exit {run_result.returncode}"
            )
    return issues


def validate_repo(repo_root: Path, cc: str) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    if issues:
        return issues

    return _compile_and_run(repo_root, cc)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_c_selftest_") as temp_dir:
        root = Path(temp_dir)
        _write(root / ABI_HEADER_PATH, SELFTEST_ABI_HEADER)
        _write(root / ABI_DUMP_PATH, SELFTEST_ABI_DUMP)
        _write(root / SMOKE_PATH, SELFTEST_SMOKE)

        issues = validate_repo(root, "cc")
        if issues:
            print("PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        broken_smoke = _read(root / SMOKE_PATH).replace(
            "zigux_default_interop_policy()",
            "",
            1,
        )
        _write(root / SMOKE_PATH, broken_smoke)
        issues = validate_repo(root, "cc")
        expected = (
            "missing zigux/tests/phase3_abi_c_header_smoke.c marker: "
            "zigux_default_interop_policy()"
        )
        if expected not in issues:
            print("PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing smoke marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        broken_header = _read(root / ABI_HEADER_PATH).replace(
            "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
            "",
            1,
        )
        _write(root / ABI_HEADER_PATH, broken_header)
        issues = validate_repo(root, "cc")
        expected = (
            "missing include/zigux/abi.h marker: "
            "static inline int zigux_notifier_chain_has_nonincreasing_priority("
        )
        if expected not in issues:
            print("PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing header marker was not reported")
            return 1

        _write(root / ABI_HEADER_PATH, SELFTEST_ABI_HEADER)
        broken_dump = _read(root / ABI_DUMP_PATH).replace(
            '"notifier"',
            "",
            1,
        )
        _write(root / ABI_DUMP_PATH, broken_dump)
        issues = validate_repo(root, "cc")
        expected = 'missing zigux/tests/phase3_abi_dump_current.zig marker: "notifier"'
        if expected not in issues:
            print("PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing dump marker was not reported")
            return 1

    print("PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST=pass")
    print("PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile and run the current Phase 3 shared ABI C header smoke."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains include/ and zigux/tests/",
    )
    parser.add_argument(
        "--cc",
        default="cc",
        help="C compiler to use for the focused smoke build",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root, args.cc)
    if issues:
        print("PHASE3_ABI_C_HEADER_SMOKE=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SMOKE_PATH}")
    print("PHASE3_ABI_C_HEADER_SMOKE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
