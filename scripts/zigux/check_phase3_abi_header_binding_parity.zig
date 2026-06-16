const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const ABI_HEADER_REL = "include/zigux/abi.h";
const ABI_BINDING_REL = "zigux/bindings/abi.zig";

const C_TO_ZIG_TYPE = std.StaticStringMap([]const u8).initComptime(.{
    .{ "uint32_t", "u32" },
    .{ "uint16_t", "u16" },
    .{ "uint8_t", "u8" },
    .{ "int32_t", "i32" },
    .{ "uintptr_t", "usize" },
    .{ "size_t", "usize" },
});

const STRUCT_NAME_MAP = [_]struct { c_name: []const u8, zig_name: []const u8 }{
    .{ .c_name = "zigux_boundary_header", .zig_name = "BoundaryHeader" },
    .{ .c_name = "zigux_export_status", .zig_name = "ExportStatus" },
    .{ .c_name = "zigux_interop_policy", .zig_name = "InteropPolicy" },
    .{ .c_name = "zigux_notifier_chain_priority_increase", .zig_name = "ChainPriorityIncrease" },
    .{ .c_name = "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view", .zig_name = "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView" },
    .{ .c_name = "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary", .zig_name = "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary" },
    .{ .c_name = "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view", .zig_name = "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView" },
    .{ .c_name = "zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary", .zig_name = "ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary" },
    .{ .c_name = "zigux_notifier_block", .zig_name = "NotifierBlock" },
    .{ .c_name = "zigux_list_head", .zig_name = "ListHead" },
    .{ .c_name = "zigux_hlist_head", .zig_name = "HListHead" },
    .{ .c_name = "zigux_hlist_node", .zig_name = "HListNode" },
    .{ .c_name = "zigux_list_backlink_break", .zig_name = "ListBackLinkBreak" },
    .{ .c_name = "zigux_hlist_prev_link_break", .zig_name = "HListPrevLinkBreak" },
};

const HELPER_NAME_MAP = [_]struct { header_name: []const u8, binding_name: []const u8 }{
    .{ .header_name = "zigux_default_header", .binding_name = "defaultHeader" },
    .{ .header_name = "zigux_compatible_header", .binding_name = "compatibleHeader" },
    .{ .header_name = "zigux_abi_version_is_current", .binding_name = "headerHasCurrentAbiVersion" },
    .{ .header_name = "zigux_header_is_canonical", .binding_name = "headerIsCanonical" },
    .{ .header_name = "zigux_header_is_compatible", .binding_name = "headerIsCompatible" },
    .{ .header_name = "zigux_header_extends_boundary", .binding_name = "extendsBoundary" },
    .{ .header_name = "zigux_header_requested_extra_bytes", .binding_name = "requestedExtraBytes" },
    .{ .header_name = "zigux_header_canonicalize", .binding_name = "canonicalizeHeader" },
    .{ .header_name = "zigux_default_interop_policy", .binding_name = "defaultInteropPolicy" },
    .{ .header_name = "zigux_make_status", .binding_name = "makeStatus" },
    .{ .header_name = "zigux_ok_status", .binding_name = "okStatus" },
    .{ .header_name = "zigux_export_status_ok", .binding_name = "statusIsOk" },
    .{ .header_name = "zigux_notifier_chain_has_nonincreasing_priority", .binding_name = "chainHasNonincreasingPriority" },
    .{ .header_name = "zigux_notifier_first_chain_priority_increase", .binding_name = "firstChainPriorityIncrease" },
    .{ .header_name = "zigux_list_has_consistent_backlinks", .binding_name = "listHasConsistentBacklinks" },
    .{ .header_name = "zigux_hlist_has_consistent_prev_links", .binding_name = "hlistHasConsistentPrevLinks" },
};

const Field = struct { name: []const u8, type_name: []const u8 };

fn parseHeaderDefines(text: []const u8, allocator: std.mem.Allocator) !std.StringHashMap(u64) {
    var defines = std.StringHashMap(u64).init(allocator);
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (!std.mem.startsWith(u8, line, "#define ")) continue;
        var parts = std.mem.tokenizeAny(u8, line[8..], " \t");
        const name = parts.next() orelse continue;
        const value_raw = parts.next() orelse continue;
        if (!std.mem.startsWith(u8, name, "ZIGUX_")) continue;
        const trimmed = std.mem.trim(u8, value_raw, " \t");
        const numeric = if (std.mem.endsWith(u8, trimmed, "U")) trimmed[0 .. trimmed.len - 1] else trimmed;
        const value = std.fmt.parseInt(u64, numeric, 10) catch continue;
        try defines.put(try allocator.dupe(u8, name), value);
    }
    return defines;
}

