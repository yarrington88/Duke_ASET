import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from sqlalchemy import create_engine
from datetime import datetime, timedelta, date
from scipy import stats
import seaborn as sns
from scipy.ndimage.filters import gaussian_filter

# initialization parameters and dates
start_date = date(year=2018, month=7, day=1)
end_date = date(year=2019, month=7, day=1)
unit = 'Sepsis'
indication = 'Skin/Soft Tissue'
remove_cefazolin = 'No'

# create the engine for accessing sql database
engine = create_engine('mssql+pyodbc://@vwp-dason-db/dason?driver=ODBC Driver 13 for SQL Server?trusted_connection=yes')

sql1 = 'SELECT * ' \
       'FROM DasonView.ClinicalIndication ' \
       'WHERE AdministrationDateTime >= ? ' \
       'and AdministrationDateTime < ? ' \
       'and HospitalId = 2000 ' \
       'and ReportedClinicalIndication = ?'


# get our data!!
allabx_inperiod = pd.read_sql(sql1, engine,
                              params=[(start_date - timedelta(days=0)), (end_date + timedelta(days=0)), indication])

# create a spectrum score dictionary to each antimicrobial
abx_dict = {'Ciprofloxacin': '8', 'Vancomycin': '5', 'Piperacillin with Tazobactam': '8',
            'Amoxicillin with Clavulanate': '6', 'Oseltamivir': '0', 'Ceftriaxone': '5',
            'Ampicillin with Sulbactam': '6', 'Sulfamethoxazole with Trimethoprim': '4', 'Gentamicin': '5',
            'Cefazolin': '3', 'Penicillin G': '2', 'Acyclovir': '0', 'Cefepime': '6', 'Voriconazole': '0',
            'Pentamidine': '0', 'Metronidazole': '2', 'Rifaximin': '0', 'Cephalexin': '2', 'Fluconazole': '0',
            'Micafungin': '0', 'Azithromycin': '4', 'Doxycycline': '5', 'Tetracycline': '5', 'Ganciclovir': '0',
            'Meropenem': '10', 'Ceftazidime': '4', 'Daptomycin': '5', 'Clindamycin': '4', 'Ertapenem': '9',
            'Moxifloxacin': '10', 'Cefotaxime': '5', 'Nystatin': '0', 'Ampicillin': '2', 'Aztreonam': '3',
            'Nitrofurantoin': '1', 'Levofloxacin': '9', 'Cefuroxime': '5', 'Amantadine': '0', 'Atovaquone': '0',
            'Valganciclovir': '0', 'Dapsone': '0', 'Clotrimazole': '0', 'Linezolid': '6',
            'Imipenem with Cilastatin': '11', 'Tigecycline': '13', 'Tedizolid': '6', 'Cefoxitin': '5',
            'Valacyclovir': '0', 'Amikacin': '6', 'Rifampin': '3', 'Amoxicillin': '2', 'Posaconazole': '0',
            'Quinupristin with Dalfopristin': '0', 'Amphotericin B liposomal': '0',
            'Abacavir/Dolutegravir/Lamivudine': '0', 'Dolutegravir': '0', 'Lamivudine': '0', 'Abacavir': '0',
            'Palivizumab': '0', 'Hydroxychloroquine': '0', 'Isavuconazole': '0', 'Ceftolozane/Tazobactam': '10',
            'Nafcillin': '1', 'Neomycin': '0', 'Letermovir': '0', 'Ribavirin': '0', 'Erythromycin': '2',
            'Amphotericin B': '0', 'Tobramycin': '5', 'Ceftaroline': '8', 'Minocycline': '5', 'Cefdinir': '3',
            'Colistin': '5', 'Polymyxin B': '5', 'Foscarnet': '0', 'Ceftazidime/Avibactam': '10', 'Fidaxomicin': '0',
            'Emtricitabine/Tenofovir': '0', 'Darunavir/Cobicistat': '0', 'Darunavir': '0', 'Ritonavir': '0',
            'Isoniazid': '0', 'Ethambutol': '0', 'Tenofovir': '0', 'Trimethoprim': '4', 'Penicillin V': '2',
            'Atazanavir/Cobicistat': '0', 'Sulfadiazine': '0', 'Pyrimethamine': '0',
            'Efavirenz/Emtricitabine/Tenofovir': '0', 'Cidofovir': '0', 'Fosfomycin': '8', 'Raltegravir': '0',
            'Efavirenz': '0', 'Emtricitabine': '0', 'Entecavir': '0', 'Cefixime': '3', 'Primaquine': '0',
            'Clarithromycin': '4', 'Elvitegravir/Cobicistat/Emtricitibine/Tenofovir': '0',
            'Bictegravir/Emtricitabine/Tenofovir': '0', 'Ivermectin': '0', 'Flucytosine': '0', 'Etravirine': '0',
            'Terbinafine': '0', 'Bacitracin': '0', 'Lamivudine/Zidovudine': '0', 'Ritonavir-Lopinavir': '0',
            'Abacavir/Lamivudine': '0', 'Zidovudine': '0', 'Streptomycin': '0',
            'Emtricitabine/Rilpivirine/Tenofovir': '0', 'Methenamine': '0', 'Ledipasvir/Sofosbuvir': '0',
            'Dicloxacillin': '1', 'Oxacillin': '1', 'Rifabutin': '3', 'Griseofulvin': '0', 'Maraviroc': '0',
            'Famciclovir': '0', 'Chloramphenicol': '6', 'Quinidine': '0', 'Elbasvir/Grazoprevir': '0', 'Zanamivir': '0',
            'Atazanavir': '0', 'Abacavir/Lamivudine/Zidovudine': '0', 'Atovaquone/Proguanil': '0', 'Rilpivirine': '0',
            'Nevirapine': '0', 'Demeclocycline': '5', 'Dalbavancin': '5', 'Paromomycin': '0', 'Albendazole': '0',
            'Velpatasvir/Sofosbuvir': '0', 'Tinidazole': '0', 'Quinine': '0', 'Glecaprevir/Pibrentasvir': '0',
            'Baloxavir': '0', 'Peramivir': '0', 'Artemether-Lumefantrine': '0', 'Ketoconazole': '0', 'Bedaquiline': '0',
            'Pyrazinamide': '0', 'Itraconazole': '0', 'Oritavancin': 5, 'Fosamprenavir': '0', 'Didanosine': '0',
            'Ombitasvir/Paritaprevir/Ritonavir/Dasabuvir': '0', 'Simeprevir': '0', 'Sofosbuvir': '0',
            'Rifapentine': '0', 'Adefovir': '0', 'Nelfinavir Mesylate': '0', 'Dolutegravir/Rilpivirine': '0',
            'Saquinavir': '0', 'Telavancin': '5', 'Daclatasvir': '0', 'Nitazoxanide': '0', 'Anidulafungin': '0',
            'Praziquantel': '0', 'Darunavir/Cobicistat/Emtricitabine/Tenofovir': '0', 'Chloroquine': '0',
            'Delafloxacin': '11', 'Meropenem/Vaborbactam': '11', 'Baloxavir Marboxil': '0', 'Caspofungin': '0',
            'Lopinavir/Ritonavir': '0', 'Doravirine': '0', 'Cefadroxil': '5', 'Cefpodoxime': '5',
            'Cefotetan': '5', 'Rimantadine': '0', 'Stavudine': '0', 'Cefprozil': '3', 'Doripenem': '11'}

