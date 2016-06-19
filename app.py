from flask import request,Flask, jsonify, Response, send_from_directory
import logging

reachOp = 13
weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

events = ['Dr. T Tropical',
'Dr. T Volcano',
'War Factory',
'Dr. T Tropical',
'Dr. T Volcano',
'Hammerman']


drtdays = [0,1,3,4]


ops = ['Milk Run',
'Early Bird',
'Venus Flytrap',
'Full Monty',
'Pencilneck',
'Charleston',
'Ticker Tape',
'Tank Tango',
'Hacksaw',
'Upper Lip',
'Powder Keg',
'Mambo',
'Sour Grapes',
'Bottleneck',
'Tinderbox',
'Foxtrot',
'Stronghold',
'Choke Point',
'Curtain Call',
'Dead End',
'Deep Cut',
'Massive Attack']

originDate = 'June 17, 2016'
originEvent = 0

import pytz

from datetime import datetime
from datetime import timedelta


class Day:
  def __init__(self, date, event, op, boost):
    self.date = date  # datetime
    self.event = event  # int
    self.op = op  # int
    self.boost = boost  # bool
  def __str__(self):
    return '<tr><td>' + weekdays[self.date.weekday()] + ', ' + self.date.strftime('%B %d') + '  </td><td>  ' + ops[self.op] + '  </td><td>  ' + ('BOOST' if self.boost else 'no boost') + '  </td><td>  ' + events[self.event] + '</td></tr>'

  
def today(tz):
  return datetime.now(tz)
  
def dayEvent(day, startDate):
  td = day - startDate
  numDays = (int(td.total_seconds()) / 60 / 60 / 24)
  todaysEvent = (originEvent + numDays) % 6
  return todaysEvent
  
def whichOp(days, currentDate, event):
  weekday = currentDate.weekday()
  if weekday in [5,6]:
    return reachOp - 2
  if weekday in [4,0]:
    return reachOp -1
  if weekday in [1,2,3]:
    j = 0
    recentReachOp = False
    for i in range(len(days)-1,-1,-1):
      if j == 4:
        break
      if days[i].op == reachOp:
        recentReachOp = True
      j+=1
    if recentReachOp:
      return reachOp -1
    if event in drtdays:
      return reachOp
    return reachOp -1

def schedule(tz):
  scheduleLen = 7
  td = today(tz) - timedelta(days=2) #+ timedelta(days=5)
  startDate = tz.localize(datetime.strptime(originDate, '%B %d, %Y'), is_dst=None)
  sd = Day(startDate, dayEvent(startDate, startDate), 11, False)
  lastDate = td + timedelta(days=scheduleLen)
  currentDate = sd.date + timedelta(days=1)
  days = [sd]
  while currentDate <= lastDate:
    event = dayEvent(currentDate, startDate)
    op = whichOp(days, currentDate, event)
    days.append(Day(currentDate, event, op, op==reachOp))
    currentDate += timedelta(days=1)
  days = days[1-scheduleLen:]
  ans = '<br /><table style="width:100%;"><tr><th>Day</th><th>Suggested Op</th><th>Boost?</th><th>Event</th></tr>'
  for day in days:
    ans+= str(day)
  return ans+'</table>'
  
def startEnd(tz):
  eastern = pytz.timezone('US/Eastern')
  startTime = eastern.localize(datetime.strptime('June 10, 2016 6:00PM', '%B %d, %Y %I:%M%p'))
  endTime = eastern.localize(datetime.strptime('June 10, 2016 11:00PM', '%B %d, %Y %I:%M%p'))
  nowE = datetime.now(eastern)
  nowTZ = datetime.now(tz)
  td = (nowE.day - nowTZ.day)*24 + (nowE.hour - nowTZ.hour) + (nowE.minute - nowTZ.minute)/60.0
  start = startTime - timedelta(hours=td)
  end = endTime - timedelta(hours=td)
  return start.strftime('%I%p').replace('0',''), end.strftime('%I%p').replace('0','')


level = logging.INFO

class NoUtilsFilter(logging.Filter):
  def filter(self, record):
    return not 'utils.py' in record.filename

filt = NoUtilsFilter()
logging.basicConfig(filename='/home/www/flask_project/gunboatgenerals/logs/debug.log', level=level, datefmt='%a, %b %d %H:%M:%S', format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s:%(message)s')

for handler in logging.root.handlers:
  handler.addFilter(filt)



app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    if 'robdvorak.com' in request.url_root:
        f = open('/home/www/flask_project/static/index.html')
        return Response(f.read(), mimetype="text/html")
    f = open('/home/www/flask_project/gunboatgenerals/index.html')
    return Response(f.read(),mimetype="text/html")

@app.route('/_add_numbers')
def add_numbers():
    tzz = request.args.get('tzz', 'UTC', type=str)
    tz = pytz.timezone('UTC')
    try:
      tz = pytz.timezone(tzz.replace('"',''))
    except:
      pass
    start,end = startEnd(tz)
    message = '<br />Ops start between %s and %s (%s) every day as soon as intel allows. If we can\'t start by %s, we skip the day completely.<br />' % (start,end,tz, end)
    sch = schedule(tz)
    loggg = str(tz) +  message + str(sch)
    logging.info(loggg)
    print loggg
    return jsonify(result=sch + message)


@app.route('/generallinks')
def links():
    if 'robdvorak' in request.url_root:
        return None
    f = open('/home/www/flask_project/gunboatgenerals/index.html')
    return Response(f.read(),mimetype="text/html")


@app.route('/generalguidelines')
def guidelines():
    if 'robdvorak' in request.url_root:
        return None
    f = open('/home/www/flask_project/gunboatgenerals/index.html') 
    return Response(f.read(),mimetype="text/html")

@app.route('/gunboatgenerals/<path:filename>')
def send2(filename):
    return send_from_directory('/home/www/flask_project/gunboatgenerals', filename)

@app.route('/static/<path:filename>')
def send(filename):
    return send_from_directory('/home/www/flask_project/static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
