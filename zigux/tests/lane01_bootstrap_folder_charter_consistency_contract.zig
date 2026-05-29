const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "Lane 01 README keeps zigux-alpha planning-only and non-mirror-tree" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux-alpha/README.md");
    defer allocator.free(readme);

    try expectContains(readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(readme, "It exists to hold:");
    try expectContains(readme, "- program-level planning");
    try expectContains(readme, "- source maps");
    try expectContains(readme, "- phase ledgers");
    try expectContains(readme, "- validation and porting rules");
    try expectContains(readme, "- first-commit sequencing for the Zigux product buildout");
    try expectContains(readme, "It does not exist to become a permanent parallel subsystem tree.");
    try expectContains(readme, "- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
}

test "Lane 01 roadmap and README agree on approved code destinations" {
    const allocator = std.testing.allocator;
    const readme = try readRepoFile(allocator, "zigux-alpha/README.md");
    defer allocator.free(readme);
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(readme, "- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.");
    try expectContains(roadmap, "3. Co-locate product code with Linux ownership.");
    try expectContains(roadmap, "- Host-side helper ports belong beside current files such as `tools/lib/*.zig`.");
    try expectContains(roadmap, "- Runtime helper ports belong beside current files such as `lib/*.zig`.");
    try expectContains(roadmap, "- Driver pilots belong in current subsystem trees such as `drivers/virtio/*.zig`.");
    try expectContains(roadmap, "4. Keep the Zigux support root small.");
    try expectContains(roadmap, "  - `zigux/kernel/`");
    try expectContains(roadmap, "  - `zigux/helpers/`");
    try expectContains(roadmap, "  - `zigux/bindings/`");
    try expectContains(roadmap, "  - `zigux/uapi/`");
    try expectContains(roadmap, "  - `zigux/tests/`");
    try expectContains(roadmap, "  - `zigux/unsafe/`");
}

test "Lane 01 roadmap keeps alpha scope before product phase expansion" {
    const allocator = std.testing.allocator;
    const roadmap = try readRepoFile(allocator, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap);

    try expectContains(roadmap, "## zigux-alpha Scope");
    try expectContains(roadmap, "`zigux-alpha/` is the staging area for:");
    try expectContains(roadmap, "`zigux-alpha/` is not the final home for:");
    try expectContains(roadmap, "Those should eventually land in:");
    try expectContains(roadmap, "- `tools/lib/*.zig`");
    try expectContains(roadmap, "- `scripts/zigux/`");
    try expectContains(roadmap, "- `Documentation/zigux/`");
    try expectContains(roadmap, "- `drivers/*/*.zig`");

    try expectBefore(roadmap, "## Non-Negotiable Product Rules", "## zigux-alpha Scope");
    try expectBefore(roadmap, "## How ZAR Should Feed Zigux", "## zigux-alpha Scope");
    try expectBefore(roadmap, "## zigux-alpha Scope", "## Product Features by Phase");
}
