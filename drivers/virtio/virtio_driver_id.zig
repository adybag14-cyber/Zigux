const virtio_core = @import("virtio_core");

pub const MatchRule = virtio_core.DriverIdMatchRule;
pub const MatchSummary = virtio_core.DriverIdMatchSummary;

pub const MatchDisposition = enum {
    unmatched,
    exact,
    device_any,
    vendor_any,
    any_any,
};

pub fn summarize(core: *const virtio_core.VirtioCoreLab, rules: []const MatchRule) MatchSummary {
    return core.driverIdMatchSummary(rules);
}

pub fn disposition(summary: MatchSummary) MatchDisposition {
    if (!summary.matched) return .unmatched;
    if (summary.matched_device_any and summary.matched_vendor_any) return .any_any;
    if (summary.matched_device_any) return .device_any;
    if (summary.matched_vendor_any) return .vendor_any;
    return .exact;
}

pub fn matchedRuleUsesWildcard(summary: MatchSummary) bool {
    return summary.matched_device_any or summary.matched_vendor_any;
}
