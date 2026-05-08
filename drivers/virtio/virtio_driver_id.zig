const std = @import("std");

pub const any_id: u32 = 0xffff_ffff;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_lab_validation: bool,
    touches_transport_mmio: bool,
};

pub const RegistrationIdentitySummary = struct {
    anchor: []const u8,
    device_index: u32,
    device_id: u32,
    vendor_id: u32,
    device_name: []const u8,
    modalias: []const u8,
};

pub const DriverIdMatchRule = struct {
    device_id: u32,
    vendor_id: u32,
};

pub const DriverIdMatchSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    candidate_count: usize,
    matched: bool,
    matched_rule_index: ?usize,
    matched_device_any: bool,
    matched_vendor_any: bool,
};

pub const DriverIdMatchSpecificity = enum {
    unmatched,
    exact,
    device_wildcard,
    vendor_wildcard,
    full_wildcard,
};

pub const DriverIdTableReviewSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    candidate_count: usize,
    matched: bool,
    matched_rule_index: ?usize,
    matched_specificity: DriverIdMatchSpecificity,
    matched_device_any: bool,
    matched_vendor_any: bool,
    shadowed_more_specific_rule_index: ?usize,
};

pub const DriverIdCoverageDisposition = enum {
    unmatched,
    exact_coverage,
    wildcard_coverage,
    wildcard_shadowing_more_specific_rule,
};

pub const DriverIdCoverageSummary = struct {
    anchor: []const u8,
    device_id: u32,
    vendor_id: u32,
    candidate_count: usize,
    matched_rule_index: ?usize,
    matched_specificity: DriverIdMatchSpecificity,
    shadowed_more_specific_rule_index: ?usize,
    disposition: DriverIdCoverageDisposition,
};

pub const VirtioDriverIdMatcher = struct {
    const Self = @This();

    device_index: u32,
    device_id: u32,
    vendor_id: u32,
    device_name_buffer: [32]u8,
    device_name_len: usize,
    modalias_buffer: [32]u8,
    modalias_len: usize,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "virtio_driver_id_matcher_lab",
            .anchor = "drivers/virtio/virtio.c",
            .provides_lab_validation = true,
            .touches_transport_mmio = false,
        };
    }

    pub fn init(device_index: u32, device_id: u32, vendor_id: u32) !Self {
        var self = Self{
            .device_index = device_index,
            .device_id = device_id,
            .vendor_id = vendor_id,
            .device_name_buffer = [_]u8{0} ** 32,
            .device_name_len = 0,
            .modalias_buffer = [_]u8{0} ** 32,
            .modalias_len = 0,
        };

        self.device_name_len = try formatInto(
            self.device_name_buffer[0..],
            "virtio{}",
            .{device_index},
        );
        self.modalias_len = try formatInto(
            self.modalias_buffer[0..],
            "virtio:d{x:0>8}v{x:0>8}",
            .{ device_id, vendor_id },
        );
        return self;
    }

    pub fn registrationSummary(self: *const Self) RegistrationIdentitySummary {
        return .{
            .anchor = descriptor().anchor,
            .device_index = self.device_index,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .device_name = self.device_name_buffer[0..self.device_name_len],
            .modalias = self.modalias_buffer[0..self.modalias_len],
        };
    }

    pub fn driverIdMatchSummary(
        self: *const Self,
        rules: []const DriverIdMatchRule,
    ) DriverIdMatchSummary {
        for (rules, 0..) |rule, index| {
            if (!self.ruleMatches(rule)) continue;

            return .{
                .anchor = descriptor().anchor,
                .device_id = self.device_id,
                .vendor_id = self.vendor_id,
                .candidate_count = rules.len,
                .matched = true,
                .matched_rule_index = index,
                .matched_device_any = rule.device_id == any_id,
                .matched_vendor_any = rule.vendor_id == any_id,
            };
        }

        return .{
            .anchor = descriptor().anchor,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .candidate_count = rules.len,
            .matched = false,
            .matched_rule_index = null,
            .matched_device_any = false,
            .matched_vendor_any = false,
        };
    }

    pub fn driverIdTableReviewSummary(
        self: *const Self,
        rules: []const DriverIdMatchRule,
    ) DriverIdTableReviewSummary {
        const match = self.driverIdMatchSummary(rules);
        var shadowed_more_specific_rule_index: ?usize = null;

        if (match.matched) {
            if (match.matched_rule_index) |matched_rule_index| {
                const selected_rank = specificityRank(
                    match.matched_device_any,
                    match.matched_vendor_any,
                );
                for (rules[matched_rule_index + 1 ..], matched_rule_index + 1..) |rule, index| {
                    if (!self.ruleMatches(rule)) continue;

                    const candidate_rank = specificityRank(
                        rule.device_id == any_id,
                        rule.vendor_id == any_id,
                    );
                    if (candidate_rank < selected_rank) {
                        shadowed_more_specific_rule_index = index;
                        break;
                    }
                }
            }
        }

        return .{
            .anchor = descriptor().anchor,
            .device_id = self.device_id,
            .vendor_id = self.vendor_id,
            .candidate_count = rules.len,
            .matched = match.matched,
            .matched_rule_index = match.matched_rule_index,
            .matched_specificity = matchSpecificity(
                match.matched,
                match.matched_device_any,
                match.matched_vendor_any,
            ),
            .matched_device_any = match.matched_device_any,
            .matched_vendor_any = match.matched_vendor_any,
            .shadowed_more_specific_rule_index = shadowed_more_specific_rule_index,
        };
    }

    pub fn driverIdCoverageSummary(
        self: *const Self,
        rules: []const DriverIdMatchRule,
    ) DriverIdCoverageSummary {
        const review = self.driverIdTableReviewSummary(rules);
        const disposition: DriverIdCoverageDisposition = if (!review.matched)
            .unmatched
        else if (review.shadowed_more_specific_rule_index != null)
            .wildcard_shadowing_more_specific_rule
        else switch (review.matched_specificity) {
            .exact => .exact_coverage,
            .device_wildcard, .vendor_wildcard, .full_wildcard => .wildcard_coverage,
            .unmatched => .unmatched,
        };

        return .{
            .anchor = review.anchor,
            .device_id = review.device_id,
            .vendor_id = review.vendor_id,
            .candidate_count = review.candidate_count,
            .matched_rule_index = review.matched_rule_index,
            .matched_specificity = review.matched_specificity,
            .shadowed_more_specific_rule_index = review.shadowed_more_specific_rule_index,
            .disposition = disposition,
        };
    }

    fn formatInto(buffer: []u8, comptime fmt: []const u8, args: anytype) !usize {
        const rendered = try std.fmt.bufPrint(buffer, fmt, args);
        return rendered.len;
    }

    fn ruleMatches(self: *const Self, rule: DriverIdMatchRule) bool {
        const device_matches = rule.device_id == self.device_id or rule.device_id == any_id;
        if (!device_matches) return false;

        return rule.vendor_id == self.vendor_id or rule.vendor_id == any_id;
    }

    fn matchSpecificity(
        matched: bool,
        matched_device_any: bool,
        matched_vendor_any: bool,
    ) DriverIdMatchSpecificity {
        if (!matched) return .unmatched;
        if (matched_device_any and matched_vendor_any) return .full_wildcard;
        if (matched_device_any) return .device_wildcard;
        if (matched_vendor_any) return .vendor_wildcard;
        return .exact;
    }

    fn specificityRank(matched_device_any: bool, matched_vendor_any: bool) u2 {
        if (matched_device_any and matched_vendor_any) return 2;
        if (matched_device_any or matched_vendor_any) return 1;
        return 0;
    }
};

