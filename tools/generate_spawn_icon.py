from __future__ import annotations

import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


ICON_SOURCE = Path("icon") / "openspawn-abstract-spawn-icon.png"
ICON_TYPES = {
    16: b"icp4",
    32: b"icp5",
    64: b"icp6",
    128: b"ic07",
    256: b"ic08",
    512: b"ic09",
    1024: b"ic10",
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / ICON_SOURCE
    if not source.exists():
        raise FileNotFoundError(f"Missing source icon: {source}")

    build_dir = root / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    output_icns = build_dir / "OpenSpawn.icns"
    output_icns.write_bytes(build_icns(source))

    app_icon = root / "OpenSpawn.app" / "Contents" / "Resources" / "droplet.icns"
    shutil.copy2(output_icns, app_icon)
    print(f"Wrote {output_icns}")
    print(f"Updated {app_icon}")


def build_icns(source: Path) -> bytes:
    blocks: list[bytes] = []
    for size, icon_type in ICON_TYPES.items():
        png_data = render_png(source, size)
        block = icon_type + struct.pack(">I", len(png_data) + 8) + png_data
        blocks.append(block)

    body = b"".join(blocks)
    return b"icns" + struct.pack(">I", len(body) + 8) + body


def render_png(source: Path, size: int) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        temp_path = Path(handle.name)
    try:
        subprocess.run(
            [
                "/usr/bin/sips",
                "-z",
                str(size),
                str(size),
                "--setProperty",
                "format",
                "png",
                str(source),
                "--out",
                str(temp_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return temp_path.read_bytes()
    finally:
        temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
