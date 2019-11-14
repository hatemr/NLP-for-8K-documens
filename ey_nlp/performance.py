# -*- coding: utf-8 -*-

import pickle
import numpy as np
import numpy.random
import pandas as pd
import matplotlib.pyplot as plt
from IPython import embed

import scipy
#import imp
import time
import os
from IPython import embed

from ey_nlp.utils import dense_identity, drop_column

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV, PredefinedSplit
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer, StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer
from sklearn.base import TransformerMixin

from gensim.test.utils import common_dictionary, common_corpus
from gensim.sklearn_api import HdpTransformer

#import warnings
#warnings.simplefilter(action='ignore', category=FutureWarning)
#warnings.simplefilter("ignore", category=PendingDeprecationWarning)
#warnings.filterwarnings('always')

#%%
# read in data
pickle_in = open("models/grid_search_ret_1-day_v2.pickle","rb")
grid_search = pickle.load(pickle_in)
pickle_in.close()

d = grid_search.cv_results_
results = pd.DataFrame(data=d)
results = results.drop(columns=['mean_fit_time', 'std_fit_time', 'mean_score_time', 'std_score_time', 'params', 'mean_test_score', 'std_test_score'])

embed()
#%%


#%%
data = pd.read_csv('data/test.csv', parse_dates=['Date'])

X_test = data
embed()
#%%


#%%
pickle_in = open("models/svd.pickle","rb")
model_svd = pickle.load(pickle_in)
pickle_in.close()

#%%
lda = model_lda['lda_rf']
svd = model_svd['svd']

#%%
print(lda.best_score_)
print(svd.best_score_)


d = {'DR_method': ['svd', 'lda'], 'CV_AUC': [lda.best_score_, svd.best_score_]}
df = pd.DataFrame(data=d)

ax = df.plot.bar(x='DR_method', y='CV_AUC', rot=0)
plt.savefig('images/results2.png')

#%%
data = pd.read_csv('data/train.csv', parse_dates=['Date'])
X = data['Content_clean'].fillna('').values
y = data['ret_1-day'].fillna(1).values
y_pred = lda.predict_proba(X)

data['y_pred_0'] = y_pred[:,0]
data['y_pred_1'] = y_pred[:,1]
data['y_pred_2'] = y_pred[:,2]

#%%
data1 = data.iloc[:, [0,1,2,19,20,21]]

data1.to_csv('data/for_max/data.csv', index=False)
#%%
data2 = pd.read_csv('data/for_max/data.csv', parse_dates=['Date'])

#%%
plt.xlabel('DR_method')
plt.ylabel('CV_AUC')
plt.bar(df.DR_method, df.CV_AUC, width=0.5);

for i, v in enumerate(df.CV_AUC.values):
    ax.text(v + .0, i + .0, str(v), color='red', fontweight='bold')
    
#%%
# make test predictions for Max (11/6/19)
pickle_in = open("models/grid_search.pickle","rb")
file = pickle.load(pickle_in)
pickle_in.close()

grid_search = file['grid_search']

#%%
test = pd.read_csv('data/test.csv', parse_dates=['Date'])

#%%
X_test = test['Content_clean'].fillna('').values
y_pred = grid_search.predict_proba(X_test)

#%%
y_test = test.loc[:,['Date','Ticker']]
y_test['y_pred_0'] = y_pred[:,0]
y_test['y_pred_1'] = y_pred[:,1]
y_test['y_pred_2'] = y_pred[:,2]

#%%
y_test.to_csv('data/y_pred_oos.csv', index=False)