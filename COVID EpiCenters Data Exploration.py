import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from sqlalchemy import create_engine
from datetime import datetime, timedelta, date
from scipy import stats
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter

start_date = date(year=2020, month=1, day=1)

engine = create_engine('mssql+pyodbc://@vwp-dason-db/dason?driver=ODBC Driver 13 for SQL Server?trusted_connection=yes')


sql2 =  'select * ' \
        'FROM DasonView.MedicationAdmin ' \
        'WHERE AdministrationDateTime > ? ' \ 
        'AND AgentId = 502'

hcq = pd.read_sql(sql2,engine, params = [start_date])

hcq['Date'] = hcq['AdministrationDateTime'].dt.date


groups = hcq.groupby(['PatientId', 'Date'])

