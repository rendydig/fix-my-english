@echo off
echo Building optimized executable...

REM Clean up previous build artifacts
echo Cleaning previous build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM First try with the simple spec file
echo Building with simple spec file...
pyinstaller simple.spec

if %ERRORLEVEL% NEQ 0 (
    echo Simple spec file failed, trying with advanced spec file...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    pyinstaller fix_my_english.spec
    
    if %ERRORLEVEL% NEQ 0 (
        echo Advanced spec file also failed.
        echo Trying with basic PyInstaller command...
        if exist build rmdir /s /q build
        if exist dist rmdir /s /q dist
        pyinstaller --onefile --noconsole --icon=icon.ico --exclude matplotlib --exclude numpy --exclude scipy main.py
    )
)

REM Check if the build succeeded
if exist dist\fix_my_english.exe (
    echo Build succeeded!
) else if exist dist\main.exe (
    echo Build succeeded with default name!
    echo Renaming main.exe to fix_my_english.exe...
    move dist\main.exe dist\fix_my_english.exe
) else (
    echo Build failed.
    pause
    exit /b 1
)

REM Optional: Try to apply UPX compression if available
echo Checking for UPX...
where upx >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Applying additional UPX compression...
    upx --best --lzma dist\fix_my_english.exe
) else (
    echo UPX not found. Skipping additional compression.
    echo To get smaller executables, install UPX: pip install upx-ucl
)

echo.
echo Build completed! Your executable is in the dist folder.
echo File size: 
for %%F in (dist\fix_my_english.exe) do echo %%~zF bytes (%%~zFB)

pause
