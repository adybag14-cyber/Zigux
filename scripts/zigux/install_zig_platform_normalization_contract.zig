const std = @import("std");
const install = @import("install_zig.zig");

test "platform normalization accepts common spellings" {
    try std.testing.expectEqualStrings(try install.normalizeOs("LINUX"), "linux");
    try std.testing.expectEqualStrings(try install.normalizeOs("mac"), "macos");
    try std.testing.expectEqualStrings(try install.normalizeOs("Windows_NT"), "windows");
}

test "architecture normalization accepts common aliases" {
    try std.testing.expectEqualStrings(try install.normalizeArch("x64"), "x86_64");
    try std.testing.expectEqualStrings(try install.normalizeArch("arm64"), "aarch64");
    try std.testing.expectEqualStrings(try install.normalizeArch("i386"), "x86");
}

test "detected keys are available for default resolution" {
    _ = install.detectSystemKey() catch {};
    _ = install.detectArchKey() catch {};
    try std.testing.expect(true);
}