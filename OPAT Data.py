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


data = pd.read_csv('opat_dataset_final.csv')

cleaned = data.dropna(subset = ['RADM_SCR'])
temp1 = data.dropna(subset = ['ID_CLIN_8W_PRIOR'])
cleaned = cleaned.drop(temp1.index) #removes the patients with ID clinic visits prior to admission

# only hash this in for ID_consult cohort
cleaned = cleaned.dropna(subset = ['ID_VISIT_DATE'])

# only hash this in for non ID consult cohort
# temp = cleaned.dropna(subset = ['ID_VISIT_DATE'])
# cleaned = cleaned.drop(temp.index)

predictor = pd.DataFrame(cleaned.RADM_SCR)

target = pd.DataFrame(cleaned.INP_READMSN30_TIME)

target = target.fillna(0)
target = target.astype(bool).astype(int)



both = cleaned[['RADM_SCR','INP_READMSN30_TIME','ED_RADMSN30_DX']]
both.INP_READMSN30_TIME = both.INP_READMSN30_TIME.fillna(0)
both.INP_READMSN30_TIME = both.INP_READMSN30_TIME.astype(bool).astype(int)
both.ED_RADMSN30_DX = both.ED_RADMSN30_DX.fillna(0)
both.ED_RADMSN30_DX = both.ED_RADMSN30_DX.astype(bool).astype(int)
both['combined'] = both.INP_READMSN30_TIME + both.ED_RADMSN30_DX


both[both.combined == 0].RADM_SCR.mean()
both[both.combined == 1].RADM_SCR.mean()


both[both.combined == 1].RADM_SCR.hist()
plt.title(f'score distribution for {len(both[both.combined == 1])} readmissions')
plt.xlabel('Readmission Risk Score')
plt.ylabel('Number of patients readmitted in 30 days')
plt.show()

both[both.combined == 0].RADM_SCR.hist()
plt.title(f'score distribution for {len(both[both.combined == 0])} patients not readmitted')
plt.xlabel('Readmission Risk Score')
plt.ylabel('Number of patients not readmitted in 30 days')
plt.show()




X = both.RADM_SCR
X = sm.add_constant(X) # adding a constant
y = both.combined
mod = sm.Logit(y,X) # creat the model
fit = mod.fit()
p_values = fit.summary()
print(p_values)


# Ok split into non ID consult cohort




