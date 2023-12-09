#!/bin/bash

# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
# https://certbot.eff.org/instructions

#self signed
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# 
#if __name__ == "__main__":
#    app.run(ssl_context=('cert.pem', 'key.pem'))
#

# flask run --cert=cert.pem --key=key.pem


# real ssl
apt-get install software-properties-common
add-apt-repository ppa:certbot/certbot
apt-get update
apt-get install certbot

sudo certbot certonly --webroot -w /var/www/html/code-workspace -d mc-mutuadeb.zonnox.net

