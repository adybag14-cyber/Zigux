const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const dev_t = @import("dev_t_binding");
const version = @import("version_binding");

const invalid_argument: i32 = -22;

pub const Header = version.Header;
pub const BoundaryHeader = Header;
pub const ExportStatus = abi.ExportStatus;
pub const Facility = abi.Facility;
pub const Version = version.Version;
pub const DevTFields = dev_t.Fields;
pub const InteropPolicy = abi.InteropPolicy;
pub const PanicMode = abi.PanicMode;
pub const AllocatorMode = abi.AllocatorMode;
pub const UnsafeScope = abi.UnsafeScope;
pub const RbtreeRootView = abi.RbtreeRootView;
pub const abi_version: u16 = abi.ABI_VERSION;
pub const header_size: u32 = version.header_size;

pub fn canonicalHeader(flags: u16) BoundaryHeader {
    return version.canonicalHeader(flags);
}

pub fn compatibleHeader(size: u32, flags: u16) BoundaryHeader {
    return version.compatibleHeader(size, flags);
}

pub fn isCurrentAbiVersion(value: u16) bool {
    return version.hasCurrentAbiVersion(value);
}

pub fn isCanonicalSize(value: u32) bool {
    return version.isCanonicalSize(value);
}

pub fn isCompatibleSize(value: u32) bool {
    return version.isCompatibleSize(value);
}

pub fn headerIsCanonical(header: BoundaryHeader) bool {
    return version.isCanonical(header);
}

pub fn headerIsCompatible(header: BoundaryHeader) bool {
    return version.isCompatible(header);
}

pub fn extendsBoundary(header: BoundaryHeader) bool {
    return version.extendsBoundary(header);
}

pub fn requestedExtraBytes(header: BoundaryHeader) u32 {
    return version.requestedExtraBytes(header);
}

pub fn canonicalizeHeader(header: BoundaryHeader) BoundaryHeader {
    return version.canonicalizeHeader(header);
}

pub fn validateBoundaryHeader(header: BoundaryHeader) ExportStatus {
    return version.validateBoundaryHeader(header);
}

pub fn currentVersion() Version {
    return version.current();
}

pub fn hasCurrentAbiMajor(value: u32) bool {
    return version.hasCurrentAbiMajor(value);
}

pub fn hasCurrentAbiMinor(value: u32) bool {
    return version.hasCurrentAbiMinor(value);
}

pub fn hasCurrentHeaderFamilyRevision(value: u32) bool {
    return version.hasCurrentHeaderFamilyRevision(value);
}

pub fn versionMatchesCurrent(candidate: Version) bool {
    return version.matchesCurrent(candidate);
}

pub fn validateVersion(candidate: Version) ExportStatus {
    return version.validate(candidate);
}

pub fn makeDevTFields(major: u32, minor: u32) DevTFields {
    return dev_t.init(major, minor);
}

pub fn encodeDeviceNumber(fields: DevTFields) ?u32 {
    if (!deviceFieldsAreValid(fields)) return null;
    return dev_t.makeDeviceNumber(fields.major, fields.minor);
}

pub fn decodeDeviceNumber(device_number: u32) DevTFields {
    return dev_t.fieldsFromDeviceNumber(device_number);
}

pub fn okStatus(facility: Facility) ExportStatus {
    return abi.okStatus(facility);
}

pub fn errorStatus(code: i32, facility: Facility) ExportStatus {
    return abi.makeStatus(code, facility);
}

pub fn statusIsOk(status: ExportStatus) bool {
    return abi.statusIsOk(status);
}

pub fn deviceFieldsAreValid(fields: DevTFields) bool {
    return dev_t.validate(fields);
}

pub fn defaultInteropPolicy() InteropPolicy {
    return abi.defaultInteropPolicy();
}

pub fn panicModeFromInteropPolicy(policy: InteropPolicy) ?PanicMode {
    return abi.panicModeFromInteropPolicy(policy);
}

pub fn allocatorModeFromInteropPolicy(policy: InteropPolicy) ?AllocatorMode {
    return abi.allocatorModeFromInteropPolicy(policy);
}

pub fn unsafeScopeFromInteropPolicy(policy: InteropPolicy) ?UnsafeScope {
    return abi.unsafeScopeFromInteropPolicy(policy);
}