fn parseBindingConsts(text: []const u8, allocator: std.mem.Allocator) !std.StringHashMap(u64) {
    var consts = std.StringHashMap(u64).init(allocator);
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (!std.mem.startsWith(u8, line, "pub const ")) continue;
        const eq = std.mem.indexOf(u8, line, "=") orelse continue;
        const left = std.mem.trim(u8, line["pub const ".len..eq], " \t");
        const colon = std.mem.indexOf(u8, left, ":") orelse continue;
        const name = std.mem.trim(u8, left[0..colon], " \t");
        const right = std.mem.trim(u8, line[eq + 1 ..], " \t;");
        const value = std.fmt.parseInt(u64, right, 10) catch continue;
        try consts.put(try allocator.dupe(u8, name), value);
    }
    return consts;
}

fn parseCFieldLine(line: []const u8) ?Field {
    const trimmed = std.mem.trim(u8, line, " \t\r");
    if (!std.mem.endsWith(u8, trimmed, ";")) return null;
    var parts = std.mem.tokenizeAny(u8, trimmed[0 .. trimmed.len - 1], " \t");
    const type_name = parts.next() orelse return null;
    const name = parts.next() orelse return null;
    const zig_type = C_TO_ZIG_TYPE.get(type_name) orelse return null;
    return .{ .name = name, .type_name = zig_type };
}

fn isIdentChar(ch: u8) bool {
    return (ch >= 'a' and ch <= 'z') or
        (ch >= 'A' and ch <= 'Z') or
        (ch >= '0' and ch <= '9') or
        ch == '_';
}

fn parseCStructs(text: []const u8, allocator: std.mem.Allocator) !std.StringHashMap([]const Field) {
    var structs = std.StringHashMap([]const Field).init(allocator);
    var index: usize = 0;
    while (index < text.len) {
        const struct_at = std.mem.indexOfPos(u8, text, index, "struct ") orelse break;
        var pos = struct_at + "struct ".len;
        while (pos < text.len and std.mem.indexOfScalar(u8, " \t\n\r", text[pos]) != null) : (pos += 1) {}
        if (pos >= text.len or !isIdentChar(text[pos])) {
            index = struct_at + 1;
            continue;
        }
        const tag_start = pos;
        while (pos < text.len and isIdentChar(text[pos])) : (pos += 1) {}
        const tag = text[tag_start..pos];
        while (pos < text.len and std.mem.indexOfScalar(u8, " \t\n\r", text[pos]) != null) : (pos += 1) {}
        if (pos >= text.len or text[pos] != '{') {
            index = struct_at + 1;
            continue;
        }
        const body_start = pos + 1;
        var depth: i32 = 1;
        pos += 1;
        while (pos < text.len and depth > 0) : (pos += 1) {
            switch (text[pos]) {
                '{' => depth += 1,
                '}' => depth -= 1,
                else => {},
            }
        }
        if (depth != 0) {
            index = struct_at + 1;
            continue;
        }
        const body = text[body_start .. pos - 1];
        while (pos < text.len and std.mem.indexOfScalar(u8, " \t\n\r", text[pos]) != null) : (pos += 1) {}
        var name = tag;
        if (pos < text.len and text[pos] != ';') {
            const alias_start = pos;
            while (pos < text.len and isIdentChar(text[pos])) : (pos += 1) {}
            if (pos > alias_start) name = text[alias_start..pos];
        }
        while (pos < text.len and std.mem.indexOfScalar(u8, " \t\n\r", text[pos]) != null) : (pos += 1) {}
        if (pos >= text.len or text[pos] != ';') {
            index = struct_at + 1;
            continue;
        }

        var fields: std.ArrayList(Field) = .empty;
        var line_iter = std.mem.splitScalar(u8, body, '\n');
        while (line_iter.next()) |line| {
            if (parseCFieldLine(line)) |field| {
                try fields.append(allocator, .{
                    .name = try allocator.dupe(u8, field.name),
                    .type_name = try allocator.dupe(u8, field.type_name),
                });
            }
        }
        if (fields.items.len > 0) {
            try structs.put(try allocator.dupe(u8, name), try fields.toOwnedSlice(allocator));
        }
        index = pos + 1;
    }
    return structs;
}

