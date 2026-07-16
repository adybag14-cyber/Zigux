const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "validated scripts/zigux/validate_phase3_selftest.zig";
pub const self_test_pass_marker = "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass",
    "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated zigux/tests/build.zig",
    "validated scripts/zigux/validate_phase3_selftest.zig",
};

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "fn addPhase3DevTStarterPacket(",
    ".root_source_file = b.path(\"../uapi/dev_t.zig\"),",
    ".root_source_file = b.path(\"../uapi/version.zig\"),",
    ".root_source_file = b.path(\"../bindings/dev_t.zig\"),",
    ".root_source_file = b.path(\"../bindings/version.zig\"),",
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    "version_binding.addImport(\"uapi_version\", uapi_version);",
    "export_shim.addImport(\"abi_bindings\", abi_bindings);",
    "export_shim.addImport(\"dev_t_binding\", dev_t_binding);",
    "export_shim.addImport(\"version_binding\", version_binding);",
    "root_module.addImport(\"uapi_dev_t\", uapi_dev_t);",
    "root_module.addImport(\"dev_t_binding\", dev_t_binding);",
    "root_module.addImport(\"version_binding\", version_binding);",
    "root_module.addImport(\"export_shim\", export_shim);",
    "fn addPhase3ErrPtrXarrayStarterPacket(",
    "fn addPhase3XarraySlotStarterPacket(",
    ".root_source_file = b.path(\"../helpers/xarray_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_xarray_slot_starter_packet.zig\"),",
    "xarray_slot_view.addImport(\"err_ptr\", err_ptr);",
    "xarray_slot_view.addImport(\"xa_value\", xa_value);",
    "root_module.addImport(\"xarray_slot_view\", xarray_slot_view);",
    "fn addPhase3BitmapCpumaskStarterPacket(",
    ".root_source_file = b.path(\"../helpers/bitmap_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/cpumask_view.zig\"),",
    ".root_source_file = b.path(\"phase3_bitmap_cpumask_starter_packet.zig\"),",
    "cpumask_view.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"cpumask_view\", cpumask_view);",
    "fn addPhase3ListHListStarterPacket(",
    ".root_source_file = b.path(\"../helpers/list_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/hlist_view.zig\"),",
    ".root_source_file = b.path(\"phase3_list_hlist_starter_packet.zig\"),",
    "root_module.addImport(\"list_view\", list_view);",
    "root_module.addImport(\"hlist_view\", hlist_view);",
    "fn addPhase3ErrPtrXarrayDump(",
    "fn addPhase3PolicyStarterPacket(",
    "fn addPhase3AbiCorePacket(",
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    ".root_source_file = b.path(\"phase3_abi.zig\"),",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "fn addPhase3ExportUapiLayout(",
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    ".root_source_file = b.path(\"../bindings/header_family.zig\"),",
    "header_family_binding.addImport(\"abi_bindings\", abi_bindings);",
    "header_family_binding.addImport(\"dev_t_binding\", dev_t_binding);",
    "header_family_binding.addImport(\"version_binding\", version_binding);",
    "header_family_binding.addImport(\"uapi_version\", uapi_version);",
    "root_module.addImport(\"uapi_version\", uapi_version);",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "fn addPhase3LowLevelWrappers(",
    "fn addPhase3AbiDump(",
    ".root_source_file = b.path(\"phase3_abi_dump_current.zig\"),",
    "\"phase3-dev-t-starter-packet\"",
    "\"phase3-errptr-xarray-starter-packet\"",
    "\"phase3-xarray-slot-starter-packet\"",
    "\"phase3-bitmap-cpumask-starter-packet\"",
    "\"phase3-list-hlist-starter-packet\"",
    "\"phase3-errptr-xarray-dump\"",
    "\"phase3-policy-starter-packet\"",
    "\"phase3-abi-core-packet\"",
    "\"phase3-export-uapi-layout\"",
    "\"phase3-low-level-wrappers\"",
    "\"phase3-test\"",
    "\"phase3-dump\"",
    "const phase3_xarray_slot_starter_packet = addPhase3XarraySlotStarterPacket(",
    "const phase3_bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket(",
    "const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket(",
    "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(",
    "const phase3_xarray_slot_step = b.step(",
    "const phase3_bitmap_cpumask_step = b.step(",
    "const phase3_list_hlist_step = b.step(",
    "const phase3_abi_core_step = b.step(",
    "const phase3_export_uapi_layout_step = b.step(",
    "phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_bitmap_cpumask_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_dev_t_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_policy_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    "smoke_step.dependOn(phase3_test_step);",
    "test_step.dependOn(phase3_test_step);",
    "b.step(",
};

