const std = @import("std");

const route = "make -C zigux phase2-cross";

const required_make_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const archive_target_scope = [_][]const u8{
    "x86_64-linux",
};

const CrossTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
    route: []const u8,
};

const cross_targets = [_]CrossTarget{
    .{
        .target = "x86_64-linux",
        .review_status = "pinned bootstrap archive",
        .validation_mode = "archive_required",
        .route = route,
    },
    .{
        .target = "aarch64-linux",
        .review_status = "route contract only",
        .validation_mode = "route_contract_only",
        .route = route,
    },
};

fn expectString(expected: []const u8, actual: []const u8) !void {
    try std.testing.expectEqualStrings(expected, actual);
}

fn targetIsArchiveScoped(target: []const u8) bool {
    for (archive_target_scope) |archive_target| {
        if (std.mem.eql(u8, archive_target, target)) {
            return true;
        }
    }
    return false;
}

test "phase2-cross stays in required policy route order" {
    try std.testing.expectEqual(@as(usize, 7), required_make_routes.len);
    try expectString("phase2-kconfig", required_make_routes[2]);
    try expectString("phase2-cross", required_make_routes[3]);
    try expectString("phase2-genksyms", required_make_routes[4]);

    var cross_route_count: usize = 0;
    for (required_make_routes) |make_route| {
        if (std.mem.eql(u8, make_route, "phase2-cross")) {
            cross_route_count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), cross_route_count);
}

test "archive scope matches the archive-required cross target" {
    try std.testing.expectEqual(@as(usize, 1), archive_target_scope.len);
    try expectString("x86_64-linux", archive_target_scope[0]);
    try std.testing.expectEqual(@as(usize, 2), cross_targets.len);

    var archive_required_count: usize = 0;
    var route_contract_count: usize = 0;
    for (cross_targets) |entry| {
        try expectString(route, entry.route);

        if (targetIsArchiveScoped(entry.target)) {
            try expectString("archive_required", entry.validation_mode);
            archive_required_count += 1;
        } else {
            try expectString("route_contract_only", entry.validation_mode);
            route_contract_count += 1;
        }
    }

    try std.testing.expectEqual(archive_target_scope.len, archive_required_count);
    try std.testing.expectEqual(@as(usize, 1), route_contract_count);
}

test "review statuses keep archive-backed and route-only targets distinct" {
    try expectString("x86_64-linux", cross_targets[0].target);
    try expectString("pinned bootstrap archive", cross_targets[0].review_status);
    try expectString("archive_required", cross_targets[0].validation_mode);

    try expectString("aarch64-linux", cross_targets[1].target);
    try expectString("route contract only", cross_targets[1].review_status);
    try expectString("route_contract_only", cross_targets[1].validation_mode);
}
