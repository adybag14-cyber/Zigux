const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_C_HEADER_SMOKE=pass";
pub const self_test_pass_marker = "PHASE3_ABI_C_HEADER_SMOKE_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_tests_phase3_abi_c_header_smoke_c = [_][]const u8{
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
};

const REQUIRED_MARKERS__include_zigux_abi_h = [_][]const u8{
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
};

const REQUIRED_MARKERS__zigux_tests_phase3_abi_dump_current_zig = [_][]const u8{
    "const default_header = abi.defaultHeader(0);",
    "const policy = abi.defaultInteropPolicy();",
    "\"boundary_header\"",
    "\"export_status\"",
    "\"chrdev_budget_window\"",
    "\"interop_policy\"",
    "\"facility\"",
    "\"notifier\"",
};

const SELFTEST_ABI_HEADER = [_][]const u8{
    "#ifndef _ZIGUX_ABI_H\n#define _ZIGUX_ABI_H\n\n#include <stddef.h>\n#include <stdint.h>\n\n#define ZIGUX_ABI_VERSION 1U\n#define ZIGUX_FACILITY_KERNEL 1U\n#define ZIGUX_FACILITY_HELPERS 2U\n#define ZIGUX_FACILITY_DRIVERS 3U\n#define ZIGUX_STATUS_FLAG_ERROR 1U\n#define ZIGUX_PANIC_ABORT 0U\n#define ZIGUX_PANIC_BUG 1U\n#define ZIGUX_PANIC_WARN 2U\n#define ZIGUX_ALLOC_CALLER_PROVIDED 0U\n#define ZIGUX_ALLOC_KERNEL_HEAP 1U\n#define ZIGUX_ALLOC_ARENA 2U\n#define ZIGUX_UNSAFE_NONE 0U\n#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U\n#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U\n#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED 1U\n#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED 1U\n#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED 1U\n#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED 1U\n#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED 1U\n\ntypedef struct zigux_boundary_header {\n    uint32_t size;\n    uint16_t abi_version;\n    uint16_t flags;\n} zigux_boundary_header;\n\nstruct zigux_export_status {\n    int32_t code;\n    uint16_t facility;\n    uint16_t flags;\n};\n\nstruct zigux_interop_policy {\n    uint8_t panic_mode;\n    uint8_t allocator_mode;\n    uint8_t unsafe_scope;\n    uint8_t reserved;\n};\n\ntypedef struct zigux_notifier_chain_priority_increase {\n    size_t previous_index;\n    size_t current_index;\n    int32_t previous_priority;\n    int32_t current_priority;\n} zigux_notifier_chain_priority_increase;\n\nstruct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {\n    uint32_t ack_window;\n    uint32_t delivery_window;\n    uint32_t status;\n};\ntypedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view\n    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view;\n\nstruct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {\n    uint32_t applied;\n    uint32_t skipped;\n    uint32_t delivered;\n};\ntypedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary\n    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary;\n\nstruct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {\n    uint32_t budget;\n    uint32_t window;\n    uint32_t flags;\n};\ntypedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view\n    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view;\n\nstruct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {\n    uint32_t attempted;\n    uint32_t applied;\n    uint32_t skipped;\n};\ntypedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary\n    zigux_chrdev_notify_ack_window_policy_budget_WINDOW_DELIVERY_WINDOW_BUDGET_SUMMARY;\n\nstruct zigux_notifier_block {\n    uintptr_t notifier_call;\n    uintptr_t next;\n    int32_t priority;\n};\n\nstruct zigux_list_head {\n    uintptr_t next;\n    uintptr_t prev;\n};\n\nstruct zigux_hlist_head {\n    uintptr_t first;\n};\n\nstruct zigux_hlist_node {\n    uintptr_t next;\n    uintptr_t pprev;\n};\n\ntypedef struct zigux_list_backlink_break {\n    size_t current_index;\n    uintptr_t expected_prev;\n    uintptr_t actual_prev;\n} zigux_list_backlink_break;\n\ntypedef struct zigux_hlist_prev_link_break {\n    size_t current_index;\n    uintptr_t expected_pprev;\n    uintptr_t actual_pprev;\n} zigux_hlist_prev_link_break;\n\nstatic inline zigux_boundary_header zigux_default_header(uint16_t flags)\n{\n    zigux_boundary_header header = {\n        .size = (uint32_t)sizeof(zigux_boundary_header),\n        .abi_version = (uint16_t)ZIGUX_ABI_VERSION,\n        .flags = flags,\n    };\n    return header;\n}\n\nstatic inline zigux_boundary_header zigux_compatible_header(uint32_t size, uint16_t flags)\n{\n    zigux_boundary_header header = zigux_default_header(flags);\n    header.size = size;\n    return header;\n}\n\nstatic inline int zigux_abi_version_is_current(uint16_t abi_version)\n{\n    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;\n}\n\nstatic inline int zigux_header_is_canonical(zigux_boundary_header header)\n{\n    return header.size == (uint32_t)sizeof(zigux_boundary_header) &&\n        zigux_abi_version_is_current(header.abi_version);\n}\n\nstatic inline int zigux_header_is_compatible(zigux_boundary_header header)\n{\n    return header.size >= (uint32_t)sizeof(zigux_boundary_header) &&\n        zigux_abi_version_is_current(header.abi_version);\n}\n\nstatic inline int zigux_header_extends_boundary(zigux_boundary_header header)\n{\n    return zigux_header_is_compatible(header) &&\n        !zigux_header_is_canonical(header);\n}\n\nstatic inline uint32_t zigux_header_requested_extra_bytes(zigux_boundary_header header)\n{\n    if (!zigux_header_extends_boundary(header))\n        return 0;\n    return header.size - (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline zigux_boundary_header zigux_header_canonicalize(zigux_boundary_header header)\n{\n    header.size = (uint32_t)sizeof(zigux_boundary_header);\n    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;\n    return header;\n}\n\nstatic inline struct zigux_interop_policy zigux_default_interop_policy(void)\n{\n    struct zigux_interop_policy policy = {\n        .panic_mode = (uint8_t)ZIGUX_PANIC_ABORT,\n        .allocator_mode = (uint8_t)ZIGUX_ALLOC_CALLER_PROVIDED,\n        .unsafe_scope = (uint8_t)ZIGUX_UNSAFE_NONE,\n        .reserved = 0,\n    };\n    return policy;\n}\n\nstatic inline struct zigux_export_status zigux_make_status(int32_t code, uint16_t facility)\n{\n    struct zigux_export_status status = {\n        .code = code,\n        .facility = facility,\n        .flags = (uint16_t)(code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0U),\n    };\n    return status;\n}\n\nstatic inline struct zigux_export_status zigux_ok_status(uint16_t facility)\n{\n    return zigux_make_status(0, facility);\n}\n\nstatic inline int zigux_export_status_ok(struct zigux_export_status status)\n{\n    return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0;\n}\n\nstatic inline int zigux_notifier_chain_has_nonincreasing_priority(\n    const struct zigux_notifier_block *head)\n{\n    int32_t previous_priority;\n    const struct zigux_notifier_block *node;\n\n    if (!head)\n        return 1;\n\n    previous_priority = head->priority;\n    while (head->next != (uintptr_t)0) {\n        node = (const struct zigux_notifier_block *)(uintptr_t)head->next;\n        if (node->priority > previous_priority)\n            return 0;\n        previous_priority = node->priority;\n        head = node;\n    }\n\n    return 1;\n}\n\nstatic inline int zigux_notifier_first_chain_priority_increase(\n    const struct zigux_notifier_block *head,\n    zigux_notifier_chain_priority_increase *out)\n{\n    size_t previous_index = 0;\n    int32_t previous_priority;\n\n    if (!head || head->next == (uintptr_t)0 || !out)\n        return 0;\n\n    previous_priority = head->priority;\n    while (head->next != (uintptr_t)0) {\n        const struct zigux_notifier_block *node =\n            (const struct zigux_notifier_block *)(uintptr_t)head->next;\n        const size_t current_index = previous_index + 1;\n        if (node->priority > previous_priority) {\n            out->previous_index = previous_index;\n            out->current_index = current_index;\n            out->previous_priority = previous_priority;\n            out->current_priority = node->priority;\n            return 1;\n        }\n        previous_index = current_index;\n        previous_priority = node->priority;\n        head = node;\n    }\n\n    return 0;\n}\n\nstatic inline int zigux_list_first_broken_backlink(\n    const struct zigux_list_head *head,\n    zigux_list_backlink_break *out)\n{\n    uintptr_t expected_prev;\n    size_t current_index = 0;\n    const struct zigux_list_head *cursor;\n\n    if (!head)\n        return 0;\n\n    expected_prev = (uintptr_t)head;\n    cursor = (const struct zigux_list_head *)(uintptr_t)head->next;\n    while (cursor && cursor != head) {\n        if (cursor->prev != expected_prev) {\n            if (out) {\n                out->current_index = current_index;\n                out->expected_prev = expected_prev;\n                out->actual_prev = cursor->prev;\n            }\n            return 1;\n        }\n        expected_prev = (uintptr_t)cursor;\n        current_index += 1;\n        cursor = (const struct zigux_list_head *)(uintptr_t)cursor->next;\n    }\n\n    if (!cursor) {\n        if (out) {\n            out->current_index = current_index;\n            out->expected_prev = expected_prev;\n            out->actual_prev = 0;\n        }\n        return 1;\n    }\n\n    if (head->prev != expected_prev) {\n        if (out) {\n            out->current_index = current_index;\n            out->expected_prev = expected_prev;\n            out->actual_prev = head->prev;\n        }\n        return 1;\n    }\n\n    return 0;\n}\n\nstatic inline int zigux_list_has_consistent_backlinks(\n    const struct zigux_list_head *head)\n{\n    return head != NULL && zigux_list_first_broken_backlink(head, NULL) == 0;\n}\n\nstatic inline int zigux_hlist_first_broken_prev_link(\n    const struct zigux_hlist_head *head,\n    zigux_hlist_prev_link_break *out)\n{\n    uintptr_t expected_pprev;\n    size_t current_index = 0;\n    const struct zigux_hlist_node *cursor;\n\n    if (!head)\n        return 0;\n\n    expected_pprev = (uintptr_t)&head->first;\n    cursor = (const struct zigux_hlist_node *)(uintptr_t)head->first;\n    while (cursor) {\n        if (cursor->pprev != expected_pprev) {\n            if (out) {\n                out->current_index = current_index;\n                out->expected_pprev = expected_pprev;\n                out->actual_pprev = cursor->pprev;\n            }\n            return 1;\n        }\n        expected_pprev = (uintptr_t)&cursor->next;\n        current_index += 1;\n        cursor = (const struct zigux_hlist_node *)(uintptr_t)cursor->next;\n    }\n\n    return 0;\n}\n\nstatic inline int zigux_hlist_has_consistent_prev_links(\n    const struct zigux_hlist_head *head)\n{\n    return head != NULL && zigux_hlist_first_broken_prev_link(head, NULL) == 0;\n}\n\n#endif\n",
};

