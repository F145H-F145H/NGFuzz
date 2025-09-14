#include <stdio.h>
#include <string.h>
// info     To compile this crashme.c into an executable named 'crashme' with debug info, run:
//          gcc -g -o crashme crashme.c
void funA(const char *input);
void funB(const char *input);
void funC(const char *input);

void funA(const char *input) {
    printf("In funA\n");
    funB(input);
}

void funB(const char *input) {
    printf("In funB\n");
    char buf[8];
    // Vulnerable: buffer overflow if input is longer than 7 chars
    strcpy(buf, input);
    printf("funB received: %s\n", buf);
    funC(input);
}

void funC(const char *input) {
    printf("In funC\n");
    char buf[16];
    // Vulnerable: buffer overflow if input is longer than 15 chars
    strcpy(buf, input);
    printf("funC received: %s\n", buf);
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        funA(argv[1]);
    } else {
        printf("Usage: ./crashme <input>\n");
    }
    return 0;
}
