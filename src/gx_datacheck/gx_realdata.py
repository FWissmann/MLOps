import great_expectations as gx
import pandas as pd
import numpy as np
import os

# Check if environment variable is set otherwise set it to default
# Input variables log data
if 'REALDATA_LOG_FILENAME' in os.environ:
    REALDATA_LOG_FILENAME = os.environ['REALDATA_LOG_FILENAME']
else:    
    REALDATA_LOG_FILENAME = '/app/data/00_rawdata/RTWIBNET_W22/RTWIBNet_W22_log.csv'
# Output variables
if 'GX_REALDATA_LOG_FILENAME' in os.environ:
    GX_REALDATA_LOG_FILENAME = os.environ['GX_REALDATA_LOG_FILENAME']
else:
    GX_REALDATA_LOG_FILENAME = '01_gx_realdata_logs.csv'
if 'GX_REALDATA_LOG_PATH' in os.environ:
    GX_REALDATA_LOG_PATH = os.environ['GX_REALDATA_LOG_PATH']
else:
    GX_REALDATA_LOG_PATH = '/app/data/01_gx'
    
# Check if environment variable is set otherwise set it to default
# Input variables grade data
if 'REALDATA_GRADE_FILENAME' in os.environ:
    REALDATA_GRADE_FILENAME = os.environ['REALDATA_GRADE_FILENAME']
else:    
    REALDATA_GRADE_FILENAME = '/app/data/00_rawdata/RTWIBNET_W22/RTWIBNet_W22_grades.csv'
# Output variables
if 'GX_REALDATA_GRADE_FILENAME' in os.environ:
    GX_REALDATA_GRADE_FILENAME = os.environ['GX_REALDATA_GRADE_FILENAME']
else:
    GX_REALDATA_GRADE_FILENAME = '01_gx_realdata_grades.csv'
if 'GX_REALDATA_GRADE_PATH' in os.environ:
    GX_REALDATA_GRADE_PATH = os.environ['GX_REALDATA_GRADE_PATH']
else:
    GX_REALDATA_GRADE_PATH = '/app/data/01_gx'
    

context = gx.get_context()

validator_log = context.sources.pandas_default.read_csv(REALDATA_LOG_FILENAME)
validator_grade = context.sources.pandas_default.read_csv(REALDATA_GRADE_FILENAME)

# #### Anforderungen festlegen (können beliebig viele sein)

# Anforderung an Logdatei: keine Nullwerte
validator_log.expect_column_values_to_not_be_null('Zeit')
validator_log.expect_column_values_to_not_be_null('Vollständiger Name')
validator_log.expect_column_values_to_not_be_null('Komponente')
validator_log.expect_column_values_to_not_be_null('Herkunft')
validator_log.expect_column_values_to_not_be_null('IP-Adresse')

# Anforderungen an Notenliste: Spaltennamen 'Vollständiger Name' und 'bewertung' sind vorhanden
validator_grade.expect_column_names_to_be_in_set(['Vollständiger Name', 'Bewertung'])


# #### Daten auf Basis der Anforderungen validieren 

checkpoint_log = gx.checkpoint.SimpleCheckpoint(
    name="checkpoint_log",
    data_context=context,
    validator=validator_log,
)

checkpoint_grade = gx.checkpoint.SimpleCheckpoint(
    name="checkpoint_grade",
    data_context=context,
    validator=validator_grade,
)

checkpoint_result_log = checkpoint_log.run()
checkpoint_result_grade = checkpoint_grade.run()

# Alternative Programmierung: result = validator.validate()

# #### Ergebnis der Validierung ausgeben lassen 

#filename = 'sim_data.parquet'
#GX_SIMDATA_FILENAME = 'sim_data.csv'
#GX_SIMDATA_PATH = '/app/data/01_data_parquet'

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

    # Speichere das Log-DataFrame als CSV-Datei unter dem ursprünglichen Dateinamen
    new_filepath = os.path.join(container_path, filename)
    #data.to_parquet(new_filepath, index=False)
    data.to_csv(new_filepath, index=False)
    print(f'Die CSV  wurde unter {filename} gespeichert.')
    
    # Speichere das Grade-DataFrame als CSV-Datei unter dem ursprünglichen Dateinamen
    new_filepath = os.path.join(container_path, filename)
    #data.to_parquet(new_filepath, index=False)
    data.to_csv(new_filepath, index=False)
    print(f'Die CSV  wurde unter {filename} gespeichert.')


if checkpoint_result_log["success"]:
    print("Die Expectations für die Logdatei wurden erfüllt. Die relevanten Spalten 'Zeit', 'Vollständiger Name', 'Komponente', 'Herkunft', und 'IP-Adresse' enthalten keine Nullwerte.")
    log_data = pd.read_csv(REALDATA_LOG_FILENAME)
    save_file_with_version(GX_REALDATA_LOG_FILENAME, GX_REALDATA_LOG_PATH, log_data)
else:
    print("Die Expectations für die Logdatei wurden nicht erfüllt.")
    

if checkpoint_result_grade["success"]:
    print("Die Expectations für die Notenliste wurden erfüllt. Die Spalten 'Vollständiger Name' und 'bewertung' sind vorhanden.")
    grade_data = pd.read_csv(REALDATA_GRADE_FILENAME)
    save_file_with_version(GX_REALDATA_GRADE_FILENAME, GX_REALDATA_GRADE_PATH, grade_data)
else:
    print("Die Expectations für die Notenliste wurden nicht erfüllt.")