fn parseZigFieldLine(line: []const u8) ?Field {
    const trimmed = std.mem.trim(u8, line, " \t\r");
    if (!std.mem.endsWith(u8, trimmed, ",")) return null;
    const colon = std.mem.indexOf(u8, trimmed, ":") orelse return null;
    const name = std.mem.trim(u8, trimmed[0..colon], " \t");
    const type_name = std.mem.trim(u8, trimmed[colon + 1 .. trimmed.len - 1], " \t");
    return .{ .name = name, .type_name = type_name };
}

fn parseZigStructs(text: []const u8, allocator: std.mem.Allocator) !std.StringHashMap([]const Field) {
    var structs = std.StringHashMap([]const Field).init(allocator);
    var iter = std.mem.splitScalar(u8, text, '\n');
    var current_name: ?[]const u8 = null;
    var fields: std.ArrayList(Field) = .empty;
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (std.mem.startsWith(u8, line, "pub const ") and std.mem.indexOf(u8, line, "extern struct {") != null) {
            if (current_name) |name| {
                try structs.put(try allocator.dupe(u8, name), try fields.toOwnedSlice(allocator));
                fields = .empty;
            }
            const after_const = line["pub const ".len..];
            const name_end = std.mem.indexOf(u8, after_const, "=") orelse continue;
            current_name = std.mem.trim(u8, after_const[0..name_end], " \t");
            continue;
        }
        if (current_name != null and std.mem.eql(u8, line, "};")) {
            try structs.put(try allocator.dupe(u8, current_name.?), try fields.toOwnedSlice(allocator));
            fields = .empty;
            current_name = null;
            continue;
        }
        if (current_name != null) {
            if (parseZigFieldLine(line)) |field| try fields.append(allocator, field);
        }
    }
    return structs;
}

fn parseHeaderHelpers(text: []const u8, allocator: std.mem.Allocator) !std.StringHashMap(void) {
    var helpers = std.StringHashMap(void).init(allocator);
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (!std.mem.startsWith(u8, line, "static inline")) continue;
        for (HELPER_NAME_MAP) |pair| {
            if (std.mem.indexOf(u8, line, pair.header_name) != null) try helpers.put(try allocator.dupe(u8, pair.header_name), {});
        }
    }
    return helpers;
}

fn parseBindingFunctions(text: []const u8, allocator: std.mem.Allocator) !std.StringHashMap(void) {
    var functions = std.StringHashMap(void).init(allocator);
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (!std.mem.startsWith(u8, line, "pub fn ")) continue;
        const after = line["pub fn ".len..];
        const name_end = std.mem.indexOf(u8, after, "(") orelse continue;
        const name = after[0..name_end];
        if (name.len > 0 and (name[0] >= 'a' and name[0] <= 'z' or name[0] >= 'A' and name[0] <= 'Z')) try functions.put(try allocator.dupe(u8, name), {});
    }
    return functions;
}

fn freeFields(allocator: std.mem.Allocator, fields: []const Field) void {
    for (fields) |field| {
        allocator.free(field.name);
        allocator.free(field.type_name);
    }
    allocator.free(fields);
}

fn fieldsEqual(left: []const Field, right: []const Field) bool {
    if (left.len != right.len) return false;
    for (left, right) |a, b| {
        if (!std.mem.eql(u8, a.name, b.name) or !std.mem.eql(u8, a.type_name, b.type_name)) return false;
    }
    return true;
}

