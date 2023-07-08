import great_expectations as gx
import os
import pandas as pd
import numpy as np

# Check if environment variable is set otherwise set it to default
# default = realdata
# Input variables
if 'DATAPREP_DATA_FILENAME' in os.environ:
    DATAPREP_EALDATA_FILENAME = os.environ['DATAPREP_DATA_FILENAME']
else:    
    DATAPREP_REALDATA_FILENAME = '/app/data/02_dataprep/02_dataprep_realdata.csv'
# Output variables
if 'DATAPREP_GX_DATA_FILENAME' in os.environ:
    DATAPREP_GX_REALDATA_FILENAME = os.environ['DATAPREP_GX_DATA_FILENAME']
else:
    DATAPREP_GX_REALDATA_FILENAME = '03_dataprep_gx_realdata.parquet'
if 'DATAPREP_GX_DATA_PATH' in os.environ:
    DATAPREP_GX_REALDATA_PATH = os.environ['DATAPREP_GX_DATA_PATH']
else:
    DATAPREP_GX_REALDATA_PATH = '/app/data/03_gx_dataprep'

context = gx.get_context()

validator_log = context.sources.pandas_default.read_csv(DATAPREP_REALDATA_FILENAME)

# #### Anforderungen festlegen (können beliebig viele sein)

# Anforderung an Logdatei: keine Nullwerte
validator_log.expect_column_values_to_not_be_null('Vollstaendiger Name')
validator_log.expect_column_values_to_not_be_null('Anzahl_log_all')

# #### Daten auf Basis der Anforderungen validieren 

checkpoint_log = gx.checkpoint.SimpleCheckpoint(
    name="checkpoint_log",
    data_context=context,
    validator=validator_log,
)

checkpoint_result_log = checkpoint_log.run()

# #### Ergebnis der Validierung ausgeben lassen 

def save_file_with_version(filename, container_path, data):
# Überprüfe, ob die Datei bereits existiert
    if os.path.exists(os.path.join(container_path, filename)):
        base_name, ext = os.path.splitext(filename)
        version = 3

        while True:
            # Erzeuge den neuen Dateinamen mit fortlaufender Nummer
            new_filename = f"{base_name}_V{version}{ext}"
            new_filepath = os.path.join(container_path, new_filename)

            if not os.path.exists(new_filepath):
                break

            version += 1

        # Benenne die bestehende Datei um
        os.rename(os.path.join(container_path, filename), new_filepath)
        print(f'Die Datei {filename} wurde umbenannt zu {new_filename}.')

    # Speichere das DataFrame als Parquet-Datei unter dem ursprünglichen Dateinamen
    new_filepath = os.path.join(container_path, filename)
    data.to_parquet(new_filepath, index=False)
    # data.to_csv(new_filepath, index=False)
    print(f'Die CSV wurde unter {filename} als Parquet-Datei gespeichert.')

if checkpoint_result_log["success"]:
    print("Die Expectations für die Logdatei wurden erfüllt. Die relevanten Spalten 'Vollstaendiger Name'und 'Anzahl_log_all' enthalten keine Nullwerte.")
    log_data = pd.read_csv(DATAPREP_REALDATA_FILENAME)
    save_file_with_version(DATAPREP_GX_REALDATA_FILENAME, DATAPREP_GX_REALDATA_PATH, log_data)
else:
    print("Die Expectations für die Logdatei wurden nicht erfüllt.")
    

