@echo off
echo ========================================
echo    Quotex Predictor Server Startup
echo ========================================
echo.
echo Starting Django development server...
echo Server will be available at: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd /d "%~dp0quotex_predictor"
python manage.py runserver 127.0.0.1:8000

echo.
echo Server stopped.
pause