fn validatePair(allocator: std.mem.Allocator, header_text: []const u8, binding_text: []const u8) ![]const []const u8 {
    var issues: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (issues.items) |issue| allocator.free(issue);
        issues.deinit(allocator);
    }

    var header_defines = try parseHeaderDefines(header_text, allocator);
    defer {
        var it = header_defines.iterator();
        while (it.next()) |entry| allocator.free(entry.key_ptr.*);
        header_defines.deinit();
    }
    var binding_consts = try parseBindingConsts(binding_text, allocator);
    defer {
        var it = binding_consts.iterator();
        while (it.next()) |entry| allocator.free(entry.key_ptr.*);
        binding_consts.deinit();
    }

    var define_names = std.ArrayList([]const u8).empty;
    defer define_names.deinit(allocator);
    var it = header_defines.iterator();
    while (it.next()) |entry| try define_names.append(allocator, entry.key_ptr.*);
    std.mem.sort([]const u8, define_names.items, {}, struct {
        fn lessThan(_: void, a: []const u8, b: []const u8) bool {
            return std.mem.order(u8, a, b) == .lt;
        }
    }.lessThan);

    for (define_names.items) |name| {
        const value = header_defines.get(name).?;
        const binding_name = if (std.mem.startsWith(u8, name, "ZIGUX_")) name["ZIGUX_".len..] else name;
        const binding_value = binding_consts.get(binding_name) orelse {
            const issue = try std.fmt.allocPrint(allocator, "missing binding constant for header define: {s}", .{name});
            try issues.append(allocator, issue);
            continue;
        };
        if (binding_value != value) {
            const issue = try std.fmt.allocPrint(allocator, "constant value mismatch for {s}: header={d} binding={d}", .{ name, value, binding_value });
            try issues.append(allocator, issue);
        }
    }

    var c_structs = try parseCStructs(header_text, allocator);
    defer {
        var sit = c_structs.iterator();
        while (sit.next()) |entry| {
            allocator.free(entry.key_ptr.*);
            freeFields(allocator, entry.value_ptr.*);
        }
        c_structs.deinit();
    }
    var zig_structs = try parseZigStructs(binding_text, allocator);
    defer {
        var zit = zig_structs.iterator();
        while (zit.next()) |entry| {
            allocator.free(entry.key_ptr.*);
            allocator.free(entry.value_ptr.*);
        }
        zig_structs.deinit();
    }

    for (STRUCT_NAME_MAP) |pair| {
        const c_fields = c_structs.get(pair.c_name) orelse {
            const issue = try std.fmt.allocPrint(allocator, "missing header struct: {s}", .{pair.c_name});
            try issues.append(allocator, issue);
            continue;
        };
        const zig_fields = zig_structs.get(pair.zig_name) orelse {
            const issue = try std.fmt.allocPrint(allocator, "missing binding extern struct: {s}", .{pair.zig_name});
            try issues.append(allocator, issue);
            continue;
        };
        if (!fieldsEqual(c_fields, zig_fields)) {
            const issue = try std.fmt.allocPrint(allocator, "struct field parity mismatch for {s} -> {s}: header={any} binding={any}", .{ pair.c_name, pair.zig_name, c_fields, zig_fields });
            try issues.append(allocator, issue);
        }
    }

    var header_helpers = try parseHeaderHelpers(header_text, allocator);
    defer {
        var hit = header_helpers.iterator();
        while (hit.next()) |entry| allocator.free(entry.key_ptr.*);
        header_helpers.deinit();
    }
    var binding_functions = try parseBindingFunctions(binding_text, allocator);
    defer {
        var fit = binding_functions.iterator();
        while (fit.next()) |entry| allocator.free(entry.key_ptr.*);
        binding_functions.deinit();
    }

    for (HELPER_NAME_MAP) |pair| {
        if (header_helpers.get(pair.header_name) == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing header helper: {s}", .{pair.header_name});
            try issues.append(allocator, issue);
            continue;
        }
        if (binding_functions.get(pair.binding_name) == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing binding helper for header helper: {s} -> {s}", .{ pair.header_name, pair.binding_name });
            try issues.append(allocator, issue);
        }
    }

    return issues.toOwnedSlice(allocator);
}

