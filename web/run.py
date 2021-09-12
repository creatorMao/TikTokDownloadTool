from flask import Flask,request
from flask import render_template
import os,json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from DBService import DBService
app=Flask(__name__)

@app.route('/')
def index(name=None):
    config=getConfig()
    print(config)
    return render_template('index.html',config=config)

@app.route('/saveConfig',methods=['POST'])
def saveConfig():
    config=json.loads(request.form["config"])
    filename = getConfigFileUrl()
    with open(filename,'w') as blog_file:
        blog_file.write(json.dumps(config))
    return "ok"

def getConfigFileUrl():
    return os.path.join(app.static_folder,  os.path.abspath(os.path.dirname(__file__))+'/config.json')

def getConfig():
    filename = getConfigFileUrl()
    with open(filename) as blog_file:
        data = json.load(blog_file)
    return data

@app.route('/downloadHistory/latest',methods=['GET'])
def getlLatestDownloadHistory():
    result=DBService().getlLatestDownloadHistory()

    return json.dumps({
        'state':'ok',
        'data':result
    })

if __name__=='__main__':
    app.run('0.0.0.0',8000,debug=False)