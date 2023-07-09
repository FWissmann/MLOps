# import pandas module
from datetime import datetime
from whylogs.api.writer.whylabs import WhyLabsWriter
import requests, json, os, pandas as pd, whylogs as why

# Environment variables for WhyLabs
os.environ["WHYLABS_DEFAULT_ORG_ID"] = "org-cF55SZ" # ORG-ID is case sensistive
os.environ["WHYLABS_API_KEY"] = 'vKz4qloaIx.gbgYmWML8mAWRpXkPpjKq1f5XiXmIAyDW7ZJbdo440VPdVKkYiieu' #API Token

# Number of rows to predict
n_rows = 0
# Logging
def get_currentTimeMicro():
    return (f'<{datetime.now().strftime("%H:%M:%S.%f")}> ')
gctm = get_currentTimeMicro

# Check if run on Docker or locally
def is_running_in_docker():
    return os.path.exists('/.dockerenv')
if is_running_in_docker():
    print(f'{gctm()}Running in Docker')
    run_in_docker  = True
else:
    print(f'{gctm()}Running locally')
    run_in_docker = False

print(f'{gctm()}Setting URLs ...')
# The REST API endpoint
if run_in_docker:
    url = 'http://172.17.0.5:8000/batch_predict'
else:
    url = "http://213.136.77.216:8000/batch_predict"

# CSV file to predict
print(f'{gctm()}Reading CSV file ...')
# Check if environmet variables are set otherwise use defaults
# Input variables
if 'MONITORING_FILE' in os.environ:
    testfile = os.environ['MONITORING_FILE']
else:
    testfile = f'./data/03_gx_dataprep/03_dataprep_gx_testdata.parquet'

print(f'{gctm()}Datei für Test: {testfile}')
# making dataframe
if testfile.endswith('.parquet'):
    df = pd.read_parquet(testfile)
elif testfile.endswith('.csv'):
    df = pd.read_csv(testfile)

if n_rows > 0:
    df = df.head(n_rows)

# Add missing columns
df_drop = df
if "('Komponente', 'Anzahl Uebersicht')" not in df_drop.columns:
    df_drop["('Komponente', 'Anzahl Uebersicht')"] = 0

# Convert the DataFrame to the Pandas split format
split_format = df_drop.to_dict('split')

# Encode the split format as a JSON string
dataset = json.dumps(split_format)

# Make a POST request
response = requests.post(
    url, 
    data={
        'dataset': dataset,
    }
)

# Process the response
if response.status_code == 200:
    print(f'{gctm()}Batch prediction successful')
    results = response.json()

    # JSON-Daten in ein Python-Wörterbuch umwandeln
    data_results = json.loads(response.text)
    data_results = data_results['data']

    # Ergebnisse in ein Pandas-Dataframe umwandeln
    df_results = df_drop
    df_results["output"] = [item for sublist in data_results for item in sublist]

    # monitoring ueber whylogs
    
    # Entscheidung ob Predictions oder Monitoring
    if "bewertung" in df_results:
        print(f'{gctm()}Dataframe enthält Spalte bewertung, daher Logging von Regression Metrics')
        os.environ["WHYLABS_DEFAULT_DATASET_ID"] = 'model-9' #can also be provided as dataset_id param in WhyLabsWriter constructor
        results = why.log_regression_metrics(df_results, target_column="bewertung", prediction_column="output", log_full_data=True)

        profile = results.profile()

        # Profil auf WhyLabs uebertragen
        writer = WhyLabsWriter()
        writer.write(file=profile.view())

        # Daten erfolgreich auf Whylabs uebertragen
        print(f'{gctm()}Profil wurde zu WhyLabs übertragen.') 

        df_results.to_csv(f'./data/05_results/05_results.csv', index=False)

    else:
        print(f'{gctm()}Dataframe enthält Spalte bewertung, daher Logging von Inputs')
        os.environ["WHYLABS_DEFAULT_DATASET_ID"] = 'model-10' #can also be provided as dataset_id param in WhyLabsWriter constructor
        results = why.log(df_results)

        profile = results.profile()
        profile.set_dataset_timestamp(datetime.now())

        # Profil auf WhyLabs uebertragen
        writer = WhyLabsWriter()
        writer.write(file=profile.view())

        # Daten erfolgreich auf Whylabs uebertragen
        print(f'{gctm()}Profil wurde zu WhyLabs übertragen.') 

        df_results.to_csv(f'./data/05_results/05_results.csv', index=False)

else:
    print(f'Error in batch prediction: {response.status_code}, {response.text}')