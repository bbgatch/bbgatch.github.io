import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score

# Read in train/test data
train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")

# Look for nulls
train.drop(columns=['Survived', 'PassengerId', 'Name']).isna().sum()
test.drop(columns=['PassengerId', 'Name']).isna().sum()
train.isna().sum()
test.isna().sum()

X_train = train
y_train = train['Survived']
X_test = test

numeric_features = ['Pclass', 'Age', 'SibSp', 'Parch', 'Fare']
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])
categorical_features = ['Sex', 'Embarked']
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)        
    ]
)
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression()
     )
])

model.fit(X_train, y_train)  # Fit model
model.score(X_train, y_train)  # Training set accuracy
y_pred = model.predict(X_test)  # Test set predictions

# Save test prediction output
output = pd.DataFrame({'PassengerId': test.PassengerId, 'Survived': y_pred})
output.to_csv('data/submission.csv', index=False)
print("Submission saved successfully!")

# Check if survival rate varies by cabin letter
# train.groupby(train['Cabin'].str[0]).agg({
#     'PassengerId': 'count',
#     'Survived': 'mean'
# }).rename(columns={
#     'PassengerId': 'Count',
#     'Survived': 'SurvivalRate'
# })

# train.groupby(train['Cabin'].str[1:]).agg({
#     'PassengerId': 'count',
#     'Survived': 'mean'
# }).rename(columns={
#     'PassengerId': 'Count',
#     'Survived': 'SurvivalRate'
# })