pub fn interopPolicyIsRecognized(policy: InteropPolicy) bool {
    return abi.interopPolicyIsRecognized(policy);
}

pub fn validateInteropPolicy(policy: InteropPolicy) ExportStatus {
    if (interopPolicyIsRecognized(policy)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

pub fn rbtreeRootViewIsCached(view: RbtreeRootView) bool {
    return abi.rbtreeRootViewIsCached(view);
}

pub fn rbtreeRootViewHasLeftmost(view: RbtreeRootView) bool {
    return abi.rbtreeRootViewHasLeftmost(view);
}

pub fn rbtreeRootViewIsValid(view: RbtreeRootView) bool {
    return abi.rbtreeRootViewIsValid(view);
}

pub fn canonicalizeRbtreeRootView(view: RbtreeRootView) RbtreeRootView {
    return abi.canonicalizeRbtreeRootView(view);
}

pub fn validateRbtreeRootView(view: RbtreeRootView) ExportStatus {
    if (rbtreeRootViewIsValid(view)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

pub fn deviceComponentsAreValid(major: u32, minor: u32) bool {
    return deviceFieldsAreValid(makeDevTFields(major, minor));
}

pub fn validateDeviceFields(fields: DevTFields) ExportStatus {
    if (deviceFieldsAreValid(fields)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

pub fn validateDeviceNumber(major: u32, minor: u32) ExportStatus {
    if (deviceComponentsAreValid(major, minor)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

pub fn deviceRangeIsValid(start: DevTFields, end: DevTFields) bool {
    return dev_t.validateRange(start, end);
}

pub fn validateDeviceRange(start: DevTFields, end: DevTFields) ExportStatus {
    if (deviceRangeIsValid(start, end)) return okStatus(.kernel);
    return errorStatus(invalid_argument, .kernel);
}

test "export shim relays interop-policy recognition through runtime status helpers" {
    const safe = defaultInteropPolicy();
    const mmio = InteropPolicy{
        .panic_mode = abi.PANIC_BUG,
        .allocator_mode = abi.ALLOC_KERNEL_HEAP,
        .unsafe_scope = abi.UNSAFE_VOLATILE_MMIO,
        .reserved = 0,
    };
    const reserved = InteropPolicy{
        .panic_mode = abi.PANIC_WARN,
        .allocator_mode = abi.ALLOC_ARENA,
        .unsafe_scope = abi.UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 1,
    };
    const unknown = InteropPolicy{
        .panic_mode = 9,
        .allocator_mode = 9,
        .unsafe_scope = 9,
        .reserved = 0,
    };

    try testing.expectEqual(abi.defaultInteropPolicy(), safe);
    try testing.expectEqual(abi.panicModeFromInteropPolicy(mmio), panicModeFromInteropPolicy(mmio));
    try testing.expectEqual(abi.allocatorModeFromInteropPolicy(mmio), allocatorModeFromInteropPolicy(mmio));
    try testing.expectEqual(abi.unsafeScopeFromInteropPolicy(mmio), unsafeScopeFromInteropPolicy(mmio));
    try testing.expect(interopPolicyIsRecognized(safe));
    try testing.expect(interopPolicyIsRecognized(mmio));
    try testing.expect(!interopPolicyIsRecognized(reserved));
    try testing.expect(!interopPolicyIsRecognized(unknown));

    const valid = validateInteropPolicy(mmio);
    const invalid_reserved = validateInteropPolicy(reserved);
    const invalid_unknown = validateInteropPolicy(unknown);

    try testing.expect(statusIsOk(valid));
    try testing.expect(!statusIsOk(invalid_reserved));
    try testing.expect(!statusIsOk(invalid_unknown));
    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_reserved.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_unknown.code);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_reserved.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_unknown.flags);
}

test "export shim relays rbtree cached-leftmost safety through runtime status helpers" {
    const uncached = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = 0,
    };
    const cached = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0x0800,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };
    const malformed = RbtreeRootView{
        .root = 0x1000,
        .cached_leftmost = 0,
        .flags = abi.RBTREE_ROOT_VIEW_FLAG_CACHED | abi.RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID,
    };

    try testing.expectEqual(abi.rbtreeRootViewIsCached(cached), rbtreeRootViewIsCached(cached));
    try testing.expectEqual(abi.rbtreeRootViewHasLeftmost(cached), rbtreeRootViewHasLeftmost(cached));
    try testing.expectEqual(abi.rbtreeRootViewIsValid(uncached), rbtreeRootViewIsValid(uncached));
    try testing.expectEqual(abi.rbtreeRootViewIsValid(cached), rbtreeRootViewIsValid(cached));
    try testing.expectEqual(abi.rbtreeRootViewIsValid(malformed), rbtreeRootViewIsValid(malformed));
    try testing.expect(rbtreeRootViewIsValid(uncached));
    try testing.expect(rbtreeRootViewIsValid(cached));
    try testing.expect(!rbtreeRootViewIsValid(malformed));

    const canonical = canonicalizeRbtreeRootView(malformed);
    try testing.expect(rbtreeRootViewIsValid(canonical));
    try testing.expectEqual(@as(u32, 0), canonical.flags);

    const valid = validateRbtreeRootView(cached);
    const invalid = validateRbtreeRootView(malformed);
    try testing.expect(statusIsOk(valid));
    try testing.expect(!statusIsOk(invalid));
    try testing.expectEqual(@as(i32, invalid_argument), invalid.code);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid.flags);
}

test "export shim preserves the canonical boundary header and version snapshot" {
    const header = canonicalHeader(0x41);
    const current = currentVersion();

    try testing.expectEqual(@as(u16, abi.ABI_VERSION), abi_version);
    try testing.expectEqual(version.header_size, header_size);
    try testing.expectEqual(@as(u32, @sizeOf(BoundaryHeader)), header_size);
    try testing.expectEqual(@as(u32, @sizeOf(version.Header)), header_size);
    try testing.expectEqual(header_size, header.size);
    try testing.expectEqual(@as(u16, abi.ABI_VERSION), header.abi_version);
    try testing.expectEqual(@as(u16, 0x41), header.flags);
    try testing.expectEqual(version.canonicalHeader(0x41), header);
    try testing.expectEqual(version.boundaryHeader(0x41), header);
    try testing.expectEqual(@as(usize, 8), @sizeOf(BoundaryHeader));
    try testing.expectEqual(@as(usize, 4), @alignOf(BoundaryHeader));

    try testing.expectEqual(@as(u32, 0), current.abi_major);
    try testing.expectEqual(@as(u32, 1), current.abi_minor);
    try testing.expectEqual(@as(u32, 1), current.header_family_revision);
    try testing.expect(version.eql(current, version.current()));
}

test "export shim keeps boundary header predicates aligned with UAPI helpers" {
    const canonical = canonicalHeader(0x15);
    const future = compatibleHeader(header_size + 8, 0x15);
    const stale = BoundaryHeader{
        .size = header_size,
        .abi_version = abi_version + 1,
        .flags = 0,
    };
    const canonicalized = canonicalizeHeader(future);

    try testing.expectEqual(version.compatibleHeader(header_size + 8, 0x15), future);
    try testing.expect(isCurrentAbiVersion(canonical.abi_version));
    try testing.expect(isCanonicalSize(canonical.size));
    try testing.expect(isCompatibleSize(canonical.size));
    try testing.expect(headerIsCanonical(canonical));
    try testing.expect(headerIsCompatible(canonical));
    try testing.expectEqual(version.isCanonical(canonical), headerIsCanonical(canonical));
    try testing.expectEqual(version.isCompatible(canonical), headerIsCompatible(canonical));
    try testing.expect(!extendsBoundary(canonical));
    try testing.expectEqual(@as(u32, 0), requestedExtraBytes(canonical));

    try testing.expect(isCompatibleSize(future.size));
    try testing.expect(!isCanonicalSize(future.size));
    try testing.expect(!headerIsCanonical(future));
    try testing.expect(headerIsCompatible(future));
    try testing.expectEqual(version.isCanonical(future), headerIsCanonical(future));
    try testing.expectEqual(version.isCompatible(future), headerIsCompatible(future));
    try testing.expect(extendsBoundary(future));
    try testing.expectEqual(@as(u32, 8), requestedExtraBytes(future));

    try testing.expect(!isCurrentAbiVersion(stale.abi_version));
    try testing.expect(!headerIsCanonical(stale));
    try testing.expect(!headerIsCompatible(stale));
    try testing.expect(!extendsBoundary(stale));
    try testing.expectEqual(@as(u32, 0), requestedExtraBytes(stale));

    try testing.expectEqual(@as(u32, header_size), canonicalized.size);
    try testing.expectEqual(@as(u16, abi_version), canonicalized.abi_version);
    try testing.expectEqual(future.flags, canonicalized.flags);
    try testing.expect(headerIsCanonical(canonicalized));
    try testing.expect(!extendsBoundary(canonicalized));
}

test "export shim relays boundary header compatibility through status helpers" {
    const canonical = canonicalHeader(0x23);
    const extended = compatibleHeader(header_size + 8, 0x23);
    const undersized = BoundaryHeader{
        .size = header_size - 1,
        .abi_version = abi_version,
        .flags = 0x23,
    };
    const stale = BoundaryHeader{
        .size = header_size,
        .abi_version = abi_version + 1,
        .flags = 0x23,
    };
    const ok = validateBoundaryHeader(canonical);
    const ok_extended = validateBoundaryHeader(extended);
    const invalid_size = validateBoundaryHeader(undersized);
    const invalid_version = validateBoundaryHeader(stale);

    try testing.expectEqual(version.validateBoundaryHeader(canonical), ok);
    try testing.expectEqual(version.validateBoundaryHeader(extended), ok_extended);
    try testing.expect(statusIsOk(ok));
    try testing.expect(statusIsOk(ok_extended));
    try testing.expect(!statusIsOk(invalid_size));
    try testing.expect(!statusIsOk(invalid_version));

    try testing.expectEqual(@as(i32, 0), ok.code);
    try testing.expectEqual(@as(i32, 0), ok_extended.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_size.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_version.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), ok.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), ok_extended.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_size.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_version.facility);
    try testing.expectEqual(@as(u16, 0), ok.flags);
    try testing.expectEqual(@as(u16, 0), ok_extended.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_size.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_version.flags);
}

test "export shim relays starter version component predicates and compatibility through status helpers" {
    const live = currentVersion();
    const stale_major = Version{
        .abi_major = version.abi_major + 1,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision,
    };
    const stale_minor = Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor + 1,
        .header_family_revision = version.header_family_revision,
    };
    const stale_revision = Version{
        .abi_major = version.abi_major,
        .abi_minor = version.abi_minor,
        .header_family_revision = version.header_family_revision + 1,
    };
    const valid = validateVersion(live);
    const invalid_major = validateVersion(stale_major);
    const invalid_minor = validateVersion(stale_minor);
    const invalid_revision = validateVersion(stale_revision);

    try testing.expect(hasCurrentAbiMajor(live.abi_major));
    try testing.expect(hasCurrentAbiMinor(live.abi_minor));
    try testing.expect(hasCurrentHeaderFamilyRevision(live.header_family_revision));
    try testing.expect(versionMatchesCurrent(live));
    try testing.expect(!hasCurrentAbiMajor(stale_major.abi_major));
    try testing.expect(!hasCurrentAbiMinor(stale_minor.abi_minor));
    try testing.expect(!hasCurrentHeaderFamilyRevision(stale_revision.header_family_revision));
    try testing.expect(!versionMatchesCurrent(stale_major));
    try testing.expect(!versionMatchesCurrent(stale_minor));
    try testing.expect(!versionMatchesCurrent(stale_revision));

    try testing.expectEqual(version.hasCurrentAbiMajor(live.abi_major), hasCurrentAbiMajor(live.abi_major));
    try testing.expectEqual(version.hasCurrentAbiMinor(live.abi_minor), hasCurrentAbiMinor(live.abi_minor));
    try testing.expectEqual(
        version.hasCurrentHeaderFamilyRevision(live.header_family_revision),
        hasCurrentHeaderFamilyRevision(live.header_family_revision),
    );
    try testing.expectEqual(version.validate(live), valid);
    try testing.expectEqual(version.validate(stale_major), invalid_major);
    try testing.expectEqual(version.validate(stale_minor), invalid_minor);
    try testing.expectEqual(version.validate(stale_revision), invalid_revision);

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, invalid_argument), invalid_major.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_minor.code);
    try testing.expectEqual(@as(i32, invalid_argument), invalid_revision.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_major.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_minor.facility);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid_revision.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_major.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_minor.flags);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid_revision.flags);
}

