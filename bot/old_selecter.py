# Старая выборка которая использовалась через чат бота


#"(?P<NewGropa>\d{4}-\d{4}\.\d)|(?P<OldGropa>\d{2} ? ?[а-яА-Я]{2,})|(?P<Kabinet>(\d ?\. ?\d{3})|(\d \d{3}))|(?P<Date>(0?[1-9]\.0?[1-9]\.20\d\d)|([1-3][1-9]\.1?[1-9]\.20\d\d))"gm


import sqlite3
from bot.botBack import usr_get_week, usr_get_settings, glb_commands 
import openpyxl as exel

#region функции форматирования вывода
def do_abr(stng):
    splt2 = stng.split(' - ')
    if len(splt2) > 1:
        if splt2[1] == '2 п/г':
            splt2[1] = '-2п/г'
        elif splt2[1] == '1 п/г':
            splt2[1] = '-1п/г'
        elif splt2[1] == '3 п/г':
            splt2[1] = '-3п/г'
        lst = splt2[0].split()
        oupt = ""
        for word in lst:
            if len(word) > 1:
                oupt += word [0]
        oupt = oupt.upper()
        oupt = oupt + splt2[1]
        return(oupt)    
    else:
        lst = splt2[0].split()
        oupt = ""
        for word in lst:
            if len(word) > 1:
                oupt += word [0]
        oupt = oupt.upper()
        return(oupt) 
def do_inc(prep):
    prep = prep[:-4]
    return(prep)
def do_grp(grp):
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    grp = grp.split(',')
    outp = ''
    for g in grp:
        cursor.execute(f"select old from groups where new = '{g}'")
        res = cursor.fetchone()
        if res:
            outp += f"{list(res)[0]} "
        else:
            outp += f"{g} "
    con.close()
    return outp
#endregion

def select(command,week):

    global glb_commands

    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()

    num,prep,kab,disc,grop,day,typ,dat,selec = '','','','','','','','',''


    for c in command.split():
        #Отбор преподавателя
        if c in [p[:-5] for p in glb_commands['preps']]:  
            if len(prep) != 0:
                prep += f" or prep like '{c} %' "
            else:
                prep += f" prep like '{c} %' "

        #Отбор кабинетов
        elif c in glb_commands['kabs']:
            if len(kab) != 0:
                kab += f" or kab = '{c}' "
            else:
                kab += f" kab = '{c}' "
        #Отбор групп
        elif c in glb_commands['groups']:
            if len(grop) != 0:
                grop += f" or grop like '%{c}%' "
            else:
                grop += f" grop like '%{c}%' "
        #Отбор типов
        elif typPip(c) in glb_commands['types']: 
            c = typPip(c)
            if len(typ) != 0:
                typ += f" or typ = '{c}' "
            else:
                typ += f" typ like '{c}' "
        #Отбор дат
        elif c in glb_commands['dates']:
            if len(dat) != 0:
                dat += f" or date = '{c}' "
            else:
                dat += f" date = '{c}' "
        #Отбор дней
        elif dayDoes(c,True) in glb_commands['days']:
            c = dayDoes(c)
            if len(day) != 0:
                day += f" or day = {c} "
            else:
                day += f" day = {c} "
        #Отбор номера пары
        elif numDum(c) in glb_commands['nums']:
            c = numDum(c)
            if len(num) != 0:
                num += f" or num = {c} "
            else:
                num += f" num = {c} "

    calls = [num,prep,kab,disc,grop,day,typ,dat]

    for c in calls:
        if c:
            if selec:
                selec += f" and ({c})"
            else:
                selec += f"({c})"

    print("выборка: ",selec)

    if selec:
        #                        0    1    2    3     4    5     6     7     8
        cursor.execute(f"select day, num, kab, prep, typ, disc, grop, date, week from ras where {selec} and week = {week} order by day,num")
    data = cursor.fetchall()
    print("Выбрано!")
    return data if data else None

