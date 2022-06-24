import time
from datetime import date
import pandas as pd

def log_time():
    input("Press enter when you're done. ")
    end = time.time()
    time_elapsed = end - start
    ready_to_record = input("Ready to record " + str(int(round(time_elapsed, 0))) + " seconds for " + task + "? (y/n) ")

    if ready_to_record in ['y', 'Y', 'Yes', 'YES']:
        df = pd.read_csv('data.csv')
        todays_date = str(date.today())
        new_row = pd.DataFrame({"task" : [task], "date" : [todays_date], "time" : [time_elapsed]})
        df = pd.concat([df, new_row])
        print(df)
        df.to_csv('data.csv', index=False)
        print("Recorded " + str(int(round(time_elapsed, 0))) + " seconds on " + todays_date + " for " + task + ".")

    else:
        log_time()

task = input("What task do you want to track? ")
print("Starting tracker for: " + task)
start = time.time()
log_time()



