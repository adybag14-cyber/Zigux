const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_HEADER_FAMILY_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass";

const self_test_output_markers = [_][]const u8{
    "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass",
    "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST_CASE_COUNT=",
};

const live_output_markers = [_][]const u8{
    "validated Documentation/zigux/phase3-abi-header-family-survey.md",
    "PHASE3_ABI_HEADER_FAMILY_SURVEY=pass",
};

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "PHASE3_ABI_HEADER_FAMILY_VALIDATOR_PATH=scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "PHASE3_ABI_SHARED_SLICE_NOTE=Documentation/zigux/phase3-abi-slice.md",
    "PHASE3_ABI_SHARED_MANIFEST_PATH=zigux/tests/fixtures/phase3_abi_manifest.json",
    "PHASE3_LINUX_ZIGUX_H_PATH=include/linux/zigux.h",
    "PHASE3_ABI_HEADER_PATH=include/zigux/abi.h",
    "PHASE3_DEV_T_HEADER_PATH=include/zigux/dev_t.h",
    "PHASE3_UAPI_VERSION_PATH=zigux/uapi/version.zig",
    "PHASE3_UAPI_DEV_T_PATH=zigux/uapi/dev_t.zig",
    "PHASE3_VERSION_BINDING_PATH=zigux/bindings/version.zig",
    "PHASE3_DEV_T_BINDING_PATH=zigux/bindings/dev_t.zig",
    "PHASE3_HEADER_FAMILY_BINDING_PATH=zigux/bindings/header_family.zig",
    "PHASE3_EXPORT_UAPI_LAYOUT_GATE=zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "- `include/linux/zigux.h` keeps the Linux-facing header-family relay bounded to `zigux_uapi_version_current()`, the `zigux_uapi_version_has_current_*()` helpers, `zigux_uapi_version_matches_current()`, and `zigux_uapi_validate_version()` rather than introducing a second semantic owner.",
    "- `include/zigux/abi.h` remains the canonical owner for `zigux_boundary_header`, `zigux_export_status`, `zigux_default_header()`, `zigux_compatible_header()`, `zigux_abi_version_is_current()`, `zigux_header_is_canonical()`, `zigux_header_is_compatible()`, `zigux_header_extends_boundary()`, `zigux_header_requested_extra_bytes()`, and `zigux_header_canonicalize()`.",
    "- `include/zigux/dev_t.h` remains the canonical owner for the starter `dev_t` limits, `zigux_dev_t_fields_make()`, `zigux_mkdev()`, `zigux_major()`, `zigux_minor()`, `zigux_dev_t_fields_is_valid()`, and `zigux_dev_t_fields_range_is_valid()`.",
    "- `zigux/uapi/version.zig` and `zigux/bindings/version.zig` keep the current version packet aligned through `current()`, `matchesCurrent()`, the `hasCurrent*` helper family, and the shared size, alignment, and field-offset constants.",
    "- `zigux/uapi/dev_t.zig` and `zigux/bindings/dev_t.zig` keep the starter `dev_t` packet aligned through `init()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validate()`, and `validateRange()`.",
    "- `zigux/bindings/header_family.zig` now keeps the shared header-family binding relay explicit through `currentVersion()`, `versionMatchesCurrent()`, `currentBoundaryHeader()`, `compatibleBoundaryHeader()`, `boundaryHeaderHasCurrentAbiVersion()`, `boundaryHeaderIsCanonicalSize()`, `boundaryHeaderIsCompatibleSize()`, `boundaryHeaderRequestedExtraBytes()`, `canonicalizeBoundaryHeader()`, `validateBoundaryHeaderStatus()`, `initDevTFields()`, `makeDeviceNumber()`, `majorFromDeviceNumber()`, `minorFromDeviceNumber()`, `fieldsFromDeviceNumber()`, `validateVersionStatus()`, `validateDevTFieldsStatus()`, `validateDevTComponentsStatus()`, and `validateDevTRangeStatus()` without creating a third semantic owner beside the canonical headers and starter bindings.",
    "Current `master` no longer has a packet-local repo-reality gap for the bounded header-family survey follow-through itself.",
};

const markers_1 = [_][]const u8{
    "Fail-close the current Phase 3 ABI header-family survey packet.",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass",
    "PHASE3_ABI_HEADER_FAMILY_SURVEY=pass",
};

const markers_2 = [_][]const u8{
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "the separate broader header-family binding follow-through remains the wider gap",
};

const markers_3 = [_][]const u8{
    "\"Documentation/zigux/phase3-abi-header-family-survey.md\"",
    "\"scripts/zigux/validate_phase3_abi_header_family_survey.zig\"",
    "\"zigux/bindings/header_family.zig\"",
};

const markers_4 = [_][]const u8{
    "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
    "static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) {",
    "static inline struct zigux_export_status zigux_uapi_validate_version(",
    "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
    "static inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(",
    "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
};

