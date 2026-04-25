const std = @import("std");

pub const max_nr_hvc_consoles: usize = 16;
pub const n_outbuf: usize = 16;
pub const invalid_vtermno: u32 = std.math.maxInt(u32);
pub const eagain: isize = -11;

pub const ModuleDescriptor = struct {
    name: []const u8,
    anchor: []const u8,
    provides_simple_driver_starter: bool,
    touches_tty_registration: bool,
    touches_polling_kthread: bool,
    touches_live_hypervisor_io: bool,
};

pub const ConsoleSlot = struct {
    adapter_present: bool = false,
    vtermno: u32 = invalid_vtermno,
};

pub const SlotSnapshot = struct {
    anchor: []const u8,
    index: usize,
    adapter_present: bool,
    vtermno: u32,
};

pub const WriteTrace = struct {
    anchor: []const u8,
    index: usize,
    vtermno: u32,
    adapter_present: bool,
    framed_output: []u8,
    chunk_count: usize,
    written_bytes: usize,
    dropped_bytes: usize,
    flush_calls: usize,
    retry_flushes: usize,

    pub fn deinit(self: *WriteTrace, allocator: std.mem.Allocator) void {
        allocator.free(self.framed_output);
        self.* = undefined;
    }
};

pub const HvcConsoleLab = struct {
    pub fn descriptor() ModuleDescriptor {
        return .{
            .name = "hvc_console_lab",
            .anchor = "drivers/tty/hvc/hvc_console.c",
            .provides_simple_driver_starter = true,
            .touches_tty_registration = false,
            .touches_polling_kthread = false,
            .touches_live_hypervisor_io = false,
        };
    }

    pub fn validateConsoleSlot(index: isize, slots: []const ConsoleSlot) !SlotSnapshot {
        if (index < 0) return error.ConsoleIndexOutOfRange;

        const console_index: usize = @intCast(index);
        if (console_index >= max_nr_hvc_consoles or console_index >= slots.len) {
            return error.ConsoleIndexOutOfRange;
        }

        const slot = slots[console_index];
        if (!slot.adapter_present or slot.vtermno == invalid_vtermno) {
            return error.ConsoleAdapterUnavailable;
        }

        return .{
            .anchor = descriptor().anchor,
            .index = console_index,
            .adapter_present = slot.adapter_present,
            .vtermno = slot.vtermno,
        };
    }

    pub fn formatConsoleBytes(
        allocator: std.mem.Allocator,
        message: []const u8,
    ) ![]u8 {
        var framed = try std.ArrayList(u8).initCapacity(allocator, message.len + 4);
        defer framed.deinit(allocator);

        var donecr = false;
        for (message) |byte| {
            if (byte == '\n' and !donecr) {
                try framed.append(allocator, '\r');
                donecr = true;
            } else {
                donecr = false;
            }

            try framed.append(allocator, byte);
            if (byte == '\r') {
                donecr = true;
            }
        }

        return framed.toOwnedSlice(allocator);
    }

    pub fn writeConsoleMessage(
        allocator: std.mem.Allocator,
        index: isize,
        slots: []const ConsoleSlot,
        message: []const u8,
        write_results: []const isize,
    ) !WriteTrace {
        const slot = try validateConsoleSlot(index, slots);
        const framed_output = try formatConsoleBytes(allocator, message);
        errdefer allocator.free(framed_output);

        var trace = WriteTrace{
            .anchor = descriptor().anchor,
            .index = slot.index,
            .vtermno = slot.vtermno,
            .adapter_present = true,
            .framed_output = framed_output,
            .chunk_count = 0,
            .written_bytes = 0,
            .dropped_bytes = 0,
            .flush_calls = 0,
            .retry_flushes = 0,
        };

        var remaining = framed_output.len;
        var attempt_index: usize = 0;

        while (remaining > 0) {
            trace.chunk_count += 1;
            var buffered = @min(n_outbuf, remaining);

            while (buffered > 0) {
                const result = if (attempt_index < write_results.len)
                    write_results[attempt_index]
                else
                    @as(isize, @intCast(buffered));
                attempt_index += 1;

                if (result == eagain) {
                    trace.flush_calls += 1;
                    trace.retry_flushes += 1;
                    continue;
                }

                if (result <= 0) {
                    trace.dropped_bytes += buffered;
                    remaining -= buffered;
                    buffered = 0;
                    continue;
                }

                const wrote = @min(buffered, @as(usize, @intCast(result)));
                trace.written_bytes += wrote;
                remaining -= wrote;
                buffered -= wrote;
            }
        }

        trace.flush_calls += 1;
        return trace;
    }
};
