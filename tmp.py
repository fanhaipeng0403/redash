from flask import Flask, render_template

app = Flask(__name__, template_folder='./')


@app.route('/')
def foo():
    response = render_template("test.py")
    return response


if __name__ == '__main__':
    app.run(debug=True)
