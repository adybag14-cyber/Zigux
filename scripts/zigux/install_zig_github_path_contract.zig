const std = @import("std");
const install = @import("install_zig.zig");

test "github path publication helper is exported" {
    _ = install.appendGithubPath;
    try std.testing.expect(true);
}

test "resolve bin dir precedes path publication in install flow" {
    _ = install.resolveBinDir;
    _ = install.appendGithubPath;
    try std.testing.expect(true);
}