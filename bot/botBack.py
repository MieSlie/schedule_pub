import sqlite3
import datetime

#issue - сделать асинхронным (возможно)

glb_users = []
glb_cur_week = 0
glb_commands = {'nums' : ['1','2','3','4','5','6','7','8'],'days':['pn','ft','sd','ct','pt','sb'],'korpuses':['1й корпус', '2й корпус', '3й корпус', '4й корпус', '5й корпус', '6й корпус' , '7й корпус', '8й корпус', '9й корпус', '10й корпус', '11й корпус', '12й корпус', '13й корпус', '14й корпус', '15й корпус', '16й корпус', '17й корпус', '18й корпус'],'preps' :None, 'discs' : None, 'kabs' : None, 'groups' : None, 'types' : None, 'dates': None}
# команды может быть переместить в селектор


def vars_INIT():
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()

    global glb_users
    global glb_cur_week
    global glb_commands

    cursor.execute(f"select val from data where name = 'cWeekGlobal'")
    res = cursor.fetchone()
    glb_cur_week = int(list(res)[0])

    cursor.execute('select DISTINCT prep from ras')
    preps = [i[0] for i in cursor.fetchall()]
    cursor.execute('select DISTINCT disc from ras') 
    discs = [i[0] for i in cursor.fetchall()]
    cursor.execute('select DISTINCT kab from ras')
    kabs = [i[0] for i in cursor.fetchall()]
    cursor.execute('select DISTINCT grop from ras')
    grops = [i[0] for i in cursor.fetchall()]
    cursor.execute('select DISTINCT typ from ras')
    typs = [i[0] for i in cursor.fetchall()]
    cursor.execute('select DISTINCT date from ras')
    dats = [i[0] for i in cursor.fetchall()]
    glb_commands = {'nums' : ['1','2','3','4','5','6','7','8'],'days':['pn','ft','sd','ct','pt','sb'],'korpuses':['1й корпус', '2й корпус', '3й корпус', '4й корпус', '5й корпус', '6й корпус' , '7й корпус', '8й корпус', '9й корпус', '10й корпус', '11й корпус', '12й корпус', '13й корпус', '14й корпус', '15й корпус', '16й корпус', '17й корпус', '18й корпус'],'preps' :preps, 'discs' : discs, 'kabs' : kabs, 'groups' : grops, 'types' : typs, 'dates': dats}

    con.commit()
    con.close()
vars_INIT()



def user_INIT(message):
    global glb_users
    if message.chat.id in glb_users:
        return
    con_UI = sqlite3.connect('ras2.db')
    cursor = con_UI.cursor()
    cursor.execute(f"select chat_id from users where chat_id = {message.chat.id}")
    res = cursor.fetchone()
    if not res:
        cursor.execute(f"insert into users (chat_id, name, username, curWeek) values ({message.chat.id} ,'{f"{message.from_user.first_name} {message.from_user.last_name}"}', '{message.from_user.username}', {glb_cur_week})") 
    con_UI.commit()
    con_UI.close()
    glb_users.append(message.chat.id)

def register_cmd(message):
    command = message.text.replace(f"{message.text.split()[0]} ",'')
    con_RC = sqlite3.connect('ras2.db')
    cursor = con_RC.cursor()
    print(message.chat.id)
    cursor.execute(f"update users set reg = '{command}' where chat_id = {message.chat.id}")
    con_RC.commit()
    con_RC.close()
    return (f"Зарегистриривано: {command}")


def usr_chg_settings(message, chName):   # 0 - abr 1 - grp 2 - inc
    chat_id = message.chat.id
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute(f"select abr,grp,inc,line,sPrep,sType,sGrop,sDate from users where chat_id = {chat_id}")
    res = list(cursor.fetchone())
    
    if chName == 'abr':
        if res[0]:
            cursor.execute(f"update users set abr = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set abr = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"сокращение дисциплин: {'выключено' if res[0] else 'включено'}")
    if chName == 'grp':
        if res[1]:
            cursor.execute(f"update users set grp = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set grp = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"раскодировка груп: {'выключено' if res[1] else 'включено'}")
    if chName == 'inc':
        if res[2]:
            cursor.execute(f"update users set inc = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set inc = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"обрезка инициалов: {'выключено' if res[2] else 'включено'}")
    if chName == 'line':
        if res[3]:
            cursor.execute(f"update users set line = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set line = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"Линии между парами: {'выключено' if res[3] else 'включено'}")

    if chName == 'sPrp':
        if res[4]:
            cursor.execute(f"update users set sPrep = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set sPrep = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"Отображение преподавателя: {'выключено' if res[4] else 'включено'}")
    if chName == 'sTyp':
        if res[5]:
            cursor.execute(f"update users set sType = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set sType = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"Отображение типа занятия: {'выключено' if res[5] else 'включено'}")
    if chName == 'sGrp':
        if res[6]:
            cursor.execute(f"update users set sGrop = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set sGrop = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"Отображене группы: {'выключено' if res[6] else 'включено'}")
    if chName == 'sDat':
        if res[7]:
            cursor.execute(f"update users set sDate = 0 where chat_id = {chat_id}")
        else:
            cursor.execute(f"update users set sDate = 1 where chat_id = {chat_id}")
        con.commit()
        con.close()
        return(f"Отображение даты: {'выключено' if res[7] else 'включено'}")   
    
def usr_get_settings(message):
    chat_id = message.chat.id
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute(f"select abr,grp,inc,line,sPrep,sType,sGrop,sDate from users where chat_id = {chat_id}")
    res = cursor.fetchone()
    con.commit()
    con.close()
    return(list(res))


def usr_chg_week(message ,week):
    chat_id = message.chat.id
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute(f"update users set curWeek = {week} where chat_id = {chat_id}")
    con.commit()
    con.close()
    return(f"Неделя сменена на {week}")

def usr_get_week(message):
    chat_id = message.chat.id
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute(f"select curWeek from users where chat_id = {chat_id}")
    res = cursor.fetchone()
    con.commit()
    con.close()
    return(list(res)[0])


def weeks_get():
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute(f"select DISTINCT week from ras order by week")
    res = cursor.fetchall()
    con.close()
    weeks = list(res)
    return [week[0] for week in weeks]


def get_week_dates(week):
    con = sqlite3.connect('ras2.db')
    cur = con.cursor()
    cur.execute(f"select * from weekdates where week = {week}")
    dates = cur.fetchone()
    con.close()
    days_dates = {}
    days_dates['pnd'] = dates[2]
    days_dates['ftr'] = dates[3]
    days_dates['srd'] = dates[4]
    days_dates['cht'] = dates[5]
    days_dates['ptn'] = dates[6]
    days_dates['sbt'] = dates[7]
    return days_dates

def get_week_by_date(date):
    con = sqlite3.connect('ras2.db')
    cur = con.cursor()
    cur.execute(f"select week from weekdates where (pnd = '{date}') or (ftr = '{date}') or (srd = '{date}') or (cht = '{date}') or (ptn = '{date}') or (sbt = '{date}')")
    week = cur.fetchone()[0]
    con.close()
    return week

def get_cur_day_num():
    cur_time = datetime.datetime.now().strftime(r'%H:%M')
    now = datetime.datetime.now()
    
    num1_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num1_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num2_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num2_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num3_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num3_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num4_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num4_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num5_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num5_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num6_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num6_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num6_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num6_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

    num7_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    num7_end =   now.replace(hour=9, minute=20, second=0, microsecond=0)

def add_one(message):
    pass