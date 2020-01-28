import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
import scipy.stats as stats
from sqlalchemy import create_engine


from datetime import datetime, timedelta, date
from scipy import stats

engine = create_engine('mssql+pyodbc://@vwp-dason-dhdb/dason?driver=ODBC Driver 13 for SQL Server?trusted_connection=yes')


sql1 = 'SELECT * ' \
       'FROM DasonView.MedicationAdmin ' \
       'WHERE AdministrationDateTime >= ? ' \
       'and AdministrationDateTime < ? ' \
       'and HospitalId = 2000 ' \
       'and (AgentName = ? OR AgentName = ?)'



start_date = date(year=2019, month=12, day=1)
end_date = date(year=2020, month=1, day=1)

# get our data!!
allabx_inperiod = pd.read_sql(sql1, engine, params=[start_date, end_date, 'Meropenem', 'Micafungin'])



data = pd.read_csv('P:\DICON_OUTREACH\Fellow DICON Files\Mike Yarrington\ASET\Mero Mica ON restriction\micafungin_meropenem_2019_duh.csv')
clean = data[data.SHORT_MED_NAME != 'MEROPENEM-VABORBACTAM']

#Let's split into three dataframes, indications, approvals, and not answered

approvals= clean[clean.QUEST_NAME.str.contains('APPROVAL', na=False)].copy()
indications = clean[~clean.QUEST_NAME.str.contains('APPROVAL', na=True)]
not_answered = clean[clean.QUEST_NAME.isna()]

#Let's work with approvals
approvals['ORDERING_DATE'] = approvals['ORDERING_DATE'].astype('datetime64[ns]')
approvals['ORDER_INST'] = approvals['ORDER_INST'].astype('datetime64[ns]')
approvals = approvals.sort_values('ORDERING_DATE')

#remove some duplicates if any
approvals = approvals.drop_duplicates(['MRN','ORDERING_DATE','SHORT_MED_NAME'])



# FIRST, let's just plot the total # of mero/mica over a year
approvals.ORDERING_DATE.hist(bins = 52)
plt.legend(['number of total approval pages for mero/mica'])
plt.show()



#Next let's group them and plot
grouped = approvals.groupby('SHORT_MED_NAME')
plt.hist([grouped.get_group('MEROPENEM')['ORDERING_DATE'],
          grouped.get_group('MICAFUNGIN')['ORDERING_DATE']],
         bins = 52, stacked= True)
labels=['meropenem','micafungin']
plt.legend(labels)
plt.show()

# check if the order was done by the new protocol

new_protocol = approvals.ORD_QUEST_RESP.str.contains('After hours')
approvals['new_protocol'] = new_protocol
approvals.new_protocol.value_counts()
new_protocol_group = approvals.groupby('new_protocol')
plt.hist([new_protocol_group.get_group(True).ORDERING_DATE,
          new_protocol_group.get_group(False).ORDERING_DATE],
          bins= 52, stacked= True)
labels_protocol =['Overnight Protocol','Text Page']
plt.legend(labels_protocol)
plt.show()


#Now, we can group by overnights (11 to 7AM)
#define a column for hours first, and histogram that

approvals['hour'] = approvals.ORDER_INST.dt.hour
approvals['weekday'] = approvals.ORDER_INST.dt.weekday
approvals['overnight'] = ~approvals.ORDER_INST.dt.hour.between(7, 22)
n, bins, patches = plt.hist(approvals.hour, bins= range(25))
plt.xlim(0,24)
plt.xlabel('hour')
plt.ylabel('# of administrations')
# plt.setp(patches[0:6],'facecolor','r')
# plt.setp(patches[23],'facecolor','r')
plt.show()

#visualize distribution by hour
sns.distplot(approvals.hour, bins=range(25))
plt.xlim(0,24)
plt.ylim(0, 0.08)
plt.xlabel('hour of day')
plt.ylabel('probability')
plt.show()

#plot density curve
kde = stats.gaussian_kde(approvals.hour)
curve = np.linspace(0,24, 24*10)
plt.plot(curve,kde(curve))
plt.xlim(0,24)
plt.ylim(0, 0.08)
plt.xlabel('hour of day')
plt.ylabel('probability')
plt.show()

#plot density curve with shade
kde = stats.gaussian_kde(approvals.hour)
curve = np.linspace(0,24, 24*10)
shade = np.linspace(0,7,24*10)
shade2 = np.linspace(23,24,24*10)
plt.plot(curve,kde(curve))
plt.fill_between(shade, kde(shade), alpha=0.5, color = 'r')
plt.fill_between(shade2,kde(shade2),alpha=0.5, color = 'r')
plt.xlim(0,24)
plt.ylim(0, 0.08)
plt.xlabel('hour of day')
plt.ylabel('probability')
plt.show()


percent = kde.integrate_box(0,7) + kde.integrate_box(23,24)




sql2 = 'SELECT * ' \
       'FROM DasonView.PatientAdmissionIds(192183306)'
       # 'WHERE DischargeDateTime >= ? ' \
       # 'and AdmissionDateTime < ? ' \
       # 'and HospitalId = 2000 ' \


encounters = pd.read_sql(sql2, engine)