# this next line checks to find the Nan and add them to the list, if we need it
# allabx_inperiod[allabx_inperiod.Spectrum.isnull()].AgentName.unique()

# Assign the spectrum score to antibiotic data
allabx_inperiod['Spectrum'] = allabx_inperiod['AgentName'].map(abx_dict)
allabx_inperiod['Spectrum'] = allabx_inperiod['Spectrum'].astype('int')

# Assign a new variable that indicates the date, the day of week, the time of day, etc.
allabx_inperiod['Date'] = allabx_inperiod['AdministrationDateTime'].dt.date
allabx_inperiod['Weekday'] = allabx_inperiod['AdministrationDateTime'].dt.weekday
allabx_inperiod['Time'] = allabx_inperiod['AdministrationDateTime'].dt.hour

# Remove all antimicrobials that have spectrum score of 0
allabx_inperiod = allabx_inperiod[allabx_inperiod.Spectrum > 0]



# Find the mean per day summed spectrum score per day of week
# first have to dedupe the agent given for any specific day so you don't sum multiple doses.  Then on each DATE
# a PATIENT will have a specific sum.  We will then reset_index so that we can sort it by weekday and get the mean
# spectrum for each weekday.


admissions = allabx_inperiod.groupby(['AdmissionId', 'PatientId'])
# should prob grab the first 24 hours of antibiotics rather than the first calendar day

