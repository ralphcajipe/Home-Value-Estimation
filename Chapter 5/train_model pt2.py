import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import ensemble
from sklearn.metrics import mean_absolute_error
#from sklearn.externals import joblib <-- old version,  discouragement of use
import joblib as joblib

# Load the data set
df = pd.read_csv("ml_house_data_set.csv")

# Remove the fields from the data set that we don't want to include in our model
del df['house_number']
del df['unit_number']
del df['street_name']
del df['zip_code']

# Replace categorical data with one-hot encoded data
features_df = pd.get_dummies(df, columns=['garage_type', 'city'])

# Remove the sale price from the feature data
del features_df['sale_price']

# Create the X and y arrays
X = features_df.to_numpy()
y = df['sale_price'].to_numpy()

# Split the data set in a training set (70%) and a test set (30%)
