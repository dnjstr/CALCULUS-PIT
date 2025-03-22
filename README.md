# CALCULUS-PIT
a Python-based application that visualizes functions and their derivatives/integrals using computational methods.

# Link to download The EXE file:
# [Click Me](https://drive.google.com/file/d/1S3p3UscpQRhf31VEvVgXfrIoqcEuaEME/view?usp=sharing)


# BUILD
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['E:\\Codes\\python\\calculus PIT\\CALCULUS-PIT\\DerivaPlot.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['scipy.special._cdflib', 'scipy.special'],
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
    a.binaries,
    a.datas,
    [],
    name='DerivaPlot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\-----\\Downloads\\screenshot_2025_03_22_182414_VRu_icon.ico'],
)

