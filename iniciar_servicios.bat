@echo off
REM Taller 5 - Arquitectura de Microservicios
REM Instala dependencias, abre VS Code y levanta los tres microservicios.
cd /d "%~dp0"
echo Instalando dependencias...
python -m pip install -r requirements.txt
call code .
start "Productos :8001" cmd /k python -m uvicorn productos:app --port 8001
start "Clientes :8002"  cmd /k python -m uvicorn clientes:app --port 8002
start "Pedidos :8003"   cmd /k python -m uvicorn pedidos:app --port 8003
timeout /t 4 >nul
start "" "%~dp0tienda.html"
echo Servicios iniciados. Cierre las tres ventanas para detenerlos.
pause
