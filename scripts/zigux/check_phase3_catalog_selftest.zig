const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_CATALOG_SELFTEST_CHECK=pass";
pub const self_test_pass_marker = "PHASE3_CATALOG_SELFTEST_CHECK_SELF_TEST=pass";

const REQUIRED_MARKERS__scripts_zigux_phase3_catalog_py = [_][]const u8{
    "PHASE3_CATALOG_PHASE = \"Phase 3\"",
    "PHASE3_CATALOG_SCOPE = \"abi-runtime\"",
    "MANIFEST_PATH = Path(\"zigux/tests/fixtures/phase3_abi_manifest.json\")",
    "\"Documentation/zigux/phase3-abi-slice.md\"",
    "\"Documentation/zigux/phase3-export-uapi-boundary-survey.md\"",
    "\"Documentation/zigux/phase3-errptr-xarray-slice.md\"",
    "\"Documentation/zigux/phase3-xarray-slot-slice.md\"",
    "\"Documentation/zigux/phase3-idr-slot-slice.md\"",
    "\"Documentation/zigux/phase3-bitmap-cpumask-slice.md\"",
    "\"Documentation/zigux/phase3-list-hlist-slice.md\"",
    "\"scripts\\zigux/check_phase3_catalog_selftest.zig\"",
    "\"scripts/zigux/check_phase3_wrapper_templates.zig\"",
    "\"scripts\\zigux/check_phase3_wrapper_templates.zig\"",
    "\"scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_xarray_slot.zig\"",
    "\"scripts\\zigux/check_phase3_idr_slot_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_idr_slot.zig\"",
    "\"scripts\\zigux/check_phase3_bitmap_cpumask.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist.zig\"",
    "\"scripts\\zigux/check_phase3_low_level_wrappers.zig\"",
    "\"zigux/helpers/idr_slot_view.zig\"",
    "\"zigux/tests/phase3_idr_slot_starter_packet.zig\"",
    "\"zigux/tests/phase3_idr_slot_starter_packet_build.zig\"",
    "\"zigux/tests/fixtures/phase3_idr_slot_manifest.json\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json\"",
    "\"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_list_hlist/expected.json\"",
    "\"zigux/tests/phase3_list_hlist_dump.zig\"",
    "\"zigux/tests/phase3_list_hlist_dump_build.zig\"",
    "\"zigux/tests/phase3_abi_dump_current.zig\"",
    "\"zigux/Makefile\"",
    "\".github/workflows/zigux-bootstrap.yml\"",
    "\"zig run scripts\\zigux/check_phase3_catalog_selftest.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_wrapper_templates.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_idr_slot_starter_packet.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_idr_slot_starter_packet.zig --repo-root .\"",
    "\"zig run scripts\\zigux/check_phase3_idr_slot.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_idr_slot.zig --repo-root . --zig zig --cc gcc\"",
    "\"zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_list_hlist.zig --repo-root . --zig zig --cc gcc\"",
    "\"zig build phase3-abi-export --build-file zigux/tests/build.zig\"",
    "\"make -C zigux phase3-abi-export\"",
    "\"zig build phase3-idr-slot --build-file zigux/tests/build.zig\"",
    "\"zig build phase3-idr-slot-starter-packet-test --build-file zigux/tests/phase3_idr_slot_starter_packet_build.zig\"",
    "\"zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig\"",
    "\"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig\"",
    "print(\"PHASE3_CATALOG_SELF_TEST=pass\")",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_abi_manifest_json = [_][]const u8{
    "\"Documentation/zigux/phase3-list-hlist-slice.md\"",
    "\"scripts\\zigux/check_phase3_catalog_selftest.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist.zig\"",
    "\"scripts\\zigux/check_phase3_low_level_wrappers.zig\"",
    "\"zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c\"",
    "\"zigux/tests/fixtures/phase3_list_hlist/phase3_list_hlist_c_harness.c\"",
    "\"zigux/tests/phase3_list_hlist_dump.zig\"",
    "\"zigux/tests/phase3_list_hlist_dump_build.zig\"",
    "\"zigux/tests/phase3_abi_dump_current.zig\"",
    "\"zigux/Makefile\"",
    "\".github/workflows/zigux-bootstrap.yml\"",
    "\"zig build phase3-abi-export --build-file zigux/tests/build.zig\"",
    "\"make -C zigux phase3-abi-export\"",
    "\"zig run scripts\\zigux/check_phase3_idr_slot.zig --repo-root . --zig zig --cc gcc\"",
    "\"zig build phase3-idr-slot --build-file zigux/tests/build.zig\"",
    "\"zig build phase3-idr-slot-dump --build-file zigux/tests/phase3_idr_slot_dump_build.zig\"",
    "\"zig run scripts\\zigux/check_phase3_list_hlist.zig --repo-root . --zig zig --cc gcc\"",
    "\"zig build phase3-list-hlist-dump --build-file zigux/tests/phase3_list_hlist_dump_build.zig\"",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-export-uapi-boundary-survey_md = [_][]const u8{
    "PHASE3_EXPORT_UAPI_CATALOG_SELFTEST_GUARD=scripts\\zigux/check_phase3_catalog_selftest.zig",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-export-uapi-survey_py = [_][]const u8{
    "CATALOG_SELFTEST_CHECK_PATH = Path(\"scripts\\zigux/check_phase3_catalog_selftest.zig\")",
    "print(\"PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass\")",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-low-level-wrapper-boundary-survey_md = [_][]const u8{
    "`scripts\\zigux/check_phase3_catalog_selftest.zig`",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-low-level-wrapper-survey_py = [_][]const u8{
    "print(\"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass\")",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-abi-header-family-survey_md = [_][]const u8{
    "PHASE3_ABI_CATALOG_SELFTEST_GUARD=scripts\\zigux/check_phase3_catalog_selftest.zig",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-abi-header-family-survey_py = [_][]const u8{
    "print(\"PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass\")",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-linux-zigux-header-governance_md = [_][]const u8{
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-linux-zigux-header-governance_py = [_][]const u8{
    "NOTE_PATH = Path(\"Documentation/zigux/phase3-linux-zigux-header-governance.md\")",
    "HEADER_PATH = Path(\"include/linux/zigux.h\")",
    "print(\"PHASE3_LINUX_ZIGUX_HEADER_GOVERNANCE_SELF_TEST=pass\")",
};

const FORBIDDEN_CATALOG_MARKERS = [_][]const u8{
    "\"zigux/tests/phase3_abi_dump.zig\"",
    "\"phase3_abi_dump_build.zig\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__scripts_zigux_phase3_catalog_py_path = try guard.joinPath(allocator, root, "scripts/zigux/phase3/catalog/py");
    defer allocator.free(text_required_markers__scripts_zigux_phase3_catalog_py_path);
    const text_required_markers__scripts_zigux_phase3_catalog_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_phase3_catalog_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_phase3_catalog_py);
    for (REQUIRED_MARKERS__scripts_zigux_phase3_catalog_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_phase3_catalog_py, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/abi/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_abi_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json, marker);
    const text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-export-uapi-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-export-uapi-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-export-uapi-boundary-survey_md, marker);
    const text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase3-export-uapi-survey/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py_path);
    const text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase3-export-uapi-survey_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase3-export-uapi-survey_py, marker);
    const text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-low-level-wrapper-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-low-level-wrapper-boundary-survey_md, marker);
    const text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase3-low-level-wrapper-survey/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py_path);
    const text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase3-low-level-wrapper-survey_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase3-low-level-wrapper-survey_py, marker);
    const text_required_markers__documentation_zigux_phase3-abi-header-family-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-abi-header-family-survey_md_path);
    const text_required_markers__documentation_zigux_phase3-abi-header-family-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-abi-header-family-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-abi-header-family-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-abi-header-family-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-abi-header-family-survey_md, marker);
    const text_required_markers__scripts_zigux_validate-phase3-abi-header-family-survey_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase3-abi-header-family-survey/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-abi-header-family-survey_py_path);
    const text_required_markers__scripts_zigux_validate-phase3-abi-header-family-survey_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase3-abi-header-family-survey_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-abi-header-family-survey_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase3-abi-header-family-survey_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase3-abi-header-family-survey_py, marker);
    const text_required_markers__documentation_zigux_phase3-linux-zigux-header-governance_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-linux-zigux-header-governance/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-linux-zigux-header-governance_md_path);
    const text_required_markers__documentation_zigux_phase3-linux-zigux-header-governance_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-linux-zigux-header-governance_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-linux-zigux-header-governance_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-linux-zigux-header-governance_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-linux-zigux-header-governance_md, marker);
    const text_required_markers__scripts_zigux_validate-phase3-linux-zigux-header-governance_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase3-linux-zigux-header-governance/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-linux-zigux-header-governance_py_path);
    const text_required_markers__scripts_zigux_validate-phase3-linux-zigux-header-governance_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase3-linux-zigux-header-governance_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase3-linux-zigux-header-governance_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase3-linux-zigux-header-governance_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase3-linux-zigux-header-governance_py, marker);
    const text_forbidden_catalog_markers_path = try guard.joinPath(allocator, root, "scripts/zigux/phase3_catalog.zig");
    defer allocator.free(text_forbidden_catalog_markers_path);
    const text_forbidden_catalog_markers = try guard.readUtf8File(io, allocator, text_forbidden_catalog_markers_path);
    defer allocator.free(text_forbidden_catalog_markers);
    for (FORBIDDEN_CATALOG_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_catalog_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
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
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
