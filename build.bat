@echo off
echo ========================================================
echo  Building AutoClicker (.NET 6 / WPF)
echo ========================================================

dotnet build AutoClicker.sln -c Release
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo  Publishing Standalone and Framework-Dependent Builds
echo ========================================================

dotnet publish src/AutoClicker/AutoClicker.csproj -c Release -r win-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -p:EnableCompressionInSingleFile=true --self-contained true -o dist/standalone
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Standalone publish failed.
    pause
    exit /b %ERRORLEVEL%
)

dotnet publish src/AutoClicker/AutoClicker.csproj -c Release -r win-x64 -p:PublishSingleFile=true --self-contained false -o dist/framework-dependent
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Framework-dependent publish failed.
    pause
    exit /b %ERRORLEVEL%
)

copy /Y "dist\standalone\AutoClicker.exe" "dist\AutoClicker.exe" >nul

echo.
echo ========================================================
echo  Build complete.
echo  - Standalone: dist\AutoClicker.exe (runs on any Windows PC)
echo  - Lightweight: dist\framework-dependent\AutoClicker.exe (295 KB)
echo ========================================================
pause
