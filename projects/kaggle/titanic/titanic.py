import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


# TODO: standardize and scale the data - this actually made the random forest 
# worse, check both ways
# TODO: add more code explaining EDA
# TODO: Classify ticket IDs based on whether or not they have characters in them?
# Could also then separate the different codes in the ticket IDs.
# TODO: add columns to identify NAs in columns that have them.


# Read in data
train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")

# Check for NaN values in each column
print(train.isna().any())
print(test.isna().any())

train_na = pd.DataFrame(train.drop(columns=['Survived']).isna().any()).reset_index()
train_na.columns = ["column", "train_nans"]

test_na = pd.DataFrame(test.isna().any()).reset_index()
test_na.columns = ["column", "test_nans"]

na_check = train_na.merge(test_na, how="outer", on="column")

train[train[['Age', 'Fare']].isnull()].index.tolist()
train[train['Age'].isnull()].index.tolist()
train[train['Embarked'].isnull()]
train[train['Fare'].isnull()]

# Change Cabin to just yes/no cabin field
train['Cabin'] = np.where(train['Cabin'].isnull(), 0, 1)
test['Cabin'] = np.where(test['Cabin'].isnull(), 0, 1)

# Recode Sex
train['Sex'] = np.where(train['Sex'] == 'female', 0, 1)
test['Sex'] = np.where(test['Sex'] == 'female', 0, 1)

# Trying out KNNImputer for Age
from sklearn.impute import KNNImputer
imputer = KNNImputer()
# Selecting just the Age values in the third column
train['Age'] = imputer.fit_transform(train[['Pclass', 'Age', 'SibSp',
                                            'Parch', 'Fare']])[:, 1]
test[['Age', 'Fare']] = imputer.fit_transform(test[['Pclass', 'Age', 'SibSp',
                                            'Parch', 'Fare']])[:, [1, 4]]

# Impute missing values
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='most_frequent')
train[['Embarked']] = imputer.fit_transform(train[['Embarked']])

# Add dummary variables for Embarked
train = pd.concat([train, pd.get_dummies(train['Embarked'], prefix='Embarked')], axis=1)
test = pd.concat([test, pd.get_dummies(test['Embarked'], prefix='Embarked')], axis=1)
train = train.drop(columns='Embarked')
test = test.drop(columns='Embarked')

# Modeling
# Get response data and choose features
y = train['Survived']
X_fields = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Cabin', 'Embarked_C', 'Embarked_Q', 'Embarked_S'] 
X_train = train[X_fields]
X_test = test[X_fields]

# Scaling
# scaler = preprocessing.StandardScaler().fit(X)
# X_train = scaler.transform(train[X_fields])
# X_test = scaler.transform(test[X_fields])

# Logistic Regression
# model = LogisticRegression(solver='liblinear').fit(X_train, y)
# predictions = model.predict(X_test)

# Run Random Forest Model
# model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=1).fit(X_train, y)
model = RandomForestClassifier().fit(X_train, y)
predictions = model.predict(X_test)

# Save test prediction output
output = pd.DataFrame({'PassengerId': test.PassengerId, 'Survived': predictions})
output.to_csv('data/submission.csv', index=False)
print("Submission saved successfully!")


