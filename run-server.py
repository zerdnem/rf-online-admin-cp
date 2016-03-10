from flask import Flask
from cp.views import cp

app = Flask(__name__)
app.register_blueprint(cp)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8666, debug=True)
