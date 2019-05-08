import eda
import unittest
import pandas as pd
from sklearn.model_selection import train_test_split
import sys
sys.path.append('./src')

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

X_train, X_test = train_test_split(profile_merge, test_size=0.20, stratify=profile_merge['Network'])

class TestEda(unittest.TestCase):
    def test_eda(self):
        self.assertEqual(eda.clean_df(X_train.copy())[0].shape[0] > 0, True)
        self.assertEqual(eda.clean_df(X_train.copy())[1].shape[0] > 0, True)
        self.assertEqual(eda.clean_df(X_train.copy())[0].shape[1] > 0, True)
if __name__=='__main__':
    unittest.main()
