import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import statsmodels.api as sm
import seaborn as sns
from sklearn import preprocessing
from sklearn.linear_model import Lasso
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

# load datasets and merge
profile_2017 = pd.read_csv('../data/Chicago_Public_Schools_-_School_Profile_Information_SY1617.csv')
header2 = ['Network', 'School_ID', 'School_Name', 'Total', 'White_Student_Count',
          'White_Student_Pct', 'African_American_Count', 'African_America_Pct',
         'AAPI_Count', 'AAPI_Pct', 'Native_American_Count', 'Native_American_Pct',
          'Hispanic_Student_Count', 'Hispanic_Student_Pct',
          'Multi-Racial_Student_Count', 'Multi-Racial_Student_Pct',
          'Asian_Student_Count', 'Asian_Student_Pct', 'Hawaiian_PI_Count',
          'Hawaiian_PI_Pct', 'Not_Available_Count', 'Not_Available_Pct']
demo_data_2017 = pd.read_excel('../data/Demographics_RacialEthnic_2017.xls', 'Schools', skiprows=2, names = header2)
demo_data_2017['School_ID'].astype(int, inplace=True)
profile_merge = pd.merge(demo_data_2017[['Network', 'School_ID']], profile_2017, how='inner', on='School_ID')

# split into train and test sets before cleaning data
X_train, X_test = train_test_split(profile_merge, test_size=0.20, stratify=profile_merge['Network'])

