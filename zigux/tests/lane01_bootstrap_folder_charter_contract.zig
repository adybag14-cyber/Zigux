const std = @import("std");

fn readFileAlloc(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "zigux-alpha remains a planning workspace, not a subsystem tree" {
    const readme = try readFileAlloc("zigux-alpha/README.md");
    defer std.testing.allocator.free(readme);

    try expectContains(readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(readme, "It does not exist to become a permanent parallel subsystem tree.");
    try expectContains(readme, "Keep product planning and bootstrap artifacts here first.");
    try expectContains(readme, "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
}

test "approved product code exits zigux-alpha before implementation" {
    const readme = try readFileAlloc("zigux-alpha/README.md");
    defer std.testing.allocator.free(readme);
    const roadmap = try readFileAlloc("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer std.testing.allocator.free(roadmap);

    try expectContains(
        readme,
        "Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
    );
    try expectContains(
        roadmap,
        "`zigux-alpha/` is the staging area for:",
    );
    try expectContains(
        roadmap,
        "`zigux-alpha/` is not the final home for:",
    );
    try expectContains(roadmap, "`tools/lib/*.zig`");
    try expectContains(roadmap, "`scripts/zigux/`");
    try expectContains(roadmap, "`Documentation/zigux/`");
}

test "ZAR and Zigux responsibilities stay separated" {
    const readme = try readFileAlloc("zigux-alpha/README.md");
    defer std.testing.allocator.free(readme);
    const roadmap = try readFileAlloc("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer std.testing.allocator.free(roadmap);

    try expectContains(readme, "Zigux as the product repo.");
    try expectContains(roadmap, "`ZAR-Zig-Agent-Runtime` remains the experimental research and proving repo.");
    try expectContains(roadmap, "`Zigux` is the product repo.");
    try expectContains(roadmap, "ZAR should not try to become Zigux.");
}