const markers_1 = [_][]const u8{
    "scripts/zigux/check_phase3_dev_t_starter_packet.zig",
    "scripts/zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "scripts/zigux/check_phase3_xarray_slot_starter_packet.zig",
    "scripts/zigux/check_phase3_xarray_slot.zig",
    "scripts/zigux/check_phase3_idr_slot_starter_packet.zig",
    "scripts/zigux/check_phase3_idr_slot.zig",
    "scripts/zigux/check_phase3_policy_starter_packet.zig",
    "scripts/zigux/check_phase3_policy_dump.zig",
    "scripts/zigux/validate_phase3.zig",
    "scripts/zigux/check_phase3_abi.zig",
    "scripts/zigux/check_phase3_abi_support_packet.zig",
    "scripts/zigux/check_phase3_abi_manifest_replay_routes.zig",
    "scripts/zigux/check_phase3_shared_tests_routes.zig",
    "scripts/zigux/check_phase3_readme_tooling_inventory.zig",
    "scripts/zigux/check_phase3_wrapper_templates.zig",
    "scripts/zigux/check_phase3_catalog_selftest.zig",
    "scripts/zigux/run_phase3_checks.zig",
    "scripts/zigux/validate_phase3_validator_support_surface.zig",
    "scripts/zigux/validate_phase3_export_uapi_survey.zig",
    "scripts/zigux/check_phase3_export_uapi_c_header_smoke.zig",
    "scripts/zigux/validate_phase3_abi_header_family_survey.zig",
    "scripts/zigux/validate_phase3_policy_unsafe_survey.zig",
    "scripts/zigux/validate_phase3_low_level_wrapper_survey.zig",
    "scripts/zigux/validate_phase3_linux_zigux_header_governance.zig",
    "scripts/zigux/check_phase3_selftest_surface.zig",
    "scripts/zigux/check_phase3_bitmap_cpumask.zig",
    "scripts/zigux/check_phase3_list_hlist_starter_packet.zig",
    "\"phase\": \"Phase 3\"",
    "\"replay_routes\"",
    "zig run check_phase3_shared_tests_routes.zig --self-test",
    "zig run check_phase3_shared_tests_routes.zig",
};

const markers_2 = [_][]const u8{
    "phase3-export-uapi-layout:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "phase3-export-uapi-layout-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "phase3-export-shim-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "phase3-low-level-wrappers:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "phase3-low-level-wrappers-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3-policy-starter-packet-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "phase3-policy-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "phase3-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-test --build-file zigux/tests/build.zig",
    "phase3-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-dump --build-file zigux/tests/build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
};

const markers_3 = [_][]const u8{
    "      - name: Self-test current Phase 3 interop packet",
    "        run: zig run scripts/zigux/validate_phase3_selftest.zig",
    "      - name: Check current Phase 3 interop packet",
    "        run: zig run scripts/zigux/run_phase3_checks.zig",
    "      - name: Run current Phase 3 export/UAPI layout replay",
    "        run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "      - name: Run current Phase 3 export shim replay",
    "        run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "      - name: Run current Phase 3 policy starter-packet replay",
    "        run: make -C zigux phase3-policy-starter-packet-test",
    "      - name: Run current Phase 3 policy dump replay",
    "        run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "      - name: Run current Phase 3 policy dump make wrapper",
    "        run: make -C zigux phase3-policy-dump",
    "      - name: Self-test current Phase 3 low-level wrapper survey validator",
    "      - name: Check current Phase 3 low-level wrapper survey packet",
    "      - name: Run current Phase 3 low-level wrapper replay",
    "        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "      - name: Run current Phase 3 low-level wrapper make route",
    "        run: make -C zigux phase3-low-level-wrappers",
    "      - name: Run current Phase 3 focused low-level wrapper make route",
    "        run: make -C zigux phase3-low-level-wrappers-test",
    "      - name: Run current Phase 3 shared tests-root packet",
    "        run: zig build phase3-test --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 3 ABI dump replay",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/build.zig", .markers = &markers_0 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_1 },
    .{ .rel = "zigux/Makefile", .markers = &markers_2 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_3 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "="))
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len })
        else
            try guard.printLine(io, "{s}", .{marker});
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const owner_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(owner_path);
        const text = try guard.readUtf8File(io, allocator, owner_path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try printOutputMarkers(io, &self_test_output_markers);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
