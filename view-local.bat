@echo off
setlocal
pushd "%~dp0" || exit /b 1
python -m ipo_ready.server --open-browser --port 0 %*
set "IPO_READY_EXIT=%ERRORLEVEL%"
if not "%IPO_READY_EXIT%"=="0" pause
popd
exit /b %IPO_READY_EXIT%
