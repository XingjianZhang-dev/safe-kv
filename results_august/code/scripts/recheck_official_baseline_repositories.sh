#!/usr/bin/env bash
set -euo pipefail

specs=(
  "LMCache|/root/autodl-tmp/safekv_ipm_journal/baselines/lmcache_v0.5.4|https://github.com/LMCache/LMCache.git|refs/tags/v0.5.4"
  "EPIC|/root/autodl-tmp/safekv_ipm_journal/baselines/epic_official|https://github.com/DerekHJH/epic.git|HEAD"
  "KVPacket|/root/autodl-tmp/safekv_ipm_journal/baselines/kvpacket_official|https://github.com/ChuangtaoChen-TUM/KVPacket.git|refs/heads/paper-artifact"
)

for spec in "${specs[@]}"; do
  IFS="|" read -r name path remote ref <<<"$spec"
  echo "BEGIN_REPO $name"
  echo "LOCAL_COMMIT $(git -C "$path" rev-parse HEAD)"
  echo "LOCAL_TREE $(git -C "$path" rev-parse 'HEAD^{tree}')"
  status=$(git -C "$path" status --porcelain)
  if [[ -n "$status" ]]; then
    echo "WORKTREE_CLEAN false"
    printf '%s\n' "$status"
    exit 1
  fi
  echo "WORKTREE_CLEAN true"
  if [[ "$ref" == "HEAD" ]]; then
    echo "REMOTE_HEADS_BEGIN"
    git ls-remote "$remote" HEAD refs/heads/main refs/heads/master
    echo "REMOTE_HEADS_END"
  else
    remote_hash=$(git ls-remote "$remote" "$ref" | awk '{print $1}')
    if [[ -z "$remote_hash" ]]; then
      echo "REMOTE_REF_MISSING $ref"
      exit 1
    fi
    echo "REMOTE_REF $ref $remote_hash"
  fi
  echo "END_REPO $name"
done
