from __future__ import annotations

import subprocess
import tempfile
import shutil
from pathlib import Path

from .app_bundle import _disable_stock_applet_icon


def ensure_folder_launcher(folder: Path) -> Path:
    runtime_root = Path(__file__).resolve().parents[1]

    app_dir = folder / "OpenSpawn Agent.app"
    if app_dir.exists():
        shutil.rmtree(app_dir)

    command_path = folder / "OpenSpawn Agent.command"
    command_path.unlink(missing_ok=True)

    script = _folder_agent_script(runtime_root, folder)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
        handle.write(script)
        source = Path(handle.name)
    try:
        subprocess.run(
            ["/usr/bin/osacompile", "-l", "JavaScript", "-o", str(app_dir), str(source)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        source.unlink(missing_ok=True)
    _copy_folder_launcher_icon(runtime_root, app_dir)
    return app_dir


def remove_folder_launcher(folder: Path) -> None:
    app_dir = folder / "OpenSpawn Agent.app"
    if app_dir.exists():
        shutil.rmtree(app_dir)

    command_path = folder / "OpenSpawn Agent.command"
    command_path.unlink(missing_ok=True)


def _folder_agent_script(runtime_root: Path, folder: Path) -> str:
    root = _js_string(str(runtime_root))
    launcher = _js_string(str(runtime_root / "bin" / "openspawn-pi-launcher.sh"))
    target = _js_string(str(folder))
    return f"""
ObjC.import('stdlib');
ObjC.import('Foundation');

function shellQuote(value) {{
  return "'" + String(value).replace(/'/g, "'\\\\''") + "'";
}}

function launcherScript() {{
  var command = "cd " + shellQuote({root}) + "\\n" +
    "/bin/bash " + shellQuote({launcher}) + " " + shellQuote({target});
  return [
    "#!/bin/bash",
    "set -euo pipefail",
    command,
    "rm -- \\"$0\\""
  ].join("\\n") + "\\n";
}}

function writeTempLauncher() {{
  var tempPath = "/tmp/openspawn-agent-launch-" + (new Date().getTime()) + ".command";
  var scriptText = launcherScript();
  var content = $(scriptText);
  content.writeToFileAtomicallyEncodingError($(tempPath), true, $.NSUTF8StringEncoding, null);
  return tempPath;
}}

function launch() {{
  var app = Application.currentApplication();
  app.includeStandardAdditions = true;
  var tempPath = writeTempLauncher();
  app.doShellScript("/bin/chmod +x " + shellQuote(tempPath));
  app.doShellScript("/usr/bin/open " + shellQuote(tempPath));
}}

function run(argv) {{
  launch();
}}
""".strip()


def _js_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _copy_folder_launcher_icon(runtime_root: Path, app_dir: Path) -> None:
    source_icon = runtime_root / "OpenSpawn.app" / "Contents" / "Resources" / "droplet.icns"
    target_icon = app_dir / "Contents" / "Resources" / "droplet.icns"
    if not (source_icon.exists() and target_icon.parent.exists()):
        return
    shutil.copy2(source_icon, target_icon)
    _disable_stock_applet_icon(app_dir)
