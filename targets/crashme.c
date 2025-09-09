#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc > 1) {
        char buf[16];
        strcpy(buf, argv[1]);  // 潜在溢出
        printf("Input: %s\n", buf);
    } else {
        printf("Usage: ./crashme <input>\n");
    }
    return 0;
}

