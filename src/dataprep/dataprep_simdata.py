#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import os
import locale
from datetime import datetime

# Check if environmet variables are set otherwise use defaults
# Input variables
if 'GX_SIMDATA_FILENAME' in os.environ:
    GX_SIMDATA_FILENAME = os.environ['GX_SIMDATA_FILENAME']
else:
    GX_SIMDATA_FILENAME = '/app/data/01_gx/01_gx_simdata.csv'

# Output variables
if 'DATAPREP_SIMDATA_FILENAME' in os.environ:
    DATAPREP_SIMDATA_FILENAME = os.environ['DATAPREP_SIMDATA_FILENAME']
else:
    DATAPREP_SIMDATA_FILENAME = '02_dataprep_simdata.csv'
if 'DATAPREP_SIMDATA_PATH' in os.environ:
    DATAPREP_SIMDATA_PATH = os.environ['DATAPREP_SIMDATA_PATH']
else:
    DATAPREP_SIMDATA_PATH = '/app/data/02_dataprep'

# erstes CSV einlesen mit den Log-Daten
sim_data = pd.read_csv(GX_SIMDATA_FILENAME)

# Neues df erstellen nur User und Abschlussnote
# Index wird standardmäßig beibehalten

# sim_data_grade = sim_data[['Vollständiger Name', 'Abschlussnote']]
sim_data_grade = sim_data.groupby('Vollständiger Name')['Abschlussnote'].mean()

# als df anlegen
# Note auf eine Dezimale runden
# Spalten umbenennen
sim_data_grade = pd.DataFrame(sim_data_grade).round(1)
sim_data_grade = sim_data_grade.rename(columns={'Vollständiger Name': 'Vollständiger Name', 'Abschlussnote': 'bewertung'})

# Noten >4.0 mit 5.0 ersetzen
sim_data_grade.loc[sim_data_grade['bewertung'] > 4.0, 'bewertung'] = 5.0

# eindeutige Werte der Spalten 'Voll.Name', 'Komponente', 'Herkunft' von sim_data als array ausgeben 

unique_name = sim_data['Vollständiger Name'].unique()
unique_komponente = sim_data['Komponente'].unique()
unique_herkunft = sim_data['Herkunft'].unique()

# länge der Arrays ausgeben 

length_name = len(unique_name)
length_komponente = len(unique_komponente)
length_herkunft = len(unique_herkunft)

# neues df mit Auswertparameter von sim_data nach Spalte 'Vollständiger Name' erstellen
# pro eindeutiger Parameter in den Spalten 'Komponente' und 'Herkunft' soll eine neue Spalte in grouped_sim erstellen werden
# Hierzu beziehen wir uns auf die zuvor erstellen arrays mit der Anzahl der eindeutigen Werte einer Spalte unique_komponente
# Nur so viele neue Spalten werden generiert, wie es eindeutige Werte pro Spalte hat
# Der Name der neuen Spalte entspricht 'Anzahl' + Name eindeutiger Wert 

sim_data['Herkunft'] = sim_data['Herkunft'].astype(str)
sim_data['Komponente'] = sim_data['Komponente'].astype(str)

# Neues gruppiertes DataFrame erstellen und Index zurücksetzen
grouped_data = sim_data.groupby('Vollständiger Name').agg({
    'Komponente': [(f'Anzahl {name}', lambda x, name=name: (x == name).sum()) for name in unique_komponente],
    'Herkunft': [(f'Anzahl {name}', lambda x, name=name: (x == name).sum()) for name in unique_herkunft],
    'IP-Adresse': 'nunique'
}).reset_index()

# im Datengenerator leider englische Namen verwendet... kann auskommentiert werden:
locale.setlocale(locale.LC_TIME, "en_US.UTF-8") # englische Monatsbezeichnung

# Anzahl der Vorkommen eines Users im ursprünglichen sim_data
user_counts = sim_data['Vollständiger Name'].value_counts().rename('Anzahl_log_all')

