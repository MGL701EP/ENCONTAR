@echo off
REM Lanzador para Windows: ejecuta gitflow.sh con el Bash que instala Git para Windows.
REM Uso (CMD o PowerShell, dentro de la carpeta del proyecto):  gitflow subir "mensaje"
setlocal
set "GB=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%GB%" set "GB=%LocalAppData%\Programs\Git\bin\bash.exe"
if not exist "%GB%" (
  echo ERROR: No encuentro Git Bash. Instala Git desde https://git-scm.com
  exit /b 1
)
"%GB%" "%~dp0gitflow.sh" %*
exit /b %ERRORLEVEL%