test "export shim status helpers keep facility and error flags explicit" {
    const ok = okStatus(.helpers);
    const err = errorStatus(-12, .kernel);
    const non_error = errorStatus(7, .drivers);

    try testing.expectEqual(@as(i32, 0), ok.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.helpers)), ok.facility);
    try testing.expectEqual(@as(u16, 0), ok.flags);

    try testing.expectEqual(@as(i32, -12), err.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), err.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), err.flags);

    try testing.expectEqual(@as(i32, 7), non_error.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.drivers)), non_error.facility);
    try testing.expectEqual(@as(u16, 0), non_error.flags);
}

test "export shim mirrors the exported status-ok flag contract" {
    const ok = okStatus(.helpers);
    const negative = errorStatus(-12, .kernel);
    const positive = errorStatus(7, .drivers);
    const flagged_positive = ExportStatus{
        .code = 7,
        .facility = @intFromEnum(Facility.drivers),
        .flags = abi.STATUS_FLAG_ERROR,
    };

    try testing.expect(statusIsOk(ok));
    try testing.expect(!statusIsOk(negative));
    try testing.expect(statusIsOk(positive));
    try testing.expect(!statusIsOk(flagged_positive));
}

test "export shim forwards starter dev_t fields without changing layout semantics" {
    const fields = makeDevTFields(11, 29);
    const same = makeDevTFields(11, 29);
    const different = makeDevTFields(11, 30);
    const invalid_major = makeDevTFields(dev_t.max_major + 1, 0);
    const invalid_minor = makeDevTFields(0, dev_t.max_minor + 1);

    try testing.expectEqual(@as(usize, 8), @sizeOf(DevTFields));
    try testing.expectEqual(@as(usize, 4), @alignOf(DevTFields));
    try testing.expectEqual(@as(u32, 11), fields.major);
    try testing.expectEqual(@as(u32, 29), fields.minor);
    try testing.expect(dev_t.eql(fields, same));
    try testing.expect(!dev_t.eql(fields, different));
    try testing.expect(deviceFieldsAreValid(fields));
    try testing.expect(deviceFieldsAreValid(same));
    try testing.expect(!deviceFieldsAreValid(invalid_major));
    try testing.expect(!deviceFieldsAreValid(invalid_minor));
    try testing.expect(deviceComponentsAreValid(11, 29));
    try testing.expect(!deviceComponentsAreValid(dev_t.max_major + 1, 0));
    try testing.expect(!deviceComponentsAreValid(0, dev_t.max_minor + 1));
}