def fixSelect(data, message, sep = False):
    if data == None:
        return('Ничего не выбрано')
    settings = usr_get_settings(message)
    pnd,ftr,srd,cht,ptn,sbt = '','','','','',''
    l = '-'*25 + '\n' if settings[3] else ''
    l2 = ''
    lastNum = None
    for d in data:
        d = list(d)

        if settings[0]:
            d[5] = do_abr(d[5])
        if settings[2]:
            d[3] = do_inc(d[3])
        if settings[1]:
            d[6] = do_grp(d[6])
        
        if not settings[4]:
            d[3] = ''
        if not settings[5]:
            d[4] = ''
        if not settings[6]:
            d[6] = ''
        if not settings[7]:
            d[7] = ''
        
        if d[0] == 1:
            if not pnd:
                pnd = f'\n<b>Понедельник</b> {d[7]}\n'
            pnd += f"{l if d[1] != lastNum else l2}<b>{d[1]}</b> | {d[2]} {d[3]} {d[5]} {d[4]} {d[6]}\n"
        elif d[0] == 2:
            if not ftr:
                ftr = f'\n<b>Вторник</b> {d[7]}\n'
            ftr += f"{l if d[1] != lastNum else l2}<b>{d[1]}</b> | {d[2]} {d[3]} {d[5]} {d[4]} {d[6]}\n"
        elif d[0] == 3:
            if not srd:
                srd = f'\n<b>Среда</b> {d[7]}\n'
            srd += f"{l if d[1] != lastNum else l2}<b>{d[1]}</b> | {d[2]} {d[3]} {d[5]} {d[4]} {d[6]}\n"
        elif d[0] == 4:
            if not cht:
                cht = f'\n<b>Четверг</b> {d[7]}\n'
            cht += f"{l if d[1] != lastNum else l2}<b>{d[1]}</b> | {d[2]} {d[3]} {d[5]} {d[4]} {d[6]}\n"
        elif d[0] == 5:
            if not ptn:
                ptn = f'\n<b>Пятница</b> {d[7]}\n'
            ptn += f"{l if d[1] != lastNum else l2}<b>{d[1]}</b> | {d[2]} {d[3]} {d[5]} {d[4]} {d[6]}\n"
        elif d[0] == 6:
            if not sbt:
                sbt = f'\n<b>Суббота</b> {d[7]}\n'
            sbt += f"{l if d[1] != lastNum else l2}<b>{d[1]}</b> | {d[2]} {d[3]} {d[5]} {d[4]} {d[6]}\n"
        lastNum = d[1]
    if sep:
        return(f"Неделя {d[8]}",pnd,ftr,srd,cht,ptn,sbt) if pnd or srd or ftr or cht or ptn or sbt else "Ничего не выбрано"
    else:
        return(f"Неделя {d[8]}"+pnd+ftr+srd+cht+ptn+sbt) if pnd or srd or ftr or cht or ptn or sbt else "Ничего не выбрано"
 

def excelSelect(data):
    wb = exel.Workbook()
    ws = wb.active
    for d in data:
        pass

#region ОтБорщики
def typPip(typ):
    if typ.upper() in ['ЭКЗ', 'ЭКЗАМЕН']:
        return('экзамен')
    if typ.upper() in ['ЗЧО']:
        return('зчО.')
    if typ.upper() in ['ЗАЧЕТ','ЗАЧЁТ','ЗАЧ']:
        return('зач.')
    if typ.upper() in ['ПРАКТИКА','ПР','П']:
        return('(пр.)')
    if typ.upper() in ['ЛЕКЦИЯ','ЛЕК','Л']:
        return('(л.)')
    if typ.upper() in ['ЛАБОРАТОНАЯ','ЛАБ','ЛАБОРАТОРКА']:
        return('(лаб.)')
def numDum(num):
    if num.upper() in ["ПЕРВАЯ","ПЕРВОЙ","1Я","1Й"]:
        return('1')
    if num.upper() in ["ВТОРАЯ","ВТОРОЙ","2Я","2Й"]:
        return('2')
    if num.upper() in ["ТРЕТЬЯ","ТРЕТЬЕЙ","3Я","3Й"]:
        return('3')
    if num.upper() in ["ЧЕТВЁРТАЯ","ЧЕТВЁРТОЙ","4Я","4Й"]:
        return('4')
    if num.upper() in ["ПЯТАЯ","ПЯТОЙ","5Я","5Й"]:
        return('5')
    if num.upper() in ["ШЕТАЯ","ШЕСТОЙ","6Я","6Й"]:
        return('6')
    if num.upper() in ["СЕДЬМАЯ","СЕДЬМОЙ","7Я","7Й"]:
        return('7')
    if num.upper() in ["ВОСЬМАЯ","ВОСЬМОЙ","8Я","8Й"]:
        return('8')
def dayDoes(day,chk=False):
    if day.upper() in ["ПНД","ПОНЕДЕЛЬНИК"]:
        return('pn') if chk else 1
    if day.upper() in ["ВТР","ВТОРНИК","ФТОРНИК"]:
        return('ft') if chk else 2
    if day.upper() in ["СРД","СРЕДА"]:
        return('sd') if chk else 3
    if day.upper() in ["ЧТВ","ЧЕТВЕРГ"]:
        return('ct') if chk else 4
    if day.upper() in ["ПТН","ПЯТНИЦА"]:
        return('pt') if chk else 5
    if day.upper() in ["СБТ","СУББОТА","СУБОТА"]:
        return('sb') if chk else 5
#endregion