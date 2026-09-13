import sqlite3
import os
import xlrd as exel
import re
import openpyxl

r_pg = r'(\ ?\-\ ?[1-4]\ ?п\/г)'

def day2num(day):
    if day == 'ПН':
        return 1
    if day == 'ВТ':
        return 2
    if day == 'СР':
        return 3
    if day == 'ЧТ':
        return 4
    if day == 'ПТ':
        return 5
    if day == 'СБ':
        return 6
    print('Проблема с днем')

def time2num(time):
    if time == '08.00-09.20':
        return [1]
    if time == '09.30-10.50':
        return [2]
    if time == '11.00-12.20':
        return [3]
    if time == '12.40-14.00':
        return [4]
    if time == '14.10-15.30':
        return [5]
    if time == '15.40-17.00':
        return [6]
    if time == '17.10-18.30':
        return [7]
    if time == '18.40-20.00':
        return [8]
    
    try:
        time_start, time_end = time.split('-')

        start_timez = {'08.00':1,'09.30':2,'11.00':3,'12.40':4,'14.10':5,'15.40':6,'17.10':7,'18.40':8}
        end_timez =   {'09.20':1,'10.50':2,'12.20':3,'14.00':4,'15.30':5,'17.00':6,'18.30':7,'20.00':8}

        outp = []
        for i in range(start_timez[time_start], end_timez[time_end]+1):
            outp.append(i)

        return outp
    except:
        print('time problem', time)






def get_ws_name(ws):
    return re.search(r'\d\d\d\d\-\d\d\d\d(\.\d)?', str(ws)).group()



