@echo off
"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" -b "%~dp0renderTemplate.blend" -P "%~dp0convertstl.py" -- %*