from openpyxl.utils.cell import get_column_letter
import xlrd as exel
import re
import excel2img
import sqlite3
import os
from datetime import datetime, timedelta
from bot.botBack import weeks_get, vars_INIT, get_week_dates
import json

wDir = os.getcwd()
rasDir = wDir + '\\ras'

cur_work_file = None
do_logs = True

#old
# r'([а-яА-ЯёЁ]+ [а-яА-ЯёЁ]\.[а-яА-ЯёЁ]\.?)|([а-яА-ЯёЁ]+\-[а-яА-ЯёЁ]+ [а-яА-ЯёЁ]\.[а-яА-ЯёЁ]\.?)|([а-яА-ЯёЁ]+\_\d+ \([а-яА-ЯёЁ]+\.\d+\))' 

#И ?
# Вакансия [каф.2]
# Вакансия                                                убрал тут маленькие буквы на инициалы
#         # Обычный адекватный преп (почти)   #    преп через дефиз                                    #  Вакансия_(каф.12)                    # И ?  #  И?.  #   Вакансия [каф.12]             # Вакансия
r_prep = r'([а-яА-ЯёЁ]+\d? ?[А-ЯЁ]\.[А-ЯЁ]\.?)|([а-яА-ЯёЁ]+\-[а-яА-ЯёЁ]+\d? ?[А-ЯЁ]\.[А-ЯЁ]\.?)|([а-яА-ЯёЁ]+\_\d+ \([а-яА-ЯёЁ]+\.\d+\))|(И \?)|(И\?\.)|([а-яА-ЯёЁ]+ \[[а-яА-ЯёЁ]+\.\d+\])|(Вакансия)'
r_type = r'\([а-яА-Я]{1,4}\.\)'
r_pg = r'(\ ?\-\ ?[1-4]\ ?п\/г)'

# region для groups_standart_cut
def standart_cut_days():
    return {'pn':[2,3], 'ft':[4,5], 'sr':[6,7], 'ct':[8,9], 'pt':[10,11], 'sb':[12,13]}
def standart_cut_nums(bS):
    return {'1':[bS+2,bS+7], '2':[bS+8,bS+13], '3':[bS+14,bS+19], '4':[bS+20,bS+25], '5':[bS+26,bS+31], '6':[bS+32,bS+37], '7':[bS+38,bS+43], '8':[bS+44,bS+49]}
#endregion

# для get_groups_cut
def groups_standart_cut(groups_borders):
    groups_cut = {}
    days_cut = standart_cut_days()
    for group, border in groups_borders.items():
        num_cut = standart_cut_nums(border[0])
        groups_cut[group] = { 'pnd':{'1':{'row':num_cut['1'], 'col':days_cut['pn']}, '2':{'row':num_cut['2'], 'col':days_cut['pn']}, '3':{'row':num_cut['3'], 'col':days_cut['pn']}, '4':{'row':num_cut['4'], 'col':days_cut['pn']}, '5':{'row':num_cut['5'], 'col':days_cut['pn']}, '6':{'row':num_cut['6'], 'col':days_cut['pn']}, '7':{'row':num_cut['7'], 'col':days_cut['pn']}, '8':{'row':num_cut['8'], 'col':days_cut['pn']}},
                              'ftr':{'1':{'row':num_cut['1'], 'col':days_cut['ft']}, '2':{'row':num_cut['2'], 'col':days_cut['ft']}, '3':{'row':num_cut['3'], 'col':days_cut['ft']}, '4':{'row':num_cut['4'], 'col':days_cut['ft']}, '5':{'row':num_cut['5'], 'col':days_cut['ft']}, '6':{'row':num_cut['6'], 'col':days_cut['ft']}, '7':{'row':num_cut['7'], 'col':days_cut['ft']}, '8':{'row':num_cut['8'], 'col':days_cut['ft']}},
                              'srd':{'1':{'row':num_cut['1'], 'col':days_cut['sr']}, '2':{'row':num_cut['2'], 'col':days_cut['sr']}, '3':{'row':num_cut['3'], 'col':days_cut['sr']}, '4':{'row':num_cut['4'], 'col':days_cut['sr']}, '5':{'row':num_cut['5'], 'col':days_cut['sr']}, '6':{'row':num_cut['6'], 'col':days_cut['sr']}, '7':{'row':num_cut['7'], 'col':days_cut['sr']}, '8':{'row':num_cut['8'], 'col':days_cut['sr']}},
                              'cht':{'1':{'row':num_cut['1'], 'col':days_cut['ct']}, '2':{'row':num_cut['2'], 'col':days_cut['ct']}, '3':{'row':num_cut['3'], 'col':days_cut['ct']}, '4':{'row':num_cut['4'], 'col':days_cut['ct']}, '5':{'row':num_cut['5'], 'col':days_cut['ct']}, '6':{'row':num_cut['6'], 'col':days_cut['ct']}, '7':{'row':num_cut['7'], 'col':days_cut['ct']}, '8':{'row':num_cut['8'], 'col':days_cut['ct']}}, 
                              'ptn':{'1':{'row':num_cut['1'], 'col':days_cut['pt']}, '2':{'row':num_cut['2'], 'col':days_cut['pt']}, '3':{'row':num_cut['3'], 'col':days_cut['pt']}, '4':{'row':num_cut['4'], 'col':days_cut['pt']}, '5':{'row':num_cut['5'], 'col':days_cut['pt']}, '6':{'row':num_cut['6'], 'col':days_cut['pt']}, '7':{'row':num_cut['7'], 'col':days_cut['pt']}, '8':{'row':num_cut['8'], 'col':days_cut['pt']}}, 
                              'sbt':{'1':{'row':num_cut['1'], 'col':days_cut['sb']}, '2':{'row':num_cut['2'], 'col':days_cut['sb']}, '3':{'row':num_cut['3'], 'col':days_cut['sb']}, '4':{'row':num_cut['4'], 'col':days_cut['sb']}, '5':{'row':num_cut['5'], 'col':days_cut['sb']}, '6':{'row':num_cut['6'], 'col':days_cut['sb']}, '7':{'row':num_cut['7'], 'col':days_cut['sb']}, '8':{'row':num_cut['8'], 'col':days_cut['sb']}}}
    return groups_cut

