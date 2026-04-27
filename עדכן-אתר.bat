@echo off
cd /d "C:\Users\danie\Documents\work\TANAH LAHAYIM"

echo.
echo ===================================
echo    מעדכן את אתר תנ"ך לחיים...
echo ===================================
echo.

echo שלב 1: בונה את האתר...
"C:\Users\danie\AppData\Local\Programs\Kaps\WPy64-39100\python-3.9.10.amd64\python.exe" parse_and_build.py
if errorlevel 1 (
    echo שגיאה בבניית האתר!
    pause
    exit /b 1
)

echo.
echo שלב 2: שומר שינויים...
git add .
git commit -m "עדכון אתר"

echo.
echo שלב 3: מעלה לאינטרנט...
git push

echo.
echo ===================================
echo   האתר עודכן בהצלחה!
echo   השינויים יופיעו תוך 30 שניות
echo ===================================
echo.
pause
