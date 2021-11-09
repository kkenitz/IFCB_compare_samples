# -*- coding: utf-8 -*-
"""
This function compares two, side-by-side IFCB deployments
"""

import pandas as pd
import numpy as np
from os import listdir
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

CURR_DIR = os.getcwd()

# Get the list of feature files + match files for comparison ifcb151 vs ifcb158 (two deployments)
ifcb151_path=os.path.join(CURR_DIR,"IFCB151_Pier_Deployments","features","")
print(ifcb151_path)

col_list = ["Area", "MajorAxisLength"]

ifcb151_files=listdir(ifcb151_path)
ifcb151_files = pd.DataFrame(list(filter(lambda f: f.endswith('.csv'), ifcb151_files)), columns=['Sample ID'])

pattern="(?P<date>D[0-9]*T[0-9]{4})(\w*.csv)"
out=ifcb151_files['Sample ID'].str.extract(pattern)
ifcb151_files['Date'] = pd.to_datetime(out['date'], format='D%Y%m%dT%H%M', errors='ignore')
ifcb151_files['Date_bin'] = ifcb151_files['Date'].apply(lambda x: x.replace(microsecond=0, second=0, minute=0))

for i in [1,2]:
    if i==1:
        ifcb158_path=os.path.join(CURR_DIR,"IFCB158_Pier_Deployments","SIO_Pier_deck_deployment","features","")
        ifcb158_files=listdir(ifcb158_path)
    if i==2:
        ifcb158_path=os.path.join(CURR_DIR,"IFCB158_Pier_Deployments","SIO_Pier_deployment_20210526","features","")
        ifcb158_files=listdir(ifcb158_path)
     
    ifcb158_files = pd.DataFrame(list(filter(lambda f: f.endswith('.csv'), ifcb158_files)), columns=['Sample ID'])
    out=ifcb158_files['Sample ID'].str.extract(pattern)
    ifcb158_files['Date'] = pd.to_datetime(out['date'], format='D%Y%m%dT%H%M', errors='ignore')
    ifcb158_files['Date_bin'] = ifcb158_files['Date'].apply(lambda x: x.replace(microsecond=0, second=0, minute=0))


    ifcb151_keep = ifcb151_files[ifcb151_files['Date_bin'].isin(ifcb158_files['Date_bin'])]
#    ifcb151_keep = ifcb151_files[ifcb151_files['Date'].between(min(ifcb158_files['Date'])-pd.Timedelta(minutes=10), max(ifcb158_files['Date'])+pd.Timedelta(minutes=10))]

# Load feature files
    ifcb158=pd.DataFrame()
    for file in ifcb158_files['Sample ID']:
        tmp=pd.read_csv(ifcb158_path + file, usecols=col_list)
        tmp['Sample ID'] = file
        ifcb158=ifcb158.append(tmp, ignore_index=True)
        
    ifcb151=pd.DataFrame()
    for file in ifcb151_keep['Sample ID']:
        tmp=pd.read_csv(ifcb151_path + file, usecols=col_list)
        tmp['Sample ID'] = file
        ifcb151=ifcb151.append(tmp, ignore_index=True)
 
