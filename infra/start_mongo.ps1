param([string]$MongoExecutable = '.local/tools/mongodb/mongodb-win32-x86_64-windows-8.0.28/bin/mongod.exe')
$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$executable = (Resolve-Path -LiteralPath (Join-Path $workspace $MongoExecutable)).Path
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 27018)
try { $listener.Start() } catch { throw 'Port 27018 is occupied; refusing to start or replace an existing database.' }
finally { $listener.Stop() }
$dbPath = Join-Path $workspace '.local/mongo-demo-data'
New-Item -ItemType Directory -Force -Path $dbPath | Out-Null
$logPath = Join-Path $workspace '.local/mongo-demo.log'
$process = Start-Process -FilePath $executable -ArgumentList @('--dbpath', ('"' + $dbPath + '"'), '--bind_ip', '127.0.0.1', '--port', '27018', '--replSet', 'rs0', '--logpath', ('"' + $logPath + '"'), '--logappend') -WindowStyle Hidden -PassThru
$process.Id | Set-Content -LiteralPath (Join-Path $workspace '.local/mongo-demo.pid')
Write-Output "Started local MongoDB PID $($process.Id), bound only to 127.0.0.1:27018. Run infra/init_replica.py next."
