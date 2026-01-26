@echo off
echo Starting Django Admin Panel on Port 8001...
cd admin_panel
python manage.py runserver 0.0.0.0:8001
pause