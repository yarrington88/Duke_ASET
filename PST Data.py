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


data = pd.read_csv('PenicillinSkinTestin_DATA_LABELS_2020-07-08_1030.csv')

data = data[data['Document all actions completed today   (choice=PST)'] == 'Checked']

def score_reaction (row):
    if row['Categories of Listed PCN Reaction (choice=rash)'] == 'Checked' or \
        row['Categories of Listed PCN Reaction (choice=anaphylaxis)'] == 'Checked':
        return 2
    else:
        return 0

def score_time (row):
    if row['How long ago did the index penicillin reaction occur? (choice=</=5 years)'] == 'Checked':
        return 2
    else:
        return 0

def score_treatment (row):
    if row['What reaction management treatment was administered at the time of the index allergic reaction? (choice=None)'] == 'Unchecked':
        return 1
    else:
        return 0

final = data.apply(lambda row: score_reaction(row), axis=1) + \
data.apply(lambda row: score_time(row), axis=1) + \
data.apply(lambda row: score_treatment(row), axis=1)

data['new'] = final

dataknown = data[data['What reaction management treatment was administered at the time of the index allergic reaction? (choice=Unknown)'] == 'Unchecked']
dataunkown = data[data['What reaction management treatment was administered at the time of the index allergic reaction? (choice=Unknown)'] == 'Checked']

data['new'].hist(bins = 6, range = (0,6), label = 'number of PSTs completed per score')
plt.legend(loc = 'upper right')
plt.show()

data['new'].value_counts()
data['new'].count()

ones = data[data.new == 1]
ones['What reaction management treatment was administered at the time of the index allergic reaction? (choice=Unknown)'].value_counts()