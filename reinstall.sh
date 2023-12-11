rm -rf code-workspace/
mkdir .ssl
ln -s /etc/letsencrypt/live/mc-mutuadeb.zonnox.net/* /var/www/html/code-workspace/.ssl/ 
mkdir .databases .logs
touch .databases/app.db .logs/app.log
service webapp restart
service webapp status