const GOOD_HEADER =
    \\#define ZIGUX_ABI_VERSION 1U
    \\#define ZIGUX_FACILITY_KERNEL 1U
    \\#define ZIGUX_STATUS_FLAG_ERROR 1U
    \\
    \\typedef struct zigux_boundary_header {
    \\    uint32_t size;
    \\    uint16_t abi_version;
    \\    uint16_t flags;
    \\} zigux_boundary_header;
    \\
    \\struct zigux_export_status {
    \\    int32_t code;
    \\    uint16_t facility;
    \\    uint16_t flags;
    \\};
    \\
    \\struct zigux_interop_policy {
    \\    uint8_t panic_mode;
    \\    uint8_t allocator_mode;
    \\    uint8_t unsafe_scope;
    \\    uint8_t reserved;
    \\};
    \\
    \\struct zigux_notifier_block {
    \\    uintptr_t notifier_call;
    \\    uintptr_t next;
    \\    int32_t priority;
    \\};
    \\
    \\typedef struct zigux_notifier_chain_priority_increase {
    \\    size_t previous_index;
    \\    size_t current_index;
    \\    int32_t previous_priority;
    \\    int32_t current_priority;
    \\} zigux_notifier_chain_priority_increase;
    \\
    \\struct zigux_list_head {
    \\    uintptr_t next;
    \\    uintptr_t prev;
    \\};
    \\
    \\struct zigux_hlist_head {
    \\    uintptr_t first;
    \\};
    \\
    \\struct zigux_hlist_node {
    \\    uintptr_t next;
    \\    uintptr_t pprev;
    \\};
    \\
    \\typedef struct zigux_list_backlink_break {
    \\    size_t current_index;
    \\    uintptr_t expected_prev;
    \\    uintptr_t actual_prev;
    \\} zigux_list_backlink_break;
    \\
    \\typedef struct zigux_hlist_prev_link_break {
    \\    size_t current_index;
    \\    uintptr_t expected_pprev;
    \\    uintptr_t actual_pprev;
    \\} zigux_hlist_prev_link_break;
    \\
    \\struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
    \\    uint32_t ack_window;
    \\    uint32_t delivery_window;
    \\    uint32_t status;
    \\};
    \\
    \\struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
    \\    uint32_t applied;
    \\    uint32_t skipped;
    \\    uint32_t delivered;
    \\};
    \\
    \\struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
    \\    uint32_t budget;
    \\    uint32_t window;
    \\    uint32_t flags;
    \\};
    \\
    \\struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
    \\    uint32_t attempted;
    \\    uint32_t applied;
    \\    uint32_t skipped;
    \\};
    \\
    \\static inline zigux_boundary_header zigux_default_header(uint16_t flags) { return (zigux_boundary_header){0}; }
    \\static inline zigux_boundary_header zigux_compatible_header(uint32_t size, uint16_t flags) { return zigux_default_header(flags); }
    \\static inline int zigux_abi_version_is_current(uint16_t abi_version) { return abi_version == 1; }
    \\static inline int zigux_header_is_canonical(zigux_boundary_header header) { return header.size == 0; }
    \\static inline int zigux_header_is_compatible(zigux_boundary_header header) { return header.size == 0; }
    \\static inline int zigux_header_extends_boundary(zigux_boundary_header header) { return header.size == 0; }
    \\static inline uint32_t zigux_header_requested_extra_bytes(zigux_boundary_header header) { return header.size; }
    \\static inline zigux_boundary_header zigux_header_canonicalize(zigux_boundary_header header) { return header; }
    \\static inline struct zigux_interop_policy zigux_default_interop_policy(void) { return (struct zigux_interop_policy){0}; }
    \\static inline struct zigux_export_status zigux_make_status(int32_t code, uint16_t facility) { return (struct zigux_export_status){0}; }
    \\static inline struct zigux_export_status zigux_ok_status(uint16_t facility) { return (struct zigux_export_status){0}; }
    \\static inline int zigux_export_status_ok(struct zigux_export_status status) { return status.flags == 0; }
    \\static inline int zigux_notifier_chain_has_nonincreasing_priority(const struct zigux_notifier_block *head) { return head != 0; }
    \\static inline int zigux_notifier_first_chain_priority_increase(const struct zigux_notifier_block *head, zigux_notifier_chain_priority_increase *out) { return out != 0 || head != 0; }
    \\static inline int zigux_list_has_consistent_backlinks(const struct zigux_list_head *head) { return head != 0; }
    \\static inline int zigux_hlist_has_consistent_prev_links(const struct zigux_hlist_head *head) { return head != 0; }
    \\
;

