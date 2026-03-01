# Home Agent 项目启动脚本 (PowerShell)
# 同时启动前端和后端开发服务器，并在同一窗口显示日志

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "  Home Agent Development Environment"  -ForegroundColor Cyan
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# 获取脚本所在目录
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置后端和前端路径
$BACKEND_DIR = Join-Path $PROJECT_ROOT "Home-backend"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "Home-frontend"

# 启动后端服务
Write-Host "[1/4] Starting Backend (FastAPI)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    & $dir\.venv\Scripts\Activate.ps1
    uvicorn main:app --reload --host 0.0.0.0 --port 8002
} -ArgumentList $BACKEND_DIR

# 启动前端服务
Write-Host "[2/4] Starting Frontend (Vite)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    npm run dev
} -ArgumentList $FRONTEND_DIR

# 启动 Celery Worker
Write-Host "[3/4] Starting Celery Worker..." -ForegroundColor Green
$workerJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    & $dir\.venv\Scripts\Activate.ps1
    # Windows 下 Celery 建议使用 solo 进程池
    celery -A app.infrastructure.celery_app worker --loglevel=info --pool=solo
} -ArgumentList $BACKEND_DIR

# 启动 Celery Beat
Write-Host "[4/4] Starting Celery Beat..." -ForegroundColor Green
$beatJob = Start-Job -ScriptBlock {
    param($dir)
    cd $dir
    & $dir\.venv\Scripts\Activate.ps1
    celery -A app.infrastructure.celery_app beat --loglevel=info
} -ArgumentList $BACKEND_DIR

# 等待让服务启动
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "  All services started!"  -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:    http://localhost:8002" -ForegroundColor White
Write-Host "Frontend:   http://localhost:5173 (or port shown below)" -ForegroundColor White
Write-Host "API Docs:   http://localhost:8002/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# 监控任务输出
while ($backendJob.State -eq "Running" -or $frontendJob.State -eq "Running" -or $workerJob.State -eq "Running") {
    if ($frontendJob.HasMoreData) {
        Receive-Job -Job $frontendJob -OutVariable frontendOutput 2>$null | Out-Null
        foreach ($line in $frontendOutput) {
            Write-Host "[Frontend] $line" -ForegroundColor Cyan
        }
    }

    if ($backendJob.HasMoreData) {
        Receive-Job -Job $backendJob -OutVariable backendOutput 2>$null | Out-Null
        foreach ($line in $backendOutput) {
            Write-Host "[Backend] $line" -ForegroundColor Green
        }
    }

    if ($workerJob.HasMoreData) {
        Receive-Job -Job $workerJob -OutVariable workerOutput 2>$null | Out-Null
        foreach ($line in $workerOutput) {
            Write-Host "[Worker] $line" -ForegroundColor Yellow
        }
    }

    if ($beatJob.HasMoreData) {
        Receive-Job -Job $beatJob -OutVariable beatOutput 2>$null | Out-Null
        foreach ($line in $beatOutput) {
            Write-Host "[Beat] $line" -ForegroundColor White
        }
    }

    Start-Sleep -Milliseconds 100
}

# 清理
Stop-Job -Job $backendJob, $frontendJob, $workerJob, $beatJob -ErrorAction SilentlyContinue
Remove-Job -Job $backendJob, $frontendJob, $workerJob, $beatJob -ErrorAction SilentlyContinue