idx = admissions.AdministrationDateTime.transform(min) + timedelta(hours=24) > allabx_inperiod.AdministrationDateTime
firsts = allabx_inperiod[idx]
deduped = firsts.copy().drop_duplicates(['AgentName', 'PatientId', 'AdmissionId'], keep='first')


#remove cefazolin?
if remove_cefazolin == 'Yes':
    deduped = deduped[deduped.AgentName != 'Cefazolin']

#remove all antimicrobials for prophylaxis
deduped = deduped[~deduped.ClinicalIndicationCategoryName.str.contains('Prophylaxis', na = False)]

#Make sure it is on the first day of therapy
# deduped = deduped[deduped.DOT == 1]

count = deduped.HospitalId.count()

# make a column in deduped with the first admin time of all abx
deduped['first admin'] = deduped.groupby(['Date', 'PatientId', 'Weekday']).Time.transform('min')

# now we can group and have the first administration time (in hour of day) as part of the group index
# This group consists of all antibiotics given to a patient on a specific date (Weekday and first admin times are
# redundant, but helpful to have in the group indices)
groupbypatient = deduped.groupby(['Date', 'PatientId', 'Weekday', 'first admin'])



# find the sum of the ASI per each group above
summedASIperday = groupbypatient.Spectrum.sum()
summedASIperday = summedASIperday.reset_index()
mean_per_day = summedASIperday.groupby('Weekday').Spectrum.mean()
ste_per_day = summedASIperday.groupby('Weekday').Spectrum.sem()

# ok but we also need to get the total mean for weekday/day, weekday/night, weekend/day and weekend/night
# so let's split it up, Mon 8AM to Friday at 7pm is 'weekday', Friday 7pm to Monday 8a is weekend.


summedASIperday['Weekend/Day'] = (summedASIperday['Weekday'] >= 5) & \
                                 ((summedASIperday['first admin'] < 19) &
                                  (summedASIperday['first admin'] >= 8))

summedASIperday['Weekend/Night'] = ((summedASIperday['Weekday'] >= 5) &
                                    (summedASIperday['Weekend/Day'] != True)) | \
                                   ((summedASIperday['Weekday'] == 0) &
                                    (summedASIperday['first admin'] < 8)) | \
                                   ((summedASIperday['Weekday'] == 4) &
                                    (summedASIperday['first admin'] >= 19))

summedASIperday['Weekday/Day'] = (summedASIperday['Weekday'] < 5) & \
                                 ((summedASIperday['first admin'] < 19) &
                                  (summedASIperday['first admin'] >= 8))

summedASIperday['Weekday/Night'] = (summedASIperday['Weekend/Day'] != True) & (
        summedASIperday['Weekend/Night'] != True) & \
                                   (summedASIperday['Weekday/Day'] != True)

# visualize the data!!!!!


# Make easy variables to compare
WDD = summedASIperday[summedASIperday['Weekday/Day'] == True].Spectrum.reset_index(drop=True)
WDN = summedASIperday[summedASIperday['Weekday/Night'] == True].Spectrum.reset_index(drop=True)
WED = summedASIperday[summedASIperday['Weekend/Day'] == True].Spectrum.reset_index(drop=True)
WEN = summedASIperday[summedASIperday['Weekend/Night'] == True].Spectrum.reset_index(drop=True)

# Plot a histogram distribution of the spectrum scores for each group

fig = plt.figure(figsize = (5,10))
# ax = fig.add_subplot(1, 1, 1)
# ax.set_ylabel(
# ax.set_xlabel('Spectrum Score')
ax1 = fig.add_subplot(4, 1, 1)
ax2 = fig.add_subplot(4, 1, 2)
ax3 = fig.add_subplot(4, 1, 3)
ax4 = fig.add_subplot(4, 1, 4)
ax1.hist(WDD, list(range(0, 25, 1)))
ax1.set_title(f'Weekday Day ({WDD.count()})')
ax2.hist(WDN, list(range(0, 25, 1)))
ax2.set_title(f'Weekday Night ({WDN.count()})')
ax3.hist(WED, list(range(0, 25, 1)))
ax3.set_title(f'Weekend Day ({WED.count()})')
ax4.hist(WEN, list(range(0, 25, 1)))
ax4.set_title(f'Weekend Night ({WEN.count()})')
plt.xlabel('Spectrum Score')
fig.text(0.015, .5, 'Number of administrations', ha='center', va='center', rotation='vertical')
plt.show()

