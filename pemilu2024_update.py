''' 
after you finish download
alter your table to add id column with autoincrement
and ts to save timestamp
1. 
-- Create a temporary table with the auto-incrementing ID column
CREATE TABLE TempTable AS
SELECT rowid as id, *
FROM fulldata;

-- Drop the original fulldata table
DROP TABLE fulldata;

-- Rename the temporary table to fulldata
ALTER TABLE TempTable RENAME TO fulldata;


2.
-- Add a timestamp column named 'timestamp_column'
ALTER TABLE fulldata
ADD COLUMN ts TIMESTAMP;


'''


import requests
import json
import sqlite3
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

 
def get_json_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Configure retry mechanism
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        if url.endswith('.json'):
            response = session.get(url, headers=headers, timeout=(3, 10))  # 3 seconds for connection timeout, 10 seconds for read timeout
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to retrieve JSON content from {url}. Status code: {response.status_code}")
                return None
        else:
            response = session.get(url, headers=headers, timeout=(3, 10))  # 3 seconds for connection timeout, 10 seconds for read timeout
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to retrieve HTML content from {url}. Status code: {response.status_code}")
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def get_data_siluman(cursor):
    qry='select propid,kabid,kecid,desid,tpsid,link_web,id from fulldata where sah1+sah2+sah3>306 and propid<>99'
    cursor.execute(qry)
    return cursor.fetchall()

 #update data yang bermasalah
#select * from fulldata where sah1+sah2+sah3>306 and propid<>99 

def main():

    data_link = 'https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/'
    folder_db_pemilu='/home/zoom/Documents/pemilu2024/'
    conn = sqlite3.connect(f'{folder_db_pemilu}pemilu2024.db')
    cursor = conn.cursor()
    
    siluman=get_data_siluman(cursor)
    jum_siluman=len(siluman)
    print(f'Jumlah tps siluman = {jum_siluman}')
    count=1
    counter=1
    #iterate to all rows
    cursor.execute("BEGIN TRANSACTION")
    for row in siluman:
        prop=row[0]
        kabupaten=row[1]
        kecamatan=row[2]
        desa=row[3]
        kode_tps=row[4]
        link_web=row[5]
        id=row[6]
        data_tps = get_json_content(f'{data_link}{prop}/{kabupaten}/{kecamatan}/{desa}/{kode_tps}.json')
                            

        perolehan=data_tps.get("chart")
        sah1 = sah2 = sah3 = 0  # Reset variables to 0
        if perolehan is not None:
            sah1=perolehan.get("100025")
            sah2=perolehan.get("100026")
            sah3=perolehan.get("100027")
        
        data_adm=data_tps.get("administrasi")
        suara_sah = suara_total = pemilih_dpt_j = pemilih_dpt_l = pemilih_dpt_p = 0  # Reset variables to 0
        pengguna_dpt_j = pengguna_dpt_l = pengguna_dpt_p = pengguna_dptb_j = pengguna_dptb_l = pengguna_dptb_p = 0  # Reset variables to 0
        suara_tidak_sah = pengguna_total_j = pengguna_total_l = pengguna_total_p = 0  # Reset variables to 0
        pengguna_non_dpt_j = pengguna_non_dpt_l = pengguna_non_dpt_p = 0  # Reset variables to 0
        
        if data_adm is not None:
            suara_sah=data_adm.get("suara_sah")
            suara_total=data_adm.get("suara_total")
            pemilih_dpt_j=data_adm.get("pemilih_dpt_j")
            pemilih_dpt_l=data_adm.get('pemilih_dpt_l')
            pemilih_dpt_p=data_adm.get('pemilih_dpt_p')
            pengguna_dpt_j=data_adm.get('pengguna_dpt_j')
            pengguna_dpt_l=data_adm.get('pengguna_dpt_l')
            pengguna_dpt_p=data_adm.get('pengguna_dpt_p')
            pengguna_dptb_j=data_adm.get('pengguna_dptb_j')
            pengguna_dptb_l=data_adm.get('pengguna_dptb_l')
            pengguna_dptb_p=data_adm.get('pengguna_dptb_p')
            suara_tidak_sah=data_adm.get('suara_tidak_sah')
            pengguna_total_j=data_adm.get('pengguna_total_j')
            pengguna_total_l=data_adm.get('pengguna_total_l')
            pengguna_total_p=data_adm.get('pengguna_total_p')
            pengguna_non_dpt_j=data_adm.get('pengguna_non_dpt_j')
            pengguna_non_dpt_l=data_adm.get('pengguna_non_dpt_l')
            pengguna_non_dpt_p=data_adm.get('pengguna_non_dpt_p')
            #print(suara_sah,link_web)
        
        images=data_tps.get("images")
        if images[0] is not None:
            folder=1#f'{target_folder}/C1/{prop}/{kabupaten}/{kecamatan}/{desa}/{kode_tps}'
            #download_images(images,folder)
        else:
            folder=None
        #save to db
        
       # Update the row in the database
        qry = """
        UPDATE fulldata 
        SET sah1=?, sah2=?, sah3=?, 
            suara_sah=?, suara_total=?, 
            pemilih_dpt_j=?, pemilih_dpt_l=?, pemilih_dpt_p=?, 
            pengguna_dpt_j=?, pengguna_dpt_l=?, pengguna_dpt_p=?, 
            pengguna_dptb_j=?, pengguna_dptb_l=?, pengguna_dptb_p=?, 
            suara_tidak_sah=?, 
            pengguna_total_j=?, pengguna_total_l=?, pengguna_total_p=?, 
            pengguna_non_dpt_j=?, pengguna_non_dpt_l=?, pengguna_non_dpt_p=?, 
            link_web=?, ts=?
        WHERE id=?
        """
        data = (sah1, sah2, sah3, 
                    suara_sah, suara_total, 
                    pemilih_dpt_j, pemilih_dpt_l, pemilih_dpt_p, 
                    pengguna_dpt_j, pengguna_dpt_l, pengguna_dpt_p, 
                    pengguna_dptb_j, pengguna_dptb_l, pengguna_dptb_p, 
                    suara_tidak_sah, 
                    pengguna_total_j, pengguna_total_l, pengguna_total_p, 
                    pengguna_non_dpt_j, pengguna_non_dpt_l, pengguna_non_dpt_p, 
                    link_web, data_tps.get("ts"),
                    id)
    
        cursor.execute(qry, data)
        print(data)
        print(f'{counter}/{jum_siluman} {link_web} updated..')
        count+=1
        counter+=1
        if count == 50:
            cursor.execute("COMMIT")
            cursor.execute("BEGIN TRANSACTION")
            count = 0  # Reset counter
    
    # Commit the transaction
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
