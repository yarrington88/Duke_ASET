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


from datetime import datetime, timedelta, date
from scipy import stats

engine = create_engine('mssql+pyodbc://@vwp-dason-dhdb/dason?driver=ODBC Driver 13 for SQL Server?trusted_connection=yes')


sql1 = 'SELECT * ' \
       'FROM DasonView.MedicationAdmin ' \
       'WHERE AdministrationDateTime >= ? ' \
       'and AdministrationDateTime < ? ' \
       'and HospitalId = 2000 ' \
       'and (AgentName = ? OR AgentName = ?)'

#
#
# start_date = date(year=2019, month=12, day=1)
# end_date = date(year=2020, month=3, day=1)
#
# # get our data!!
# allabx_inperiod = pd.read_sql(sql1, engine, params=[start_date, end_date, 'Meropenem', 'Micafungin'])
#


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
approvals = approvals.sort_values(by = 'ORDER_INST')
approvals = approvals.drop_duplicates(['PAT_ENC_CSN_ID','SHORT_MED_NAME'])


# FIRST, let's just plot the total # of mero/mica over a year
approvals.ORDERING_DATE.hist(bins = 61, color = 'deepskyblue', grid = False)
plt.title('Estimated Approvals per Week')
plt.ylabel('# New Antibiotic Starts')
plt.show()




#Next let's group them and plot
grouped = approvals.groupby('SHORT_MED_NAME')
plt.hist([grouped.get_group('MEROPENEM')['ORDERING_DATE'],
          grouped.get_group('MICAFUNGIN')['ORDERING_DATE']],
         bins = 61, stacked= True, color = ['mediumseagreen','slategray'])
plt.title('Estimated Approvals per Week')
plt.ylabel('# New Antibiotic Starts')
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
          bins= 61, stacked= True, color = ['r','deepskyblue'])
labels_protocol =['Overnight Protocol','Text Page']
plt.title('Estimated Approvals per Week')
plt.ylabel('# New Antibiotic Starts')
plt.legend(labels_protocol)
plt.show()


# Try to get data by week of year

approvals['Week'] = approvals.ORDERING_DATE.dt.weekofyear
approvals['year'] = approvals.ORDERING_DATE.dt.year

count_per_week = approvals.groupby(['year','Week']).new_protocol.count()
count_per_week.sort_index()


# Then, lets add data for an ITS analysis, we will have the target and the predictor dataframes

target = pd.DataFrame(count_per_week.reset_index()).new_protocol # this is our target (dependent variable)

predictors = pd.DataFrame()
predictors['Week#'] = range(1,62)
predictors['time after intervention'] = list(np.zeros(shape = 40)) + list(range(1,22))
predictors['time after intervention'] = predictors['time after intervention'].astype(int)
predictors['intervention'] = list(np.zeros(shape = 40)) + list(np.ones(shape = 21))
predictors['intervention'] = predictors['intervention'].astype(int)


# now set up the linear model

lm = linear_model.LinearRegression()
model = lm.fit(predictors, target)
predictions = lm.predict(predictors)


lm.score(predictors, target)
lm.coef_


plt.bar(predictors['Week#'],count_per_week, color = 'deepskyblue', zorder = 1)
plt.scatter(predictors['Week#'], predictions, color = 'darkblue', zorder = 2)
plt.ylim(0, 57)
plt.title('Estimated Approvals per Week')
plt.ylabel('# New Antibiotic Starts')
plt.show()

# the linear regression works but we need stats


X = predictors
X = sm.add_constant(X) # adding a constant
y = target
mod = sm.OLS(y,X) # creat th
fit = mod.fit()
p_values = fit.summary()
print(p_values)

# MORE GRAPHING for day of time distributions

# Now, we can group by overnights (11 to 7AM)
# define a column for hours first, and histogram that

