import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
import scipy.stats as stats
from sqlalchemy import create_engine


engine = create_engine('mssql+pyodbc://@vwp-dason-dhdb/dason?driver=ODBC Driver 13 for SQL Server?trusted_connection=yes')


sql1 = 'SELECT * ' \
       'FROM DasonView.MedicationAdmin ' \
       'WHERE PatientId = 20000067542'

allabx_inperiod = pd.read_sql(sql1, engine)



nhsn_code_duration = pd.read_csv('P:\\DICON_OUTREACH\\Fellow DICON Files\\Mike Yarrington\\final_nhsn_for_cohort_with_duration.csv')

# Remove NAN


#create dictionary
category_dict = {'COLO': 'Colorectal', 'REC':'Colorectal', 'PVBY':'Vascular', 'CEA':'Vascular', 'AAA':'Vascular','AVSD':'Vascular',
                 'CABG':'Cardiac','CARD':'Cardiac','APPY':'General Surgery','CHOL':'General Surgery','HER':'General Surgery','SB':'General Surgery',
                 'XLAP':'General Surgery','BILI':'General Surgery','LAM':'Spine','FUSN':'Spine','THYR':'Head/Neck','NECK':'Head/Neck',
                 'NEPH':'Urology','PRST':'Urology','HYST':'OB/GYN','VHYS':'OB/GYN','OVRY':'OB/GYN','CSEC':'OB/GYN',
                 'KPRO':'Orthopedic','HPRO':'Orthopedic','OPRO':'Orthopedic','AMP':'Orthopedic','FX':'Orthopedic',
                 'CRAN':'Neurosurgery','VHSN':'Neurosurgery','VSHN':'Neurosurgery','BRST':'Plastics','SKGR':'Plastics'}

category_dict = {'COLO': 'Colo/Gen.Surg', 'REC':'Colo/Gen.Surg', 'PVBY':'Vascular', 'CEA':'Vascular', 'AAA':'Vascular','AVSD':'Vascular',
                 'CABG':'Cardiac','CARD':'Cardiac','APPY':'Colo/Gen.Surg','CHOL':'Colo/Gen.Surg','HER':'Colo/Gen.Surg','SB':'Colo/Gen.Surg',
                 'XLAP':'Colo/Gen.Surg','BILI':'Colo/Gen.Surg','LAM':'Ortho/Spine','FUSN':'Ortho/Spine','THYR':'Head/Neck','NECK':'Head/Neck',
                 'NEPH':'Urology','PRST':'Urology','HYST':'OB/GYN','VHYS':'OB/GYN','OVRY':'OB/GYN','CSEC':'OB/GYN',
                 'KPRO':'Ortho/Spine','HPRO':'Ortho/Spine','OPRO':'Ortho/Spine','AMP':'Ortho/Spine','FX':'Ortho/Spine',
                 'CRAN':'Neurosurgery','VHSN':'Neurosurgery','VSHN':'Neurosurgery','BRST':'Plastics','SKGR':'Plastics'}


nhsn_code_duration['Category'] = nhsn_code_duration.NHSN_code.map(category_dict)



nhsn_code_duration = nhsn_code_duration[~nhsn_code_duration.hours.isnull()]
nhsn_code_duration = nhsn_code_duration[~nhsn_code_duration.Category.isnull()]

#these two lines are to get the order to put the categories in: group them, find the median, and resort the index and use that
grouped=nhsn_code_duration.groupby(nhsn_code_duration.Category)
medians = pd.DataFrame({col:vals['hours'] for col,vals in grouped}).median().sort_values(ascending=True)



plt.figure(figsize=(12,4))
sns.boxplot(data = nhsn_code_duration, x='Category', y = 'hours', order = medians.index, whis = [5,95], showfliers = False)
plt.ylabel('Hours')
plt.xlabel('Category Based on NHSN Code')
plt.ylim(0,60)
plt.show()



#split into cohorts and do boxplots that way
first_cohort = nhsn_code_duration[nhsn_code_duration.Category.isin(['Plastics', 'Urology', 'Neurosurgery','Ortho/Spine','Cardiac'])].reset_index()
second_cohort = nhsn_code_duration[nhsn_code_duration.Category.isin(['Colo/Gen.Surg','Head/Neck','OB/GYN','Vascular'])].reset_index()

#first cohort order
first_grouped =first_cohort.groupby(first_cohort.Category)
first_medians = pd.DataFrame({col:vals['hours'] for col,vals in first_grouped}).median().sort_values(ascending=True)


#second cohort order
second_grouped =second_cohort.groupby(second_cohort.Category)
second_medians = pd.DataFrame({col:vals['hours'] for col,vals in second_grouped}).median().sort_values(ascending=True)



plt.figure(figsize=(8,4))
sns.boxplot(data = first_cohort, x='Category', y = 'hours', order = first_medians.index, showfliers = False)
plt.ylabel('Hours')
plt.xlabel('Category Based on NHSN Code')
plt.ylim(0,40)
plt.show()


plt.figure(figsize=(12,4))
sns.boxplot(data = second_cohort, x='Category', y = 'hours', order = second_medians.index, whis = [25,75], showfliers = False)
plt.ylabel('Hours')
plt.xlabel('Category Based on NHSN Code')
plt.ylim(0,10)
plt.show()


#ADULT and PEDS

plt.figure(figsize=(6,6))
sns.boxplot(data = nhsn_code_duration, x='age', y = 'hours')
plt.ylabel('Hours')
plt.xlabel('Category Based on Age')
plt.ylim(0,70)
plt.show()
