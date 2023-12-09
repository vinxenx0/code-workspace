# run.py

from app import app

if __name__ == '__main__':
   #app.run(debug=True)
   # app.run(ssl_context='adhoc')
   app.run(ssl_context=('cert.pem', 'privkey.pem'), debug=True)


   # flask --app run run --host=0.0.0.0 --cert=adhoc --debug
