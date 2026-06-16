const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_HEADER_FAMILY_SURVEY=pass";
pub const self_test_pass_marker = "PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-abi-header-family-survey_md = [_][]const u8{
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

const REQUIRED_MARKERS__scripts_zigux_validate-phase3-abi-header-family-survey_py = [_][]const u8{
    "\"\"\"Fail-close the current Phase 3 ABI header-family survey packet.\"\"\"",
    "SURVEY_PATH = Path(\"Documentation/zigux/phase3-abi-header-family-survey.md\")",
    "print(\"PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass\")",
    "print(\"PHASE3_ABI_HEADER_FAMILY_SURVEY=pass\")",
};

const REQUIRED_MARKERS__Documentation_zigux_phase3-abi-slice_md = [_][]const u8{
    "scripts\\zigux/validate_phase3_abi_header_family_survey.zig",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "the separate broader header-family binding follow-through remains the wider gap",
};

const REQUIRED_MARKERS__zigux_tests_fixtures_phase3_abi_manifest_json = [_][]const u8{
    "\"Documentation/zigux/phase3-abi-header-family-survey.md\"",
    "\"scripts\\zigux/validate_phase3_abi_header_family_survey.zig\"",
    "\"zigux/bindings/header_family.zig\"",
};

const REQUIRED_MARKERS__include_linux_zigux_h = [_][]const u8{
    "static inline struct zigux_uapi_version zigux_uapi_version_current(void) {",
    "static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) {",
    "static inline struct zigux_export_status zigux_uapi_validate_version(",
    "static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)",
    "static inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(",
    "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
};

const REQUIRED_MARKERS__include_zigux_abi_h = [_][]const u8{
    "typedef struct zigux_boundary_header {",
    "struct zigux_export_status {",
    "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
    "static inline int zigux_header_is_canonical(zigux_boundary_header header)",
    "static inline uint32_t zigux_header_requested_extra_bytes(",
};

const REQUIRED_MARKERS__include_zigux_dev_t_h = [_][]const u8{
    "struct zigux_dev_t_fields {",
    "static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(",
    "static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)",
    "static inline int zigux_dev_t_fields_range_is_valid(",
};

const REQUIRED_MARKERS__zigux_uapi_version_zig = [_][]const u8{
    "pub const abi_major: u32 = 0;",
    "pub const abi_minor: u32 = 1;",
    "pub const header_family_revision: u32 = 1;",
    "pub fn current() Version {",
    "pub fn matchesCurrent(version: Version) bool {",
};

