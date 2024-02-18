import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import os
import subprocess
import time

def create_folder_structure(prop, kab, kec, desa, tps):
    folder_path = os.path.join(prop, kab, kec, desa, tps)
    os.makedirs(folder_path, exist_ok=True)

def download_images(urls, download_folder):
    try:
        if not os.path.exists(download_folder):
            # Extract prop, kab, kec, desa, and tps from download_folder
            folder_parts = download_folder.split(os.path.sep)
            if len(folder_parts) >= 5:
                prop, kab, kec, desa, tps = folder_parts[:5]
                create_folder_structure(prop, kab, kec, desa, tps)

        for url in urls:
            if url is None:
                continue  # Skip None URLs
            image_name = os.path.basename(url)
            image_path = os.path.join(download_folder, image_name)
            if os.path.exists(image_path):
                print(f"Image {image_name} already exists. Skipping...")
                continue  # Skip downloading if the image already exists
            subprocess.run(['aria2c', '-d', download_folder, url])
    except Exception as e:
        print(f"An error occurred while downloading images: {e}")
        pass
    
def get_json_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        if url.endswith('.json'):
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to retrieve JSON content from {url}. Status code: {response.status_code}")
                return None
        else:
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to retrieve HTML content from {url}. Status code: {response.status_code}")
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    
def create_folder_structure(prop, kab, kec, desa, tps):
    folder_path = os.path.join(prop, kab, kec, desa, tps)
    os.makedirs(folder_path, exist_ok=True)
    
def is_link_in_table(cur,link_web):
    cur.execute("SELECT * FROM fulldata WHERE link_web = ?", (link_web,))
    row = cur.fetchone()
    if row:
        return True  # Link found in the table
    else:
        return False  # Link not found in the table
    
def get_last_record(cursor):
    qry='SELECT * FROM fulldata ORDER BY tpsid DESC LIMIT 1;'
    cursor.execute(qry)
    return cursor.fetchone()

def json_sorted(json_data,key_sorting):
    # Sort the JSON data based on the "id" key (converted to int)
    sorted_json_data = sorted(json_data, key=lambda x: int(x[key_sorting]))
    return sorted_json_data
def main():
    conn = sqlite3.connect('pemilu2024/pemilu2024.db')
    cursor = conn.cursor()
    # Get the last recorded entry
    last_record = get_last_record(cursor)

    if last_record is None:
        last_prop=last_kab=last_kec=last_desa=last_tps=0
    else:
        
        last_prop = int(last_record[0])
        last_kab = int(last_record[1])
        last_kec = int(last_record[2])
        last_desa = int(last_record[3])
        last_tps = int(last_record[4])

    # URLs
    wil_link = 'https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/'
    data_link = 'https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/'
    target_folder='/media/harry/DATA125/pemilu2024/'

    # Fetching JSON content
    url = 'https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json'
    json_content = get_json_content(url)
    
    if json_content:
        print("Iterating over provinces:")
        for js in json_sorted(json_content,"kode"):
            prop = js.get("kode")
            prop_name = js.get("nama")
            
            if int(prop) < last_prop:
                continue
            
            print(f"Province: {prop} - {prop_name}")

            kab_kode = get_json_content(f'{wil_link}{prop}.json')
            for kab in json_sorted(kab_kode,"kode"):
                kabupaten = kab.get("kode")
                
                if int(prop) == last_prop and int(kabupaten) < last_kab:
                    continue
                
                kec_kode = get_json_content(f'{wil_link}{prop}/{kabupaten}.json')
                for kec in json_sorted(kec_kode,"kode"):
                    kecamatan = kec.get("kode")
                    
                    if int(prop) == last_prop and int(kabupaten) == last_kab and int(kecamatan) < last_kec:
                        continue
                        
                    desa_kode = get_json_content(f'{wil_link}{prop}/{kabupaten}/{kecamatan}.json')
                    for ds in json_sorted(desa_kode,"kode"):
                        desa = ds.get("kode")
                        
                        if int(prop) == last_prop and int(kabupaten) == last_kab and int(kecamatan) == last_kec and int(desa) < last_desa:
                            continue
                        
                        tps_kode = get_json_content(f'{wil_link}{prop}/{kabupaten}/{kecamatan}/{desa}.json')
                        time.sleep(0.01)
                        for tps in json_sorted(tps_kode,"kode"):
                            kode_tps = tps.get("kode")
                            
                            if prop == last_prop and kabupaten == last_kab and kecamatan == last_kec and desa == last_desa and kode_tps < last_tps:
                                continue
                            
                            data_tps = get_json_content(f'{data_link}{prop}/{kabupaten}/{kecamatan}/{desa}/{kode_tps}.json')
                            link_web = f'http://pemilu2024.kpu.go.id/pilpres/hitung-suara/{prop}/{kabupaten}/{kecamatan}/{desa}/{kode_tps}'
                            
                            #buat folder tiap tps
                            if not is_link_in_table(cursor,link_web):
                                cursor.execute("BEGIN TRANSACTION")
                                #create_folder_structure(f'pemilu2024/C1/{prop}', kabupaten, kecamatan, desa, kode_tps)
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
                                    print(suara_sah,link_web)

                                images=data_tps.get("images")
                                if images[0] is not None:
                                    folder=1#f'{target_folder}/C1/{prop}/{kabupaten}/{kecamatan}/{desa}/{kode_tps}'
                                    #download_images(images,folder)
                                else:
                                    folder=None

                                #save to db
                                data=[prop,kabupaten,kecamatan,desa,kode_tps,sah1,sah2,sah3,
                                      suara_sah, suara_total,
                                      pemilih_dpt_j, pemilih_dpt_l, pemilih_dpt_p,
                                      pengguna_dpt_j, pengguna_dpt_l, pengguna_dpt_p,
                                      pengguna_dptb_j, pengguna_dptb_l, pengguna_dptb_p, 
                                      suara_tidak_sah,  
                                      pengguna_total_j, pengguna_total_l, pengguna_total_p, 
                                      pengguna_non_dpt_j, pengguna_non_dpt_l, pengguna_non_dpt_p, 
                                      folder, link_web]

                                #print(data)

                           # Generate the SQL query dynamically
                                placeholders = ', '.join(['?' for _ in range(len(data))])
                                query = f'INSERT INTO fulldata VALUES ({placeholders})' 
                                cursor.execute(query,data)

                                # Commit the transaction
                                cursor.execute("COMMIT")
                                #print("Transaction committed successfully")    

                                #print("------------------")


                    
                
    conn.close()
        
if __name__ == "__main__":
    main()
