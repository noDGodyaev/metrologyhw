from flask import Flask
from flask import render_template, redirect
from flask import jsonify, request
from werkzeug.utils import secure_filename
import os
import count
import sys

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'UPLOAD_FOLDER')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt'}
input_list = ['name', 'split', 'f']


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index(name=None):
    return redirect('/file_upload')


@app.route('/file_upload', methods=["POST", "GET"])
def file_upload():
    error = True
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            input_list[0] = filename
            error = True
            return redirect('/number_upload')
    else:
        error = False
    return render_template('file_upload.html', error=error)


@app.route('/number_upload', methods=["POST", "GET"])
def number_upload():
    error = True
    if request.method == "POST":
        mystr = request.form.get('number')
        if len(mystr) == 1 and mystr.isdigit() and mystr > '3':
            input_list[1] = int(mystr)
            app.logger.info(input_list)
            error = True
            return redirect('/confidence_upload')
    else:
        error = False
    return render_template('number_upload.html', error=error)



@app.route('/confidence_upload', methods=["POST", "GET"])
def confidence_upload():
    error = True
    if request.method == "POST":
        mystr = request.form.get('number')
        if isfloat(mystr):
            input_list[2] = float(mystr)
            app.logger.info(input_list)
            return redirect('/result')
    else:
        error = False
    return render_template('confidence_upload.html', error=error)


Flag = True


@app.route('/result', methods=["POST", "GET"])
def result():
    resultans = count.calculate(str(input_list[0]), input_list[1], input_list[2])
    os.remove('UPLOAD_FOLDER/' + input_list[0])
    input_list.clear()
    return render_template('result.html', error=True,
                           S_between=resultans[1],
                           S_within=resultans[2],
                           Ft=resultans[3],
                           confidence=resultans[4],
                           Fq=resultans[5], )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
