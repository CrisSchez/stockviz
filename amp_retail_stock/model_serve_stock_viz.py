import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
#from churnexplainer import ExplainedModel
import pickle
import os
#from pandas.io.json import json_normalize
from pandas import json_normalize

from categoricalencoding import CategoricalEncoder
import cdsw, numpy
filename=os.getcwd()+"/models/champion/champion.pkl"
#Load the model save earlier.
loaded_model = pickle.load(open(filename, 'rb'))
filename=os.getcwd()+"/models/champion/ce.pkl"
#Load the model save earlier.
ce = pickle.load(open(filename, 'rb'))


# *Note:* If you want to test this in a session, comment out the line 
#`@cdsw.model_metrics` below. Don't forget to uncomment when you
# deploy, or it won't write the metrics to the database 
#cols=['shipmode', 'city', 'state', 'postalcode', 'region','productid', 'sales', 'profit', 'segment', 'loyaltycard', 'avgmonthlycharges',
#      'category', 'subcategory', 'ordermonth', 'weekday', 'day']
cols=['state', 'productid', 'category', 'subcategory', 'ordermonth', 'weekday', 'day','unitprice']

catcols = ['state',  'productid','category', 'subcategory']
#cols = (('gender', True),
#        ('SeniorCitizen', True),
#        ('Partner', True),
#        ('Dependents', True),
#        ('tenure', False),
#        ('PhoneService', True),
#        ('MultipleLines', True),
#        ('InternetService', True),
#        ('OnlineSecurity', True),
#        ('OnlineBackup', True),
#        ('DeviceProtection', True),
#        ('TechSupport', True),
#        ('StreamingTV', True),
#        ('StreamingMovies', True),
#        ('Contract', True),
#        ('PaperlessBilling', True),
#        ('PaymentMethod', True),
#        ('MonthlyCharges', False),
#        ('TotalCharges', False))

@cdsw.model_metrics
# This is the main function used for serving the model. It will take in the JSON formatted arguments , calculate the probablity of 
# churn and create a LIME explainer explained instance and return that as JSON.

def predict(args):
  df=pd.DataFrame(args["data"]["rows"])
  df.columns=args["data"]["colnames"]
  #df.convert_dtypes=args["data"]["coltypes"]
  df.columns=args["data"]["colnames"]
  #df.convert_dtypes=args["data"]["coltypes"]
  #df=df.sort_index(axis = 1)
  #df.columns= sorted(cols,key=str.lower)
  df=df[cols]
  numCols=['ordermonth', 'weekday', 'day','unitprice']
  for ncol in numCols:
    df[ncol]=pd.to_numeric(df[ncol])
  

  data = df[[c for c in cols]]

  for col in catcols:
    data[col] = pd.Categorical(data[col])
  
  
  X = ce.transform(data)
 
  
  
  df['final']=np.ceil(loaded_model.predict(X))
  #df['final']=df['MonthlyCharges']*df['tenure']*df['TotalCharges']
  df['final']=df['final'].fillna(0)
  outRows = []
  for row in range(len(df['final'])):
    outRows.append([int(df['final'][row])])
   
  
 

  return {'data': {'colnames': ['result'],
  'coltypes': ['INT'],
  'rows': outRows}}