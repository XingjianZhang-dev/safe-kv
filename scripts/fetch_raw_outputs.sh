#!/usr/bin/env bash
# Restore the raw per-example output files that are kept out of git for size (see RAW_OUTPUTS_IN_RELEASE.txt next to
# each affected run). Downloads the release asset for the given tag (default v1.0.0), verifies it, and extracts it
# into the repository root. Requires curl and shasum.
set -euo pipefail
TAG="${1:-v1.0.0}"
REPO_URL="https://github.com/XingjianZhang-dev/safe-kv"
ASSET="safe-kv-raw-outputs-${TAG}.tar.gz"
cd "$(dirname "$0")/.."
curl -L --fail -o "$ASSET" "${REPO_URL}/releases/download/${TAG}/${ASSET}"
curl -L --fail -o "${ASSET}.sha256" "${REPO_URL}/releases/download/${TAG}/${ASSET}.sha256"
shasum -a 256 -c "${ASSET}.sha256"
tar -xzf "$ASSET"
echo "verifying extracted files against RAW_OUTPUTS_MANIFEST.tsv"
tail -n +2 RAW_OUTPUTS_MANIFEST.tsv | while IFS=$'\t' read -r path size digest; do
  echo "${digest}  ${path}"
done | shasum -a 256 -c
rm -f "$ASSET" "${ASSET}.sha256" RAW_OUTPUTS_MANIFEST.tsv
echo "raw outputs restored"
