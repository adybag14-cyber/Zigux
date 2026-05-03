#include <stddef.h>
#include <stdio.h>

typedef unsigned int gfp_t;

char **argv_split(gfp_t gfp, const char *str, int *argcp);
void argv_free(char **argv);

static void emit_json_string(const char *value)
{
    const unsigned char *cursor = (const unsigned char *)value;

    putchar('"');
    while (*cursor) {
        switch (*cursor) {
        case '\\':
            fputs("\\\\", stdout);
            break;
        case '"':
            fputs("\\\"", stdout);
            break;
        case '\n':
            fputs("\\n", stdout);
            break;
        case '\r':
            fputs("\\r", stdout);
            break;
        case '\t':
            fputs("\\t", stdout);
            break;
        default:
            if (*cursor < 0x20)
                printf("\\u%04x", *cursor);
            else
                putchar(*cursor);
            break;
        }
        cursor++;
    }
    putchar('"');
}

static void emit_json_array(char **argv)
{
    size_t index = 0;

    putchar('[');
    while (argv[index]) {
        if (index)
            putchar(',');
        emit_json_string(argv[index]);
        index++;
    }
    putchar(']');
}

static void emit_case(const char *name, const char *input, int use_null_argcp)
{
    int argc = -1;
    char **argv = argv_split(0, input, use_null_argcp ? NULL : &argc);
    size_t observed_argc = 0;

    emit_json_string(name);
    printf(":{");
    if (!argv) {
        printf("\"allocation_failed\":true}");
        return;
    }

    while (argv[observed_argc])
        observed_argc++;

    printf("\"argc\":%d,", use_null_argcp ? (int)observed_argc : argc);
    printf("\"argv\":");
    emit_json_array(argv);
    printf("}");
    argv_free(argv);
}

int main(void)
{
    static const char blank_input[] = " \t\n";
    static const char whitespace_input[] = " init=/init   console=ttyS0\tpanic=-1 ";
    static const char quote_literal_input[] = "root=\"/dev/sda 1\" single";
    static const char nul_stops_input[] = "root=/dev/vda rw\0ignored debug";
    static const char leading_nul_input[] = "\0ignored debug";

    printf("{");
    emit_case("blank_input", blank_input, 0);
    printf(",");
    emit_case("whitespace_collapse", whitespace_input, 0);
    printf(",");
    emit_case("first_nul_stops", nul_stops_input, 0);
    printf(",");
    emit_case("leading_nul_stays_empty", leading_nul_input, 0);
    printf(",");
    emit_case("quote_characters_stay_literal", quote_literal_input, 1);
    printf("}\n");
    return 0;
}