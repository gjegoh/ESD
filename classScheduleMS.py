import pymysql.cursors
import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            status = 0
            subjects = ''
            grades = ''
            years = ''
            days = ''
            timings = ''
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
                                sql = "INSERT INTO classSchedule (classID, year, day, timing) VALUES ({classID}, {year}, '{day}', {timing})".format(classID=classID, year=year, day=day, timing=timing)
                                cursor.execute(sql)
                                connection.commit()
                subjects = ", ".join(chosenSubjects)
                grades = ", ".join(chosenGrades)
                years = ", ".join(chosenYears)
                days = ", ".join(chosenDays)
                timings = ", ".join(chosenTimings)
                status = 1
                # return 'Successfully created class schedules for: \n subjects: {subjects} \n grades: {grades} \n years: {years} \n days: {days} \n timings: {timings}'.format(subjects=", ".join(chosenSubjects), grades=", ".join(chosenGrades), years=", ".join(chosenYears), days=", ".join(chosenDays), timings=", ".join(chosenTimings))
                # return redirect(url_for('.index'))
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
            return render_template('adminCreateSchedules.html', subjectList=subjectList, gradeList=gradeList, yearList=yearList, status=status, subjects=subjects, grades=grades, years=years, days=days, timings=timings)

@app.route('/schedule')
def schedule():
    connection = pymysql.connect(host='studentdb2.cw0jtpvjeb4t.us-east-1.rds.amazonaws.com',
                            user='admin',
                            password='thisismypw',
                            cursorclass=pymysql.cursors.DictCursor)
    scheduleList = []
    classDict = {}
    with connection:
        with connection.cursor() as cursor:
            sql = "USE classScheduleDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT * FROM classSchedule"
            cursor.execute(sql)
            scheduleList = cursor.fetchall()
            sql = "USE classDB"
            cursor.execute(sql)
            connection.commit()
            sql = "SELECT classID, subject, grade FROM Class"
            cursor.execute(sql)
            result = cursor.fetchall()
            for details in result:
                classDict[details['classID']] = [details['subject'], details['grade']]
        return render_template('adminViewSchedules.html', scheduleList=scheduleList, classDict=classDict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)