def dbINIT_ZO():

    ras = os.listdir('ras2')

    maincon = sqlite3.connect('ras2.db')
    
    for r in ras:
        if r.split('.')[-1].lower() == 'xlsx':
            print('\n\n\n***NO XLSX***\n\n\n')
            continue

        cur_work_file = r
        book = exel.open_workbook(f"ras2\\{r}", formatting_info=True)
        print(r)
        for ws in book.sheets():

            if not re.search(r"\d\d\d\d\-\d\d\d\d(\.\d)?", str(ws)):
                if ws.cell_value(16-1,3-1) or ws.cell_value(17-1,3-1):
                    print(str(ws.cell_value(15-1,1-1)).lower())
                    print(r)
                    print(ws)
                    print('Error NO FIND GROUP BUT DATA')
                continue

            ras_start = None
            for i_row in range(0,ws.nrows):
                if str(ws.cell_value(i_row,1-1)).lower().strip() == 'дата':
                    ras_start = i_row
                    break
            if not ras_start:
                print(r)
                print(ws)
                print('Error NON FIND DATE CELL')
                continue
            
            grp, day, time, disc, prep, kab = None,None,None,None,None,None

            for i_row in range(ras_start+1,ws.nrows-1, 2):
                if ws.cell_value(i_row, 3-1):
                    if ws.cell_value(i_row, 1-1):
                        daykey = ws.cell_value(i_row, 1-1)
                    grp = get_ws_name(ws)
                    day = daykey
                    time = ws.cell_value(i_row, 2-1)
                    disc = ws.cell_value(i_row, 3-1)
                    prep = ws.cell_value(i_row+1, 3-1)
                    kab  = ws.cell_value(i_row, 4-1)

                    dbin_grp, dbin_day, dbin_date, dbin_num, dbin_type, dbin_prep, dbin_kab, dbin_disc, dbin_num2, dbin_prep2, dbin_kab2, dbin_disc2, dbin_type2, dbin_pg, dbin_pg2 = None,None,None,None,None,None,None,None,None,None,None,None,None,None,None
                        
                    try:
                        mch = re.search(r'\d?\d\.\d\d', rf"{day}")
                        dbin_day = day2num(rf"{day}".replace('\n','').replace(mch.group(),'').strip())
                        dbin_date = mch.group()
                        curfordate = maincon.cursor()
                        curfordate.execute(f"select week from weekdates where (pnd = '{dbin_date}') or (ftr = '{dbin_date}') or (srd = '{dbin_date}') or (cht = '{dbin_date}') or (ptn = '{dbin_date}') or (sbt = '{dbin_date}')")
                        week = curfordate.fetchone()[0]
                    except:
                        print('\nDAY CUT PROBLEM ', day, grp)
                    
                    

                    if len(rf"{prep}".split('\n')) > 1:
                        dbin_prep = rf"{prep}".split('\n')[0]
                        dbin_prep2 = rf"{prep}".split('\n')[1]
                    else:
                        dbin_prep = prep
                    if len(rf"{kab}".split('\n')) > 1:
                        dbin_kab = rf"{kab}".split('\n')[0]
                        dbin_kab2 = rf"{kab}".split('\n')[1]
                    else:
                        dbin_kab = kab
                    if len(rf"{disc}".split('\n')) > 1:
                        dbin_disc = rf"{disc}".split('\n')[0]
                        srch = re.search(r"(экзамен)|(л\.)|(пр\.)|(лаб\.)|(зач\.)|(зчО\.)",dbin_disc)
                        dbin_type = srch.group() if srch else None
                        dbin_disc = dbin_disc.replace(srch.group(), '') if srch else dbin_disc
                        dbin_disc2 = rf"{disc}".split('\n')[1]
                        srch2 = re.search(r"(экзамен)|(л\.)|(пр\.)|(лаб\.)|(зач\.)|(зчО\.)",dbin_disc2)
                        dbin_type2 = srch2.group() if srch2 else None
                        dbin_disc2 = dbin_disc2.replace(srch.group(), '') if srch2 else dbin_disc2
                    else:
                        dbin_disc = disc
                        srch = re.search(r"(экзамен)|(л\.)|(пр\.)|(лаб\.)|(зач\.)|(зчО\.)",dbin_disc)
                        dbin_type = srch.group() if srch else None
                        dbin_disc = dbin_disc.replace(srch.group(), '') if srch else dbin_disc

                    
                    dbin_grp = grp

                    if not dbin_type:
                        dbin_type = 'н.т.'
                    if not dbin_prep:
                        dbin_prep = 'Не указан'

                    if dbin_disc2:
                        mch = re.search(r_pg, dbin_disc2)
                        if mch: 
                            mch_ok = mch.group()
                            dbin_disc2 = dbin_disc2.replace(mch_ok,'')
                            dbin_pg2 = mch_ok.replace('-', '').strip()

                    mch = re.search(r_pg, dbin_disc)
                    if mch: 
                        mch_ok = mch.group()
                        dbin_disc = dbin_disc.replace(mch_ok,'')
                        dbin_pg = mch_ok.replace('-', '').strip()

                    if dbin_disc: dbin_disc = dbin_disc.strip()
                    if dbin_disc2: dbin_disc2 = dbin_disc2.strip()

                    cursor = maincon.cursor()

                    for i_num in time2num(time):
                        dbin_num = i_num

                        if not dbin_grp or not dbin_day or not dbin_date or not dbin_num or not dbin_kab or not dbin_disc:
                            print(f"Проблема\n{week}, {dbin_day}, {dbin_num}, '{dbin_prep}', '{dbin_kab}', '{dbin_disc}', '{dbin_grp}', '{dbin_type}', '{dbin_date}' \n\n")
                            continue

                        cursor.execute(f"select * from ras where week = {week} and day = {dbin_day} and num = {dbin_num} and prep = '{dbin_prep}' and kab = '{dbin_kab}' and disc = '{dbin_disc}' and grop = '{dbin_grp}' and typ = '{dbin_type}' and date = '{dbin_date}'")
                        ex_chk = cursor.fetchone()
                        if not ex_chk:
                            cursor.execute(f"INSERT INTO ras (week, day, num, prep, kab, disc, grop, typ, date, pg) VALUES ({week}, {dbin_day}, {dbin_num}, '{dbin_prep}', '{dbin_kab}', '{dbin_disc}', '{dbin_grp}', '{dbin_type}', '{dbin_date}', '{dbin_pg}')")

                        if (dbin_prep2 and dbin_prep2 != dbin_prep) or (dbin_kab2 and dbin_kab2 != dbin_kab) or dbin_disc2 or dbin_type2:
                            dbin_kab = dbin_kab2 if dbin_kab2 else dbin_kab
                            dbin_prep = dbin_prep2 if dbin_prep2 else dbin_prep
                            dbin_disc = dbin_disc2 if dbin_disc2 else dbin_disc
                            dbin_type = dbin_type2 if dbin_type2 else dbin_type
                            dbin_pg = dbin_pg2 if dbin_pg2 else None
                            cursor.execute(f"select * from ras where week = {week} and day = {dbin_day} and num = {dbin_num} and prep = '{dbin_prep}' and kab = '{dbin_kab}' and disc = '{dbin_disc}' and grop = '{dbin_grp}' and typ = '{dbin_type}' and date = '{dbin_date}'")
                            ex_chk2 = cursor.fetchone()
                            if not ex_chk2:
                                cursor.execute(f"INSERT INTO ras (week, day, num, prep, kab, disc, grop, typ, date, pg) VALUES ({week}, {dbin_day}, {dbin_num}, '{dbin_prep}', '{dbin_kab}', '{dbin_disc}', '{dbin_grp}', '{dbin_type}', '{dbin_date}', '{dbin_pg}')")
    maincon.commit()
    maincon.close()
    rmExelOZFO()


def rmExelOZFO():
    for r in os.listdir('ras2'):
        os.remove('ras2/'+r)