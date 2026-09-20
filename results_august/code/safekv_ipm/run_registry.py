"""Auditable experiment launcher that preserves successful and failed runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import socket
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


REGISTRY_SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_fingerprint(root: Path) -> dict[str, Any]:
    """Hash code files by relative path and content, excluding generated state."""
    suffixes = {".py", ".yaml", ".yml", ".toml", ".json", ".txt", ".md", ".sh"}
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        if any(part in {"__pycache__", ".pytest_cache", ".git"} for part in path.parts):
            continue
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    digest = hashlib.sha256()
    for item in files:
        digest.update(f"{item['path']}\0{item['sha256']}\n".encode())
    return {"root": str(root), "sha256": digest.hexdigest(), "files": files}


def ensure_code_snapshot(
    registry_dir: Path,
    fingerprint: dict[str, Any],
) -> dict[str, Any]:
    """Persist one immutable, content-addressed copy of every fingerprinted file."""

    snapshot_dir = registry_dir / "_code_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    output = snapshot_dir / f"{fingerprint['sha256']}.zip"
    if not output.exists():
        temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
        root = Path(str(fingerprint["root"]))
        try:
            with zipfile.ZipFile(
                temporary,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            ) as archive:
                for item in fingerprint["files"]:
                    path = root / item["path"]
                    data = path.read_bytes()
                    if hashlib.sha256(data).hexdigest() != item["sha256"]:
                        raise RuntimeError(
                            f"code file changed while snapshotting: {path}"
                        )
                    info = zipfile.ZipInfo(item["path"], date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
            if output.exists():
                temporary.unlink()
            else:
                temporary.replace(output)
        finally:
            if temporary.exists():
                temporary.unlink()
    return {
        "path": str(output.resolve()),
        "sha256": sha256_file(output),
        "size_bytes": output.stat().st_size,
        "tree_sha256": fingerprint["sha256"],
    }


def gpu_snapshot() -> list[dict[str, str]]:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,uuid,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    rows: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        fields = [field.strip() for field in line.split(",")]
        if len(fields) == 5:
            rows.append(dict(zip(("index", "name", "uuid", "driver", "memory_mib"), fields)))
    return rows


def input_fingerprints(paths: Sequence[Path]) -> list[dict[str, Any]]:
    fingerprints: list[dict[str, Any]] = []
    for path in paths:
        resolved = path.resolve()
        if not resolved.is_file():
            raise FileNotFoundError(f"declared input is not a file: {resolved}")
        fingerprints.append(
            {
                "path": str(resolved),
                "sha256": sha256_file(resolved),
                "size_bytes": resolved.stat().st_size,
            }
        )
    return fingerprints


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def run_tracked(args: argparse.Namespace) -> int:
    registry_dir = Path(args.registry_dir).resolve()
    run_dir = registry_dir / args.run_id
    manifest_path = run_dir / "run_manifest.json"
    if run_dir.exists():
        raise FileExistsError(f"run id already exists and will not be overwritten: {run_dir}")
    run_dir.mkdir(parents=True)

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("missing command after --")

    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    code_root = Path(args.code_root).resolve()
    code_fingerprint = tree_fingerprint(code_root)
    code_snapshot = ensure_code_snapshot(registry_dir, code_fingerprint)
    start_wall = time.time()
    manifest: dict[str, Any] = {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "run_id": args.run_id,
        "label": args.label,
        "status": "running",
        "started_at_utc": utc_now(),
        "working_directory": str(Path(args.working_directory).resolve()),
        "command_argv": command,
        "command_display": shlex.join(command),
        "inputs": input_fingerprints([Path(path) for path in args.input]),
        "code": {**code_fingerprint, "snapshot": code_snapshot},
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version,
            "gpu": gpu_snapshot(),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        },
        "logs": {"stdout": str(stdout_path), "stderr": str(stderr_path)},
    }
    atomic_write_json(manifest_path, manifest)

    try:
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            result = subprocess.run(
                command,
                cwd=Path(args.working_directory).resolve(),
                stdout=stdout_handle,
                stderr=stderr_handle,
                check=False,
            )
        manifest["exit_code"] = result.returncode
        manifest["status"] = "completed" if result.returncode == 0 else "failed"
        return_code = result.returncode
    except BaseException as error:
        manifest["status"] = "launcher_error"
        manifest["launcher_error"] = f"{type(error).__name__}: {error}"
        return_code = 125
    finally:
        manifest["finished_at_utc"] = utc_now()
        manifest["duration_seconds"] = time.time() - start_wall
        for label, path in (("stdout", stdout_path), ("stderr", stderr_path)):
            if path.exists():
                manifest["logs"][f"{label}_sha256"] = sha256_file(path)
                manifest["logs"][f"{label}_size_bytes"] = path.stat().st_size
        atomic_write_json(manifest_path, manifest)
    return return_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--working-directory", required=True)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> None:
    raise SystemExit(run_tracked(parse_args()))


if __name__ == "__main__":
    main()
