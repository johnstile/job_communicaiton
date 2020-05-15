:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: By: John Stile <john@stilen.com>
:: Purpose: Setup isolated python environemtn and required modules 
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@echo off
@SETLOCAL ENABLEDELAYEDEXPANSION
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
echo Find Python3 installation using PATH
for /f %%p in ('where python.exe') do (
  for /f %%f in ('echo %%p ^| findstr "Python3"') do (
   echo %%f
   set PY3=%%f
  )
)
if not defined PY3 (
  @echo ERROR: Can't find python 3!!!
  @echo FIX: Add Python3 to PATH!!!.&goto end
)
echo Using: Python3 exe:%PY3%
@echo =====================================
@echo Test PATH for pip
for %%X in (python.exe, pip3.exe) do (set FOUND=%%~$PATH:X)
if not defined FOUND (
  @echo FIX: Add Python3 to PATH!!!.&goto end
) else (
  @echo FOUND: pip3.exe, python.exe
)
@echo =====================================
@echo Install virtualenv python module
for %%X in (virtualenv.exe) do (set FOUND=%%~$PATH:X)
if not defined FOUND (
  @echo not found. installing virtualenv
  pip3 install virtualenv
  IF ERRORLEVEL 1 (
     @echo Failed to setup virtualenv!!!&goto end
  )
) else (
  @echo virtualenv Already installed.
)
@echo =====================================
@echo Create virtualenv in venv if it does not exist
@set VENV_DIR=venv
@SET VENV_PATH=%CD%\%VENV_DIR%
@IF NOT EXIST %VENV_PATH% (
  @echo DOES NOT EXIST. Creating.
  virtualenv -p %PY3% %VENV_DIR%
  IF ERRORLEVEL 1 (
    @echo Failed to setup virtualenv!!!&goto end
  )
) else (
  @echo Found existing %VENV_PATH%
)
@echo =====================================
@echo Activate virtualenv if not acitve
if NOT DEFINED VIRTUAL_ENV (
  @call %VENV_DIR%\Scripts\Activate
  IF ERRORLEVEL 1 (
     @echo Failed to activate virtualenv!!!&goto end
  )
)

if DEFINED VIRTUAL_ENV (
  @echo Activated Virtualenv
) else (
  goto end
)
@echo =====================================
@echo Install python modules requriements
@pip install -r pip_requirements.txt

@echo =====================================
@echo Update everything
@pip install pip-review
@pip-review --auto

@echo =====================================
@echo SETUP Complete
exit /b %ERRORLEVEL%

:: Creating Exit point
:end
@echo AN ERROR OCCCURRED. EARLY EXIT!!!