const markers_5 = [_][]const u8{
    "typedef struct zigux_boundary_header {",
    "struct zigux_export_status {",
    "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
    "static inline int zigux_header_is_canonical(zigux_boundary_header header)",
    "static inline uint32_t zigux_header_requested_extra_bytes(",
};

const markers_6 = [_][]const u8{
    "struct zigux_dev_t_fields {",
    "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
    "static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)",
    "static inline int zigux_dev_t_fields_range_is_valid(",
};

const markers_7 = [_][]const u8{
    "pub const abi_major: u32 = 0;",
    "pub const abi_minor: u32 = 1;",
    "pub const header_family_revision: u32 = 1;",
    "pub fn current() Version {",
    "pub fn matchesCurrent(version: Version) bool {",
};

const markers_8 = [_][]const u8{
    "pub const abi_version: u32 = 1;",
    "pub fn init(major: u32, minor: u32) Fields {",
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validate(fields: Fields) bool {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const markers_9 = [_][]const u8{
    "pub const abi_major = uapi.abi_major;",
    "pub const header_family_revision = uapi.header_family_revision;",
    "pub fn current() Version {",
    "pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {",
    "pub fn matchesCurrent(version: Version) bool {",
};

const markers_10 = [_][]const u8{
    "pub const abi_version = uapi.abi_version;",
    "pub fn init(major: u32, minor: u32) Fields {",
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validate(fields: Fields) bool {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const markers_11 = [_][]const u8{
    "pub const abi_major: u32 = uapi_version.abi_major;",
    "pub const abi_minor: u32 = uapi_version.abi_minor;",
    "pub const header_family_revision: u32 = uapi_version.header_family_revision;",
    "pub const abi_version: u16 = abi.ABI_VERSION;",
    "pub const uapi_dev_t_packet_present: u32 = 1;",
    "pub fn currentVersion() Version {",
    "pub fn versionMatchesCurrent(version: Version) bool {",
    "pub fn currentBoundaryHeader(flags: u16) BoundaryHeader {",
    "pub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {",
    "pub fn initDevTFields(major: u32, minor: u32) DevTFields {",
    "pub fn fieldsFromDeviceNumber(device_number: u32) DevTFields {",
    "pub fn validateVersionStatus(version: Version) ExportStatus {",
    "pub fn validateDevTFieldsStatus(fields: DevTFields) ExportStatus {",
    "pub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {",
};

const markers_12 = [_][]const u8{
    "test \"export and uapi version layouts stay aligned\" {",
    "test \"export shim relays version compatibility without widening the boundary\" {",
    "test \"export shim reuses the canonical boundary header contract\" {",
    "test \"export shim mirrors boundary header predicate helpers\" {",
    "test \"export shim relays starter dev_t validation and range checks through the focused replay\" {",
};

const markers_13 = [_][]const u8{
    ".root_source_file = b.path(\"../uapi/dev_t.zig\"),",
    ".root_source_file = b.path(\"../uapi/version.zig\"),",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    "\"phase3-export-uapi-layout-test\"",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-abi-header-family-survey.md", .markers = &markers_0 },
    .{ .rel = "scripts/zigux/validate_phase3_abi_header_family_survey.zig", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase3-abi-slice.md", .markers = &markers_2 },
    .{ .rel = "zigux/tests/fixtures/phase3_abi_manifest.json", .markers = &markers_3 },
    .{ .rel = "include/linux/zigux.h", .markers = &markers_4 },
    .{ .rel = "include/zigux/abi.h", .markers = &markers_5 },
    .{ .rel = "include/zigux/dev_t.h", .markers = &markers_6 },
    .{ .rel = "zigux/uapi/version.zig", .markers = &markers_7 },
    .{ .rel = "zigux/uapi/dev_t.zig", .markers = &markers_8 },
    .{ .rel = "zigux/bindings/version.zig", .markers = &markers_9 },
    .{ .rel = "zigux/bindings/dev_t.zig", .markers = &markers_10 },
    .{ .rel = "zigux/bindings/header_family.zig", .markers = &markers_11 },
    .{ .rel = "zigux/tests/phase3_export_uapi_layout.zig", .markers = &markers_12 },
    .{ .rel = "zigux/tests/phase3_export_uapi_layout_build.zig", .markers = &markers_13 },
};

fn printOutputMarkers(io: Io, markers: []const []const u8) !void {
    for (markers) |marker| {
        if (std.mem.endsWith(u8, marker, "=")) {
            try guard.printLine(io, "{s}{d}", .{ marker, contracts.len });
        } else {
            try guard.printLine(io, "{s}", .{marker});
        }
    }
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
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
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig") or std.mem.eql(u8, arg, "--cc")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) std.process.exit(try runSelfTest(io, allocator));

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try printOutputMarkers(io, &live_output_markers);
}
