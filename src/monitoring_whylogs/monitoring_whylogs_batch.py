# import pandas module
from datetime import datetime
from whylogs.api.writer.whylabs import WhyLabsWriter
import requests, json, os, pandas as pd, whylogs as why

# Environment variables for WhyLabs
os.environ["WHYLABS_DEFAULT_ORG_ID"] = "org-cF55SZ" # ORG-ID is case sensistive
os.environ["WHYLABS_API_KEY"] = 'ISLeaKPb4S.pfYBCL9O9U5ruVWHVGC8gkChH7kOwf6jU540vV7fW3aQlIKcPGMTt' #API Token
os.environ["WHYLABS_DEFAULT_DATASET_ID"] = 'model-9' #can also be provided as dataset_id param in WhyLabsWriter constructor

# Number of rows to predict
n_rows = 10
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
    url = 'http://172.17.0.5:8000/batch_predict'
else:
    url = "http://213.136.77.216:8000/batch_predict"

# CSV file to predict
print(f'{gctm()}Main thread: Reading CSV file ...')
file = '/home/aml/MLOps/pipeline/00_sim_data_output/simulated_data_grade.csv'

# making dataframe
df = pd.read_csv(file)
df = df.head(n_rows)

# drop columns
df_drop = df.drop(columns=['Betroffene/r Nutzer/in', 'Vollständiger Name', 'Abschlussnote', 'Herkunft'], axis=1)

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
    print("Batch prediction successful")
    # Parse the response JSON, process the results as needed
    results = response.json()
    #print(results)

    # JSON-Daten in ein Python-Wörterbuch umwandeln
    data_results = json.loads(response.text)
    data_results = data_results['data']

    # DataFrame erstellen
    #df_results = pd.DataFrame.from_dict(data_results, orient='index')
    
    #print(df_results.head())
    print("Tatsächliche Abschlussnoten: ")
    print(df["Abschlussnote"])
    df_results = pd.DataFrame(data_results)
    print("Vorhergesagte Abschlussnoten: ")
    print(df_results[0])
    print("Differenz: ")
    print(df_results[0] - df["Abschlussnote"])

# results_whylogs = why.log(pandas=df_results)

#     # grab profile object from result set
#     profile = results_whylogs.profile()

#     prof_view = profile.view()

#     # inspect profile as a Pandas DataFrame
#     prof_df = prof_view.to_pandas()

#     print("Head of df:")
#     print(df_results.head())
#     print("Head of profile:")
#     print(profile)

#     #print(prof_view)

#     #print(prof_df)

#     writer = WhyLabsWriter()

#     #writer.write(file=profile.view())

#     #Ausgeben, dass Daten zu Whylabs uebertragen worden sind:
#     print("Profiles are sucessfully added to Whylabs Plattform.") 
# """
else:
    print(f"Error in batch prediction: {response.status_code}, {response.text}")