test "virtio driver id coverage summary reports exact coverage" {
    const matcher = try VirtioDriverIdMatcher.init(2, 0x1040, 0x1af4);
    const summary = matcher.driverIdCoverageSummary(&.{
        .{ .device_id = 0x1040, .vendor_id = 0x1af4 },
        .{ .device_id = any_id, .vendor_id = any_id },
    });

    try std.testing.expectEqualStrings("drivers/virtio/virtio.c", summary.anchor);
    try std.testing.expectEqual(DriverIdCoverageDisposition.exact_coverage, summary.disposition);
    try std.testing.expectEqual(DriverIdMatchSpecificity.exact, summary.matched_specificity);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expectEqual(@as(?usize, null), summary.shadowed_more_specific_rule_index);
}

test "virtio driver id coverage summary reports wildcard coverage" {
    const matcher = try VirtioDriverIdMatcher.init(3, 0x1050, 0x1af4);
    const summary = matcher.driverIdCoverageSummary(&.{
        .{ .device_id = any_id, .vendor_id = 0x1af4 },
        .{ .device_id = 0x1040, .vendor_id = 0x1af4 },
    });

    try std.testing.expectEqual(DriverIdCoverageDisposition.wildcard_coverage, summary.disposition);
    try std.testing.expectEqual(DriverIdMatchSpecificity.device_wildcard, summary.matched_specificity);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expectEqual(@as(?usize, null), summary.shadowed_more_specific_rule_index);
}

test "virtio driver id coverage summary reports wildcard shadowing a later more specific rule" {
    const matcher = try VirtioDriverIdMatcher.init(4, 0x1050, 0x1af4);
    const summary = matcher.driverIdCoverageSummary(&.{
        .{ .device_id = any_id, .vendor_id = 0x1af4 },
        .{ .device_id = 0x1050, .vendor_id = 0x1af4 },
    });

    try std.testing.expectEqual(
        DriverIdCoverageDisposition.wildcard_shadowing_more_specific_rule,
        summary.disposition,
    );
    try std.testing.expectEqual(DriverIdMatchSpecificity.device_wildcard, summary.matched_specificity);
    try std.testing.expectEqual(@as(?usize, 0), summary.matched_rule_index);
    try std.testing.expectEqual(@as(?usize, 1), summary.shadowed_more_specific_rule_index);
}

test "virtio driver id coverage summary reports unmatched coverage" {
    const matcher = try VirtioDriverIdMatcher.init(5, 0x1051, 0x1af4);
    const summary = matcher.driverIdCoverageSummary(&.{
        .{ .device_id = 0x1040, .vendor_id = 0x1af4 },
        .{ .device_id = any_id, .vendor_id = 0x10ec },
    });

    try std.testing.expectEqual(DriverIdCoverageDisposition.unmatched, summary.disposition);
    try std.testing.expectEqual(DriverIdMatchSpecificity.unmatched, summary.matched_specificity);
    try std.testing.expectEqual(@as(?usize, null), summary.matched_rule_index);
    try std.testing.expectEqual(@as(?usize, null), summary.shadowed_more_specific_rule_index);
}
