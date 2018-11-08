from flask import Flask, render_template, send_file, jsonify

###指定template目录
app = Flask(__name__, template_folder='./')



#####多个路由
@app.route('/xxx')
@app.route('/')
def foo():
    response = render_template("test.py")
    return response

@app.route('/zzz')
def foo1():
    ###直接渲染文件内容,或作为附件
    response = send_file("test.py")
    return response


@app.route('/yyy')
def foo2():
    # 几种方式
    # return jsonify(a=1)
    # return jsonify({'a':1})
    # return jsonify({'a':1},{'b':2})
    return jsonify(a=1,b=2)

if __name__ == '__main__':
    app.run(debug=True)