test "export shim keeps validated dev_t encoding explicit" {
    const fields = makeDevTFields(11, 29);
    const encoded = encodeDeviceNumber(fields) orelse unreachable;
    const decoded = decodeDeviceNumber(encoded);
    const invalid = makeDevTFields(dev_t.max_major + 1, 0);

    try testing.expectEqual(dev_t.makeDeviceNumber(fields.major, fields.minor), encoded);
    try testing.expect(dev_t.eql(fields, decoded));
    try testing.expect(encodeDeviceNumber(invalid) == null);
}

test "export shim relays bounded dev_t validation through status helpers" {
    const valid = validateDeviceNumber(dev_t.max_major, dev_t.max_minor);
    const invalid = validateDeviceNumber(dev_t.max_major + 1, 0);
    const same = makeDevTFields(1, 2);
    const later = makeDevTFields(1, 3);
    const invalid_minor = makeDevTFields(0, dev_t.max_minor + 1);
    const good_range = validateDeviceRange(same, later);
    const bad_range = validateDeviceRange(later, same);

    try testing.expect(deviceRangeIsValid(same, later));
    try testing.expect(deviceRangeIsValid(same, same));
    try testing.expect(!deviceRangeIsValid(later, same));
    try testing.expect(!deviceRangeIsValid(same, invalid_minor));

    try testing.expectEqual(@as(i32, 0), valid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), valid.facility);
    try testing.expectEqual(@as(u16, 0), valid.flags);

    try testing.expectEqual(@as(i32, invalid_argument), invalid.code);
    try testing.expectEqual(@as(u16, @intFromEnum(Facility.kernel)), invalid.facility);
    try testing.expectEqual(@as(u16, abi.STATUS_FLAG_ERROR), invalid.flags);

    try testing.expectEqual(@as(i32, 0), good_range.code);
    try testing.expectEqual(@as(i32, invalid_argument), bad_range.code);
}