const REQUIRED_MARKERS__zigux_uapi_dev_t_zig = [_][]const u8{
    "pub const abi_version: u32 = 1;",
    "pub fn init(major: u32, minor: u32) Fields {",
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validate(fields: Fields) bool {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const REQUIRED_MARKERS__zigux_bindings_version_zig = [_][]const u8{
    "pub const abi_major = uapi.abi_major;",
    "pub const header_family_revision = uapi.header_family_revision;",
    "pub fn current() Version {",
    "pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {",
    "pub fn matchesCurrent(version: Version) bool {",
};

const REQUIRED_MARKERS__zigux_bindings_dev_t_zig = [_][]const u8{
    "pub const abi_version = uapi.abi_version;",
    "pub fn init(major: u32, minor: u32) Fields {",
    "pub fn makeDeviceNumber(major: u32, minor: u32) u32 {",
    "pub fn validate(fields: Fields) bool {",
    "pub fn validateRange(start: Fields, end: Fields) bool {",
};

const REQUIRED_MARKERS__zigux_bindings_header_family_zig = [_][]const u8{
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

const REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_zig = [_][]const u8{
    "test \"export and uapi version layouts stay aligned\" {",
    "test \"export shim relays version compatibility without widening the boundary\" {",
    "test \"export shim reuses the canonical boundary header contract\" {",
    "test \"export shim mirrors boundary header predicate helpers\" {",
    "test \"export shim relays starter dev_t validation and range checks through the focused replay\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../uapi/dev_t.zig\"),",
    ".root_source_file = b.path(\"../uapi/version.zig\"),",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    "\"phase3-export-uapi-layout-test\"",
};

const SAMPLE_LINUX_HEADER = [_][]const u8{
    "#define ZIGUX_UAPI_ABI_MAJOR 0u\n#define ZIGUX_UAPI_ABI_MINOR 1u\n#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u\nstatic inline struct zigux_uapi_version zigux_uapi_version_current(void) {\n    return (struct zigux_uapi_version){0};\n}\nstatic inline int zigux_uapi_version_has_current_abi_major(uint32_t abi_major) {\n    return abi_major == ZIGUX_UAPI_ABI_MAJOR;\n}\nstatic inline int zigux_uapi_version_has_current_abi_minor(uint32_t abi_minor) {\n    return abi_minor == ZIGUX_UAPI_ABI_MINOR;\n}\nstatic inline int zigux_uapi_version_has_current_header_family_revision(uint32_t header_family_revision) {\n    return header_family_revision == ZIGUX_UAPI_HEADER_FAMILY_REVISION;\n}\nstatic inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) {\n    return version.abi_major == ZIGUX_UAPI_ABI_MAJOR;\n}\nstatic inline struct zigux_export_status zigux_uapi_validate_version(\n    struct zigux_uapi_version version)\n{\n    return (struct zigux_export_status){0};\n}\nstatic inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)\n{\n    return (zigux_boundary_header){ .size = 8u, .abi_version = 1u, .flags = flags };\n}\nstatic inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(\n    zigux_boundary_header header)\n{\n    return header.size;\n}\nstatic inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)\n{\n    return fields.major <= 1u;\n}\n",
};

const SAMPLE_DEV_T_HEADER = [_][]const u8{
    "#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u\n#define ZIGUX_DEV_T_FIELDS_SIZE 8u\n#define ZIGUX_DEV_T_FIELDS_ALIGN 4u\n#define ZIGUX_DEV_T_MAJOR_OFFSET 0u\n#define ZIGUX_DEV_T_MINOR_OFFSET 4u\n#define ZIGUX_DEV_MINOR_BITS 20u\nstruct zigux_dev_t_fields {\n    uint32_t major;\n    uint32_t minor;\n};\nstatic inline struct zigux_dev_t_fields zigux_dev_t_fields_make(\n    uint32_t major,\n    uint32_t minor\n) {\n    return (struct zigux_dev_t_fields){ .major = major, .minor = minor };\n}\nstatic inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)\n{\n    return major | minor;\n}\nstatic inline uint32_t zigux_major(uint32_t dev)\n{\n    return dev;\n}\nstatic inline uint32_t zigux_minor(uint32_t dev)\n{\n    return dev;\n}\nstatic inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)\n{\n    return fields.major >= fields.minor;\n}\nstatic inline int zigux_dev_t_fields_range_is_valid(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end\n)\n{\n    return start.major <= end.major;\n}\n",
};

const SAMPLE_UAPI_VERSION = [_][]const u8{
    "pub const abi_major: u32 = 0;\npub const abi_minor: u32 = 1;\npub const header_family_revision: u32 = 1;\npub fn current() Version {\n    return undefined;\n}\npub fn hasCurrentAbiMajor(value: u32) bool {\n    return value == abi_major;\n}\npub fn hasCurrentAbiMinor(value: u32) bool {\n    return value == abi_minor;\n}\npub fn hasCurrentHeaderFamilyRevision(value: u32) bool {\n    return value == header_family_revision;\n}\npub fn matchesCurrent(version: Version) bool {\n    return version.abi_major == abi_major;\n}\n",
};

const SAMPLE_UAPI_DEV_T = [_][]const u8{
    "pub const abi_version: u32 = 1;\npub const major_bits: u6 = 12;\npub const minor_bits: u6 = 20;\npub fn init(major: u32, minor: u32) Fields {\n    _ = major;\n    _ = minor;\n    return undefined;\n}\npub fn makeDeviceNumber(major: u32, minor: u32) u32 {\n    return major + minor;\n}\npub fn majorFromDeviceNumber(device_number: u32) u32 {\n    return device_number;\n}\npub fn minorFromDeviceNumber(device_number: u32) u32 {\n    return device_number;\n}\npub fn validate(fields: Fields) bool {\n    _ = fields;\n    return true;\n}\npub fn validateRange(start: Fields, end: Fields) bool {\n    _ = start;\n    _ = end;\n    return true;\n}\n",
};

const SAMPLE_VERSION_BINDING = [_][]const u8{
    "pub const abi_major = uapi.abi_major;\npub const abi_minor = uapi.abi_minor;\npub const header_family_revision = uapi.header_family_revision;\npub const version_size = uapi.version_size;\npub const version_align = uapi.version_align;\npub const abi_major_offset = uapi.abi_major_offset;\npub const abi_minor_offset = uapi.abi_minor_offset;\npub const header_family_revision_offset = uapi.header_family_revision_offset;\npub fn current() Version {\n    return uapi.current();\n}\npub fn hasCurrentAbiMajor(value: u32) bool {\n    return uapi.hasCurrentAbiMajor(value);\n}\npub fn hasCurrentAbiMinor(value: u32) bool {\n    return uapi.hasCurrentAbiMinor(value);\n}\npub fn hasCurrentHeaderFamilyRevision(value: u32) bool {\n    return uapi.hasCurrentHeaderFamilyRevision(value);\n}\npub fn matchesCurrent(version: Version) bool {\n    return uapi.matchesCurrent(version);\n}\n",
};

const SAMPLE_DEV_T_BINDING = [_][]const u8{
    "pub const abi_version = uapi.abi_version;\npub const major_bits = uapi.major_bits;\npub const minor_bits = uapi.minor_bits;\npub const max_major = uapi.max_major;\npub const max_minor = uapi.max_minor;\npub const fields_size = uapi.fields_size;\npub const fields_align = uapi.fields_align;\npub const major_offset = uapi.major_offset;\npub const minor_offset = uapi.minor_offset;\npub fn init(major: u32, minor: u32) Fields {\n    return uapi.init(major, minor);\n}\npub fn makeDeviceNumber(major: u32, minor: u32) u32 {\n    return uapi.makeDeviceNumber(major, minor);\n}\npub fn majorFromDeviceNumber(device_number: u32) u32 {\n    return uapi.majorFromDeviceNumber(device_number);\n}\npub fn minorFromDeviceNumber(device_number: u32) u32 {\n    return uapi.minorFromDeviceNumber(device_number);\n}\npub fn validate(fields: Fields) bool {\n    return uapi.validate(fields);\n}\npub fn validateRange(start: Fields, end: Fields) bool {\n    return uapi.validateRange(start, end);\n}\n",
};

const SAMPLE_HEADER_FAMILY_BINDING = [_][]const u8{
    "pub const abi_major: u32 = uapi_version.abi_major;\npub const abi_minor: u32 = uapi_version.abi_minor;\npub const header_family_revision: u32 = uapi_version.header_family_revision;\npub const abi_version: u16 = abi.ABI_VERSION;\npub const uapi_dev_t_packet_present: u32 = 1;\npub const version_size: usize = version_binding.version_size;\npub const version_align: usize = version_binding.version_align;\npub const abi_major_offset: usize = version_binding.abi_major_offset;\npub const abi_minor_offset: usize = version_binding.abi_minor_offset;\npub const header_family_revision_offset: usize = version_binding.header_family_revision_offset;\npub const fields_size: usize = dev_t_binding.fields_size;\npub const fields_align: usize = dev_t_binding.fields_align;\npub const major_offset: usize = dev_t_binding.major_offset;\npub const minor_offset: usize = dev_t_binding.minor_offset;\npub const max_major: u32 = dev_t_binding.max_major;\npub const max_minor: u32 = dev_t_binding.max_minor;\npub fn currentVersion() Version {\n    return version_binding.current();\n}\npub fn versionMatchesCurrent(version: Version) bool {\n    return version_binding.matchesCurrent(version);\n}\npub fn currentBoundaryHeader(flags: u16) BoundaryHeader {\n    return abi.defaultHeader(flags);\n}\npub fn boundaryHeaderRequestedExtraBytes(header: BoundaryHeader) u32 {\n    return header.size;\n}\npub fn initDevTFields(major: u32, minor: u32) DevTFields {\n    return dev_t_binding.init(major, minor);\n}\npub fn fieldsFromDeviceNumber(device_number: u32) DevTFields {\n    return dev_t_binding.fieldsFromDeviceNumber(device_number);\n}\npub fn validateVersionStatus(version: Version) ExportStatus {\n    _ = version;\n    return undefined;\n}\npub fn validateDevTFieldsStatus(fields: DevTFields) ExportStatus {\n    _ = fields;\n    return undefined;\n}\npub fn validateDevTRangeStatus(start: DevTFields, end: DevTFields) ExportStatus {\n    _ = start;\n    _ = end;\n    return undefined;\n}\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
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
    const text_required_markers__documentation_zigux_phase3-abi-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-abi-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-abi-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-abi-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-abi-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-abi-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-abi-slice_md, marker);
    const text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3/abi/manifest/json");
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path);
    const text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json_path);
    defer allocator.free(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json);
    for (REQUIRED_MARKERS__zigux_tests_fixtures_phase3_abi_manifest_json) |marker| try guard.requireMarker(text_required_markers__zigux_tests_fixtures_phase3_abi_manifest_json, marker);
    const text_required_markers__include_linux_zigux_h_path = try guard.joinPath(allocator, root, "include/linux/zigux/h");
    defer allocator.free(text_required_markers__include_linux_zigux_h_path);
    const text_required_markers__include_linux_zigux_h = try guard.readUtf8File(io, allocator, text_required_markers__include_linux_zigux_h_path);
    defer allocator.free(text_required_markers__include_linux_zigux_h);
    for (REQUIRED_MARKERS__include_linux_zigux_h) |marker| try guard.requireMarker(text_required_markers__include_linux_zigux_h, marker);
    const text_required_markers__include_zigux_abi_h_path = try guard.joinPath(allocator, root, "include/zigux/abi/h");
    defer allocator.free(text_required_markers__include_zigux_abi_h_path);
    const text_required_markers__include_zigux_abi_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_abi_h_path);
    defer allocator.free(text_required_markers__include_zigux_abi_h);
    for (REQUIRED_MARKERS__include_zigux_abi_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_abi_h, marker);
    const text_required_markers__include_zigux_dev_t_h_path = try guard.joinPath(allocator, root, "include/zigux/dev/t/h");
    defer allocator.free(text_required_markers__include_zigux_dev_t_h_path);
    const text_required_markers__include_zigux_dev_t_h = try guard.readUtf8File(io, allocator, text_required_markers__include_zigux_dev_t_h_path);
    defer allocator.free(text_required_markers__include_zigux_dev_t_h);
    for (REQUIRED_MARKERS__include_zigux_dev_t_h) |marker| try guard.requireMarker(text_required_markers__include_zigux_dev_t_h, marker);
    const text_required_markers__zigux_uapi_version_zig_path = try guard.joinPath(allocator, root, "zigux/uapi/version/zig");
    defer allocator.free(text_required_markers__zigux_uapi_version_zig_path);
    const text_required_markers__zigux_uapi_version_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_uapi_version_zig_path);
    defer allocator.free(text_required_markers__zigux_uapi_version_zig);
    for (REQUIRED_MARKERS__zigux_uapi_version_zig) |marker| try guard.requireMarker(text_required_markers__zigux_uapi_version_zig, marker);
    const text_required_markers__zigux_uapi_dev_t_zig_path = try guard.joinPath(allocator, root, "zigux/uapi/dev/t/zig");
    defer allocator.free(text_required_markers__zigux_uapi_dev_t_zig_path);
    const text_required_markers__zigux_uapi_dev_t_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_uapi_dev_t_zig_path);
    defer allocator.free(text_required_markers__zigux_uapi_dev_t_zig);
    for (REQUIRED_MARKERS__zigux_uapi_dev_t_zig) |marker| try guard.requireMarker(text_required_markers__zigux_uapi_dev_t_zig, marker);
    const text_required_markers__zigux_bindings_version_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/version/zig");
    defer allocator.free(text_required_markers__zigux_bindings_version_zig_path);
    const text_required_markers__zigux_bindings_version_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_version_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_version_zig);
    for (REQUIRED_MARKERS__zigux_bindings_version_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_version_zig, marker);
    const text_required_markers__zigux_bindings_dev_t_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/dev/t/zig");
    defer allocator.free(text_required_markers__zigux_bindings_dev_t_zig_path);
    const text_required_markers__zigux_bindings_dev_t_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_dev_t_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_dev_t_zig);
    for (REQUIRED_MARKERS__zigux_bindings_dev_t_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_dev_t_zig, marker);
    const text_required_markers__zigux_bindings_header_family_zig_path = try guard.joinPath(allocator, root, "zigux/bindings/header/family/zig");
    defer allocator.free(text_required_markers__zigux_bindings_header_family_zig_path);
    const text_required_markers__zigux_bindings_header_family_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_bindings_header_family_zig_path);
    defer allocator.free(text_required_markers__zigux_bindings_header_family_zig);
    for (REQUIRED_MARKERS__zigux_bindings_header_family_zig) |marker| try guard.requireMarker(text_required_markers__zigux_bindings_header_family_zig, marker);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/uapi/layout/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_zig_path);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_uapi_layout_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_uapi_layout_zig, marker);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/uapi/layout/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig_path);
    const text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_layout_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_uapi_layout_build_zig, marker);
    const text_sample_linux_header_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_linux_header_path);
    const text_sample_linux_header = try guard.readUtf8File(io, allocator, text_sample_linux_header_path);
    defer allocator.free(text_sample_linux_header);
    for (SAMPLE_LINUX_HEADER) |marker| try guard.requireMarker(text_sample_linux_header, marker);
    const text_sample_dev_t_header_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_dev_t_header_path);
    const text_sample_dev_t_header = try guard.readUtf8File(io, allocator, text_sample_dev_t_header_path);
    defer allocator.free(text_sample_dev_t_header);
    for (SAMPLE_DEV_T_HEADER) |marker| try guard.requireMarker(text_sample_dev_t_header, marker);
    const text_sample_uapi_version_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_uapi_version_path);
    const text_sample_uapi_version = try guard.readUtf8File(io, allocator, text_sample_uapi_version_path);
    defer allocator.free(text_sample_uapi_version);
    for (SAMPLE_UAPI_VERSION) |marker| try guard.requireMarker(text_sample_uapi_version, marker);
    const text_sample_uapi_dev_t_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_uapi_dev_t_path);
    const text_sample_uapi_dev_t = try guard.readUtf8File(io, allocator, text_sample_uapi_dev_t_path);
    defer allocator.free(text_sample_uapi_dev_t);
    for (SAMPLE_UAPI_DEV_T) |marker| try guard.requireMarker(text_sample_uapi_dev_t, marker);
    const text_sample_version_binding_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_version_binding_path);
    const text_sample_version_binding = try guard.readUtf8File(io, allocator, text_sample_version_binding_path);
    defer allocator.free(text_sample_version_binding);
    for (SAMPLE_VERSION_BINDING) |marker| try guard.requireMarker(text_sample_version_binding, marker);
    const text_sample_dev_t_binding_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_dev_t_binding_path);
    const text_sample_dev_t_binding = try guard.readUtf8File(io, allocator, text_sample_dev_t_binding_path);
    defer allocator.free(text_sample_dev_t_binding);
    for (SAMPLE_DEV_T_BINDING) |marker| try guard.requireMarker(text_sample_dev_t_binding, marker);
    const text_sample_header_family_binding_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-header-family-survey.md");
    defer allocator.free(text_sample_header_family_binding_path);
    const text_sample_header_family_binding = try guard.readUtf8File(io, allocator, text_sample_header_family_binding_path);
    defer allocator.free(text_sample_header_family_binding);
    for (SAMPLE_HEADER_FAMILY_BINDING) |marker| try guard.requireMarker(text_sample_header_family_binding, marker);
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
