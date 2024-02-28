# -*- coding: utf-8 -*-
"""Preprocessing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12X9Ili9bBdAZaypxqJdtnCUOd4L2xM78
"""

import pandas as pd
import glob
from google.colab import files

# Path to the directory containing your CSV files
files_path = '*.csv'

# Use glob to get a list of all CSV files in the specified directory
files = glob.glob(files_path)

# Use a list comprehension to read each file into a DataFrame
dfs = [pd.read_csv(file) for file in files]

# Concatenate the list of DataFrames into a single DataFrame
merged_df = pd.concat(dfs, ignore_index=True)

merged_df.to_csv('preprocessing-normal.csv', index=False)

# @title Processing data

import pandas as pd
from google.colab import files
import requests

# Check if the certificate was registered at letsencrypt.org
def check_certificate_registration(domain):
    # Make a GET request to the LetsEncrypt certificate transparency API
    response = requests.get('https://crt.sh/?i={}'.format(domain))

    # Check if the response status code is 200
    if response.status_code == 200:
        return True
    else:
        return False

# Read the three CSV files
df_conn = pd.read_csv('*.csv')
df_ssl = pd.read_csv('*.csv')
df_x509 = pd.read_csv('*.csv')

# Convert 'server_name' to 'server_name_len' in df_ssl
df_ssl['server_name_len'] = df_ssl['server_name'].astype(str).apply(len)

# Convert 'san.dns' to 'san_dns_num' in df_x509 for the length of DNS
df_x509['san_dns_num'] = df_x509['san.dns'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)

# Convert 'san.ip' to 'san_ip_num' in df_x509 for the length of IP address
df_x509['san_ip_num'] = df_x509['san.ip'].apply(lambda x: len(str(x)) if pd.notnull(x) else 0)

# Extract 'domain_name' in df_x509
df_x509['domain_name'] = df_x509['certificate.subject'].str.extract(r'CN=.*?\.([^,]+)')
df_x509['lets_encrypt'] = (
    (check_certificate_registration(df_x509['domain_name']))
)

# Extract 'first_value' from 'cert_chain_fuids' in df_ssl
df_ssl['first_value'] = df_ssl['cert_chain_fuids'].apply(lambda x: x.split('"')[1] if isinstance(x, str) else None)

# Extract specific columns from each DataFrame
columns_to_extract_df_conn = ['uid', 'proto', 'service', 'duration', 'orig_bytes', 'resp_bytes', 'conn_state', 'history', 'missed_bytes', 'orig_pkts', 'resp_ip_bytes', 'resp_pkts', 'orig_ip_bytes']
columns_to_extract_df_ssl = ['uid', 'version', 'cipher', 'resumed', 'established', 'server_name_len', 'next_protocol', 'validation_status', 'cert_chain_fuids', 'first_value']
columns_to_extract_df_x509 = ['id', 'certificate.version', 'san_dns_num', 'san_ip_num', 'lets_encrypt', 'certificate.key_alg', 'certificate.sig_alg', 'certificate.key_type', 'certificate.key_length', 'basic_constraints.ca', 'certificate.curve']

df_conn_selected = df_conn[columns_to_extract_df_conn]
df_ssl_selected = df_ssl[columns_to_extract_df_ssl]
df_x509_selected = df_x509[columns_to_extract_df_x509]

# Merge df_conn and df_ssl by 'uid'
merged_conn_ssl = pd.merge(df_conn_selected, df_ssl_selected, on='uid', how='inner')
merged_result = pd.merge(merged_conn_ssl, df_x509_selected, left_on='first_value', right_on='id', how='inner')

# Drop unnecessary columns
merged_result = merged_result.drop(columns = ['first_value', 'uid', 'id', 'cert_chain_fuids'])

# Download file after processing
merged_result.to_csv('*.csv', index=False)
files.download('*.csv')