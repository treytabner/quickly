#!/bin/sh

export DEBIAN_FRONTEND=noninteractive

dpkg -P rpcbind nfs-common exim4 exim4-base exim4-config exim4-daemon-light bsd-mailx \
    libgssglue1 liblockfile1 libnfsidmap2 libtirpc1
