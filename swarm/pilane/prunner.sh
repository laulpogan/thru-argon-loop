#!/bin/bash
# prunner.sh <shard> <nshards> <P>  (ON POD) runs this shard of /work/swarm-bundle/todo.tsv (swarm Argon jobs first, then council models).
S=$1; N=$2; P=$3; mkdir -p /work/lanes/swarm-$S
awk -v s=$S -v n=$N 'NR%n==s' /work/swarm-bundle/todo.tsv | xargs -P $P -L 1 bash -c 'bash /work/pjob.sh '"$S"' $0 $1 $2'
echo "SHARD_DONE $(date +%T)" >> /work/lanes/swarm-$S/progress.tsv
