#!/usr/bin/python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
# Copyright (c) 2017 Juniper Networks, Inc. All rights reserved.
#

"""
Tungsten CNI plugin
"""
import ConfigParser

from mesos_cni import tungsten_mesos_cni
from kube_cni import tungsten_kube_cni

ORCHES_FILE = '/etc/tungsten/orchestrator.ini'

ORCHES_MESOS = 'mesos'
ORCHES_K8S   = 'kubernetes'


def main():
    try:
        config = ConfigParser.RawConfigParser()
        config.read(ORCHES_FILE)
        orches = config.get('DEFAULT', 'orchestrator')
    except ConfigParser.Error:
        orches = ORCHES_MESOS

    if orches == ORCHES_K8S:
        tungsten_kube_cni.main()
    else:
        tungsten_mesos_cni.main()

if __name__ == "__main__":
    main()
