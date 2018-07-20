/*
 * Copyright (c) 2017 Juniper Networks, Inc. All rights reserved.
 */
#include "base/logging.h"
#include "bfd/tungsten_bfd.h"

int main(int argc, char *argv[]) {
    LoggingInit();
    TungstenBfd tungsten_bfd;

    // Event loop.
    tungsten_bfd.evm()->Run();
    return 0;
}
