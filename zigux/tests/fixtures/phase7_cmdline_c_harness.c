#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

int get_option(char **str, int *pint);
char *get_options(const char *str, int nints, int *ints);
unsigned long long memparse(const char *ptr, char **retptr);
bool parse_option_str(const char *str, const char *option);
char *next_arg(char *args, char **param, char **val);

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

static void emit_int_array(const int *values, size_t count)
{
    size_t i;

    putchar('[');
    for (i = 0; i < count; i++) {
        if (i)
            putchar(',');
        printf("%d", values[i]);
    }
    putchar(']');
}

static void run_get_option_section(void)
{
    char range_input[] = "3-5";
    char plus_input[] = "+7,panic";
    char plus_hex_input[] = "+0x10,panic";
    char wrapped_positive_input[] = "18446744073709551615,tail";
    char wrapped_negative_input[] = "-18446744073709551615,tail";
    char *range_rest = range_input;
    char *plus_rest = plus_input;
    char *plus_hex_rest = plus_hex_input;
    char *wrapped_positive_rest = wrapped_positive_input;
    char *wrapped_negative_rest = wrapped_negative_input;
    int range_value = -1;
    int plus_value = -1;
    int plus_hex_value = -1;
    int wrapped_positive_value = 0;
    int wrapped_negative_value = 0;
    int range_rc = get_option(&range_rest, &range_value);
    int plus_rc = get_option(&plus_rest, &plus_value);
    int plus_hex_rc = get_option(&plus_hex_rest, &plus_hex_value);
    int wrapped_positive_rc = get_option(&wrapped_positive_rest, &wrapped_positive_value);
    int wrapped_negative_rc = get_option(&wrapped_negative_rest, &wrapped_negative_value);

    printf("\"get_option\":{");
    printf("\"range\":{");
    printf("\"rc\":%d,", range_rc);
    printf("\"value\":%d,", range_value);
    printf("\"rest\":");
    emit_json_string(range_rest);
    printf("},");
    printf("\"leading_plus\":{");
    printf("\"rc\":%d,", plus_rc);
    printf("\"value\":%d,", plus_value);
    printf("\"rest\":");
    emit_json_string(plus_rest);
    printf("},");
    printf("\"leading_plus_hex\":{");
    printf("\"rc\":%d,", plus_hex_rc);
    printf("\"value\":%d,", plus_hex_value);
    printf("\"rest\":");
    emit_json_string(plus_hex_rest);
    printf("},");
    printf("\"wrapped_positive_low_word\":{");
    printf("\"rc\":%d,", wrapped_positive_rc);
    printf("\"value\":%d,", wrapped_positive_value);
    printf("\"rest\":");
    emit_json_string(wrapped_positive_rest);
    printf("},");
    printf("\"wrapped_negative_low_word\":{");
    printf("\"rc\":%d,", wrapped_negative_rc);
    printf("\"value\":%d,", wrapped_negative_value);
    printf("\"rest\":");
    emit_json_string(wrapped_negative_rest);
    printf("}}");
}

static void run_get_options_section(void)
{
    char limited_input[] = "1-4,8";
    char validate_input[] = "1-4,8";
    int limited[3] = { 0, 0, 0 };
    int validate[8] = { 0 };
    char *limited_rest = get_options(limited_input, 3, limited);
    char *validate_rest = get_options(validate_input, 0, validate);

    printf("\"get_options\":{");
    printf("\"limited_capacity\":{");
    printf("\"rest\":");
    emit_json_string(limited_rest);
    printf(",\"values\":");
    emit_int_array(limited, 3);
    printf("},");
    printf("\"validation_only\":{");
    printf("\"rest\":");
    emit_json_string(validate_rest);
    printf(",\"values\":");
    emit_int_array(validate, 8);
    printf("}}");
}