def clean_df(X):
    # get ethnic group totals per district to calculate theil index
    grouped_1 = X.groupby('Network')
    network_totals = grouped_1['Student_Count_Total'].sum()
    black_student_totals = grouped_1['Student_Count_Black'].sum()
    hispanic_student_totals = grouped_1['Student_Count_Hispanic'].sum()
    white_student_totals = grouped_1['Student_Count_White'].sum()
    asian_student_totals = grouped_1['Student_Count_Asian'].sum()
    native_american_totals = grouped_1['Student_Count_Native_American'].sum()
    hawaiian_pi_totals = grouped_1['Student_Count_Hawaiian_Pacific_Islander'].sum()
    asian_pi_totals = grouped_1['Student_Count_Asian_Pacific_Islander'].sum()
    other_ethnicity_totals = grouped_1['Student_Count_Other_Ethnicity'].sum()
    multi_totals = grouped_1['Student_Count_Multi'].sum()
    na_totals = grouped_1['Student_Count_Ethnicity_Not_Available'].sum()

    # calculate network entropies
    df = {'Network_Totals': network_totals, 'Black_Student_Totals': black_student_totals,
         'Hispanic_Student_Totals': hispanic_student_totals, 'White_Student_Totals':
          white_student_totals, 'Asian_Student_Totals': asian_student_totals,
         'Native_American_Student_Totals': native_american_totals, 'Hawaiian_Pacific_Islander_Totals':
         hawaiian_pi_totals, 'Asian_Pacific_Islander_Totals': asian_pi_totals, 'Other_Ethnicity_Totals':
         other_ethnicity_totals, 'Multi_Ethnicity_Totals': multi_totals,
          'Ethnicity_NA_Totals': na_totals}
    df = pd.DataFrame(df)
    df.drop('Other_Ethnicity_Totals', axis=1, inplace=True)
    df['Totals-Ethnicity_NA'] = df['Network_Totals']-df['Ethnicity_NA_Totals']
    df.drop('Ethnicity_NA_Totals', axis=1, inplace=True)

    row_total = []
    test = df['Totals-Ethnicity_NA']
    for n in range(len(df.index)):
        network_total = df.iloc[n, 9]
        x = df.iloc[n, 1:9]
        row_total.append(sum([(j/network_total)*np.log(1/(j/network_total)) for j in x if j!=0]))
    df['Network_Entropy'] = np.array(row_total)

    X['Network_Entropy'] = X['Network']
    network_list = ['Network 1', 'Network 2', 'Network 3', 'Network 4', 'Network 5', 'Network 6',
                    'Network 7', 'Network 8', 'Network 9', 'Network 10', 'Network 11',
                   'Network 12', 'Network 13', 'AUSL', 'Charter', 'Contract', 'ISP', 'Options',
                   'Service Leadership Academies']
    mapdict = {network:df.loc[network, 'Network_Entropy'] for network in network_list}
    X['Network_Entropy'] = X['Network_Entropy'].map(mapdict)

    # Calculate School Entropies

    X.drop('Student_Count_Other_Ethnicity', axis=1, inplace=True)
    X['Adjusted_Counts'] = X['Student_Count_Total'] - X['Student_Count_Ethnicity_Not_Available']
    X.drop('Student_Count_Ethnicity_Not_Available', axis=1, inplace=True)

    row_total = []
    for i in range(len(X.index)):
        school_total = X.iloc[i, 91]
        x = X.iloc[i, 36:44]
        row_total.append(sum([(i/school_total)*np.log(1/(i/school_total)) for i in x if i!=0]))

    X.loc[:,'School_Entropy'] = np.array(row_total)
    X['District_Student_Count'] = X['Network']
    mapdict_count = {network: df.loc[network, 'Totals-Ethnicity_NA'] for network in network_list}
    X['District_Student_Count'] = X['District_Student_Count'].map(mapdict_count)

    # Calculate Theil Scores
    X['School_Theil'] = (X['Adjusted_Counts']*(X['Network_Entropy']-X['School_Entropy'])
                        /(X['Network_Entropy']*X['District_Student_Count']))

    # Cleaning for Linear Regression
    dropped = X.copy()
    to_drop = ['Long_Name', 'Grades_Offered_All', 'Statistics_Description', 'Demographic_Description', 'School_Hours', 'Freshman_Start_End_Time', 'After_School_Hours', 'Earliest_Drop_Off_Time', 'Classification_Description', 'Third_Contact_Title', 'Third_Contact_Name', 'Fourth_Contact_Title', 'Fourth_Contact_Name', 'Fifth_Contact_Title', 'Fifth_Contact_Name', 'Sixth_Contact_Title', 'Sixth_Contact_Name', 'Seventh_Contact_Title', 'Seventh_Contact_Name', 'Rating_Statement', 'School_Year', 'Significantly_Modified', 'Adjusted_Counts', 'Transportation_Bus', 'Transportation_El', 'Transportation_Metra', 'School_ID', 'Legacy_Unit_ID', 'Finance_ID', 'Short_Name', 'Primary_Category', 'Summary', 'Administrator_Title', 'Administrator', 'Secondary_Contact_Title', 'Secondary_Contact', 'Address', 'City', 'State', 'Zip', 'Phone', 'Fax', 'CPS_School_Profile', 'Website', 'Facebook', 'Twitter', 'Youtube', 'Pinterest', 'Attendance_Boundaries', 'Grades_Offered']
    dropped.drop(to_drop, axis=1, inplace=True)
    dropped['PreK_School_Day'] = dropped['PreK_School_Day'].fillna(0)
    dropped['Kindergarten_School_Day'] = dropped['Kindergarten_School_Day'].fillna(0)
    dropped['Classroom_Languages'] = dropped['Classroom_Languages'].fillna(0)
    dropped['Classroom_Languages'] = np.where(dropped['Classroom_Languages'] != 0, 1, 0)
    idx = dropped.index[~dropped['Classroom_Languages'].isnull()]
    dropped['Classroom_Languages'].loc[idx]  = 1
    dropped['Classroom_Languages'].fillna(0, inplace=True)
    dropped['Bilingual_Services'].fillna(0, inplace=True)
    dropped['Refugee_Services'].fillna(0, inplace=True)
    dropped['Title_1_Eligible'].fillna(0, inplace=True)
    dropped['Hard_Of_Hearing'].fillna('False', inplace=True)
    dropped['Visual_Impairments'].fillna('False', inplace=True)
    dropped['PreSchool_Inclusive'] = np.where(dropped['PreSchool_Inclusive'] == 'Y', 1, 0)
    dropped['Preschool_Instructional'] = np.where(dropped['Preschool_Instructional'] == 'Y', 1, 0)
    dropped["Average_ACT_School"] = dropped.groupby("Network").transform(lambda x: x.fillna(x.mean()))['Average_ACT_School']
    dropped["College_Enrollment_Rate_School"] = dropped.groupby("Network").transform(lambda x: x.fillna(x.mean()))['College_Enrollment_Rate_School']
    dropped["Graduation_Rate_School"] = dropped.groupby("Network").transform(lambda x: x.fillna(x.mean()))['Graduation_Rate_School']
    # dropped.dropna(inplace=True)
    dropped['Visual_Impairments'] = np.where(dropped['Visual_Impairments']=='Y', 1, 0)
    dropped['Hard_Of_Hearing'] = np.where(dropped['Hard_Of_Hearing']=='Y', 1, 0)
    dropped['Title_1_Eligible'] = np.where(dropped['Title_1_Eligible']=='Y', 1, 0)
    dropped['Refugee_Services'] = np.where(dropped['Refugee_Services']=='Y', 1, 0)
    dropped['Bilingual_Services'] = np.where(dropped['Bilingual_Services']=='Y', 1, 0)
    dropped['Kindergarten_School_Day'] = np.where(dropped['Kindergarten_School_Day']=='Full Day', 1, 0)
    dropped['Dress_Code'] = np.where(dropped['Dress_Code']=='Y', 1, 0)
    dropped['Is_Pre_School'] = np.where(dropped['Is_Pre_School']=='Y', 1, 0)
    dropped['Is_Elementary_School'] = np.where(dropped['Is_Elementary_School']=='Y', 1, 0)
    dropped['Is_Middle_School'] = np.where(dropped['Is_Middle_School']=='Y', 1, 0)
    dropped['Is_High_School'] = np.where(dropped['Is_High_School']=='Y', 1, 0)
    dropped.drop(['District_Student_Count', 'School_Theil', 'Network_Entropy', 'Location', 'Overall_Rating', 'Graduation_Rate_Mean', 'College_Enrollment_Rate_Mean',
    'Mean_ACT', 'School_Latitude', 'School_Longitude', 'Classroom_Languages', 'Student_Count_Total','Network'], axis=1, inplace=True)

    dropped_dummies = pd.get_dummies(dropped)
    drop_lin_reg = ['Is_Pre_School', 'School_Type_Career academy', 'ADA_Accessible_No/unknown accessibility',
                    'PreK_School_Day_0', 'Rating_Status_Not Applicable']
    for col in drop_lin_reg:
        try:
            dropped_dummies.drop(col, axis=1, inplace=True)
        except KeyError:
            pass
    y = dropped_dummies.pop('School_Entropy')
    X= dropped_dummies
    for col in X.columns:
        col = col.replace(' ', '_')
    X_scaled = preprocessing.scale(X)
    return X, y.values

if __name__ == '__main__':
    X_train, y_train = clean_df(X_train)
    X_test, y_test = clean_df(X_test)
    extra_col = [col for col in X_train.columns if col not in X_test.columns]
    X_train.drop(extra_col, axis=1, inplace=True)
    # X_train = sm.add_constant(X_train)
    # model = sm.OLS(y_train, X_train).fit()
    # predictions = model.predict(X_train)
    # print(model.summary())
