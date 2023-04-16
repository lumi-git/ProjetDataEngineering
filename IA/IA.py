import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

nomLine = "C1"
sens = 0
# open the dataframe from the csv file data_C1_0.csv
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '/DataIA/data_' + nomLine + '_' + sens + '.csv'))

# split the data into train and test
X_train, X_test, y_train, y_test = train_test_split(
    df[['avg_distance', 'avg_time_diff', 'bus_count', 'length', 'day']],
    df[['maxFreqL', 'maxFreqM', 'maxFreqH']], test_size=0.2)

# normalize the data columns per column between 0 and 1
for col in X_train.columns:
    scaler = MinMaxScaler()
    X_train[col] = scaler.fit_transform(X_train[[col]])
    X_test[col] = scaler.transform(X_test[[col]])

# Convert the target variable to a single column of labels
y_train = y_train.idxmax(axis=1)
y_test = y_test.idxmax(axis=1)

# Create and train a random forest classifier
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Make predictions on the test set
y_pred = clf.predict(X_test)

# Calculate the accuracy of the model
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: ", accuracy)

# Create and train a random forest classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Convert the trained model to ONNX format
initial_type = [('input', FloatTensorType([None, 5]))]
onnx_model = convert_sklearn(clf, initial_types=initial_type)

# Save the ONNX model to a file
onnx.save(onnx_model, f'Models/model_{nomLine}_sens{sens}.onnx')