const GOOD_BINDING =
    \\pub const ABI_VERSION: u16 = 1;
    \\pub const FACILITY_KERNEL: u16 = 1;
    \\pub const STATUS_FLAG_ERROR: u16 = 1;
    \\
    \\pub const BoundaryHeader = extern struct {
    \\    size: u32,
    \\    abi_version: u16,
    \\    flags: u16,
    \\};
    \\
    \\pub const ExportStatus = extern struct {
    \\    code: i32,
    \\    facility: u16,
    \\    flags: u16,
    \\};
    \\
    \\pub const InteropPolicy = extern struct {
    \\    panic_mode: u8,
    \\    allocator_mode: u8,
    \\    unsafe_scope: u8,
    \\    reserved: u8,
    \\};
    \\
    \\pub const NotifierBlock = extern struct {
    \\    notifier_call: usize,
    \\    next: usize,
    \\    priority: i32,
    \\};
    \\
    \\pub const ChainPriorityIncrease = extern struct {
    \\    previous_index: usize,
    \\    current_index: usize,
    \\    previous_priority: i32,
    \\    current_priority: i32,
    \\};
    \\
    \\pub const ListHead = extern struct {
    \\    next: usize,
    \\    prev: usize,
    \\};
    \\
    \\pub const HListHead = extern struct {
    \\    first: usize,
    \\};
    \\
    \\pub const HListNode = extern struct {
    \\    next: usize,
    \\    pprev: usize,
    \\};
    \\
    \\pub const ListBackLinkBreak = extern struct {
    \\    current_index: usize,
    \\    expected_prev: usize,
    \\    actual_prev: usize,
    \\};
    \\
    \\pub const HListPrevLinkBreak = extern struct {
    \\    current_index: usize,
    \\    expected_pprev: usize,
    \\    actual_pprev: usize,
    \\};
    \\
    \\pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {
    \\    ack_window: u32,
    \\    delivery_window: u32,
    \\    status: u32,
    \\};
    \\
    \\pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {
    \\    applied: u32,
    \\    skipped: u32,
    \\    delivered: u32,
    \\};
    \\
    \\pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView = extern struct {
    \\    budget: u32,
    \\    window: u32,
    \\    flags: u32,
    \\};
    \\
    \\pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary = extern struct {
    \\    attempted: u32,
    \\    applied: u32,
    \\    skipped: u32,
    \\};
    \\
    \\pub fn defaultHeader(flags: u16) BoundaryHeader { _ = flags; return undefined; }
    \\pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader { _ = .{ size, flags }; return undefined; }
    \\pub fn headerHasCurrentAbiVersion(abi_version: u16) bool { return abi_version == 1; }
    \\pub fn headerIsCanonical(header: BoundaryHeader) bool { _ = header; return true; }
    \\pub fn headerIsCompatible(header: BoundaryHeader) bool { _ = header; return true; }
    \\pub fn extendsBoundary(header: BoundaryHeader) bool { _ = header; return false; }
    \\pub fn requestedExtraBytes(header: BoundaryHeader) u32 { _ = header; return 0; }
    \\pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader { return header; }
    \\pub fn defaultInteropPolicy() InteropPolicy { return undefined; }
    \\pub fn makeStatus(code: i32, facility: u16) ExportStatus { _ = .{ code, facility }; return undefined; }
    \\pub fn okStatus(facility: u16) ExportStatus { _ = facility; return undefined; }
    \\pub fn statusIsOk(status: ExportStatus) bool { _ = status; return true; }
    \\pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool { _ = head; return true; }
    \\pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease { _ = head; return null; }
    \\pub fn listHasConsistentBacklinks(head: ?*const ListHead) bool { _ = head; return true; }
    \\pub fn hlistHasConsistentPrevLinks(head: ?*const HListHead) bool { _ = head; return true; }
    \\
;

