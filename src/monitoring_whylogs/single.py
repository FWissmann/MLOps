# import pandas module
from datetime import datetime
from whylogs.api.writer.whylabs import WhyLabsWriter
import requests, json, os, pandas as pd, whylogs as why

# Environment variables for WhyLabs
os.environ["WHYLABS_DEFAULT_ORG_ID"] = "org-cF55SZ" # ORG-ID is case sensistive
os.environ["WHYLABS_API_KEY"] = 'hveTvWgi6q.IioRvkcZ6YZJBqP1DCSV2fYtZrInZsnWLL4eCB3DFYrobV0rM3AOo' #API Token
os.environ["WHYLABS_DEFAULT_DATASET_ID"] = 'model-7' #can also be provided as dataset_id param in WhyLabsWriter constructor

# Number of rows to predict
n_rows = 1
# Logging
def get_currentTimeMicro():
    return (f'<{datetime.now().strftime("%H:%M:%S.%f")}> ')
gctm = get_currentTimeMicro

# Check if run on Docker or locally
def is_running_in_docker():
    return os.path.exists('/.dockerenv')
if is_running_in_docker():
    print(f'{gctm()}Main thread: Running in Docker')
    run_in_docker  = True
else:
    print(f'{gctm()}Main thread: Running locally')
    run_in_docker = False

print(f'{gctm()}Main thread: Setting URLs ...')
# The REST API endpoint
if run_in_docker:
    url = 'http://172.17.0.5:8000/predict'
else:
    url = "http://213.136.77.216:8000/predict"

# CSV file to predict
print(f'{gctm()}Main thread: Reading CSV file ...')
# Check if environmet variables are set otherwise use defaults
# Input variables
if 'MONITORING_FILE' in os.environ:
    testfile = os.environ['MONITORING_FILE']
else:
    #testfile = f'C:\Git\MLOps\data\\03_dataprep_gx_testdata.parquet'
    testfile = f'C:\Git\MLOps\data\\02_dataprep_testdata.csv'

df = pd.read_csv(testfile)
df = df.head(n_rows)

df_drop = df
df_drop["('Komponente', 'Anzahl Uebersicht')"] = 0

print(df_drop)
# Convert the DataFrame to the Pandas split format
split_format = df_drop.iloc[0, :].to_dict()
# Encode the split format as a JSON string
dataset = json.dumps(split_format)

print(dataset)

data = {
    'Ereigniskontext': 'Forum: xxx',
    'Beschreibung': 'The user with id ffkdd created xxx.',
    'IP-Adresse': '179.49.49.54',
    'Zeit': '00:02:59',
    'Ereignisname': 'Test Satz erfolgreich',
    'Komponente': 'System'
}

data 

response = requests.post(url, data=split_format)
print(response.text)
import json

# JSON-Daten in ein Python-Wörterbuch umwandeln
data = json.loads(response.text)

# DataFrame erstellen

#df = pd.DataFrame.from_dict(split_format, orient='columns')
df =pd.DataFrame([split_format])
df['prediction'] = data['bewertung_predictions']
print(df)

results = why.log(pandas=df)

# grab profile object from result set
profile = results.profile()

prof_view = profile.view()

# inspect profile as a Pandas DataFrame
prof_df = prof_view.to_pandas()

print("Head of df:")
print(df.head())
print("Head of profile:")
print(profile)

#print(prof_view)

#print(prof_df)


#auf WhyLabs Plattform darstellen lassen
import os
from whylogs.api.writer.whylabs import WhyLabsWriter

os.environ["WHYLABS_DEFAULT_ORG_ID"] = "org-cF55SZ" # ORG-ID is case sensistive
os.environ["WHYLABS_API_KEY"] = 'ISLeaKPb4S.pfYBCL9O9U5ruVWHVGC8gkChH7kOwf6jU540vV7fW3aQlIKcPGMTt' #API Token
os.environ["WHYLABS_DEFAULT_DATASET_ID"] = 'model-6' #can also be provided as dataset_id param in WhyLabsWriter constructor

writer = WhyLabsWriter()

writer.write(file=profile.view())

#Ausgeben, dass Daten zu Whylabs uebertragen worden sind:
print("Profiles are sucessfully  added to Whylabs Plattform.")


#from whylogs.viz import NotebookProfileVisualizer
 
#profile = client.download_artifacts(run_id, "profile.bin", local_dir)
 
#viz = NotebookProfileVisualizer()
#viz.set_profiles(target_profile=profile)
#viz.profile_summary()