# делает список с нарезкой групп
def get_groups_cut(ws):
    groups_borders = {}
    last_grp = None
    for row in range(0,ws.nrows):
        mch = re.search(r'\d{4}-\d{4}\.\d', rf"{ws.cell_value(row,0)}")
        if mch:
            if last_grp : last_grp[1] = row-2
            groups_borders[mch.group()] = [row+1,0]
            last_grp = groups_borders[mch.group()]
    if last_grp : last_grp[1] = ws.nrows - 8

    return groups_standart_cut(groups_borders)

 
def day2num(day):
    if day == 'pnd':
        return 1
    if day == 'ftr':
        return 2
    if day == 'srd':
        return 3
    if day == 'cht':
        return 4
    if day == 'ptn':
        return 5
    if day == 'sbt':
        return 6


def get_img(grp, day, num, ws, name):
    groups_cut = get_groups_cut(ws)
    rS = groups_cut[grp][day][num]['row'][0]+1
    rE = groups_cut[grp][day][num]['row'][1]+1
    cS = get_column_letter(groups_cut[grp][day][num]['col'][0]+1)
    cE = get_column_letter(groups_cut[grp][day][num]['col'][1]+1)
    try:
        excel2img.export_img(f"ras/{cur_work_file}",f"logs/{name}.png", _range=f"{cS}{rS}:{cE}{rE}")
    except:
        print(f"ig problem {name}")

def get_values(grp, day, num, ws):
    groups_cut = get_groups_cut(ws)
    rowS = groups_cut[grp][day][num]['row'][0]
    rowE = groups_cut[grp][day][num]['row'][1]
    colS = groups_cut[grp][day][num]['col'][0]
    colE = groups_cut[grp][day][num]['col'][1]
    for row in range(rowS, rowE+1):
        for col in range(colS, colE+1):
            print(f"{get_column_letter(col+1)}{row+1} - {ws.cell_value(row, col)}")


last_problem = None

