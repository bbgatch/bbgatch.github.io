import duckdb
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

duckdb.sql("""
select
    -- case
    --     when lower(name) like '%mrs%' then 'mrs'
    --     when lower(name) like '%miss%' then 'miss'
    --     when lower(name) like '%rev%' then 'rev'
    --     else 'other'
    -- end as title
    -- case when cabin is null then null else 'cabin' end as cabin
    ticket
    ,regexp_extract(ticket, '\d+') as ticket_number
    ,avg(survived) as survival_rate
        
from train
group by 1, 2
""")


# Combine train and test for reviewing values
df = pd.concat([train, test])
df['Cabin'].unique()
df['Cabin'].unique()

df['Cabin'] = df['Cabin'].str.replace('F ', '')


with pd.option_context('display.max_rows', 1000):
    print(df['Ticket'].sort_values(ascending=False))

print(train[['Ticket', 'Survived']].sort_values(by='Ticket', ascending=False).to_string(max_rows=1000))
print(train[['Name']].sort_values(by='Name', ascending=False).to_string(max_rows=1000))

categorical_features = ['Sex', 'Embarked']
numeric_features = ['Pclass', 'Age', 'SibSp', 'Parch', 'Fare']
set(list(df.columns)).symmetric_difference(categorical_features + numeric_features)

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
train.groupby(train['Cabin'].str[0]).agg({
    'PassengerId': 'count',
    'Survived': 'mean'
}).rename(columns={
    'PassengerId': 'Count',
    'Survived': 'SurvivalRate'
})

# train.groupby(train['Cabin'].str[1:]).agg({
#     'PassengerId': 'count',
#     'Survived': 'mean'
# }).rename(columns={
#     'PassengerId': 'Count',
#     'Survived': 'SurvivalRate'
# })


