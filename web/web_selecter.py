import sqlite3

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bot.botBack import glb_commands


def select(com:str, week, outp_type):

    global glb_commands

    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()

    num,prep,kab,disc,grop,day,typ,dat,korpus,selec = '','','','','','','','','',''
    nums,preps,kabs,discs,grops,days,typs,dats,korpuses = [],[],[],[],[],[],[],[],[]

    for c in com.split('+'):
        #Отбор преподавателя
        if c in glb_commands['preps']:
            preps.append(c)
            if len(prep) != 0:
                prep += f" or prep = '{c}' "
            else:
                prep += f" prep = '{c}' "
        #Отбор кабинетов
        elif c in glb_commands['kabs']:
            kabs.append(c)
            if len(kab) != 0:
                kab += f" or kab = '{c}' "
            else:
                kab += f" kab = '{c}' "
        #Отбор групп
        elif c in glb_commands['groups']:
            grops.append(c)
            if len(grop) != 0:
                grop += f" or grop = '{c}' "
            else:
                grop += f" grop = '{c}' "
        #Отбор типов
        elif c in glb_commands['types']:
            typs.append(c)
            if len(typ) != 0:
                typ += f" or typ = '{c}' "
            else:
                typ += f" typ = '{c}' "
        #Отбор дат
        elif c in glb_commands['dates']:
            dats.append(c)
            if len(dat) != 0:
                dat += f" or date = '{c}' "
            else:
                dat += f" date = '{c}' "
        #Отбор дней
        elif c in glb_commands['days']:
            days.append(c)
            if len(day) != 0:
                day += f" or day = {c} "
            else:
                day += f" day = {c} "
        #Отбор номера пары
        elif c in glb_commands['nums']:
            nums.append(c)
            if len(num) != 0:
                num += f" or num = {c} "
            else:
                num += f" num = {c} "
        elif c in glb_commands['discs']:
            discs.append(c)
            if len(num) != 0:
                num += f" or disc = '{c}' "
            else:
                num += f" disc = '{c}' "

        #strange shtuki
        elif c in glb_commands['korpuses']:
            korpuses.append(c)
            c = c.replace('й корпус', '')
            if len(num) != 0:
                korpus += f" or kab like '{c}.%' "
            else:
                korpus += f" kab like '{c}.%' "

    calls = [num,prep,kab,disc,grop,day,typ,dat,korpus]

    for c in calls:
        if c:
            if selec:
                selec += f" and ({c})"
            else:
                selec += f"({c})"

    print("выборка: ",selec, week)

    if selec:
        #                        0    1    2    3     4    5     6     7     8    9
        cursor.execute(f"select day, num, kab, prep, typ, disc, grop, date, week, pg from ras where {selec} and week = {week} order by day,num")
    data = cursor.fetchall()
    
    if not data:
        return None,None,None

    # region ЭТАП 2 ФОРМАТ ВЫВОДА


    if outp_type == 'auto':
      if len(preps)>1 or len(kabs)>1 or len(grops)>1: #длинна запроса
        if len(preps) > len(kabs) and len(preps) > len(grops): 
          gridType = 'prep'
          GL = len(preps)
          y = preps
        elif len(kabs) > len(preps) and len(kabs) > len(grops): 
          gridType = 'kab'
          GL = len(kabs)
          y = kabs
        elif len(grops) > len(kabs) and len(grops) > len(preps): 
          gridType = 'grp'
          GL = len(grops)
          y = grops
      else:
        gridType = 'stndrt'
        y=None
    
    elif outp_type == 'stndrt': 
        gridType = 'stndrt'
        y=None
    elif outp_type == 'prepods':  
        gridType = 'prep'
        GL = len(preps)
        y = preps
    elif outp_type == 'auditoris':
        gridType = 'kab'
        GL = len(kabs)
        y = kabs
    elif outp_type == 'grupos':   
        gridType = 'grp'
        GL = len(grops)
        y = grops

    
    if gridType == 'stndrt':

        outp = [[[],[],[],[],[],[]],
                [[],[],[],[],[],[]],
                [[],[],[],[],[],[]],
                [[],[],[],[],[],[]],
                [[],[],[],[],[],[]],
                [[],[],[],[],[],[]],
                [[],[],[],[],[],[]],
                [[],[],[],[],[],[]]]

        for d in data:

            append_output = True
            if outp[int(d[1])-1][int(d[0])-1]:
                for i in range(0, len(outp[int(d[1])-1][int(d[0])-1])):
                    pos = outp[int(d[1])-1][int(d[0])-1][i]
                    if pos['kab'] == d[2] and pos['prep'] == d[3] and pos['disc'] == d[5]:
                        outp[int(d[1])-1][int(d[0])-1][i]['grop'].append(d[6])
                        append_output = False

            if append_output: outp[int(d[1])-1][int(d[0])-1].append({'day':d[0], 'num':d[1], 'kab':d[2], 'prep':d[3], 'type':d[4], 'disc':d[5], 'grop':[d[6]], 'date':d[7], 'week':d[8], 'pg':d[9]})
        
    else:
        outp = [[[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL],
                [[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL],
                [[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL],
                [[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL],
                [[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL],
                [[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL,[None]*GL]]
        
        for d in data:
            if   gridType == 'grp': inx = d[6]
            elif gridType == 'kab': inx = d[2]
            elif gridType == 'prep':inx = d[3]
            if outp[int(d[0])-1][int(d[1])-1][y.index(inx)] == None: outp[int(d[0])-1][int(d[1])-1][y.index(inx)] = []

            append_output = True
            if outp[int(d[0])-1][int(d[1])-1][y.index(inx)]:
                for i in range(0, len(outp[int(d[0])-1][int(d[1])-1][y.index(inx)])):
                    pos = outp[int(d[0])-1][int(d[1])-1][y.index(inx)][i]
                    if pos['kab'] == d[2] and pos['prep'] == d[3] and pos['disc'] == d[5]:
                        outp[int(d[0])-1][int(d[1])-1][y.index(inx)][i]['grop'].append(d[6])
                        append_output = False
            
            if append_output: outp[int(d[0])-1][int(d[1])-1][y.index(inx)].append({'day':d[0], 'num':d[1], 'kab':d[2], 'prep':d[3], 'type':d[4], 'disc':d[5], 'grop':[d[6]], 'date':d[7], 'week':d[8], 'pg':d[9]})

    return outp,y,gridType
    #endregion