approvals['hour'] = approvals.ORDER_INST.dt.hour
approvals['weekday'] = approvals.ORDER_INST.dt.weekday
approvals['overnight'] = ~approvals.ORDER_INST.dt.hour.between(7, 22)
n, bins, patches = plt.hist(approvals.hour, bins= range(25))
plt.xlim(0,24)
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.xlabel('hour of day')
plt.ylabel('# of orders')
plt.title('Approvals by Hour of Day')
# plt.setp(patches[0:6],'facecolor','r')
# plt.setp(patches[23],'facecolor','r')
plt.show()


# visualize distribution by hour
sns.distplot(approvals.hour, bins=range(25))
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.xlim(0,24)
plt.ylim(0, 0.0825)
plt.xlabel('hour of day')
plt.ylabel('percent of orders during time period')
plt.title('Approvals by Hour of Day')
plt.show()

# plot density curve
kde = stats.gaussian_kde(approvals.hour)
curve = np.linspace(0,24, 24*10)
plt.plot(curve,kde(curve))
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.xlim(0,24)
plt.ylim(0, 0.0825)
plt.xlabel('hour of day')
plt.ylabel('percent of orders during time period')
plt.title('Approvals by Hour of Day')
plt.show()

# plot density curve with shade
kde = stats.gaussian_kde(approvals.hour)
curve = np.linspace(0,24, 24*10)
shade = np.linspace(0,7,24*10)
shade2 = np.linspace(23,24,24*10)
plt.plot(curve,kde(curve))
plt.fill_between(shade, kde(shade), alpha=0.5, color = 'r')
plt.fill_between(shade2,kde(shade2),alpha=0.5, color = 'r')
plt.xlim(0,24)
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.ylim(0, 0.0825)
plt.xlabel('hour of day')
plt.ylabel('percent of orders during time period')
plt.title('Approvals by Hour of Day')
plt.show()


percent = kde.integrate_box(0,7) + kde.integrate_box(23,24)


approvals.PAT_ENC_CSN_ID.nunique()

# can we split into pre and post intervention

pre_intervention = approvals[approvals['ORDERING_DATE'] < datetime(2019, 10, 5)]
post_intervention = approvals[(approvals['ORDERING_DATE'] >= datetime(2019, 10, 5)) & (approvals['ORDERING_DATE'] <= datetime(2019, 12, 31))]

# plot density curves for pre and post
kde1 = stats.gaussian_kde(pre_intervention.hour)
kde2 = stats.gaussian_kde(post_intervention.hour)
curve = np.linspace(0,24, 24*100)
plt.plot(curve,kde1(curve))
plt.plot(curve,kde2(curve))
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.xlim(0,24)
plt.ylim(0, 0.0825)
plt.legend(['Pre-Intervention','Post-Intervention'])
plt.xlabel('hour of day')
plt.ylabel('percent of orders during time period')
plt.title('Approvals by Hour of Day')
plt.show()


# visualize distribution by hour
sns.distplot(post_intervention.hour, bins=range(25))
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.xlim(0,24)
plt.ylim(0, 0.0825)
plt.xlabel('hour of day')
plt.ylabel('percent of orders during time period')
plt.title('Approvals by Hour of Day')
plt.show()


percent_pre = kde1.integrate_box(0,7) + kde1.integrate_box(23,24)
percent_post = kde2.integrate_box(0,7) + kde2.integrate_box(23,24)


# plot density curve with shade
curve = np.linspace(0,24, 24*10)
shade = np.linspace(0,7,24*10)
shade2 = np.linspace(23,24,24*10)
plt.plot(curve,kde1(curve))
plt.plot(curve,kde2(curve))
plt.fill_between(shade, kde1(shade), alpha=0.1, color = 'b', hatch = '-')
plt.fill_between(shade2,kde1(shade2),alpha=0.1, color = 'b', hatch = '-')
plt.fill_between(shade, kde2(shade), alpha=0.1, color = 'r', hatch = '/')
plt.fill_between(shade2,kde2(shade2),alpha=0.1, color = 'r', hatch = '/')
plt.xlim(0,24)
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
plt.ylim(0, 0.0825)
plt.legend(['Pre-Intervention','Post-Intervention'])
plt.xlabel('hour of day')
plt.ylabel('percent of orders during time period')
plt.title('Approvals by Hour of Day')
plt.show()
