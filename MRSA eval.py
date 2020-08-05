import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
from sqlalchemy import create_engine
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from datetime import datetime, timedelta, date
from scipy import stats

engine = create_engine('mssql+pyodbc://@vwp-dason-dhdb/dason?driver=ODBC Driver 17 for SQL Server?trusted_connection=yes')

start_date = date(year=2019, month=7, day=1)
end_date = date(year=2020, month=7, day=1)
sql1 = 'SELECT * ' \
       'FROM DasonView.MicroIsolate ' \
       'WHERE CultureDateTime >= ? ' \
       'and CultureDateTime <= ? ' \ 
       'and HospitalId = 2000 ' \
       'and PathogenId = 2081'


allisolates = pd.read_sql(sql1, engine,
                              params=[(start_date - timedelta(days=0)), (end_date + timedelta(days=0))])

mrsa = allisolates[allisolates['ReportedPathogen'] != 'STAPHYLOCOCCUS AUREUS']

# bsi = mrsa[mrsa.ReportedSpecimenSource.isin(['BLOOD','BRONCHIAL WASH/BAL', 'TISSUE','SYNOVIAL/JOINT FLUID','CEREBROSPINAL FLUID'])]
bsi = mrsa[mrsa.ReportedSpecimenSource.isin(['BLOOD'])]

bsi['first_culture'] = bsi.groupby('PatientId').CultureDateTime.transform('min')

deduped = bsi.drop_duplicates(['PatientId','first_culture'])

deduped['day_of_week'] = deduped['first_culture'].dt.weekday

deduped.day_of_week.hist(bins=np.arange(8)-0.5)
plt.xticks([0,1,2,3,4,5,6],['mon','tues','wed','thurs','fri','sat','sun'])
plt.show()

deduped.ReportedUnitName.value_counts()
bsi.ReportedUnitName.value_counts()



sql2 = 'SELECT * ' \
       'FROM DasonView.MedicationAdmin ' \
       'WHERE AdministrationDateTime >= ? ' \
       'and AdministrationDateTime < ? ' \
       'and HospitalId = 2000'

    # 'and (HospitalId = 1001 OR HospitalId = 1011) '

       # 'and ReportedClinicalIndication != ?'


# get our data!!
allabx_inperiod = pd.read_sql(sql2, engine,
                              params=[(start_date - timedelta(days=0)), (end_date + timedelta(days=0))])


only_mrsa_patients_abx = allabx_inperiod[allabx_inperiod.PatientId.isin(list(deduped.PatientId.unique()))]

vanco_doses = only_mrsa_patients_abx[only_mrsa_patients_abx.AgentName == 'Vancomycin']\\


vanco_doses.UnitName.value_counts().sort_values().plot(kind = 'bar')
plt.show()


mrsa.ReportedSpecimenSource.unique()

deduped.ReportedUnitName.value_counts()
bsi.ReportedUnitName.value_counts()

