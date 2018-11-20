from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)


@app.route('/', methods=('GET', 'POST'))
def register():
    """To run this web application:
        1) Input the following into the command line in the directory with test.py
            a) for mac:
                i) "export FLASK_APP=hello.py"
                ii) "flask run"
            b) for windows on command prompt:
                i) C:\path\to\app>set FLASK_APP=test.py
            c) for windows on power shell
                i) PS C:\path\to\app> $env:FLASK_APP = "hello.py"
        2) Head over to the URL "http://127.0.0.1:5000/"

        Input something in the box and click "submit". The new screen rendered is the input
        (demonstrating use of request.form)."""
    if request.method == 'POST':
        input = request.form['input']
        return(input)
    else:
        return render_template('start.html')
