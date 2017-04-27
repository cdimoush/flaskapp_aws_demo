'''
Simple Flask application to test deployment to Amazon Web Services
Uses Elastic Beanstalk and RDS

Author: Scott Rodkey - rodkeyscott@gmail.com

Step-by-step tutorial: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80
'''

from flask import Flask, render_template, request
from flask_ask import Ask, statement, question
from application import db
from application.models import Data
from application.forms import EnterDBInfo, RetrieveDBInfo
import requests

url = 'https://9f5181d321c07cc611924340bc167791f8e0e54000c82b5e97637fcea4dad6.resindevice.io'

# Elastic Beanstalk initalization
application = Flask(__name__)
ask = Ask(application, '/alexa')
application.debug=True
# change this to your own value
application.secret_key = 'cC1YCIWOj9GgWspgNEo2'   

@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    form1 = EnterDBInfo(request.form) 
    form2 = RetrieveDBInfo(request.form) 
    
    if request.method == 'POST' and form1.validate():
        data_entered = Data(notes=form1.dbNotes.data)
        try:     
            db.session.add(data_entered)
            db.session.commit()        
            db.session.close()
        except:
            db.session.rollback()
        return render_template('thanks.html', notes=form1.dbNotes.data)
        
    if request.method == 'POST' and form2.validate():
        try:   
            num_return = int(form2.numRetrieve.data)
            query_db = Data.query.order_by(Data.id.desc()).limit(num_return)
            for q in query_db:
                print(q.notes)
            db.session.close()
        except:
            db.session.rollback()
        return render_template('results.html', results=query_db, num_return=num_return)                
    
    return render_template('index.html', form1=form1, form2=form2)


@ask.launch
def new_ask():
    welcome = 'What would you like me to do?'
    return question(welcome)


@ask.intent('LightIntent')
def request_light(color):
    if not color:
        return question('I did no recieve a color, Try again')
    else:
        request_url = url + '/' + color  # color is passed to alexa and is a variable from interaction model
        requests.post(request_url)
        return statement('turning the lights ' + color)


@ask.intent('NoIntent')
def no_intent():
    stop_text = 'I am here if you need me'
    return statement(stop_text)


if __name__ == '__main__':
    application.run(host='0.0.0.0')
