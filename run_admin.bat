@echo off
echo Starting Django Server...
cd admin_panel
python manage.py runserver 0.0.0.0:8000
pause