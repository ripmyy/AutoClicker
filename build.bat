@echo off
echo ========================================================
echo  Building AutoClicker C# WPF (.NET 6)
echo ========================================================

dotnet build AutoClicker.sln -c Release
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo  Publishing Standalone Single-File Windows Executable
echo ========================================================
dotnet publish src/AutoClicker/AutoClicker.csproj -c Release -r win-x64 -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true --self-contained true -o dist/
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Publish failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo  SUCCESS! Executable is ready at: dist\AutoClicker.exe
echo ========================================================
pause
