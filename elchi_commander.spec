# -*- mode: python ; coding: utf-8 -*-

import shutil
from pathlib import Path

# ----- Elchi Commander -----
elchi_commander_a = Analysis(
    ['src\\elchi_commander.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
elchi_commander_pyz = PYZ(elchi_commander_a.pure)

elchi_commander_exe = EXE(
    elchi_commander_pyz,
    elchi_commander_a.scripts,
    exclude_binaries=True,
    name='Elchi Commander',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ----- Elchi Creator -----
elchi_creator_a = Analysis(
    ['src\\elchi_creator.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
elchi_creator_pyz = PYZ(elchi_creator_a.pure)

elchi_creator_exe = EXE(
    elchi_creator_pyz,
    elchi_creator_a.scripts,
    exclude_binaries=True,
    name='Elchi Creator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ----- Shared output folder -----
coll = COLLECT(
    elchi_commander_exe,
    elchi_commander_a.binaries,
    elchi_commander_a.datas,
    elchi_creator_exe,
    elchi_creator_a.binaries,
    elchi_creator_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='elchi_commander',   # this becomes dist/elchi_commander/
)

# Extra files into the same shared folder
dist_dir = Path("dist") / 'elchi_commander'
dist_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2("make_default_config.bat", dist_dir / "make_default_config.bat")
shutil.copy2("make_test_config.bat", dist_dir / "make_test_config.bat")
shutil.copy2("Readme.md", dist_dir / "Readme.md")
