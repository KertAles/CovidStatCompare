# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 12:36:07 2021

@author: Kert PC
"""

import json
import os

import PIL
from PIL import ImageOps, Image
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np

import datetime


def getWeekData(countryCode) :
    
    country_data = []
    
    country_case_data = [a for a in case_data['records']
                         if a['geoId']  == countryCode 
                         and datetime.datetime.strptime(a['dateRep'], "%d/%m/%Y").date().strftime('%Y-W%V') >= from_date
                         and datetime.datetime.strptime(a['dateRep'], "%d/%m/%Y").date().strftime('%Y-W%V') <= to_date]
    
    country_case_data.reverse()
    
    country_vacc_data = [a for a in vacc_data['records']
                         if a['ReportingCountry']  == countryCode 
                         and a['YearWeekISO'] <= to_date
                         and a['TargetGroup'] == 'ALL']
    
    pop = int(country_case_data[0]['popData2020']) / 100000
    i = 0
    for day_data in country_case_data :
        if i % 7 == 0 :
            prev_vacc_sum = 0.0
            if i > 0:
                country_data[-1]['cases'] /= pop
                country_data[-1]['deaths'] /= pop
                
                vaccs_1 = 0.0
                vaccs_2 = 0.0
                week = country_data[-1]['week']
                
                for vacc in country_vacc_data :
                    if vacc['YearWeekISO'] <= week :
                        if vacc['Vaccine'] == 'JANSS' :
                            vaccs_2 += vacc['FirstDose']
                        else :
                            vaccs_1 += vacc['FirstDose']
                            vaccs_2 += vacc['SecondDose']
                
                
                country_data[-1]['vaccs_1'] = vaccs_1 / (pop * 1000)
                country_data[-1]['vaccs_2'] = vaccs_2 / (pop * 1000)
                
                if countryCode == 'PT' or countryCode == 'FR' or countryCode == 'IT' :
                    country_data[-1]['vaccs_1'] /= 2
                    country_data[-1]['vaccs_2'] /= 2
                        
            country_data.append({'week' : datetime.datetime.strptime(day_data['dateRep'], "%d/%m/%Y").date().strftime('%Y-W%V'),
                                 'cases' : 0.0,
                                 'deaths' : 0.0,
                                 'vaccs_1' : 0.0,
                                 'vaccs_2' : 0.0})
        
        country_data[-1]['cases'] += int(day_data['cases'])
        country_data[-1]['deaths'] += int(day_data['deaths'])
        
        i += 1
    
    country_data[-1]['cases'] /= pop
    country_data[-1]['deaths'] /= pop
    
    vaccs_1 = 0.0
    vaccs_2 = 0.0
    week = country_data[-1]['week']
                
    for vacc in country_vacc_data :
        if vacc['YearWeekISO'] <= week :
            if vacc['Vaccine'] == 'JANSS' :
                vaccs_2 += vacc['FirstDose']
            else :
                vaccs_1 += vacc['FirstDose']
                vaccs_2 += vacc['SecondDose']
                
    country_data[-1]['vaccs_1'] = vaccs_1 / (pop * 1000)
    country_data[-1]['vaccs_2'] = vaccs_2 / (pop * 1000)
    
    if countryCode == 'PT' or countryCode == 'FR' or countryCode == 'IT' :
        country_data[-1]['vaccs_1'] /= 2
        country_data[-1]['vaccs_2'] /= 2
    
    if not i % 7 == 0 :
        country_data[-1]['cases'] *= 7 / (i % 7)
        country_data[-1]['deaths'] *= 7 / (i % 7)
    
    return {'code': countryCode, 'data' : country_data}


"""
040 	Austria 	AT 	AUT
056 	Belgium 	BE 	BEL
100 	Bulgaria 	BG 	BGR
191 	Croatia 	HR 	HRV
196 	Cyprus 	    CY 	CYP
203 	Czechia 	CZ 	CZE
208 	Denmark 	DK 	DNK
233 	Estonia 	EE 	EST
246 	Finland 	FI 	FIN
250 	France 	    FR 	FRA
276 	Germany 	DE 	DEU
300 	Greece 	    GR 	GRC
348 	Hungary 	HU 	HUN
372 	Ireland 	IE 	IRL
380 	Italy 	    IT 	ITA
428 	Latvia   	LV 	LVA
440 	Lithuania 	LT 	LTU
442 	Luxembourg 	LU 	LUX
470 	Malta 	    MT 	MLT
528 	Netherlands NL 	NLD
616 	Poland 	    PL 	POL
620 	Portugal 	PT 	PRT
642 	Romania 	RO 	ROU
703 	Slovakia 	SK 	SVK
705 	Slovenia 	SI 	SVN
724 	Spain 	    ES 	ESP
752 	Sweden 	    SE 	SWE
826 	UK 	        GB 	GBR
"""

path = './'

countries = ['BG', 'HR', 'SK', 'SI', 'AT', 'FR', 'DE', 'IT', 'BE', 'ES', 'PT', 'DK']

from_date = datetime.date(2021, 3, 8).strftime('%Y-W%V')
to_date = datetime.date(2022, 1, 4).strftime('%Y-W%V')



case_data = json.load(open(path + 'cases.json'))
vacc_data = json.load(open(path + 'vacc.json'))

data = []

for country in countries :
    data.append(getWeekData(country))
    
    
num_of_vals = len(countries)
    

fig = plt.figure(figsize=(40., 110.))
fig.subplots_adjust(hspace=0.25, wspace=0.15)

degrees = 70

for i in range(1, num_of_vals * 3 + 1):
    ax = fig.add_subplot(num_of_vals, 3, i)
    
    if i % 3 == 1 :
        ax.plot([x['cases'] for x in data[(i - 1) // 3]['data']], 'r')
        ax.set_xticks(np.arange(len([x['week'] for x in data[(i - 1) // 3]['data']])))
        ax.set_xticklabels([x['week'] for x in data[(i - 1) // 3]['data']], rotation=degrees)
        ax.title.set_text(countries[(i - 1) // 3] + ' - 7-day incidence')
        ax.set_ylabel('cases / 100k')
        ax.set_xlabel('week')
        ax.legend(['7-day incidence'], loc='upper left')
        ax.grid()
    elif i % 3 == 2 :
        ax.plot([x['deaths'] for x in data[(i - 1) // 3]['data']], 'k')
        ax.set_xticks(np.arange(len([x['week'] for x in data[(i - 1) // 3]['data']])))
        ax.set_xticklabels([x['week'] for x in data[(i - 1) // 3]['data']], rotation=degrees)
        ax.title.set_text(countries[(i - 1) // 3] + ' - 7-day deaths')
        ax.set_ylabel('deaths / 100k')
        ax.set_xlabel('week')
        ax.legend(['7-day deaths'], loc='upper left')
        ax.grid()
    else :
        ax.plot([x['vaccs_1'] for x in data[(i - 1) // 3]['data']], 'c')
        ax.plot([x['vaccs_2'] for x in data[(i - 1) // 3]['data']], 'g')
        ax.set_xticks(np.arange(len([x['week'] for x in data[(i - 1) // 3]['data']])))
        ax.set_xticklabels([x['week'] for x in data[(i - 1) // 3]['data']], rotation=degrees)
        ax.title.set_text(countries[(i - 1) // 3] + ' - vaccination rate')
        ax.set_ylabel('vaccinated')
        ax.set_xlabel('week')
        ax.legend(['1st dose', '2nd dose'], loc='upper left')
        ax.set_ylim(0,100)
        ax.grid()
        

figures = os.listdir('./figures/')
fig.savefig('./figures/fig_' + str(len(figures)) + '.png')