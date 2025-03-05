# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Only include the specific Google Generative AI modules we need
genai_hidden_imports = [
    'google.generativeai.types',
    'google.generativeai.client',
    'google.generativeai.models',
    'google.generativeai.generation_models',
]

# Collect only necessary data files
genai_datas = []
for module in ['google.generativeai']:
    datas = collect_data_files(module, include_py_files=False)
    # Filter out unnecessary data files
    filtered_datas = [(src, dst) for src, dst in datas if not any(pattern in src for pattern in [
        'test', 'tests', 'example', 'examples', 'doc', 'docs', '__pycache__'
    ])]
    genai_datas.extend(filtered_datas)

# Explicitly include only the modules we need
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'keyboard',
        'pyautogui',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'google.generativeai',
        'show_api_key_dialog',
        'show_explanation_window',
        'show_latest_tips',
        'tray_icon',
        'loading_window',
        'notification_window',
        'donate_window',
        'donation_page_html',
    ] + genai_hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Large modules we don't need
        'matplotlib', 'numpy', 'scipy', 'pandas', 'PyQt5', 'PySide2', 'wx',
        'IPython', 'nbconvert', 'nbformat', 'notebook', 'jupyter',
        'tensorflow', 'torch', 'cv2', 'opencv', 'sphinx', 'pytest',
        'sqlalchemy', 'django', 'flask', 'werkzeug', 'jinja2', 'babel',
        'pytz', 'dateutil', 'wtforms', 'alembic', 'gevent', 'eventlet',
        'gunicorn', 'waitress', 'xmlrpc', 'distutils', 'setuptools',
        'pkg_resources', 'email', 'html', 'http', 'urllib', 'xml',
        'pydoc_data', 'test', 'unittest', 'bdb', 'pdb',
        
        # Crypto modules we don't need
        'Crypto.SelfTest', 'Crypto.Math', 'Crypto.Protocol', 
        'Crypto.PublicKey', 'Crypto.Signature',
        
        # Tkinter modules we don't need
        'tkinter.test', 'tkinter.colorchooser', 'tkinter.dnd',
        'tkinter.font', 'tkinter.messagebox', 'tkinter.simpledialog',
        
        # Windows modules we don't need
        'win32com.demos', 'win32com.test', 'win32com.servers',
        'pywin.mfc', 'pywin.scintilla',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add our data files
a.datas += genai_datas

# Define a function to filter binaries
def should_keep_binary(binary):
    # Make sure we have the right structure
    if len(binary) < 3:
        return True
        
    name, path, typecode = binary
    
    # Skip test and example files
    if isinstance(path, str):
        excluded_patterns = [
            'test', 'tests', 'testing', 'unittest', 
            'demo', 'demos', 'sample', 'samples', 
            'example', 'examples', 'doc', 'docs',
            '__pycache__'
        ]
        if any(pattern in path.lower() for pattern in excluded_patterns):
            return False
            
        # Skip large DLLs we don't need
        excluded_dlls = [
            'qwindows.dll', 'qt5', 'pyqt5', 'tcl86t', 'tk86t',
            'vcruntime140_1.dll', 'msvcp140.dll', 'msvcp140_1.dll',
            'libopenblas', 'mkl_', 'libiomp5md.dll'
        ]
        if any(dll in path.lower() for dll in excluded_dlls):
            return False
    
    return True

# Filter binaries - keep the original structure
filtered_binaries = []
for binary in a.binaries:
    if should_keep_binary(binary):
        filtered_binaries.append(binary)
a.binaries = filtered_binaries

# Filter datas to remove unnecessary files
def should_keep_data(data):
    # Make sure we have the right structure
    if len(data) < 3:
        return True
        
    name, path, typecode = data
    
    if isinstance(path, str):
        excluded_patterns = [
            'test', 'tests', 'testing', 'unittest', 
            'demo', 'demos', 'sample', 'samples', 
            'example', 'examples', 'doc', 'docs',
            '__pycache__', '.pyc', '.pyo', '.pyd'
        ]
        if any(pattern in path.lower() for pattern in excluded_patterns):
            return False
    
    return True

# Filter datas - keep the original structure
filtered_datas = []
for data in a.datas:
    if should_keep_data(data):
        filtered_datas.append(data)
a.datas = filtered_datas

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fix_my_english',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip symbols to reduce size
    upx=True,    # Use UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
