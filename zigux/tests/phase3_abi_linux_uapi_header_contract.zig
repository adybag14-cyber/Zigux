const std = @import("std");
const testing = std.testing;

const build_options = @import("build_options");

fn readLinuxHeader(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        build_options.linux_header_path,
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

test "Linux UAPI header keeps public include and version facade visible" {
    const header = try readLinuxHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "#include <stdint.h>");
    try expectContains(header, "#include <zigux/abi.h>");
    try expectContains(header, "#include <zigux/dev_t.h>");
    try expectContains(header, "#define ZIGUX_UAPI_ABI_MAJOR 0u");
    try expectContains(header, "#define ZIGUX_UAPI_ABI_MINOR 1u");
    try expectContains(header, "#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u");
    try expectContains(header, "#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u");
    try expectContains(header, "#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)");
    try expectContains(header, "struct zigux_uapi_version");
    try expectContains(header, "static inline struct zigux_uapi_version zigux_uapi_version_current(void)");
    try expectContains(header, "static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version)");
    try expectContains(header, "static inline struct zigux_export_status zigux_uapi_validate_version(");

    try expectOrdered(header, "#include <zigux/abi.h>", "#include <zigux/dev_t.h>");
    try expectOrdered(header, "zigux_uapi_version_current", "zigux_uapi_version_matches_current");
    try expectOrdered(header, "zigux_uapi_version_matches_current", "zigux_uapi_validate_version");
}

test "Linux UAPI header keeps boundary-header facade and compatibility aliases aligned" {
    const header = try readLinuxHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)");
    try expectContains(header, "static inline zigux_boundary_header zigux_uapi_boundary_header_compatible(");
    try expectContains(header, "static inline int zigux_uapi_boundary_header_has_current_abi_version(uint16_t abi_version)");
    try expectContains(header, "static inline int zigux_uapi_boundary_header_is_compatible_size(uint32_t size)");
    try expectContains(header, "static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)");
    try expectContains(header, "static inline int zigux_uapi_boundary_header_is_canonical(zigux_boundary_header header)");
    try expectContains(header, "static inline int zigux_uapi_boundary_header_is_compatible(zigux_boundary_header header)");
    try expectContains(header, "static inline int zigux_uapi_boundary_header_extends_boundary(zigux_boundary_header header)");
    try expectContains(header, "static inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(");
    try expectContains(header, "static inline zigux_boundary_header zigux_uapi_boundary_header_canonicalize(zigux_boundary_header header)");
    try expectContains(header, "static inline struct zigux_export_status zigux_uapi_validate_boundary_header(");

    try expectContains(header, "static inline struct zigux_export_status zigux_validate_boundary_header(");
    try expectContains(header, "static inline zigux_boundary_header zigux_boundary_header_make(uint16_t flags)");
    try expectContains(header, "static inline zigux_boundary_header zigux_boundary_header_make_compatible(");
    try expectContains(header, "static inline int zigux_boundary_header_is_current_abi_version(uint16_t abi_version)");
    try expectContains(header, "static inline int zigux_boundary_header_is_compatible(zigux_boundary_header header)");
    try expectContains(header, "static inline zigux_boundary_header zigux_boundary_header_canonicalize(");

    try expectOrdered(header, "zigux_uapi_boundary_header_current", "zigux_uapi_boundary_header_compatible");
    try expectOrdered(header, "zigux_uapi_boundary_header_is_compatible", "zigux_uapi_boundary_header_extends_boundary");
    try expectOrdered(header, "zigux_uapi_boundary_header_requested_extra_bytes", "zigux_uapi_boundary_header_canonicalize");
    try expectOrdered(header, "zigux_uapi_validate_boundary_header", "zigux_validate_boundary_header");
    try expectOrdered(header, "zigux_boundary_header_make", "zigux_boundary_header_is_current_abi_version");
}

test "Linux UAPI header keeps policy status rbtree and dev_t relays visible" {
    const header = try readLinuxHeader(testing.allocator);
    defer testing.allocator.free(header);

    try expectContains(header, "static inline struct zigux_interop_policy zigux_uapi_default_interop_policy(void)");
    try expectContains(header, "static inline int zigux_uapi_panic_mode_is_known(uint8_t mode)");
    try expectContains(header, "static inline int zigux_uapi_allocator_mode_is_known(uint8_t mode)");
    try expectContains(header, "static inline int zigux_uapi_unsafe_scope_is_known(uint8_t scope)");
    try expectContains(header, "static inline int zigux_uapi_interop_policy_reserved_clear(");
    try expectContains(header, "static inline int zigux_uapi_interop_policy_is_recognized(");
    try expectContains(header, "static inline struct zigux_export_status zigux_uapi_validate_interop_policy(");

    try expectContains(header, "static inline int zigux_uapi_rbtree_root_view_is_cached(zigux_rbtree_root_view view)");
    try expectContains(header, "static inline int zigux_uapi_rbtree_root_view_has_leftmost(zigux_rbtree_root_view view)");
    try expectContains(header, "static inline int zigux_uapi_rbtree_root_view_is_valid(zigux_rbtree_root_view view)");
    try expectContains(header, "static inline zigux_rbtree_root_view zigux_uapi_rbtree_root_view_canonicalize(");
    try expectContains(header, "static inline struct zigux_export_status zigux_uapi_validate_rbtree_root_view(");
    try expectContains(header, "static inline int zigux_uapi_facility_is_known(uint16_t facility)");
    try expectContains(header, "static inline int zigux_uapi_export_status_has_known_facility(");

    try expectContains(header, "static inline struct zigux_dev_t_fields zigux_uapi_dev_t_fields_make(");
    try expectContains(header, "static inline uint32_t zigux_uapi_mkdev(uint32_t major, uint32_t minor)");
    try expectContains(header, "static inline uint32_t zigux_uapi_major(uint32_t dev)");
    try expectContains(header, "static inline uint32_t zigux_uapi_minor(uint32_t dev)");
    try expectContains(header, "static inline struct zigux_export_status zigux_uapi_validate_dev_t_components(");
    try expectContains(header, "static inline int zigux_uapi_dev_t_fields_range_is_valid(");
    try expectContains(header, "static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(");

    try expectOrdered(header, "zigux_uapi_interop_policy_is_recognized", "zigux_uapi_validate_interop_policy");
    try expectOrdered(header, "zigux_uapi_rbtree_root_view_is_valid", "zigux_uapi_validate_rbtree_root_view");
    try expectOrdered(header, "zigux_uapi_facility_is_known", "zigux_uapi_export_status_has_known_facility");
    try expectOrdered(header, "zigux_uapi_dev_t_fields_make", "zigux_uapi_validate_dev_t_components");
    try expectOrdered(header, "zigux_uapi_dev_t_fields_range_is_valid", "zigux_uapi_validate_dev_t_range");
}