# Find number of ROIs per sample       
    IFCB151_ROIcount=ifcb151.groupby('Sample ID').size()  
    IFCB158_ROIcount=ifcb158.groupby('Sample ID').size()  
        
    ifcb151_files.set_index('Sample ID', inplace=True)
    IFCB151_ROIcount = IFCB151_ROIcount.to_frame().join(ifcb151_files)
    IFCB151_ROIcount=IFCB151_ROIcount.rename(columns={0: 'Total ROIs'})

    ifcb158_files.set_index('Sample ID', inplace=True)
    IFCB158_ROIcount = IFCB158_ROIcount.to_frame().join(ifcb158_files)
    IFCB158_ROIcount=IFCB158_ROIcount.rename(columns={0: 'Total ROIs'})
    ifcb151_files.reset_index(inplace=True)

    IFCB158_ROIcount['Date'] = IFCB158_ROIcount['Date'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
    IFCB151_ROIcount['Date'] = IFCB151_ROIcount['Date'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))

    IFCB158_time = [dt.datetime.strptime(d,'%Y-%m-%d %H:%M') for d in IFCB158_ROIcount['Date']]
    IFCB151_time = [dt.datetime.strptime(d,'%Y-%m-%d %H:%M') for d in IFCB151_ROIcount['Date']]

    figure, axes = plt.subplots(3, 1, figsize=(8,12))#,sharex=True)
    plt.style.use('classic')
    if i==1:
        axes[0].title.set_text('Deployment 1: 5/13 to 5/24')
    if i==2:
        axes[0].title.set_text('Deployment 2: 5/26 to 6/02')

    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=2))

    axes[0].plot(IFCB158_time,IFCB158_ROIcount['Total ROIs'],'crimson', marker=".", markersize=12, linestyle='none', markerfacecolor="none", label='IFCB158 (samples={:d})'.format(len(ifcb158_files)))
    axes[0].plot(IFCB151_time,IFCB151_ROIcount['Total ROIs'],'steelblue', marker=".", markersize=12, linestyle='none', markerfacecolor="none", label='IFCB151 (samples={:d})'.format(len(ifcb151_keep)))
    axes[0].set_ylabel('#ROIs per sample',fontsize=12)
    axes[0].set_xlim([min(IFCB158_time)-pd.Timedelta(hours=6), max(IFCB158_time)+pd.Timedelta(hours=6)])
#    L=axes[0].legend(loc=1, frameon=True)
 #   axes[0].set_xticklabels(axes[0].get_xticks(), rotation = 45)

    axes[1].hist(ifcb158['Area']/3.4/3.4+1,bins=np.logspace(np.log10(1),np.log10(np.ceil(np.max(ifcb158['Area']/3.4/3.4))), num=80,base=10), alpha=0.5, color='crimson', label='IFCB158 (samples={:d})'.format(len(ifcb158_files)))
    axes[1].hist(ifcb151['Area']/3.4/3.4+1,bins=np.logspace(np.log10(1),np.log10(np.ceil(np.max(ifcb158['Area']/3.4/3.4))), num=80,base=10), alpha=0.5, color='steelblue', label='IFCB151 (samples={:d})'.format(len(ifcb151_keep)))
#    axes[1].hist(np.log10(ifcb158['Area']/3.4/3.4+1),bins=80, alpha=0.5, color='crimson', label='IFCB158 (samples={:d})'.format(len(ifcb158_files)))
#    axes[1].hist(np.log10(ifcb151['Area']/3.4/3.4+1),bins=80, alpha=0.5, color='steelblue', label='IFCB151 (samples={:d})'.format(len(ifcb151_keep)))
    axes[1].set_xlabel(r'Area ($\mu$m$^2$)',fontsize=12)
    axes[1].set_ylabel('# occurrences',fontsize=12)
    L=axes[1].legend(loc=1, frameon=True)
    axes[1].set_xscale('log')
    axes[1].set_xlim(0)

    axes[2].hist(ifcb158['MajorAxisLength']/3.4+1,bins=np.logspace(np.log10(1),np.log10(np.ceil(np.max(ifcb158['MajorAxisLength']/3.4))), num=80,base=10), alpha=0.5, color='crimson')
    axes[2].hist(ifcb151['MajorAxisLength']/3.4+1,bins=np.logspace(np.log10(1),np.log10(np.ceil(np.max(ifcb158['MajorAxisLength']/3.4))), num=80,base=10), alpha=0.5, color='steelblue')
#    axes[2].hist(np.log10(ifcb158['MajorAxisLength']/3.4+1),bins=80, alpha=0.5, color='crimson')
#    axes[2].hist(np.log10(ifcb151['MajorAxisLength']/3.4+1),bins=80, alpha=0.5, color='steelblue')
    axes[2].set_xlabel(r'Major Axis Length ($\mu$m)',fontsize=12)
    axes[2].set_ylabel('# occurrences',fontsize=12)
    axes[2].set_xscale('log')
  #  axes[2].set_xticks(np.log10([1, 5, 10, 50, 100, 500, 1000]))
    axes[2].set_xlim(0)  
#    axes[2].set_xticklabels(np.around(np.power(10,axes[2].get_xticks()),decimals=0))

    plt.savefig('IFCB_compare_deployment_{:d}.png'.format(i),facecolor='w', edgecolor='w',
        format='png')