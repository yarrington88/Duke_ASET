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
       'WHERE PatientId = 20000120244'

allabx_inperiod = pd.read_sql(sql1, engine)



test = pd.read_csv('C:\\Users\\mey10\\Desktop\\psweb_surgery_list_2015_2019_v2_11_2020.csv')

test['Nhsn Code'].unique()


groupers = test.groupby(test.Grouper)

groupers['Nhsn Code'].value_counts()