# получить значения(список) 1 пары по группе дню и номеру
def get_one(grp, day, num, borders, ws):
    rowS = borders['row'][0]
    rowE = borders['row'][1]
    colS = borders['col'][0]
    colE = borders['col'][1]

    num_out = num
    day_out = day
    grp_out = grp
    aud_out = None
    aud2_out = None
    prep_out = None
    prep2_out = None
    typ_out = None
    typ2_out = None
    disc_out = None
    pg_out = None
    disc2_out = None
    pg2_out = None
    date_out = None

    if do_logs : logs = open('logs/logs.txt', 'a', encoding='utf-8')

    #region СЧИТАЕМ ЧТО ПО СКОЛЬКО
    aud_count = 0
    typ_count = 0
    prep_count = 0
    for row in range(rowS, rowE+1):
        if ws.cell_value(row, colE):
            aud_count += 1
        if re.search(r_type, rf"{ws.cell_value(row,colS)}"):
            typs = [m.group() for m in re.finditer(r_type, ws.cell_value(row,colS))]
            typ_count += len(typs)
        if re.search(r_prep, rf"{ws.cell_value(row,colS)}"):
            preps = [m.group() for m in re.finditer(r_prep, ws.cell_value(row,colS))]
            prep_count += len(preps)
    #endregion

    #region 3 штуки не поддерживаем (бе-бе-бе)
    if prep_count >= 3:
        if do_logs : logs.write(f"3 PREPODA {grp} {day} {num}\n")
    if aud_count >= 3:
        if do_logs : logs.write(f"3 aud {grp} {day} {num}\n")
    if typ_count >= 3:
        if do_logs : logs.write(f"3 typa {grp} {day} {num}\n")
    #endregion


    #region ВСЁ ПО 1 - СТАНДАРТНАЯ ПАРА
    if aud_count == 1 and typ_count == 1 and prep_count == 1:# ТУТ НУЖНО ПОФИКСИТЬ ВЫБОР ДИСЦИПЛИНЫ

        if ws.cell_value(rowS+1, colS): #?????????
            disc_out = ws.cell_value(rowS+1, colS)
            if disc_out:
                mch = re.search(r_pg, disc_out)
                if mch: 
                    mch_ok = mch.group()
                    disc_out = disc_out.replace(mch_ok,'')
                    pg_out = mch_ok.replace('-', '').strip()

        for row in range(rowS, rowE+1):
            if ws.cell_value(row, colE):
                aud_out = ws.cell_value(row, colE)
            
            mch_prep = re.search(r_prep, rf"{ws.cell_value(row,colS)}")
            if mch_prep:
                prep_out = mch_prep.group()

            mch_typ = re.search(r_type, rf"{ws.cell_value(row,colS)}")
            if mch_typ:
                typ_out = mch_typ.group()
    #endregion


    #region ОШИБУНЬКИ УЧ ОТДЕЛА
    elif aud_count == 2 and typ_count == 1 and prep_count == 1:
        if do_logs : logs.write(f"\n\nPROBLEMA AUD 2 OSTALNOE PO 1!!!!!!!!!\ngrp={grp} day={day} num={num}\n\n")
    elif aud_count == 0 and typ_count >= 1 and prep_count >= 1:
        if do_logs : logs.write(f"\n\nPROBLEMA AUD NET OSTALNOE YEST!!!!!!!!!\ngrp={grp} day={day} num={num} typ-{typ_count} prep-{prep_count}\n\n")
    elif aud_count >= 1 and typ_count >= 1 and prep_count == 0:
        if do_logs : logs.write(f"\n\nPROBLEMA PREP NET OSTALNOE YEST!!!!!!!!!\ngrp={grp} day={day} num={num} typ-{typ_count} aud-{aud_count}\n\n")
    #endregion


    #region АЛГОРИТМ БЕЗ-ТИПНОГО ОТБОРА
    elif aud_count >= 1 and typ_count == 0 and prep_count >= 1:
        if do_logs : logs.write(f"\n\nPROBLEMA TYP NET OSTALNOE YEST!!!!!!!!!\ngrp={grp} day={day} num={num} prep-{prep_count} aud-{aud_count}\n\n")
        
        if ws.cell_value(rowS+1, colS): #?????????
            disc_out = ws.cell_value(rowS+1, colS)
            if disc_out:
                mch = re.search(r_pg, disc_out)
                if mch: 
                    mch_ok = mch.group()
                    disc_out = disc_out.replace(mch_ok,'')
                    pg_out = mch_ok.replace('-', '').strip()
        
        typ_out='(н.т.)'

        for row in range(rowS, rowE+1):
            if ws.cell_value(row, colE):
                if aud_out: logs.write(f"\n\n!!!!!!!OSHIBKA ALGORITMA BEZYPNOGO OTBORA 2 aud!!!!!!!!!\ngrp={grp} day={day} num={num} prep-{prep_count} aud-{aud_count}\n\n")
                aud_out = ws.cell_value(row, colE)

            mch_prep = re.search(r_prep, rf"{ws.cell_value(row,colS)}")
            if mch_prep:
                if prep_out:  logs.write(f"\n\n!!!!!!!OSHIBKA ALGORITMA BEZYPNOGO OTBORA 2 prep!!!!!!!!!\ngrp={grp} day={day} num={num} prep-{prep_count} aud-{aud_count}\n\n")
                prep_out = mch_prep.group()
    #endregion
    

    #region КОГДА НА ОДНУ ДИСЦИПЛИНУ 2 ПРЕПОДОВАТЕЛЯ в 2 АУДИТОРИИ
    elif aud_count == 2 and typ_count == 1 and prep_count == 2:


        if ws.cell_value(rowS+1, colS): #?????????
            disc_out = ws.cell_value(rowS+1, colS)
            mch = re.search(r_pg, disc_out)
            if disc_out:
                if mch: 
                    mch_ok = mch.group()
                    disc_out = disc_out.replace(mch_ok,'')
                    pg_out = mch_ok.replace('-', '').strip()

        for row in range(rowS, rowE+1):
            if ws.cell_value(row, colE):
                if aud_out:
                    aud2_out = ws.cell_value(row, colE) 
                elif aud2_out:
                    if do_logs : logs.write(f"\n\n!!!!!!!!!!PROBLEMA AUDITORII 3!!!!!!!! no dannie dobavlini!!!!\ngrp={grp} day={day} num={num} prep-{prep_count} aud-{aud_count}\n\n")
                else:
                    aud_out = ws.cell_value(row, colE) 

            mch_prep = [m.group() for m in re.finditer(r_prep, ws.cell_value(row,colS))]
            if mch_prep:
                prep_out = mch_prep[0]
                prep2_out = mch_prep[1]

            mch_typ = re.search(r_type, rf"{ws.cell_value(row,colS)}")
            if mch_typ:
                typ_out = mch_typ.group()
    #region

    #region 2 ПАРЫ В ОДНОЙ ЯЧЕЙКЕ единственная ситуация когда 2 дисциплины
    elif aud_count == 2 and typ_count == 2 and prep_count == 2: # ТУТ ТОЖЕ


        for row in range(rowS, rowE+1):

            if ws.cell_value(row, colE):
                if aud_out:
                    aud2_out = ws.cell_value(row, colE) 
                elif aud2_out:
                    if do_logs : logs.write("PROBLEMA AUDITORII 3!!!!!\n")
                else:
                    aud_out = ws.cell_value(row, colE) 

            mch_prep = [m.group() for m in re.finditer(r_prep, ws.cell_value(row,colS))]
            if mch_prep:
                if len(mch_prep) > 1:
                    prep_out = mch_prep[0]
                    prep2_out = mch_prep[1]
                    if do_logs : logs.write('prekol s prepodami\n')
                else:
                    if prep_out:
                        prep2_out = mch_prep[0]
                    elif prep2_out:
                        if do_logs : logs.write('\n\nPROBLEMA S PREPODAMI 3 cherez pervichiy proshli!!!!!!!\n\n')
                    else:
                        prep_out = mch_prep[0]
                

            mch_typ = re.search(r_type, rf"{ws.cell_value(row,colS)}")
            if mch_typ:
                if len(mch_prep) > 1:
                    typ_out = mch_typ[0]
                    typ2_out = mch_typ[1]
                    if do_logs : logs.write('prekol s tipami\n')
                else:
                    if typ_out:
                        typ2_out = mch_typ[0]
                    elif typ2_out:
                        if do_logs : logs.write('PROBLEMA S PREPODAMI\n')
                    else:
                        typ_out = mch_typ[0]

            if ws.cell_value(row, colS):
                if disc_out:
                    if mch_prep and mch_typ and ws.cell_value(row, colS).replace(mch_prep[0], '').replace(mch_typ[0], ''):
                        disc2_out = ws.cell_value(row, colS).replace(mch_prep[0], '').replace(mch_typ[0], '')
                    elif mch_prep and ws.cell_value(row, colS).replace(mch_prep[0], ''):
                        disc2_out = ws.cell_value(row, colS).replace(mch_prep[0], '')
                    elif mch_typ and ws.cell_value(row, colS).replace(mch_typ[0], ''):
                        disc2_out = ws.cell_value(row, colS).replace(mch_typ[0], '')

                    if disc2_out:
                        mch = re.search(r_pg, disc2_out)
                        if mch: 
                            mch_ok = mch.group()
                            disc2_out = disc2_out.replace(mch_ok,'')
                            pg2_out = mch_ok.replace('-', '').strip()

                elif disc2_out:
                    if do_logs : logs.write('DISCIPLINI 3!!!!!!!!!!!!!!!!!!\n')
                else:
                    if mch_prep and mch_typ and ws.cell_value(row, colS).replace(mch_prep[0], '').replace(mch_typ[0], ''):
                        disc_out = ws.cell_value(row, colS).replace(mch_prep[0], '').replace(mch_typ[0], '')
                    elif mch_prep and ws.cell_value(row, colS).replace(mch_prep[0], ''):
                        disc_out = ws.cell_value(row, colS).replace(mch_prep[0], '')
                    elif mch_typ and ws.cell_value(row, colS).replace(mch_typ[0], ''):
                        disc_out = ws.cell_value(row, colS).replace(mch_typ[0], '')

                    if disc_out:
                        mch = re.search(r_pg, disc_out)
                        if mch: 
                            mch_ok = mch.group()
                            disc_out = disc_out.replace(mch_ok,'')
                            pg_out = mch_ok.replace('-', '').strip()
    #endregion


    if not num_out or not day_out or not grp_out or not aud_out or not prep_out or not typ_out or not disc_out:
        for row in range(rowS, rowE+1):
            if ws.cell_value(row, colE) and do_logs:
                logs.write(f"{[num_out ,day_out ,grp_out ,aud_out ,prep_out ,typ_out ,disc_out, prep2_out, aud2_out, typ2_out, disc2_out]}\n")
                logs.write(f"PROBLEMA NICHEGO NET NO YEST DANNIE v audiorii - {ws.cell_value(row, colE)}\ngrp={grp} day={day} num={num} typ-{typ_count} aud-{aud_count} prep-{prep_count}\n\n")
                get_img(grp,day,num,ws,f"{cur_work_file.split('.')[0].replace(' ','_')}{grp}_{day}_{num}")
                logs.close()
                break
            if ws.cell_value(row, colS) and do_logs:
                global last_problem
                if last_problem == ws.cell_value(row,colS):
                    continue
                else:
                    last_problem = ws.cell_value(row,colS)
                logs.write(f"{[num_out ,day_out ,grp_out ,aud_out ,prep_out ,typ_out ,disc_out, prep2_out, aud2_out, typ2_out, disc2_out]}\n")
                logs.write(f"PROBLEMA NICHEGO NET NO YEST DANNIE - {ws.cell_value(row, colS)}\ngrp={grp} day={day} num={num} typ-{typ_count} aud-{aud_count} prep-{prep_count}\n\n")
        if do_logs : logs.close()
        return False
    
    else:        
        grp_cut = {'aud': aud_out ,'prp': prep_out ,'typ': typ_out ,'dsc': disc_out, 'prp2': prep2_out, 'aud2': aud2_out, 'typ2': typ2_out, 'dsc2': disc2_out, 'pg':pg_out,'pg2':pg2_out}
        
        if grp_cut['typ']: grp_cut['typ'] = grp_cut['typ'].replace('(','').replace(')','')
        if grp_cut['typ2']: grp_cut['typ2'] = grp_cut['typ2'].replace('(','').replace(')','')

        for key, val in grp_cut.items():
            if val:
                grp_cut[key] = val.replace('\n', '').strip()
        if do_logs : logs.close()
        return grp_cut


