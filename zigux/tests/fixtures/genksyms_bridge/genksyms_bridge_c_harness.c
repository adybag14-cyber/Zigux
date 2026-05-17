// SPDX-License-Identifier: GPL-2.0-or-later
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static void json_write_escaped(FILE *out, const char *text, size_t len) {
    size_t i;
    for (i = 0; i < len; ++i) {
        unsigned char ch = (unsigned char)text[i];
        switch (ch) {
        case '\\':
            fputs("\\\\", out);
            break;
        case '"':
            fputs("\\\"", out);
            break;
        case '\n':
            fputs("\\n", out);
            break;
        case '\r':
            fputs("\\r", out);
            break;
        case '\t':
            fputs("\\t", out);
            break;
        default:
            fputc((int)ch, out);
            break;
        }
    }
}

static char *read_fd_all(int fd, size_t *len_out) {
    size_t used = 0;
    size_t capacity = 256;
    char *buffer = (char *)malloc(capacity);
    if (buffer == NULL) {
        return NULL;
    }

    for (;;) {
        ssize_t read_count;
        if (used == capacity) {
            size_t next_capacity = capacity * 2;
            char *next = (char *)realloc(buffer, next_capacity);
            if (next == NULL) {
                free(buffer);
                return NULL;
            }
            buffer = next;
            capacity = next_capacity;
        }

        read_count = read(fd, buffer + used, capacity - used);
        if (read_count == 0) {
            break;
        }
        if (read_count < 0) {
            if (errno == EINTR) {
                continue;
            }
            free(buffer);
            return NULL;
        }
        used += (size_t)read_count;
    }

    if (used == capacity) {
        char *next = (char *)realloc(buffer, capacity + 1);
        if (next == NULL) {
            free(buffer);
            return NULL;
        }
        buffer = next;
    }
    buffer[used] = '\0';
    *len_out = used;
    return buffer;
}

int main(int argc, char **argv) {
    const char *tool_path = getenv("ZIGUX_GENKSYMS_TOOL");
    int stdout_pipe[2];
    int stderr_pipe[2];
    pid_t child_pid;
    char **child_argv;
    char *stdout_text = NULL;
    char *stderr_text = NULL;
    size_t stdout_len = 0;
    size_t stderr_len = 0;
    int status = 0;
    int exit_code;
    int i;

    if (tool_path == NULL || tool_path[0] == '\0') {
        tool_path = "scripts/genksyms/genksyms";
    }

    child_argv = (char **)calloc((size_t)argc + 1, sizeof(char *));
    if (child_argv == NULL) {
        fprintf(stderr, "genksyms_bridge_c_harness: calloc failed\n");
        return 125;
    }
    child_argv[0] = (char *)tool_path;
    for (i = 1; i < argc; ++i) {
        child_argv[i] = argv[i];
    }
    child_argv[argc] = NULL;

    if (pipe(stdout_pipe) != 0 || pipe(stderr_pipe) != 0) {
        fprintf(stderr, "genksyms_bridge_c_harness: pipe failed: %s\n", strerror(errno));
        free(child_argv);
        return 125;
    }

    child_pid = fork();
    if (child_pid < 0) {
        fprintf(stderr, "genksyms_bridge_c_harness: fork failed: %s\n", strerror(errno));
        close(stdout_pipe[0]);
        close(stdout_pipe[1]);
        close(stderr_pipe[0]);
        close(stderr_pipe[1]);
        free(child_argv);
        return 125;
    }

    if (child_pid == 0) {
        close(stdout_pipe[0]);
        close(stderr_pipe[0]);
        if (dup2(stdout_pipe[1], STDOUT_FILENO) < 0 || dup2(stderr_pipe[1], STDERR_FILENO) < 0) {
            fprintf(stderr, "genksyms_bridge_c_harness: dup2 failed: %s\n", strerror(errno));
            _exit(127);
        }
        close(stdout_pipe[1]);
        close(stderr_pipe[1]);
        execv(tool_path, child_argv);
        fprintf(stderr, "genksyms_bridge_c_harness: execv(%s) failed: %s\n", tool_path, strerror(errno));
        _exit(127);
    }

    close(stdout_pipe[1]);
    close(stderr_pipe[1]);
    stdout_text = read_fd_all(stdout_pipe[0], &stdout_len);
    stderr_text = read_fd_all(stderr_pipe[0], &stderr_len);
    close(stdout_pipe[0]);
    close(stderr_pipe[0]);

    if (stdout_text == NULL || stderr_text == NULL) {
        free(stdout_text);
        free(stderr_text);
        free(child_argv);
        return 125;
    }

    while (waitpid(child_pid, &status, 0) < 0) {
        if (errno != EINTR) {
            free(stdout_text);
            free(stderr_text);
            free(child_argv);
            return 125;
        }
    }

    if (WIFEXITED(status)) {
        exit_code = WEXITSTATUS(status);
    } else if (WIFSIGNALED(status)) {
        exit_code = 128 + WTERMSIG(status);
    } else {
        exit_code = 125;
    }

    fputs("{\"stdout\":\"", stdout);
    json_write_escaped(stdout, stdout_text, stdout_len);
    fputs("\",\"stderr\":\"", stdout);
    json_write_escaped(stdout, stderr_text, stderr_len);
    fprintf(stdout, "\",\"exit_code\":%d}\n", exit_code);

    free(stdout_text);
    free(stderr_text);
    free(child_argv);
    return 0;
}
