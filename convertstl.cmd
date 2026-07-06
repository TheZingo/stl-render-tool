@echo off
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b "%~dp0renderTemplate.blend" -P "%~dp0convertstl.py" -- %*