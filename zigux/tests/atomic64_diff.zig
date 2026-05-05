// Keep the roadmap-named Phase 4 entrypoint while reusing the shared
// runtime-backed atomic64 replay that Phase 9 still imports directly.
comptime {
    _ = @import("runtime_atomic64_diff.zig");
}
