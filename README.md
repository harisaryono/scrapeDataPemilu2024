# scrapeDataPemilu2024
 scrape data dari website kpu
 
 langkah 1. buat 1 database sqlite, beri nama pemilu2024.db
 langkah 2. selanjutnya buat table dengan copas perintah sql dibawah ini 
 

 
 CREATE TABLE "fulldata" (
	"propid"	INTEGER,
	"kabid"	TEXT,
	"kecid"	TEXT,
	"desid"	TEXT,
	"tpsid"	TEXT,
	"sah1"	INTEGER,
	"sah2"	INTEGER,
	"sah3"	INTEGER,
	"suara_sah"	INTEGER,
	"suara_total"	INTEGER,
	"pemilih_dpt_j"	INTEGER,
	"pemilih_dpt_l"	INTEGER,
	"pemilih_dpt_p"	INTEGER,
	"pengguna_dpt_j"	INTEGER,
	"pengguna_dpt_l"	INTEGER,
	"pengguna_dpt_p"	INTEGER,
	"pengguna_dptb_j"	INTEGER,
	"pengguna_dptb_l"	INTEGER,
	"pengguna_dptb_p"	INTEGER,
	"suara_tidak_sah"	INTEGER,
	"pengguna_total_j"	INTEGER,
	"pengguna_total_l"	INTEGER,
	"pengguna_total_p"	INTEGER,
	"pengguna_non_dpt_j"	INTEGER,
	"pengguna_non_dpt_l"	INTEGER,
	"pengguna_non_dpt_p"	INTEGER,
	"link_folder"	TEXT,
	"link_web"	TEXT
);

langkah 3. Pastikan menggunakan python versi 3. Saya pakai versi 3.8
langkah 4. pastikan semua requirement terpenuhi. Bila belum ada, install menggunakan perintah pip


import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import os
import subprocess
import time

langkah 5. jalankan program dengan perintah: python3 pemilu2024_sorted.py

**** catatan ********

dalam program ini saya tidak mendownload formulir c1, saya hanya menandai pada folder_web angka 1 bila formulir sudah bisa didownload

program khusus download, akan saya buat kemudian, dengan membaca database hasil scraping tadi.


