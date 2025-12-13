@echo off
echo Starting Quotex Trading Predictor...
echo =====================================

cd quotex_predictor

echo Checking database...
python manage.py migrate --run-syncdb

echo Starting development server...
echo Open http://localhost:8000 in your browser
echo Press Ctrl+C to stop the server

python manage.py runserver