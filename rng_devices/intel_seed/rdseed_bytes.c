#include <immintrin.h>
#include <stdint.h>
#include <stddef.h>

// Fill a buffer with random bytes from RDSEED
// Returns number of bytes written (should equal n if successful)
size_t rdseed_bytes(uint8_t *buf, size_t n) {
    size_t written = 0;

    while (written < n) {
        uint64_t val;
        if (_rdseed64_step((unsigned long long *)&val)) {
            // Copy up to 8 bytes into buffer
            size_t chunk = (n - written >= 8) ? 8 : (n - written);
            for (size_t i = 0; i < chunk; i++) {
                buf[written + i] = (val >> (8 * i)) & 0xFF;  // little endian
            }
            written += chunk;
        }
        // If no entropy available, loop until it succeeds
    }

    return written;
}
