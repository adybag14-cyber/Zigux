const std = @import("std");

pub const ModuleStage = enum(u8) {
    cold,
    initialized,
    selftest_complete,
    exited,
};

pub const ProbeFocus = enum {
    entry_timestamp,
    return_value,
    duration_ns,
    missed_instances,
};

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    requires_runtime_substrate: bool,
    provides_selftest_hook: bool,
};

pub const ProbeResult = struct {
    retval: usize,
    duration_ns: i64,
};

pub const SelftestSummary = struct {
    anchor: []const u8,
    symbol_name: []const u8,
    probe_focus: []const ProbeFocus,
    skipped_kernel_thread_path_checked: bool,
    duration_path_checked: bool,
    missed_instance_path_checked: bool,
    last_retval: usize,
    last_duration_ns: i64,
    nmissed: usize,
    maxactive: usize,
};

pub const RuntimeKretprobeSample = struct {
    const Self = @This();

    pub const default_symbol_name = "kernel_clone";
    pub const default_maxactive: usize = 20;

    stage_state: ModuleStage = .cold,
    symbol_name: []const u8 = default_symbol_name,
    maxactive: usize = default_maxactive,
    active_instances: usize = 0,
    skipped_kernel_threads: usize = 0,
    nmissed: usize = 0,
    entry_stamp_ns: i64 = -1,
    last_retval: usize = 0,
    last_duration_ns: i64 = 0,
    init_runs: usize = 0,
    selftest_runs: usize = 0,
    exit_runs: usize = 0,

    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "runtime_kretprobe",
            .anchor = "samples/kprobes/kretprobe_example.c",
            .requires_runtime_substrate = true,
            .provides_selftest_hook = true,
        };
    }

    pub fn stage(self: *const Self) ModuleStage {
        return self.stage_state;
    }

    fn ensureMutable(self: *const Self) !void {
        return switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => error.InvalidLifecycleTransition,
        };
    }

    pub fn retargetSymbol(self: *Self, symbol_name: []const u8) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (symbol_name.len == 0) return error.InvalidSymbolName;

        self.symbol_name = symbol_name;
    }

    pub fn init(self: *Self) !void {
        if (self.stage() != .cold) return error.InvalidLifecycleTransition;
        if (self.symbol_name.len == 0) return error.InvalidSymbolName;

        self.active_instances = 0;
        self.skipped_kernel_threads = 0;
        self.nmissed = 0;
        self.entry_stamp_ns = -1;
        self.last_retval = 0;
        self.last_duration_ns = 0;
        self.init_runs += 1;
        self.stage_state = .initialized;
    }

    pub fn entryHandler(self: *Self, has_mm: bool, stamp_ns: i64) !bool {
        try self.ensureMutable();

        if (!has_mm) {
            self.skipped_kernel_threads += 1;
            return false;
        }
        if (self.active_instances >= self.maxactive) {
            self.nmissed += 1;
            return error.MaxactiveExceeded;
        }

        self.active_instances += 1;
        self.entry_stamp_ns = stamp_ns;
        return true;
    }

    pub fn retHandler(self: *Self, retval: usize, now_ns: i64) !ProbeResult {
        try self.ensureMutable();
        if (self.active_instances == 0 or self.entry_stamp_ns < 0) return error.MissingEntryTimestamp;
        if (now_ns < self.entry_stamp_ns) return error.InvalidTimestampOrder;

        const duration_ns = now_ns - self.entry_stamp_ns;
        self.active_instances -= 1;
        if (self.active_instances == 0) {
            self.entry_stamp_ns = -1;
        }
        self.last_retval = retval;
        self.last_duration_ns = duration_ns;
        return .{
            .retval = retval,
            .duration_ns = duration_ns,
        };
    }

    pub fn recordMissedInstance(self: *Self) !void {
        try self.ensureMutable();
        self.nmissed += 1;
    }

    pub fn runSelftest(self: *Self) !SelftestSummary {
        if (self.stage() != .initialized) return error.InvalidLifecycleTransition;

        const skipped = try self.entryHandler(false, 10);
        if (skipped) return error.UnexpectedEntryArming;

        const armed = try self.entryHandler(true, 100);
        if (!armed) return error.UnexpectedEntrySkip;

        const result = try self.retHandler(42, 175);
        try self.recordMissedInstance();

        self.selftest_runs += 1;
        self.stage_state = .selftest_complete;
        return .{
            .anchor = descriptor().anchor,
            .symbol_name = self.symbol_name,
            .probe_focus = &.{
                .entry_timestamp,
                .return_value,
                .duration_ns,
                .missed_instances,
            },
            .skipped_kernel_thread_path_checked = self.skipped_kernel_threads > 0,
            .duration_path_checked = result.duration_ns > 0,
            .missed_instance_path_checked = self.nmissed > 0,
            .last_retval = self.last_retval,
            .last_duration_ns = self.last_duration_ns,
            .nmissed = self.nmissed,
            .maxactive = self.maxactive,
        };
    }

    pub fn exit(self: *Self) !void {
        switch (self.stage()) {
            .initialized, .selftest_complete => {},
            else => return error.InvalidLifecycleTransition,
        }
        if (self.active_instances != 0) return error.OutstandingProbeInstance;

        self.exit_runs += 1;
        self.stage_state = .exited;
    }
};