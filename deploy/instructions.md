1. apt update && apt upgrade -y
2. adduser bot
3. usermod -aG sudo bot
4. sudo apt install redis-server
5. sudo nano /etc/redis/redis.conf and set supervised to systemd
6. sudo systemctl restart redis.service
7. sudo systemctl status redis
8. git clone https://github.com/greatjudge/accounting-bot.git
9. cd accounting-bot
10. python3 -m venv env && source env/bin/activate && pip install -r requirements.txt
11. create /etc/systemd/system/accounting-bot.service
12. sudo systemctl enable passgenbot --now
