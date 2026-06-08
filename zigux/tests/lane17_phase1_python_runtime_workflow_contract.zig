const std = @import("std");
const testing = std.testing;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingCheckoutStep,
    MissingSetupPythonStep,
    MissingSetupPythonAction,
    MissingPythonVersion,
    MissingPinnedZigStep,
    MissingCompileScriptsStep,
    MissingCompileRoster,
    MissingEmptyRosterGuard,
    MissingCompileCommand,
    MissingFirstStandaloneChecker,
    SetupPythonNotAfterCheckout,
    SetupPythonNotBeforePinnedZig,
    CompileScriptsNotAfterPinnedZig,
    CompileScriptsNotBeforeStandaloneChecker,
    CompileStepContainsStandaloneChecker,
};

fn requireIndex(haystack: []const u8, needle: []const u8, missing: ContractError) ContractError!usize {
    return std.mem.indexOf(u8, haystack, needle) orelse missing;
}

fn requireAfter(haystack: []const u8, start: usize, needle: []const u8, missing: ContractError) ContractError!usize {
    const relative = std.mem.indexOf(u8, haystack[start..], needle) orelse return missing;
    return start + relative;
}

fn containsBetween(haystack: []const u8, start: usize, end: usize, needle: []const u8) bool {
    if (end < start) return false;
    return std.mem.indexOf(u8, haystack[start..end], needle) != null;
}

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn validatePythonRuntimeOrdering(text: []const u8) ContractError!void {
    const checkout = try requireIndex(text, "      - name: Checkout workspace snapshot\n", error.MissingCheckoutStep);
    const setup_python = try requireIndex(text, "      - name: Setup Python\n", error.MissingSetupPythonStep);
    const setup_zig = try requireIndex(text, "      - name: Setup pinned Zig toolchain\n", error.MissingPinnedZigStep);
    const compile_scripts = try requireIndex(text, "      - name: Compile current scripts\n", error.MissingCompileScriptsStep);
    const first_checker = try requireIndex(text, "      - name: Self-test current Zig toolchain checker\n", error.MissingFirstStandaloneChecker);

    if (setup_python <= checkout) return error.SetupPythonNotAfterCheckout;
    if (setup_python >= setup_zig) return error.SetupPythonNotBeforePinnedZig;
    if (compile_scripts <= setup_zig) return error.CompileScriptsNotAfterPinnedZig;
    if (compile_scripts >= first_checker) return error.CompileScriptsNotBeforeStandaloneChecker;

    const setup_python_end = setup_zig;
    _ = requireAfter(text, setup_python, "        uses: actions/setup-python@v6.2.0\n", error.MissingSetupPythonAction) catch |err| return err;
    _ = requireAfter(text, setup_python, "          python-version: '3.x'\n", error.MissingPythonVersion) catch |err| return err;
    if (!containsBetween(text, setup_python, setup_python_end, "        uses: actions/setup-python@v6.2.0\n")) {
        return error.MissingSetupPythonAction;
    }
    if (!containsBetween(text, setup_python, setup_python_end, "          python-version: '3.x'\n")) {
        return error.MissingPythonVersion;
    }

    const compile_end = first_checker;
    if (!containsBetween(text, compile_scripts, compile_end, "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)\n")) {
        return error.MissingCompileRoster;
    }
    if (!containsBetween(text, compile_scripts, compile_end, "if [ \"${#scripts[@]}\" -eq 0 ]; then\n")) {
        return error.MissingEmptyRosterGuard;
    }
    if (!containsBetween(text, compile_scripts, compile_end, "python3 -m py_compile \"${scripts[@]}\"\n")) {
        return error.MissingCompileCommand;
    }
    if (containsBetween(text, compile_scripts, compile_end, "python3 scripts/zigux/")) {
        return error.CompileStepContainsStandaloneChecker;
    }
}

test "live workflow pins Python runtime before pinned Zig setup" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try validatePythonRuntimeOrdering(workflow);
}

test "contract rejects missing setup-python pin" {
    const fixture =
        \\      - name: Checkout workspace snapshot
        \\        run: echo checkout
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v6.1.0
        \\        with:
        \\          python-version: '3.x'
        \\      - name: Setup pinned Zig toolchain
        \\        run: echo zig
        \\      - name: Compile current scripts
        \\        run: |
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
        \\          if [ "${#scripts[@]}" -eq 0 ]; then
        \\            exit 1
        \\          fi
        \\          python3 -m py_compile "${scripts[@]}"
        \\      - name: Self-test current Zig toolchain checker
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
        \\
    ;

    try testing.expectError(error.MissingSetupPythonAction, validatePythonRuntimeOrdering(fixture));
}

test "contract rejects compile sweep after first standalone checker" {
    const fixture =
        \\      - name: Checkout workspace snapshot
        \\        run: echo checkout
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v6.2.0
        \\        with:
        \\          python-version: '3.x'
        \\      - name: Setup pinned Zig toolchain
        \\        run: echo zig
        \\      - name: Self-test current Zig toolchain checker
        \\        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
        \\      - name: Compile current scripts
        \\        run: |
        \\          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)
        \\          if [ "${#scripts[@]}" -eq 0 ]; then
        \\            exit 1
        \\          fi
        \\          python3 -m py_compile "${scripts[@]}"
        \\
    ;

    try testing.expectError(error.CompileScriptsNotBeforeStandaloneChecker, validatePythonRuntimeOrdering(fixture));
}