# сделать список с расписанием 1 группы
def make_dict(grp_cut, ws):
    raspisanie = {}
    for group, val in grp_cut.items():
        raspisanie[group] = {}
        for day, numbers in val.items():
            raspisanie[group][day] = {}
            for number, borders in numbers.items():
                t_cut_1 = get_one(group, day, number, borders, ws)
                if t_cut_1:
                    raspisanie[group][day][number] = t_cut_1
                else:
                    raspisanie[group][day][number] = None
    return raspisanie

#print(make_dict(get_groups_cut())) #fix it


def week_clear(week):
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute(f"delete from ras where week = {week}")
    con.commit()
    con.close()

def dbINIT(week):

    global cur_work_file

    weeks = weeks_get()

    # if int(week) in weeks:
    #     week_clear(week)

    days_dates = get_week_dates(week)

    maincon = sqlite3.connect('ras2.db')
    
    ras = os.listdir(rasDir)
    for r in ras:
        cur_work_file = r
        book = exel.open_workbook(f"ras\\{r}", formatting_info=True)
        ws = book.sheet_by_index(0)
        print(r)

        grp_cut = get_groups_cut(ws)

        for group, val in grp_cut.items():
            for day, numbers in val.items():
                for number, borders in numbers.items():
                    cut = get_one(group, day, number, borders, ws)
                    if cut:
                        dbin_day = day2num(day)
                        dbin_grop = group
                        dbin_num = number
                        dbin_prep = cut['prp']
                        dbin_kab = cut['aud']
                        dbin_disc = cut['dsc']
                        dbin_typ = cut['typ']
                        dbin_pg = cut['pg']
                        dbin_dat = days_dates[day]
                        cursor = maincon.cursor()
                        cursor.execute(f"select * from ras where week = {week} and day = {dbin_day} and num = {dbin_num} and prep = '{dbin_prep}' and kab = '{dbin_kab}' and disc = '{dbin_disc}' and grop = '{dbin_grop}' and typ = '{dbin_typ}' and date = '{dbin_dat}'")
                        ex_chk = cursor.fetchone()
                        if not ex_chk:
                            cursor.execute(f"INSERT INTO ras (week, day, num, prep, kab, disc, grop, typ, date, pg) VALUES ({week}, {dbin_day}, {dbin_num}, '{dbin_prep}', '{dbin_kab}', '{dbin_disc}', '{dbin_grop}', '{dbin_typ}', '{dbin_dat}', '{dbin_pg}')")
                        if (cut['prp2'] and cut['prp2'] != cut['prp']) or (cut['aud2'] and cut['aud2'] != cut['aud']) or cut['dsc2'] or cut['typ2']:
                            dbin_kab = cut['aud2'] if cut['aud2'] else cut['aud']
                            dbin_prep = cut['prp2'] if cut['prp2'] else cut['prp']
                            dbin_disc = cut['dsc2'] if cut['dsc2'] else cut['dsc']
                            dbin_typ = cut['typ2'] if cut['typ2'] else cut['typ']
                            dbin_pg = cut['pg2'] if cut['pg2'] else None
                            cursor.execute(f"select * from ras where week = {week} and day = {dbin_day} and num = {dbin_num} and prep = '{dbin_prep}' and kab = '{dbin_kab}' and disc = '{dbin_disc}' and grop = '{dbin_grop}' and typ = '{dbin_typ}' and date = '{dbin_dat}'")
                            ex_chk2 = cursor.fetchone()
                            if not ex_chk2:
                                cursor.execute(f"INSERT INTO ras (week, day, num, prep, kab, disc, grop, typ, date, pg) VALUES ({week}, {dbin_day}, {dbin_num}, '{dbin_prep}', '{dbin_kab}', '{dbin_disc}', '{dbin_grop}', '{dbin_typ}', '{dbin_dat}', '{dbin_pg}')")
                    else:
                        pass
                
    maincon.commit()
    maincon.close()
    rmExelOFO()
    vars_INIT()
    print("done!")

def cleardb():
    con = sqlite3.connect('ras2.db')
    cursor = con.cursor()
    cursor.execute('delete from ras')
    con.commit()
    con.close()

def rmExelOFO():
    for r in os.listdir('ras'):
        os.remove('ras/'+r)



#print(f"number = {t_cut_1['num']}\nday = {t_cut_1['day']}\ngroup = {t_cut_1['grp']}\naudit = {t_cut_1['aud']} | {t_cut_1['aud2'] if t_cut_1['aud2'] else ''}\nprep = {t_cut_1['prp']} | {t_cut_1['prp2'] if t_cut_1['prp2'] else ''}\ntype = {t_cut_1['typ']} | {t_cut_1['typ2'] if t_cut_1['typ2'] else ''}\ndisc = {t_cut_1['dsc']} | {t_cut_1['dsc2'] if t_cut_1['dsc2'] else ''}")
