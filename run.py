# run.py

from app import app

if __name__ == '__main__':
   #app.run(debug=True)
   # app.run(ssl_context='adhoc')
   app.run(ssl_context=('.ssl/cert.pem', '.ssl/privkey.pem'), debug=True)
