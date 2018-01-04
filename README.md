# Kubernetes Stuck Pod Reaper

## PURPOSE

When you have a large cluster, with many deployments, sometimes you get pods
that restart many times. If this is due to a bad node, or some pressure on the
node, it would be convenient to move the pod to another node.

This app is meant to run as a CronJob, on a schedule of your choice,
and it will clean up these pods by evicting them.

## RBAC

If you are using RBAC, you need to add appropriate ClusterRole and
ClusterRoleBinding - see the example files in this repo.
