/**
 * PM Tool v2 - PM2 配置文件
 * 
 * 使用方法：
 *   pm2 start ecosystem.config.js   # 启动所有服务
 *   pm2 stop all                    # 停止所有服务
 *   pm2 restart all                 # 重启所有服务
 *   pm2 logs                        # 查看日志
 *   pm2 status                      # 查看状态
 */

module.exports = {
  apps: [
    {
      name: 'pm-backend',
      cwd: 'C:/Users/WIN/Desktop/Cursor Project/pm-tool-v2/backend',
      script: 'C:/Users/WIN/AppData/Local/Python/bin/python.exe',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8001',
      interpreter: 'none',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 1000
    },
    {
      name: 'pm-frontend',
      cwd: 'C:/Users/WIN/Desktop/Cursor Project/pm-tool-v2/frontend',
      script: 'D:/Program Files/nodejs/npx.cmd',
      args: 'next dev --port 3001',
      interpreter: 'none',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 1000
    }
  ]
}
