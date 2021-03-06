/*
 * Copyright (c) Pavol Rusnak, SatoshiLabs
 *
 * Licensed under TREZOR License
 * see LICENSE file for details
 */

#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "common.h"
#include "sdcard.h"

#ifndef SDCARD_FILE
#define SDCARD_FILE "/var/tmp/trezor.sdcard"
#endif

#define SDCARD_SIZE (32 * 1024 * 1024)

static uint8_t *sdcard_buffer;
static secbool sdcard_powered;

static void sdcard_exit(void)
{
    int r = munmap(sdcard_buffer, SDCARD_SIZE);
    ensure(sectrue * (r == 0), "munmap failed");
}

void sdcard_init(void) {
    int r;

    // check whether the file exists and it has the correct size
    struct stat sb;
    r = stat(SDCARD_FILE, &sb);

    // (re)create if non existant or wrong size
    if (r != 0 || sb.st_size != SDCARD_SIZE) {
        int fd = open(SDCARD_FILE, O_RDWR | O_CREAT | O_TRUNC, (mode_t)0600);
        ensure(sectrue * (fd >= 0), "open failed");
        for (int i = 0; i < SDCARD_SIZE / 16; i++) {
            ssize_t s = write(fd, "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF", 16);
            ensure(sectrue * (s >= 0), "write failed");
        }
        r = close(fd);
        ensure(sectrue * (r == 0), "close failed");
    }

    // mmap file
    int fd = open(SDCARD_FILE, O_RDWR);
    ensure(sectrue * (fd >= 0), "open failed");

    void *map = mmap(0, SDCARD_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    ensure(sectrue * (map != MAP_FAILED), "mmap failed");

    sdcard_buffer = (uint8_t *)map;

    sdcard_powered = secfalse;

    atexit(sdcard_exit);
}

secbool sdcard_is_present(void) {
    return sectrue;
}

secbool sdcard_power_on(void) {
    sdcard_powered = sectrue;
    return sectrue;
}

void sdcard_power_off(void) {
    sdcard_powered = secfalse;
}

uint64_t sdcard_get_capacity_in_bytes(void) {
    return sdcard_powered == sectrue ? SDCARD_SIZE : 0;
}

secbool sdcard_read_blocks(uint32_t *dest, uint32_t block_num, uint32_t num_blocks) {
    if (sectrue != sdcard_powered) {
        return secfalse;
    }
    memcpy(dest, sdcard_buffer + block_num * SDCARD_BLOCK_SIZE, num_blocks * SDCARD_BLOCK_SIZE);
    return sectrue;
}

secbool sdcard_write_blocks(const uint32_t *src, uint32_t block_num, uint32_t num_blocks) {
    if (sectrue != sdcard_powered) {
        return secfalse;
    }
    memcpy(sdcard_buffer + block_num * SDCARD_BLOCK_SIZE, src, num_blocks * SDCARD_BLOCK_SIZE);
    return sectrue;
}
