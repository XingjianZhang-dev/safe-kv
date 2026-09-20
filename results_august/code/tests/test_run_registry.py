from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from safekv_ipm.run_registry import run_tracked


def args(tmp_path, run_id: str, command: list[str]) -> argparse.Namespace:
    input_path = tmp_path / "input.json"
    input_path.write_text("{}\n", encoding="utf-8")
    code_root = tmp_path / "code"
    code_root.mkdir(exist_ok=True)
    (code_root / "experiment.py").write_text("VALUE = 1\n", encoding="utf-8")
    return argparse.Namespace(
        registry_dir=str(tmp_path / "registry"),
        run_id=run_id,
        label="contract-test",
        code_root=str(code_root),
        working_directory=str(tmp_path),
        input=[str(input_path)],
        command=command,
    )


def test_registry_preserves_success_and_provenance(tmp_path):
    run_args = args(
        tmp_path,
        "success",
        ["--", sys.executable, "-c", "print('complete')"],
    )
    assert run_tracked(run_args) == 0
    manifest = json.loads(
        (tmp_path / "registry" / "success" / "run_manifest.json").read_text()
    )
    assert manifest["status"] == "completed"
    assert manifest["exit_code"] == 0
    assert manifest["inputs"][0]["sha256"]
    assert manifest["code"]["sha256"]
    snapshot = Path(manifest["code"]["snapshot"]["path"])
    assert snapshot.is_file()
    with zipfile.ZipFile(snapshot) as archive:
        assert archive.read("experiment.py") == b"VALUE = 1\n"
    assert manifest["logs"]["stdout_sha256"]


def test_registry_preserves_failed_run_and_refuses_overwrite(tmp_path):
    run_args = args(
        tmp_path,
        "failure",
        ["--", sys.executable, "-c", "raise SystemExit(7)"],
    )
    assert run_tracked(run_args) == 7
    manifest_path = tmp_path / "registry" / "failure" / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["status"] == "failed"
    assert manifest["exit_code"] == 7
    with pytest.raises(FileExistsError):
        run_tracked(run_args)


def test_registry_cli_resolves_package_without_pythonpath(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "run_tracked.py"
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--registry-dir" in result.stdout