const SELFTEST_ABI_DUMP = [_][]const u8{
    "const abi = @import(\"abi_bindings\");\nconst default_header = abi.defaultHeader(0);\nconst policy = abi.defaultInteropPolicy();\n\"boundary_header\"\n\"export_status\"\n\"chrdev_budget_window\"\n\"interop_policy\"\n\"facility\"\n\"notifier\"\n",
};

const SELFTEST_SMOKE = [_][]const u8{
    "#include <stddef.h>\n#include <zigux/abi.h>\n\nstatic int check_header_helpers(void)\n{\n    zigux_boundary_header canonical = zigux_default_header(0x41u);\n    zigux_boundary_header compatible =\n        zigux_compatible_header((uint32_t)sizeof(zigux_boundary_header) + 8u, 0x41u);\n    zigux_boundary_header stale = canonical;\n    zigux_boundary_header canonicalized;\n\n    stale.abi_version += 1u;\n    canonicalized = zigux_header_canonicalize(compatible);\n\n    if (!zigux_abi_version_is_current(canonical.abi_version))\n        return __LINE__;\n    if (!zigux_header_is_canonical(canonical))\n        return __LINE__;\n    if (!zigux_header_is_compatible(canonical))\n        return __LINE__;\n    if (zigux_header_extends_boundary(canonical))\n        return __LINE__;\n    if (zigux_header_requested_extra_bytes(canonical) != 0u)\n        return __LINE__;\n\n    if (zigux_header_is_canonical(compatible))\n        return __LINE__;\n    if (!zigux_header_is_compatible(compatible))\n        return __LINE__;\n    if (!zigux_header_extends_boundary(compatible))\n        return __LINE__;\n    if (zigux_header_requested_extra_bytes(compatible) != 8u)\n        return __LINE__;\n\n    if (zigux_header_is_compatible(stale))\n        return __LINE__;\n    if (!zigux_header_is_canonical(canonicalized))\n        return __LINE__;\n    if (canonicalized.flags != compatible.flags)\n        return __LINE__;\n\n    return 0;\n}\n\nstatic int check_status_and_policy_helpers(void)\n{\n    struct zigux_interop_policy policy = zigux_default_interop_policy();\n    struct zigux_export_status ok = zigux_ok_status((uint16_t)ZIGUX_FACILITY_HELPERS);\n    struct zigux_export_status err = zigux_make_status(-22, (uint16_t)ZIGUX_FACILITY_KERNEL);\n\n    if (sizeof(struct zigux_interop_policy) != 4u)\n        return __LINE__;\n    if (offsetof(struct zigux_interop_policy, panic_mode) != 0u)\n        return __LINE__;\n    if (offsetof(struct zigux_interop_policy, allocator_mode) != 1u)\n        return __LINE__;\n    if (policy.panic_mode != ZIGUX_PANIC_ABORT)\n        return __LINE__;\n    if (policy.allocator_mode != ZIGUX_ALLOC_CALLER_PROVIDED)\n        return __LINE__;\n    if (policy.unsafe_scope != ZIGUX_UNSAFE_NONE)\n        return __LINE__;\n    if (policy.reserved != 0u)\n        return __LINE__;\n    if (!zigux_export_status_ok(ok))\n        return __LINE__;\n    if (zigux_export_status_ok(err))\n        return __LINE__;\n    if (err.flags != ZIGUX_STATUS_FLAG_ERROR)\n        return __LINE__;\n\n    return 0;\n}\n\nstatic int check_notifier_and_list_helpers(void)\n{\n    struct zigux_notifier_block tail = { .notifier_call = 0, .next = 0, .priority = 7 };\n    struct zigux_notifier_block head = {\n        .notifier_call = 0,\n        .next = (uintptr_t)&tail,\n        .priority = 3,\n    };\n    zigux_notifier_chain_priority_increase increase;\n    struct zigux_list_head list_head = { .next = 0, .prev = 0 };\n    struct zigux_list_head list_first = { .next = 0, .prev = 0 };\n    struct zigux_list_head list_second = { .next = 0, .prev = 0 };\n    zigux_list_backlink_break list_break;\n    struct zigux_hlist_head hlist_head = { .first = 0 };\n    struct zigux_hlist_node hlist_first = { .next = 0, .pprev = 0 };\n    struct zigux_hlist_node hlist_second = { .next = 0, .pprev = 0 };\n    zigux_hlist_prev_link_break hlist_break;\n\n    if (zigux_notifier_chain_has_nonincreasing_priority(&head))\n        return __LINE__;\n    if (!zigux_notifier_first_chain_priority_increase(&head, &increase))\n        return __LINE__;\n    if (increase.previous_index != 0u || increase.current_index != 1u)\n        return __LINE__;\n    if (increase.previous_priority != 3 || increase.current_priority != 7)\n        return __LINE__;\n\n    list_head.next = (uintptr_t)&list_first;\n    list_head.prev = (uintptr_t)&list_second;\n    list_first.next = (uintptr_t)&list_second;\n    list_first.prev = (uintptr_t)&list_head;\n    list_second.next = (uintptr_t)&list_head;\n    list_second.prev = (uintptr_t)&list_head;\n    if (zigux_list_has_consistent_backlinks(&list_head))\n        return __LINE__;\n    if (!zigux_list_first_broken_backlink(&list_head, &list_break))\n        return __LINE__;\n    if (list_break.current_index != 1u)\n        return __LINE__;\n\n    hlist_head.first = (uintptr_t)&hlist_first;\n    hlist_first.next = (uintptr_t)&hlist_second;\n    hlist_first.pprev = (uintptr_t)&hlist_head.first;\n    hlist_second.next = 0;\n    hlist_second.pprev = (uintptr_t)&hlist_head.first;\n    if (zigux_hlist_has_consistent_prev_links(&hlist_head))\n        return __LINE__;\n    if (!zigux_hlist_first_broken_prev_link(&hlist_head, &hlist_break))\n        return __LINE__;\n    if (hlist_break.current_index != 1u)\n        return __LINE__;\n\n    return 0;\n}\n\nstatic int check_chrdev_layout_helpers(void)\n{\n    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view view = {\n        .ack_window = 7u,\n        .delivery_window = 11u,\n        .status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,\n    };\n\n    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED != 1u)\n        return __LINE__;\n    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED != 1u)\n        return __LINE__;\n    if (sizeof(view) != 12u)\n        return __LINE__;\n    if (offsetof(\n            zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view,\n            status) != 8u)\n        return __LINE__;\n\n    return 0;\n}\n\nint main(void)\n{\n    int rc = check_header_helpers();\n    if (rc != 0)\n        return rc;\n\n    rc = check_status_and_policy_helpers();\n    if (rc != 0)\n        return rc;\n\n    rc = check_notifier_and_list_helpers();\n    if (rc != 0)\n        return rc;\n\n    rc = check_chrdev_layout_helpers();\n    if (rc != 0)\n        return rc;\n\n    return 0;\n}\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_tests_phase3_abi_c_header_smoke_c_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/abi/c/header/smoke/c");
    defer allocator.free(text_required_markers__zigux_tests_phase3_abi_c_header_smoke_c_path);
    const text_required_markers__zigux_tests_phase3_abi_c_header_smoke_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_abi_c_header_smoke_c_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_abi_c_header_smoke_c);
    for (REQUIRED_MARKERS__zigux_tests_phase3_abi_c_header_smoke_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_abi_c_header_smoke_c, marker);
    const text_required_markers__include_zigux_abi_h_path = try guard.joinPath(allocator, root, "include/zigux/abi/h");
    defer allocator.free(text_required_markers__include_zigux_abi_h_path);
    const text_required_markers__include_zigux_abi_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_abi_h_path);
    defer allocator.free(text_required_markers__include_zigux_abi_h);
    for (REQUIRED_MARKERS__include_zigux_abi_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_abi_h, marker);
    const text_required_markers__zigux_tests_phase3_abi_dump_current_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/abi/dump/current/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_abi_dump_current_zig_path);
    const text_required_markers__zigux_tests_phase3_abi_dump_current_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_abi_dump_current_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_abi_dump_current_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_abi_dump_current_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_abi_dump_current_zig, marker);
    const text_selftest_abi_header_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_abi_c_header_smoke.c");
    defer allocator.free(text_selftest_abi_header_path);
    const text_selftest_abi_header = try guard.readUtf8File(io, allocator, text_selftest_abi_header_path);
    defer allocator.free(text_selftest_abi_header);
    for (SELFTEST_ABI_HEADER) |marker| try guard.requireMarker(text_selftest_abi_header, marker);
    const text_selftest_abi_dump_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_abi_c_header_smoke.c");
    defer allocator.free(text_selftest_abi_dump_path);
    const text_selftest_abi_dump = try guard.readUtf8File(io, allocator, text_selftest_abi_dump_path);
    defer allocator.free(text_selftest_abi_dump);
    for (SELFTEST_ABI_DUMP) |marker| try guard.requireMarker(text_selftest_abi_dump, marker);
    const text_selftest_smoke_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_abi_c_header_smoke.c");
    defer allocator.free(text_selftest_smoke_path);
    const text_selftest_smoke = try guard.readUtf8File(io, allocator, text_selftest_smoke_path);
    defer allocator.free(text_selftest_smoke);
    for (SELFTEST_SMOKE) |marker| try guard.requireMarker(text_selftest_smoke, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
