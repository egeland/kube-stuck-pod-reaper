#!/usr/bin/env python3

# kube-stuck-pod-reaper - helps you clean up pods stuck in crashloops.
# Copyright (C) 2018  Frode Egeland <egeland@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from kubernetes import client, config
import os

global MAX_RESTART
MAX_RESTART = int(os.getenv("MAX_RESTART", 20))

global DRYRUN
DRYRUN = os.getenv("DRYRUN", False) == "True" or os.getenv("DRYRUN", False) == "true"


def container_info(pod):
    restart_count = 0
    container_creating = False
    for c in pod.status.container_statuses:
        restart_count += c.restart_count
        if c.state.waiting and c.state.waiting.reason == "ContainerCreating":
            container_creating = True
    return (restart_count, container_creating)


def evict_pod(pod):
    delete_options = client.V1DeleteOptions(grace_period_seconds=30)
    eviction = client.V1beta1Eviction(delete_options=delete_options, metadata=pod.metadata)
    if pod.metadata.namespace in ["kube-system"]:
        print("PROTECTED: not evicting from {}: {}".format(pod.metadata.namespace, pod.metadata.name))
    elif DRYRUN:
        print("DRYRUN: skipping evict_pod step for {}/{}".format(pod.metadata.namespace, pod.metadata.name))
    else:
        v1.create_namespaced_pod_eviction(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            body=eviction
        )


def main():
    config.load_incluster_config()

    global v1
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for pod in ret.items:
        if pod.status.phase in ["Succeeded"]:
            continue
        restart_count, is_container_creating = container_info(pod)
        if is_container_creating:
            continue
        if restart_count >= MAX_RESTART:
            evict_pod(pod)


if __name__ == '__main__':
    main()
