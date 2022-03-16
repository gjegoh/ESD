from asyncio import run_coroutine_threadsafe
import pymysql.cursors
import datetime
from flask import Flask, render_template, request, template_rendered
from sqlalchemy import DateTime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            if request.method == 'POST':
                submitted = request.form
                chosenSubjects = submitted.getlist('subjects[]')
                chosenGrades = submitted.getlist('grades[]')
                chosenDays = submitted.getlist('days[]')
                chosenTimings = submitted.getlist('timings[]')
                chosenYears = submitted.getlist('years[]')
                sql = "USE classDB"
                cursor.execute(sql)
                connection.commit()
                classIDList = []
                for subject in chosenSubjects:
                    for grade in chosenGrades:
                        sql = "SELECT classID FROM Class WHERE subject='{subject}' and grade='{grade}'".format(subject=subject, grade=grade)
                        cursor.execute(sql)
                        result = cursor.fetchall()
                        classIDList.append(result[0]['classID'])
                sql = "USE classScheduleDB"
                cursor.execute(sql)
                connection.commit()
                for classID in classIDList:
                    for year in chosenYears:
                        for day in chosenDays:
                            for timing in chosenTimings:
                                sql = "INSERT INTO classSchedule (classID, year, day, timing) VALUES ({classID}, {year}, {day}, {timing})".format(classID=classID, year=year, day=day, timing=timing)
                                cursor.execute(sql)
                                connection.commit()
                return "Success!"
            sql = "USE classDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT DISTINCT subject FROM Class"
            cursor.execute(sql)
            result = cursor.fetchall()
            subjectList = [i['subject'] for i in result]
            sql = "SELECT DISTINCT grade FROM Class"
            cursor.execute(sql)
            result = cursor.fetchall()
            gradeList = [i['grade'] for i in result]
            currentYear = int(datetime.datetime.now().date().strftime("%Y"))
            yearList = [currentYear, currentYear+1, currentYear+2]
            return render_template('adminCreateSchedules.html', subjectList=subjectList, gradeList=gradeList, yearList=yearList)

@app.route('/schedule')
def schedule():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    scheduleList = []
    with connection:
        with connection.cursor() as cursor:
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * FROM classSchedule"
            status = cursor.execute(sql)
            if status > 0:
                scheduleList = cursor.fetchall()
        return render_template('adminViewSchedules.html', scheduleList=scheduleList)

if __name__ == '__main__':
    app.run(debug=True)