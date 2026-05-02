from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def build_main_app(destination: Path) -> Path:
    runtime_root = Path(__file__).resolve().parents[1]
    script = _jxa_script(runtime_root)

    if destination.exists():
        shutil.rmtree(destination)

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as handle:
        handle.write(script)
        source = Path(handle.name)
    try:
        subprocess.run(
            ["/usr/bin/osacompile", "-l", "JavaScript", "-o", str(destination), str(source)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        source.unlink(missing_ok=True)
    _copy_app_icon(runtime_root, destination)
    return destination


def _jxa_script(runtime_root: Path) -> str:
    root = _js_string(str(runtime_root))
    launcher = _js_string(str(runtime_root / "bin" / "openspawn-pi-launcher.sh"))
    return f"""
ObjC.import('stdlib');
ObjC.import('Foundation');

function shellQuote(value) {{
  return "'" + String(value).replace(/'/g, "'\\\\''") + "'";
}}

function launcherScript(target) {{
  var command = "cd " + shellQuote({root}) + "\\n" + "/bin/bash " + shellQuote({launcher});
  if (target) {{
    command += " " + shellQuote(target);
  }}
  return [
    "#!/bin/bash",
    "set -euo pipefail",
    command,
    "rm -- \\\"$0\\\""
  ].join("\\n") + "\\n";
}}

function writeTempLauncher(target) {{
  var tempPath = "/tmp/openspawn-launch-" + (new Date().getTime()) + ".command";
  var scriptText = launcherScript(target);
  var content = $(scriptText);
  content.writeToFileAtomicallyEncodingError($(tempPath), true, $.NSUTF8StringEncoding, null);
  return tempPath;
}}

function launch(target) {{
  var app = Application.currentApplication();
  app.includeStandardAdditions = true;
  var tempPath = writeTempLauncher(target);
  app.doShellScript("/bin/chmod +x " + shellQuote(tempPath));
  app.doShellScript("/usr/bin/open " + shellQuote(tempPath));
}}

function run(argv) {{
  launch(null);
}}

function openDocuments(items) {{
  if (!items || items.length === 0) {{
    launch(null);
    return;
  }}
  launch(String(items[0]));
}}
""".strip()


def _js_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _copy_app_icon(runtime_root: Path, destination: Path) -> None:
    source_icon = runtime_root / "build" / "OpenSpawn.icns"
    target_icon = destination / "Contents" / "Resources" / "droplet.icns"
    if not (source_icon.exists() and target_icon.parent.exists()):
        return
    shutil.copy2(source_icon, target_icon)
    _disable_stock_applet_icon(destination)


def _disable_stock_applet_icon(app_dir: Path) -> None:
    plist = app_dir / "Contents" / "Info.plist"
    assets = app_dir / "Contents" / "Resources" / "Assets.car"
    subprocess.run(
        ["/usr/bin/plutil", "-remove", "CFBundleIconName", str(plist)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if assets.exists():
        assets.unlink()
    bundle_icon = app_dir / "Icon\r"
    if bundle_icon.exists():
        bundle_icon.unlink()
    subprocess.run(["/usr/bin/SetFile", "-a", "Bc", str(app_dir)], check=True)
