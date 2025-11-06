# -*- mode: python ; coding: utf-8 -*-

import shutil
from pathlib import Path

a = Analysis(
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
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
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
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='elchi_commander',
)

dist_dir = Path("dist") / 'elchi_commander'
dist_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2("make_default_config.bat", dist_dir / "make_default_config.bat")
shutil.copy2("make_test_config.bat", dist_dir / "make_test_config.bat")
shutil.copy2("Readme.md", dist_dir / "Readme.md.bat")
