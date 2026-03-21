# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\a2\\CAMASOTS\\master_interface.py'],
    pathex=['c:\\a2\\CAMASOTS\\venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('c:\\a2\\CAMASOTS\\ATHENEA', 'ATHENEA'), ('c:\\a2\\CAMASOTS\\VIRGILIO', 'VIRGILIO'), ('c:\\a2\\CAMASOTS\\GUILLECODER', 'GUILLECODER'), ('c:\\a2\\CAMASOTS\\PUENTE', 'PUENTE'), ('c:\\a2\\CAMASOTS\\DATABASE', 'DATABASE')],
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
    a.binaries,
    a.datas,
    [],
    name='CAMASOTS_MASTER',
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
)