static void run_memparse_section(void)
{
    char memparse_input[] = "64K,panic";
    char leading_plus_input[] = "+0x10";
    char bare_suffix_input[] = "G5";
    char bare_hex_prefix_input[] = "0xK";
    char *memparse_rest = NULL;
    char *leading_plus_rest = NULL;
    char *bare_suffix_rest = NULL;
    char *bare_hex_prefix_rest = NULL;
    unsigned long long sized = memparse(memparse_input, &memparse_rest);
    unsigned long long leading_plus = memparse(leading_plus_input, &leading_plus_rest);
    unsigned long long bare_suffix = memparse(bare_suffix_input, &bare_suffix_rest);
    unsigned long long bare_hex_prefix = memparse(bare_hex_prefix_input, &bare_hex_prefix_rest);

    printf("\"memparse\":{");
    printf("\"suffix_scaling\":{");
    printf("\"value\":%llu,", sized);
    printf("\"stop_index\":%ld", (long)(memparse_rest - memparse_input));
    printf("},");
    printf("\"bare_suffix\":{");
    printf("\"value\":%llu,", bare_suffix);
    printf("\"stop_index\":%ld", (long)(bare_suffix_rest - bare_suffix_input));
    printf("},");
    printf("\"bare_hex_prefix\":{");
    printf("\"value\":%llu,", bare_hex_prefix);
    printf("\"stop_index\":%ld", (long)(bare_hex_prefix_rest - bare_hex_prefix_input));
    printf("},");
    printf("\"leading_plus\":{");
    printf("\"value\":%llu,", leading_plus);
    printf("\"stop_index\":%ld", (long)(leading_plus_rest - leading_plus_input));
    printf("}}");
}

static void run_parse_option_section(void)
{
    const char nul_stop_input[] = {
        'q', 'u', 'i', 'e', 't', ',',
        'd', 'e', 'b', 'u', 'g', '\0',
        ',', 'n', 'o', 'h', 'l', 't', '\0',
    };

    printf("\"parse_option_str\":{");
    printf("\"empty_between_commas\":%s,", parse_option_str("quiet,,debug", "") ? "true" : "false");
    printf("\"empty_trailing_comma\":%s,", parse_option_str("quiet,", "") ? "true" : "false");
    printf("\"empty_source\":%s,", parse_option_str("", "") ? "true" : "false");
    printf("\"exact_bare_option\":%s,", parse_option_str("quiet,debug,nohlt", "debug") ? "true" : "false");
    printf("\"assignment_not_bare\":%s,", parse_option_str("quiet,debug=1,nohlt", "debug") ? "true" : "false");
    printf("\"nul_stop_bare_scan\":%s", parse_option_str(nul_stop_input, "nohlt") ? "true" : "false");
    printf("}");
}

static void emit_next_arg_case(const char *name, const char *input)
{
    char buffer[128];
    char *param = NULL;
    char *value = NULL;
    char *rest;

    memset(buffer, 0, sizeof(buffer));
    memcpy(buffer, input, strlen(input));
    rest = next_arg(buffer, &param, &value);

    emit_json_string(name);
    printf(":{");
    printf("\"param\":");
    emit_json_string(param);
    printf(",\"value\":");
    if (value)
        emit_json_string(value);
    else
        fputs("null", stdout);
    printf(",\"rest\":");
    emit_json_string(rest);
    printf("}");
}

static void run_next_arg_section(void)
{
    printf("\"next_arg\":{");
    emit_next_arg_case("quoted_value", "root=\"/dev/sda 1\" ro");
    printf(",");
    emit_next_arg_case("quoted_bare_token", "\"noparam value\" next");
    printf(",");
    emit_next_arg_case("first_equals_value_split", "key=alpha=beta tail");
    printf(",");
    emit_next_arg_case("leading_equals", "=bad next");
    printf(",");
    emit_next_arg_case("trimmed_empty_rest", "mode=fast   ");
    printf(",");
    emit_next_arg_case("unterminated_quoted_value", "mode=\"fast boot");
    printf("}");
}

int main(void)
{
    printf("{");
    run_get_option_section();
    printf(",");
    run_get_options_section();
    printf(",");
    run_memparse_section();
    printf(",");
    run_parse_option_section();
    printf(",");
    run_next_arg_section();
    printf("}\n");
    return 0;
}