# Boxplots for each of the 4 groups
fig, axs = plt.subplots(figsize=(6, 6))
plt.title(f'({unit}, {count} Antibiotic Starts)')
plt.ylabel('ASI per Antibiotic Start')
axs.boxplot([WDD, WDN, WED, WEN], showmeans=True, showfliers=False)
axs.set_ylim(0, 25.15)
plt.xticks([1, 2, 3, 4], ['Weekday Day', 'Weekday Night', 'Weekend Day', 'Weekend Night'])
plt.show()

# Means per grouped time of the weekday/end/day/night
weekday_day_mean = summedASIperday.groupby('Weekday/Day').Spectrum.mean()[True]
weekday_night_mean = summedASIperday.groupby('Weekday/Night').Spectrum.mean()[True]
weekend_day_mean = summedASIperday.groupby('Weekend/Day').Spectrum.mean()[True]
weekend_night_mean = summedASIperday.groupby('Weekend/Night').Spectrum.mean()[True]

WDN_compare = sp.stats.mannwhitneyu(WDD, WDN, alternative='two-sided')
WED_compare = sp.stats.mannwhitneyu(WDD, WED, alternative='two-sided')
WEN_compare = sp.stats.mannwhitneyu(WDD, WEN, alternative='two-sided')

# PLOT THE BAR AND BOXPLOTS per day of the week

plt.bar(['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'], mean_per_day, yerr=ste_per_day * 1.96)
plt.axis([-0.5, 6.5, 0, 12])
plt.title(f'({unit}, {count} Admissions, {start_date} to {end_date})')
plt.ylabel('Mean of Cumulative ASI')
plt.show()

summedASIperday.boxplot(column='Spectrum', by='Weekday')
plt.suptitle('')
plt.title(f'({unit}, {count} Admissions, {start_date} to {end_date})')
plt.ylabel('Mean of Cumulative ASI')
plt.xlabel('Day of Week')
plt.xticks([1, 2, 3, 4, 5, 6, 7], ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'])
plt.show()

# get the heatmap and add buffers to the sides and top to make it more presentable on the graph
heatmapgroup = summedASIperday.groupby(['Weekday', 'first admin'])
heatmap_score = heatmapgroup.Spectrum.mean().unstack(
    level=1).transpose()  # this finds mean of the spectrum sum per day/hour combo and then puts it into dataframe, and transposes DF
heatmap_score.columns = ['Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
heatmap_score_buffer = heatmap_score.copy()
heatmap_score_buffer['Sun 2'] = heatmap_score['Mon']
heatmap_score_buffer['Mon 2'] = heatmap_score['Mon']
order = ['Sun 2', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun', 'Mon 2']
heatmap_score_buffer = heatmap_score_buffer[order]
heatmap_score_buffer.loc[24] = heatmap_score_buffer.iloc[23]

# PLOT HEAT MAP

fig, ax = plt.subplots(figsize=(6, 6))
figure = ax.pcolormesh(heatmap_score_buffer, cmap='viridis', shading='gouraud')
plt.yticks(np.arange(0, len(heatmap_score_buffer.index), 1), heatmap_score.index)
plt.xticks(np.arange(0, len(heatmap_score_buffer.columns), 1), ['', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'])
bar = fig.colorbar(figure)
plt.title(f'{indication}, {count} Admissions')
plt.ylabel('Hour')
plt.xlabel('Day of Week')
plt.axis([0.5, 7.5, 0, 24])
plt.show()

# PLOT USING SEABORN
plt.figure(figsize=(6, 6))
ax = sns.heatmap(heatmap_score, annot=True, cmap='viridis')
ax.invert_yaxis()
plt.title(f'{indication}, {count} Admissions')
plt.yticks(np.arange(0, len(heatmap_score_buffer.index), 1), heatmap_score.index, rotation='horizontal')
plt.xlabel('Day of Week')
plt.ylabel('Hour')
plt.show()

print(WDD.describe(), WDN.describe(), WED.describe(), WEN.describe())
print(WDD.median(), WDN.median(), WED.median(), WEN.median())


# Check a certain hour of day.
deduped[deduped.Time == 23].AgentName.value_counts().nlargest(5)
