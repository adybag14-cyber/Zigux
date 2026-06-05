const std = @import("std");
const testing = std.testing;

const build_options = @import("build_options");

fn readAbiHeader(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        build_options.abi_header_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

test "C ABI header keeps boundary-header inline helper packet visible" {
    const header = try readAbiHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "typedef struct zigux_boundary_header");
    try expectContains(header, "static inline zigux_boundary_header zigux_default_header(uint16_t flags)");
    try expectContains(header, "static inline zigux_boundary_header zigux_compatible_header(");
    try expectContains(header, "static inline int zigux_abi_version_is_current(uint16_t abi_version)");
    try expectContains(header, "static inline int zigux_header_is_compatible_size(uint32_t size)");
    try expectContains(header, "static inline int zigux_header_is_canonical_size(uint32_t size)");
    try expectContains(header, "static inline int zigux_header_is_canonical(zigux_boundary_header header)");
    try expectContains(header, "static inline int zigux_header_is_compatible(zigux_boundary_header header)");
    try expectContains(header, "static inline int zigux_header_extends_boundary(zigux_boundary_header header)");
    try expectContains(header, "static inline uint32_t zigux_header_requested_extra_bytes(");
    try expectContains(header, "static inline zigux_boundary_header zigux_header_canonicalize(");

    try expectOrdered(header, "zigux_default_header", "zigux_compatible_header");
    try expectOrdered(header, "zigux_header_is_compatible", "zigux_header_extends_boundary");
    try expectOrdered(header, "zigux_header_extends_boundary", "zigux_header_requested_extra_bytes");
    try expectOrdered(header, "zigux_header_requested_extra_bytes", "zigux_header_canonicalize");
}

test "C ABI header keeps policy and status inline helpers fail-closed" {
    const header = try readAbiHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "struct zigux_interop_policy");
    try expectContains(header, "static inline struct zigux_interop_policy zigux_default_interop_policy(void)");
    try expectContains(header, "static inline int zigux_panic_mode_is_known(uint8_t mode)");
    try expectContains(header, "static inline int zigux_allocator_mode_is_known(uint8_t mode)");
    try expectContains(header, "static inline int zigux_unsafe_scope_is_known(uint8_t scope)");
    try expectContains(header, "static inline int zigux_interop_policy_reserved_clear(");
    try expectContains(header, "static inline int zigux_interop_policy_is_recognized(");

    try expectContains(header, "struct zigux_export_status");
    try expectContains(header, "static inline int zigux_facility_is_known(uint16_t facility)");
    try expectContains(header, "static inline struct zigux_export_status zigux_make_status(");
    try expectContains(header, "static inline struct zigux_export_status zigux_ok_status(uint16_t facility)");
    try expectContains(header, "static inline int zigux_export_status_ok(struct zigux_export_status status)");
    try expectContains(header, "static inline int zigux_export_status_has_known_facility(");

    try expectOrdered(header, "zigux_interop_policy_reserved_clear", "zigux_interop_policy_is_recognized");
    try expectOrdered(header, "zigux_facility_is_known", "zigux_make_status");
    try expectOrdered(header, "zigux_make_status", "zigux_ok_status");
    try expectOrdered(header, "zigux_export_status_ok", "zigux_export_status_has_known_facility");
}

test "C ABI header keeps notifier result and priority-chain helpers exported" {
    const header = try readAbiHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "#define ZIGUX_NOTIFIER_DONE 0U");
    try expectContains(header, "#define ZIGUX_NOTIFIER_OK 1U");
    try expectContains(header, "#define ZIGUX_NOTIFIER_STOP 2U");
    try expectContains(header, "typedef struct zigux_notifier_chain_priority_increase");
    try expectContains(header, "struct zigux_notifier_block");
    try expectContains(header, "static inline int zigux_notifier_result_is_known(uint32_t result)");
    try expectContains(header, "static inline int zigux_notifier_result_stops_chain(uint32_t result)");
    try expectContains(header, "static inline int zigux_notifier_chain_has_nonincreasing_priority(");
    try expectContains(header, "static inline int zigux_notifier_first_chain_priority_increase(");

    try expectOrdered(header, "zigux_notifier_result_is_known", "zigux_notifier_result_stops_chain");
    try expectOrdered(header, "zigux_notifier_chain_has_nonincreasing_priority", "zigux_notifier_first_chain_priority_increase");
}

test "C ABI header keeps list and hlist inline consistency helpers exported" {
    const header = try readAbiHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "struct zigux_list_head");
    try expectContains(header, "struct zigux_hlist_head");
    try expectContains(header, "struct zigux_hlist_node");
    try expectContains(header, "typedef struct zigux_list_backlink_break");
    try expectContains(header, "typedef struct zigux_hlist_prev_link_break");
    try expectContains(header, "static inline int zigux_list_is_empty(const struct zigux_list_head *head)");
    try expectContains(header, "static inline int zigux_list_first_broken_backlink(");
    try expectContains(header, "static inline int zigux_list_has_consistent_backlinks(");
    try expectContains(header, "static inline int zigux_hlist_first_pprev_matches_head(");
    try expectContains(header, "static inline int zigux_hlist_first_broken_prev_link(");
    try expectContains(header, "static inline int zigux_hlist_has_consistent_prev_links(");
    try expectContains(header, "static inline int zigux_hlist_tail_next_is_null(");

    try expectOrdered(header, "zigux_list_is_empty", "zigux_list_first_broken_backlink");
    try expectOrdered(header, "zigux_list_first_broken_backlink", "zigux_list_has_consistent_backlinks");
    try expectOrdered(header, "zigux_hlist_first_pprev_matches_head", "zigux_hlist_first_broken_prev_link");
    try expectOrdered(header, "zigux_hlist_first_broken_prev_link", "zigux_hlist_has_consistent_prev_links");
    try expectOrdered(header, "zigux_hlist_has_consistent_prev_links", "zigux_hlist_tail_next_is_null");
}