fn runCaseSelfTest(allocator: std.mem.Allocator, header: []const u8, binding: []const u8, needles: []const []const u8) !void {
    const issues = try validatePair(allocator, header, binding);
    defer {
        for (issues) |issue| allocator.free(issue);
        allocator.free(issues);
    }
    if (needles.len == 0) {
        try guard.expectSelfTest(issues.len == 0);
        return;
    }
    try guard.expectSelfTest(issues.len > 0);
    for (needles) |needle| {
        var found = false;
        for (issues) |issue| {
            if (std.mem.indexOf(u8, issue, needle) != null) found = true;
        }
        try guard.expectSelfTest(found);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try runCaseSelfTest(allocator, GOOD_HEADER, GOOD_BINDING, &.{});

    const mismatch_constant_binding = try std.mem.replaceOwned(u8, allocator, GOOD_BINDING, "pub const STATUS_FLAG_ERROR: u16 = 1;", "pub const STATUS_FLAG_ERROR: u16 = 2;");
    defer allocator.free(mismatch_constant_binding);
    try runCaseSelfTest(allocator, GOOD_HEADER, mismatch_constant_binding, &.{"constant value mismatch for ZIGUX_STATUS_FLAG_ERROR: header=1 binding=2"});

    const mismatch_struct_binding = try std.mem.replaceOwned(u8, allocator, GOOD_BINDING, "allocator_mode: u8,\n    unsafe_scope: u8,", "unsafe_scope: u8,\n    allocator_mode: u8,");
    defer allocator.free(mismatch_struct_binding);
    try runCaseSelfTest(allocator, GOOD_HEADER, mismatch_struct_binding, &.{"struct field parity mismatch for zigux_interop_policy -> InteropPolicy:"});

    const missing_helper_binding = try std.mem.replaceOwned(u8, allocator, GOOD_BINDING, "pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader { return header; }\n", "");
    defer allocator.free(missing_helper_binding);
    try runCaseSelfTest(allocator, GOOD_HEADER, missing_helper_binding, &.{"missing binding helper for header helper: zigux_header_canonicalize -> canonicalizeHeader"});

    var tmp = try guard.TempWorkspace.init(io, allocator, "phase3_abi_parity");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    try tmp.write(ABI_HEADER_REL, GOOD_HEADER);
    try tmp.write(ABI_BINDING_REL, GOOD_BINDING);
    const header_path = try guard.joinPath(allocator, root, ABI_HEADER_REL);
    defer allocator.free(header_path);
    const binding_path = try guard.joinPath(allocator, root, ABI_BINDING_REL);
    defer allocator.free(binding_path);
    const header_text = try guard.readUtf8File(io, allocator, header_path);
    defer allocator.free(header_text);
    const binding_text = try guard.readUtf8File(io, allocator, binding_path);
    defer allocator.free(binding_text);
    const repo_issues = try validatePair(allocator, header_text, binding_text);
    defer {
        for (repo_issues) |issue| allocator.free(issue);
        allocator.free(repo_issues);
    }
    try guard.expectSelfTest(repo_issues.len == 0);

    try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_SELF_TEST_CASE_COUNT={d}", .{5});
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
        if (std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    const header_path = try guard.joinPath(allocator, root, ABI_HEADER_REL);
    defer allocator.free(header_path);
    const binding_path = try guard.joinPath(allocator, root, ABI_BINDING_REL);
    defer allocator.free(binding_path);
    if (!guard.pathExists(io, header_path) or !guard.pathExists(io, binding_path)) {
        if (!guard.pathExists(io, header_path)) try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE=missing repo file: {s}", .{ABI_HEADER_REL});
        if (!guard.pathExists(io, binding_path)) try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE=missing repo file: {s}", .{ABI_BINDING_REL});
        try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY=fail", .{});
        try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE_COUNT={d}", .{2});
        std.process.exit(1);
    }
    const header_text = try guard.readUtf8File(io, allocator, header_path);
    defer allocator.free(header_text);
    const binding_text = try guard.readUtf8File(io, allocator, binding_path);
    defer allocator.free(binding_text);
    const issues = try validatePair(allocator, header_text, binding_text);
    defer {
        for (issues) |issue| allocator.free(issue);
        allocator.free(issues);
    }
    if (issues.len != 0) {
        for (issues) |issue| try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE={s}", .{issue});
        try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY=fail", .{});
        try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_ISSUE_COUNT={d}", .{issues.len});
        std.process.exit(1);
    }

    var header_defines = try parseHeaderDefines(header_text, allocator);
    defer {
        var dit = header_defines.iterator();
        while (dit.next()) |entry| allocator.free(entry.key_ptr.*);
        header_defines.deinit();
    }
    try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY=pass", .{});
    try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_HEADER_DEFINE_COUNT={d}", .{header_defines.count()});
    try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_STRUCT_COUNT={d}", .{STRUCT_NAME_MAP.len});
    try guard.printLine(io, "PHASE3_ABI_HEADER_BINDING_PARITY_HELPER_COUNT={d}", .{HELPER_NAME_MAP.len});
}