# nur das Datum extrahieren
# teilweise gemisches Datenformat... d.h. Formatangabe rausnehmen #, format='%d. %B %Y, %H:%M:%S'
sim_data['Zeit'] = pd.to_datetime(sim_data['Zeit']).dt.date

# Definiere den Start- und Endzeitpunkt für den ersten Zeitraum
# Start: erster Log-Eintrag
start_date = sim_data['Zeit'].min()

# 16 Wochen später als der erste Eintrag (Dauer eines Semesters)
end_date = start_date + pd.DateOffset(weeks=20)
# Beobachtung: teilweise Einträge nach 16 Wochen - Enddatum = Letzter Log-Eintrag der Logdatei
# end_date = sim_data['Zeit'].max()

# Definiere den Zeitraumabstand
period_offset = pd.DateOffset(weeks=2)

# Liste zur Speicherung der Zeitraumgrenzen
period_boundaries = []

# Generiere die Zeitraumgrenzen mit einem Abstand von zwei Wochen
# pro Zeitraumgrenze wird es eine neue Spalte in dem DataFrame log_counts geben
# Wenn keine Werte für die Zeiträume z.B. bei 16 Wochen vorhanden sind, werden die Spalten mit dem Mittelwert der vorherigen
# Zeitraumsgrenzen aufgefüllt

current_date = start_date
# Error-Handling
current_date = pd.Timestamp(current_date)
while current_date <= end_date:
    period_boundaries.append(current_date)
    current_date += period_offset

# Erstelle das DataFrame log_counts mit den Zeitraumspalten
log_counts = pd.DataFrame()
log_counts['Vollständiger Name'] = user_counts.index.unique() # Eindeutige Namen im Index verwenden
log_counts['Anzahl_log_all'] = user_counts.reindex(log_counts['Vollständiger Name']).values # Werte entsprechend den eindeutigen Namen im Index reindexieren

# Überprüfung des letzten Datums in sim_data
last_date = sim_data['Zeit'].max()

# Auffüllen der fehlenden Zeiträume basierend auf dem letzten Datum
for i in range(len(period_boundaries)):
    period_start = period_boundaries[i]
    if i == len(period_boundaries) - 1:
        # Letzter Zeitraum, fiktiven Wert verwenden - Mittelwert der vorherigen Zeiträume
        log_counts[f'Anzahl_log_f{i+1}'] = np.mean(log_counts[[f'Anzahl_log_f{j}' for j in range(1, i+1)]], axis=1).astype(int)
    else:
        period_end = period_boundaries[i + 1]
        # Error-Handling
        period_start_date = period_start.date()
        period_end_date = period_end.date()
        if last_date >= period_end_date:
            # Datum liegt im Zeitraum, Log-Einträge zählen
            log_entries_by_period = sim_data[(sim_data['Zeit'] >= period_start_date) & (sim_data['Zeit'] < period_end_date)].groupby('Vollständiger Name').count()
            log_counts[f'Anzahl_log_f{i+1}'] = log_entries_by_period['Zeit'].reindex(log_counts['Vollständiger Name'], fill_value=0).values
        else:
            # Datum liegt außerhalb des Zeitraums, mit Mittelwert auffüllen als Ganzzahl
            log_counts[f'Anzahl_log_f{i+1}'] = np.mean(log_counts[[f'Anzahl_log_f{j}' for j in range(1, i+1)]], axis=1).astype(int)


# Anzahl log-Einträge mit sim_data mergen nach 'Vollständiger Name'
grouped_data_sim = grouped_data.merge(log_counts, on='Vollständiger Name')

# Abschlussnote aus nach jeweiligen User mergen

grouped_data_grade = pd.merge(grouped_data_sim, sim_data_grade, on='Vollständiger Name', how='left')
grouped_data_grade = grouped_data_grade.drop(('Vollständiger Name', ''), axis=1)

grouped_data_grade = grouped_data_grade.rename(columns={'Vollständiger Name': 'Vollstaendiger Name'})

print(grouped_data_grade.head())

filename = DATAPREP_SIMDATA_PATH + '/' + DATAPREP_SIMDATA_FILENAME
grouped_data_grade.to_csv(filename, index=False)