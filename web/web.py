from flask import Flask, render_template, redirect, request
import datetime

from web_selecter import select
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot.botBack import glb_commands, weeks_get, get_week_dates, get_week_by_date

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():

  cur_week = get_week_by_date(datetime.datetime.now().strftime(r'%d.%m'))
  return render_template('index.html', commands=glb_commands, weeks=weeks_get(), cur_week=cur_week)

@app.route('/test', methods=['POST', 'GET'])
def test():
  return render_template('a.html')

@app.route('/admin1336', methods=['POST', 'GET'])
def admin():
  if request.method == 'POST':
    pass
  return render_template('admin.html')



@app.route('/select', methods=['POST', 'GET'])
def sel():
  if request.method == 'POST':
    week = request.form['week']
    values = request.form['valus']
    # out_type = request.form['output']    
    
    # weeks = get_week_dates(week)
    # data, y, gridType = select(values, week, out_type)

    return redirect(f'/select/{values}/{week}') #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return render_template('select.html', week=week, values=values.replace('+',', '), data=data, dates=weeks, grid=gridType, cols=y)
  
  else: return redirect('/')


@app.route('/select/<com>')
@app.route('/select/<com>/<int:week>', methods=['POST', 'GET'])
def users(com, week=get_week_by_date(datetime.datetime.now().strftime(r'%d.%m'))):
  
  values = com
    
  weeks = get_week_dates(week)
  data, y, gridType = select(values, week, 'auto')
  
  return render_template('select.html', week=week, values=values.replace('+',', '), data=data, dates=weeks, grid=gridType, cols=y)


if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0' ,port='80')