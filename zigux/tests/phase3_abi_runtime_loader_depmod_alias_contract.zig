const std = @import("std");
const runtime_loader_contract = @import("runtime_loader_contract");

const DepmodAliasRecord = runtime_loader_contract.DepmodAliasRecord;
const LoadPlan = runtime_loader_contract.LoadPlan;
const ModuleMetadata = runtime_loader_contract.ModuleMetadata;

fn runtimeBitmapPlan(metadata: ModuleMetadata) LoadPlan {
    return .{
        .module_name = "runtime_bitmap",
        .anchor = "lib/test_bitmap.c",
        .entry_symbol = "zigux_runtime_bitmap_init",
        .exit_symbol = "zigux_runtime_bitmap_exit",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .module_metadata = metadata,
        .allocator_handoff = .arena,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

test "depmod alias readiness requires license and runtime-pilot aliases" {
    const ready = ModuleMetadata{
        .license = "GPL",
        .aliases = &.{
            "zigux:runtime-pilot:runtime_bitmap",
            "zigux:runtime-pilot:bitmap-anchor",
        },
    };
    try std.testing.expect(runtime_loader_contract.keepsDepmodAliasReady(ready));

    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasReady(.{
        .license = "",
        .aliases = ready.aliases,
    }));
    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasReady(.{
        .license = "GPL",
        .aliases = &.{},
    }));
    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasReady(.{
        .license = "GPL",
        .aliases = &.{""},
    }));
    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasReady(.{
        .license = "GPL",
        .aliases = &.{"runtime_bitmap"},
    }));
}

test "depmod alias records preserve module name and alias order" {
    const plan = runtimeBitmapPlan(.{
        .license = "GPL",
        .aliases = &.{
            "zigux:runtime-pilot:runtime_bitmap",
            "zigux:runtime-pilot:bitmap-anchor",
            "zigux:runtime-pilot:selftest",
        },
    });

    try std.testing.expectEqual(@as(usize, 3), runtime_loader_contract.depmodAliasRecordCount(plan));
    try std.testing.expectEqualStrings("runtime_bitmap", runtime_loader_contract.depmodAliasRecordFor(plan, 0).?.module_name);
    try std.testing.expectEqualStrings(
        "zigux:runtime-pilot:runtime_bitmap",
        runtime_loader_contract.depmodAliasRecordFor(plan, 0).?.module_alias,
    );
    try std.testing.expectEqualStrings(
        "zigux:runtime-pilot:bitmap-anchor",
        runtime_loader_contract.depmodAliasRecordFor(plan, 1).?.module_alias,
    );
    try std.testing.expectEqualStrings(
        "zigux:runtime-pilot:selftest",
        runtime_loader_contract.depmodAliasRecordFor(plan, 2).?.module_alias,
    );
    try std.testing.expect(runtime_loader_contract.depmodAliasRecordFor(plan, 3) == null);
}

test "depmod alias record comparison catches count name and alias drift" {
    const plan = runtimeBitmapPlan(.{
        .license = "GPL",
        .aliases = &.{
            "zigux:runtime-pilot:runtime_bitmap",
            "zigux:runtime-pilot:bitmap-anchor",
        },
    });
    const expected = [_]DepmodAliasRecord{
        .{
            .module_name = "runtime_bitmap",
            .module_alias = "zigux:runtime-pilot:runtime_bitmap",
        },
        .{
            .module_name = "runtime_bitmap",
            .module_alias = "zigux:runtime-pilot:bitmap-anchor",
        },
    };
    try std.testing.expect(runtime_loader_contract.keepsDepmodAliasRecordsExplicit(plan, &expected));

    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasRecordsExplicit(plan, expected[0..1]));

    var drifted = expected;
    drifted[0].module_name = "runtime_bitmap_drift";
    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasRecordsExplicit(plan, &drifted));

    drifted = expected;
    drifted[1].module_alias = "zigux:runtime-pilot:other";
    try std.testing.expect(!runtime_loader_contract.keepsDepmodAliasRecordsExplicit(plan, &drifted));
}

test "depmod alias relay stays independent from request state fields" {
    const blocked_alias_record_fields = [_][]const u8{
        "request_state",
        "runtime_substrate_ready",
        "requires_runtime_substrate",
        "provides_selftest_hook",
    };

    inline for (blocked_alias_record_fields) |field| {
        try std.testing.expect(!@hasField(DepmodAliasRecord, field));
    }
}
