# Copas faceid 9, untuk export 
import customtkinter
from tkinter import PhotoImage
from PIL import Image, ImageTk
from CTkTable import *
from pytablericons import TablerIcons, OutlineIcon
import cv2
import numpy as np
from threading import Thread
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from operator import itemgetter
from datetime import datetime, timedelta
from datetime import time as time2
from bson import ObjectId
import sys
import os, shutil
from functools import partial
from multiprocessing import Process, freeze_support, Queue, cpu_count, Event, active_children
import dlib
import uuid
import os
from tktooltip import ToolTip
import tempfile, os
from CTkScrollableDropdown import *
import asyncio
import motor.motor_asyncio
import nest_asyncio
import requests
from CTkMessagebox import CTkMessagebox

# Enable nested event loops if running in Jupyter or a similar environment
nest_asyncio.apply()

# Use this code to signal the splash screen removal.
if "NUITKA_ONEFILE_PARENT" in os.environ:
   splash_filename = os.path.join(
      tempfile.gettempdir(),
      "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
   )

   if os.path.exists(splash_filename):
      os.unlink(splash_filename)
# np.save("data/temp/jadwal", [])

stop_event = Event()

cpu_count = cpu_count()

kamera_ok = False
ruang_ok = True
jeda_ok = False
dur_ok = False
exp_ok = False
toleransi_ok = False
nama_ok = False

db_url = "mongodb+srv://afriandypramana:bczFDLSJSzrATKdP@cluster0.yqmayik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
   client_async = motor.motor_asyncio.AsyncIOMotorClient(db_url)
except:
   print("Gagal terhubung dengan basisdata. Pastikan perangkat memiliki koneksi internet & coba lagi.")
   sys.exit()

db_async = client_async["face_identification_3"]  # Replace with your database name

client = MongoClient(db_url, server_api=ServerApi('1'))
db = client["face_identification_3"]

def ambil_ruangan(ruangan_lama):
   try_count = 0
   while try_count < 10:
      try:
         try_count += 1
         print(f"Mengambil data ruangan...")
         client = MongoClient(db_url, server_api=ServerApi('1'))
         db = client["face_identification_3"]
         collection_ruangan = db["ruangan"]
         ruang = collection_ruangan.find({"sedang_digunakan": False})
         list_ruang = []
         for el in ruang:
            list_ruang.append(el)
         new_list = sorted(list_ruang, key=itemgetter("kode_ruangan"))
         print("Data ruangan didapati")
         return new_list
      except Exception as e:
         pass
   print("Mengambil data ruangan gagal : ", e)
   return ruangan_lama

def ambil_ruangan_2():
   try:
      print("Mengambil data ruangan...")
      client = MongoClient(db_url, server_api=ServerApi('1'))
      db = client["face_identification_3"]
      collection_ruangan = db["ruangan"]
      ruang = collection_ruangan.find({"sedang_digunakan": False})
      list_ruang = []
      for el in ruang:
         list_ruang.append(el)
      new_list = sorted(list_ruang, key=itemgetter("kode_ruangan"))
      # print("new list : ", new_list)
      np.save("data/temp/ruang", new_list)
      print("Data ruangan didapati")
   except Exception as e:
      print("Mengambil data ruangan gagal : ", e)
      np.save("data/temp/ruang", [])

def ambil_aktivitas(tanggal):
   try_count = 0
   while try_count < 10:
      try:
         try_count += 1
         print(f"Mengambil data aktivitas...")
         client = MongoClient(db_url, server_api=ServerApi('1'))
         db = client["face_identification_3"]
         collection_aktivitas = db["aktivitas"]
         aktivitas = collection_aktivitas.find({"tanggal": tanggal})
         # aktivitas = []
         list_aktivitas = []
         for el in aktivitas:
            list_aktivitas.append(el)
         np.save("data/temp/aktivitas", list_aktivitas)
         print("Data aktivitas didapati: ", len(list_aktivitas))
         break
      except Exception as e:
         print("Ambil data aktivitas gagal : ", e)

def ambil_aktivitas2(start_date):
   try_count = 0
   while try_count < 10:
      try:
         try_count += 1
         print(f"Mengambil data aktivitas...")
         client = MongoClient(db_url, server_api=ServerApi('1'))
         db = client["face_identification_3"]
         collection_aktivitas = db["aktivitas2"]
         # aktivitas = collection_aktivitas.find({"tanggal": tanggal})
         aktivitas = collection_aktivitas.find({
            "timestamp": {
               "$gte": start_date,
               "$lt": datetime.combine(start_date, time2.max)
            }
         }).sort("timestamp", 1)
         # aktivitas = []
         list_aktivitas = []
         for el in aktivitas:
            list_aktivitas.append(el)
         np.save("data/temp/aktivitas", [])
         print("Data aktivitas didapati: ", list_aktivitas)
         break
      except Exception as e:
         print("Ambil data aktivitas gagal : ", e)

def insert_ruangan(kode, nama):
   print("Insert ruangan...")
   try:
      client = MongoClient(db_url, server_api=ServerApi('1'))
      db = client["face_identification_3"]
      collection_ruangan = db["ruangan"]
      kode = kode.replace(" ", "").upper()
      match_kode = collection_ruangan.find_one({"kode_ruangan": kode})
      if match_kode:
         return False, "Kode ruangan yang anda masukan telah terdaftar."
      else:
         collection_ruangan.insert_one({"kode_ruangan": kode, "nama_ruangan": nama.title(), "sedang_digunakan": False})
         print("Berhasil insert ruangan.")
         return True, ""
   except Exception as e:
      print("Gagal insert ruangan: ", e)
      return False, "Kesalahan dalam akses basis data."

def check_nama_komputer(nama_komputer):
   try:
      client = MongoClient(db_url, server_api=ServerApi('1'))
      db = client["face_identification_3"]
      collection_frame = db["frame"]
      match = collection_frame.find_one({"nama_komputer": nama_komputer})
      if match:
         return False
      return True
   except Exception as e:
      return False

def ambil_jadwal_all(tanggal):
   print("Mengambil jadwal...")
   client = MongoClient(db_url, server_api=ServerApi('1'))
   db = client["face_identification_3"]
   collection_jadwal = db["jadwal"]
   collection_ruangan = db["ruangan"]
   collection_dosen = db["dosen"]

   datetime_object = datetime.strptime(tanggal, "%Y-%m-%d") + timedelta(days=1)

   # print("datetime object ", datetime_object)

   waktu_sekarang = datetime.now()

   jadwal = collection_jadwal.find({"waktu_selesai": {"$gt": waktu_sekarang, "$lt": datetime_object}}).to_list(None)
   ruangan = collection_ruangan.find({}).to_list(None)
   dosen = collection_dosen.find({}).to_list(None)

   result = []
   for el in jadwal:
      for ruang in ruangan:
         if str(el["ruangan_id"]) == str(ruang["_id"]):
            el["ruangan"] = f"{ruang['kode_ruangan']} - {ruang['nama_ruangan']}"
            for dos in dosen:
               if str(el["dosen_id"]) == str(dos["_id"]):
                  el["dosen"] = {"id_dosen": dos["_id"], "nama_dosen": dos["nama"], "foto_profil_path": dos["foto_profil_path"]}
                  break
            break
      # if waktu_sekarang < el["waktu_selesai"]:
      #    result.append(el)
      result.append(el)

   print("Data jadwal didapati: ", len(result))
   np.save("data/temp/jadwal_all", result)


class CustomThread(Thread):
   def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
      super().__init__(group, target, name, args, kwargs)
      self._return = None
   
   def run(self):
      if self._target is not None:
         self._return = self._target(*self._args, **self._kwargs)
   
   def join(self, timeout=None):
      super().join(timeout=timeout)
      return self._return


def get_cam_index2():
   for cap in captures:
      cap.release()
   print("Mencari kamera yang terhubung...")
   index = 0
   arr = []
   while True:
      cap = cv2.VideoCapture(index)
      if not cap.read()[0]:
         break
      else:
         arr.append(f"Kamera {index}")
      cap.release()
      index += 1
   return arr

def get_cam_index():
   print("Mencari kamera yang terhubung...")
   index = 0
   arr = []
   while True:
      cap = cv2.VideoCapture(index)
      if not cap.read()[0]:
         break
      else:
         arr.append(f"Kamera {index}")
      cap.release()
      index += 1
   return arr

def on_select(dropdown_id, choice):
   print(f"Dropdown {dropdown_id} selected: {choice}")

def cek_cams(*args):
   global kamera_ok
   global cam_ls
   global curr_index

   # print("ceking cam")

   cam_ls_in = []
   for x in opsi_cam:
      cam_ls_in.append(x.get())
   st = set(cam_ls_in)
   if len(st) == len(cam_ls_in):
      kamera_ok = True
   else:
      kamera_ok = False

   for a,b in zip(cam_ls, cam_ls_in):
      if a != b:
         curr_index = int(str(b).split(" ")[1])


   cam_ls = cam_ls_in

   check_all()

def cek_cams2(var, *args):
   global kamera_ok
   global cam_ls
   global curr_index

   # print("New value:", int(str(var.get()).split(" ")[1]))
   curr_index = int(str(var.get()).split(" ")[1])

   cam_ls_in = []
   for x in opsi_cam:
      cam_ls_in.append(x.get())
   st = set(cam_ls_in)
   if len(st) == len(cam_ls_in):
      kamera_ok = True
   else:
      kamera_ok = False

   cam_ls = cam_ls_in

   check_all()

def cek_ruang(*args):
   global ruang_ok
   global ruang_ls
   
   ls = []
   for x in opsi_ruang:
      ls.append(x.get())
   # st = set(ls)
   # if len(st) == len(ls):
   #    ruang_ok = True
   # else:
   #    ruang_ok = False
   
   ruang_ls = ls

   # print("ruang ls :", ruang_ls)

   # check_all()


def check_exp(*args):
   global exp_ok
   
   expires = exp_entry.get()
   if not expires:
      exp_ok = False
   else:
      exp_ok = True
      try:
         a = int(expires)
         if a <= 0:
            exp_ok = False
      except:
         exp_ok = False

   check_all()

def check_nama(*args):
   global nama_ok
   nama = nama_entry.get()
   if not nama:
      nama_ok = False
   elif nama.isspace():
      nama_ok = False
   else:
      nama_ok = True

   check_all()

def check_dur(*args):
   global dur_ok
   
   durasi = dur_entry.get()
   if not durasi:
      dur_ok = False
   else:
      dur_ok = True
      try:
         a = int(durasi)
         if a <= 0:
            dur_ok = False
      except:
         dur_ok = False

   check_all()


def check_jeda(*args):
   global jeda_ok
   jeda = jeda_entry.get()
   if not jeda:
      jeda_ok = False
   else:
      jeda_ok = True
      try:
         a = int(jeda)
         if a <= 0:
            jeda_ok = False
      except:
         jeda_ok = False
   
   check_all()

def check_toleransi(*args):
   global toleransi_ok
   toleransi = toleransi_entry.get()
   if not toleransi:
      toleransi_ok = False
   else:
      toleransi_ok = True
      try:
         val = float(toleransi)
         if val <= 0 or val >= 1:
            toleransi_ok = False
      except:
         toleransi_ok = False
   
   check_all()


def check_all():
   if kamera_ok and ruang_ok and dur_ok and jeda_ok and exp_ok and toleransi_ok and nama_ok:
      button_mulai.configure(state="normal")
   else:
      button_mulai.configure(state="disabled")


def refresh_kamera(my_frame):
   global opsi_ruang
   global opsi_cam
   global framex_list
   global opsi_ruang_2
   global opsi_kam_2
   global cam_indexes
   global frames
   global captures
   global cam_ls


   for x in framex_list:
      x.pack_forget()

   # for cap in captures:
   #    cap.release()

   cam_indexes = get_cam_index2()
   
   # frames = []
   # captures = []
   # cam_ls = []
   
   # for cam in cam_indexes:
      # frames.append(False)
      # captures.append(cam)
      # cam_ls.append(cam)

   id_jum_kam.configure(text=len(cam_indexes))

   opsi_cam = []
   opsi_ruang = []

   framex_list = []

   opsi_ruang_2 = []
   opsi_kam_2 = []

   print(f"Ditemukan {len(cam_indexes)} kamera terhubung.")

   for x in range(len(cam_indexes)):
      framex = customtkinter.CTkFrame(my_frame)
      
      clicked_opsi_kam = customtkinter.StringVar()
      clicked_opsi_kam.set(cam_indexes[0])
      opsi_cam.append(clicked_opsi_kam)
      opsi_2 = customtkinter.CTkOptionMenu(framex, variable=opsi_cam[x], values=cam_indexes, text_color="black", width=115, font=customtkinter.CTkFont("", 14))
      opsi_kam_2.append(opsi_2)
      opsi_2.grid(column=0, row=0)
      opsi_cam[x].trace_add("write", partial(cek_cams2, opsi_cam[x]))

      clicked_opsi_ruang = customtkinter.StringVar()
      clicked_opsi_ruang.set(ruang_indexes[0])
      opsi_ruang.append(clicked_opsi_ruang)
      opsi = customtkinter.CTkOptionMenu(framex, variable=opsi_ruang[x], values=ruang_indexes , text_color="black", width=242, font=customtkinter.CTkFont("", 14))
      CTkScrollableDropdown(opsi, values=ruang_indexes, height=300, justify="left", width=265, font=customtkinter.CTkFont("", 14))
      opsi_ruang_2.append(opsi)
      opsi.grid(column=1, row=0, padx=(10,0))
      # opsi_ruang[x].trace_add("write", cek_ruang)
      
      framex.pack(padx=5, pady=5)
      framex_list.append(framex)
   
   get_all_captures()

def konfirmasi_quit():
   np.save(f"data/temp/ruang", [])
   np.save("data/temp/jadwal_all", [])
   
   p2.join()
   p2.terminate()
   p3.join()
   p3.terminate()
   p4.join()
   p4.terminate()
   root.destroy()
   sys.exit()

   # Close the SFTP connection
   # sftp.close()
   # transport.close()


def refresh_cek_db():
   global ruang
   global ruang_indexes
   global ruang_list
   global opsi_cam
   global opsi_ruang
   global opsi_kam_2
   global opsi_ruang_2
   global framex_list
   global framex

   # ruang = np.load("data/temp/ruang.npy", allow_pickle=True)
   
   if len(ruang) == 0:
      ambil_ruangan_2()
      ruang = np.load("data/temp/ruang.npy", allow_pickle=True)

   cek_database(ruang)

   if len(ruang) > 0:
      frame1_1.grid(row=1, column=0, ipadx=12, pady=(15, 10))
      frame1_2.grid(row=1, column=1, ipadx=12, pady=(15, 10))
      frame2.grid(column=0, row=2, padx=10,pady=5, sticky="w", columnspan=2)
      my_frame.grid(column=0, row=3, padx=10, pady=(0,10), sticky="w", columnspan=2)

      ruang_indexes = []
      ruang_list = []

      for el in ruang:
         if len(f"{el['kode_ruangan']} - {el['nama_ruangan']}") > 28 :
            ruang_indexes.append(f"{el['nama_ruangan']} ({el['kode_ruangan']})"[:28] + "..")
         else:
            ruang_indexes.append(f"{el['nama_ruangan']} ({el['kode_ruangan']})")
         ruang_list.append([el['kode_ruangan'], el['nama_ruangan']])

      opsi_cam = []
      opsi_ruang = []

      framex_list = []

      opsi_ruang_2 = []
      opsi_kam_2 = []

      # Komen 2
      for x in range(len(cam_indexes)):
         framex = customtkinter.CTkFrame(my_frame)
         
         clicked_opsi_kam = customtkinter.StringVar()
         clicked_opsi_kam.set(cam_indexes[0])
         opsi_cam.append(clicked_opsi_kam)
         opsi_2 = customtkinter.CTkOptionMenu(framex, variable=opsi_cam[x], values=cam_indexes, text_color="black", width=115)
         opsi_kam_2.append(opsi_2)
         opsi_2.grid(column=0, row=0)
         opsi_cam[x].trace_add("write", partial(cek_cams2, opsi_cam[x]))

         clicked_opsi_ruang = customtkinter.StringVar()
         clicked_opsi_ruang.set(ruang_indexes[0])
         opsi_ruang.append(clicked_opsi_ruang)
         opsi = customtkinter.CTkOptionMenu(framex, variable=opsi_ruang[x], values=ruang_indexes , text_color="black", width=242)
         CTkScrollableDropdown(opsi, values=ruang_indexes, height=300, justify="left", width=265)
         opsi_ruang_2.append(opsi)
         opsi.grid(column=1, row=0, padx=(10,0))
         # opsi_ruang[x].trace_add("write", cek_ruang)
         
         framex.pack(padx=5, pady=5)
         framex_list.append(framex)

      frame3.grid(column=0, row=4, padx=(10,0),pady=5, sticky="w", columnspan=2)
      frame4.grid(column=0, row=5, padx=10,pady=5, sticky="w", columnspan=2)
      frame5.grid(column=0, row=6, padx=10,pady=5, sticky="w", columnspan=2)
      button_mulai.grid(column=0, row=7, pady=(10,15), columnspan=2)


def cek_database(ruang):   
   if len(ruang) == 0:
      frame1_1.grid_forget()
      frame1_2.grid_forget()
      frame2.grid_forget()
      my_frame.grid_forget()
      frame3.grid_forget()
      frame4.grid_forget()
      frame5.grid_forget()
      button_mulai.grid_forget()
   else:
      frame0.grid_forget()
      get_all_captures()
      get_all_frames()
      show_cam()
   
def do_nothing():
   pass


def retry_box(my_comm):
   global retry_window
   if retry_window:
      retry_window.destroy()

   retry_window = customtkinter.CTkToplevel()
   retry_window.wm_transient(root)
   retry_window.title("Alert")
   retry_window.iconphoto(False, global_icon_image)

   frame0 = customtkinter.CTkFrame(retry_window, width=300, border_color="yellow", border_width=2)
   icon_warning = TablerIcons.load(OutlineIcon.ALERT_TRIANGLE, size=46, color="#FFF", stroke_width=2.0)
   icon_warning_img = customtkinter.CTkImage(icon_warning)
   customtkinter.CTkLabel(frame0, text="", image=icon_warning_img, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, pady=(5,0))
   label_koneksi_database = customtkinter.CTkLabel(frame0, text="Gagal terhubung ke basisdata, periksa kembali koneksi internet anda.", padx=5, wraplength=320, width=300, font=customtkinter.CTkFont("", 14))
   label_koneksi_database.grid(row=1, column=0, sticky=customtkinter.W, padx=10, pady=10)
   btn_refresh_db = customtkinter.CTkButton(frame0, text="Coba lagi", command=my_comm)
   btn_refresh_db.grid(row=2, column=0, pady=(0, 10))
   frame0.pack(padx=10,pady=10, anchor="w")

   x = root.winfo_rootx() + root.winfo_width()/2 - retry_window.winfo_width()/2 + 75
   y = root.winfo_rooty() + root.winfo_height()/2 - retry_window.winfo_height()/2 - 20

   retry_window.geometry("+%i+%i" % (x, y))

def tambah_ruangan():
   global opsi_ruang
   global opsi_cam
   global framex_list
   global opsi_ruang_2
   global opsi_kam_2

   if len(opsi_ruang) < cpu_count:
         
      framex = customtkinter.CTkFrame(my_frame)
      
      clicked_opsi_kam = customtkinter.StringVar()
      clicked_opsi_kam.set(cam_indexes[0])
      opsi_cam.append(clicked_opsi_kam)
      opsi_2 = customtkinter.CTkOptionMenu(framex, variable=opsi_cam[len(opsi_cam)-1], values=cam_indexes, text_color="black", width=115, font=customtkinter.CTkFont("", 14))
      opsi_kam_2.append(opsi_2)
      opsi_2.grid(column=0, row=0)
      opsi_cam[len(opsi_cam)-1].trace_add("write", partial(cek_cams2, opsi_cam[len(opsi_cam)-1]))

      clicked_opsi_ruang = customtkinter.StringVar()
      clicked_opsi_ruang.set(ruang_indexes[0])
      opsi_ruang.append(clicked_opsi_ruang)
      opsi = customtkinter.CTkOptionMenu(framex, variable=opsi_ruang[len(opsi_ruang)-1], values=ruang_indexes, text_color="black", width=242, font=customtkinter.CTkFont("", 14))
      CTkScrollableDropdown(opsi, values=ruang_indexes, height=300, justify="left", width=265)
      opsi_ruang_2.append(opsi)
      opsi.grid(column=1, row=0, padx=(10,0))
      # opsi_ruang[len(opsi_ruang)-1].trace_add("write", cek_ruang)
      
      framex.pack(padx=5, pady=5)
      framex_list.append(framex)

      cek_cams()
      cek_ruang()

def hapus_ruangan():
   global opsi_ruang
   global opsi_cam
   global framex_list
   if len(framex_list) > 1:
      framex_list[len(framex_list)-1].pack_forget()
      framex_list.pop()
      opsi_ruang.pop()
      opsi_cam.pop()

   cek_cams()
   cek_ruang()


def cek_kode_ruang(*args):
   global kode_ruangan_ok
   kode_ruangan = kode_ruangan_entry.get()
   if len(kode_ruangan) > 0 and len(kode_ruangan) < 7:
      kode_ruangan_ok = True
   else:
      kode_ruangan_ok = False
   cek_all2()

def cek_nama_ruang(*args):
   global nama_ruangan_ok
   nama_ruangan = nama_ruangan_entry.get()
   if len(nama_ruangan) > 0 and len(nama_ruangan) < 15:
      nama_ruangan_ok = True
   else:
      nama_ruangan_ok = False
   cek_all2()

def cek_all2():
   if kode_ruangan_ok and nama_ruangan_ok:
      button_kirim.configure(state="normal")
   else:
      button_kirim.configure(state="disabled")

def simpan_ruangan():
   global secondary_window_d
   global ruang_indexes
   global ruang_list
   global ruang
   
   kode_ruangan = kode_ruangan_entry.get()
   nama_ruangan = nama_ruangan_entry.get()
   
   res, res_msg = insert_ruangan(kode_ruangan, nama_ruangan)

   secondary_window_e.destroy()
   secondary_window_d.destroy()

   ruang = ambil_ruangan(ruang)

   if ruang:
      ruang_indexes = []
      ruang_list = []

      for el in ruang:
         if len(f"{el['kode_ruangan']} - {el['nama_ruangan']}") > 28 :
            ruang_indexes.append(f"{el['nama_ruangan']} ({el['kode_ruangan']})"[:28] + "..")
         else:
            ruang_indexes.append(f"{el['nama_ruangan']} ({el['kode_ruangan']})")
         ruang_list.append([el['kode_ruangan'], el['nama_ruangan']])

      if secondary_window_a:
         secondary_window_a.destroy()
      if secondary_window_b:
         secondary_window_b.destroy()
      if secondary_window_c:
         secondary_window_c.destroy()
      if secondary_window_d:
         secondary_window_d.destroy()

      secondary_window_d = customtkinter.CTkToplevel()
      secondary_window_d.wm_transient(root)
      secondary_window_d.title("Daftar Ruangan")
      secondary_window_d.iconphoto(False, global_icon_image)
      secondary_window_d.geometry("+%i+%i" % (725, 250))

      icon_close = TablerIcons.load(OutlineIcon.X, size=30, color="gray5", stroke_width=2.0)
      icon_close_img = customtkinter.CTkImage(icon_close)

      if res:
         frame0 = customtkinter.CTkFrame(secondary_window_d, width=385, border_color="green", border_width=2, fg_color="pale green")
         customtkinter.CTkLabel(frame0, text="Berhasil menambahkan data ruangan baru.", font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, pady=5, padx=15)
         customtkinter.CTkButton(frame0, image=icon_close_img, text="", width=30, command=frame0.pack_forget, fg_color="light grey", text_color="black", hover_color="dim gray", font=customtkinter.CTkFont("", 14)).grid(row=0, column=1, pady=5, padx=(0, 15))
         frame0.pack(padx=10, pady=(10, 0))
      else:
         frame1 = customtkinter.CTkFrame(secondary_window_d, width=385, border_color="red", border_width=2, fg_color="salmon")
         customtkinter.CTkLabel(frame1, text="Gagal menambahkan data ruangan baru!", font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, pady=(5,0), padx=10)
         customtkinter.CTkButton(frame1, image=icon_close_img, text="", width=30, command=frame1.pack_forget, fg_color="light grey", text_color="black",hover_color="dim gray", font=customtkinter.CTkFont("", 14)).grid(row=0, column=1, pady=(5,0), padx=(0, 15))
         customtkinter.CTkLabel(frame1, text=res_msg, font=customtkinter.CTkFont("", 14)).grid(row=1, column=0, pady=5, padx=15, columnspan=2)
         frame1.pack(padx=10, pady=5)

      btn_tambah_ruangan = customtkinter.CTkButton(secondary_window_d, text="Tambah Ruangan", command=insert_data_ruangan, text_color="black", font=customtkinter.CTkFont("", 14))
      ToolTip(btn_tambah_ruangan, msg="Daftarkan ruangan baru untuk dapat digunakan.")
      btn_tambah_ruangan.pack(anchor="w", padx=10, pady=(15,0))

      my_frame = customtkinter.CTkScrollableFrame(secondary_window_d, width=385, height=300)
      my_frame.pack(padx=10, pady=(10,15))

      value = [["Kode","Nama Ruangan"]] + ruang_list
      table = CTkTable(my_frame, row=len(ruang_list)+1, column=2, values=value, header_color="SpringGreen3", wraplength=250, font=customtkinter.CTkFont("", 14))

      table.pack(expand=True, fill="both", padx=10, pady=10)

      for el in opsi_ruang_3:
         el.configure(values=ruang_indexes)
   else:
      frame1_1.grid_forget()
      frame1_2.grid_forget()
      frame2.grid_forget()
      my_frame.grid_forget()
      frame3.grid_forget()
      frame4.grid_forget()
      frame5.grid_forget()
      button_mulai.grid_forget()
      frame0.grid(column=0, row=0, padx=10,pady=10, sticky="w", columnspan=2)

def insert_data_ruangan():
   global kode_ruangan_entry
   global nama_ruangan_entry
   global button_kirim
   global secondary_window_e

   if secondary_window_a:
      secondary_window_a.destroy()
   if secondary_window_b:
      secondary_window_b.destroy()
   if secondary_window_c:
      secondary_window_c.destroy()
   if secondary_window_e:
      secondary_window_e.destroy()
   
   secondary_window_e = customtkinter.CTkToplevel()
   secondary_window_e.wm_transient(secondary_window_d)
   secondary_window_e.title("Tambah Ruangan")
   secondary_window_e.iconphoto(False, global_icon_image)
   secondary_window_e.geometry("+%i+%i" % (692, 435))

   frame1 = customtkinter.CTkFrame(secondary_window_e, width=300)
   frame_kode = customtkinter.CTkFrame(frame1)
   frame_kode.grid(row=0, column=0, sticky="w")
   customtkinter.CTkLabel(frame_kode, text="Kode ruangan (max 7 char):", anchor="w", justify="left", padx=5, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, padx=(10, 18))
   sv_kode_ruang = customtkinter.StringVar()
   sv_kode_ruang.trace_add("write", cek_kode_ruang)
   kode_ruangan_entry = customtkinter.CTkEntry(frame1, width=200, textvariable=sv_kode_ruang, font=customtkinter.CTkFont("", 14))
   kode_ruangan_entry.grid(row=0, column=1, padx=(26,0))
   frame1.pack(padx=20,pady=(20,10), anchor="w")

   frame2 = customtkinter.CTkFrame(secondary_window_e, width=300)
   frame_nama = customtkinter.CTkFrame(frame2)
   frame_nama.grid(row=0, column=0, sticky="w")
   customtkinter.CTkLabel(frame_nama, text="Nama ruangan (max 15 char):", anchor="w", justify="left", padx=5, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, padx=10)
   sv_nama_ruang = customtkinter.StringVar()
   sv_nama_ruang.trace_add("write", cek_nama_ruang)
   nama_ruangan_entry = customtkinter.CTkEntry(frame2, width=200, textvariable=sv_nama_ruang, font=customtkinter.CTkFont("", 14))
   nama_ruangan_entry.grid(row=0, column=1, padx=(20,0))
   frame2.pack(padx=20,pady=10, anchor="w")

   button_kirim = customtkinter.CTkButton(secondary_window_e, width=100, text="Simpan", state="disabled", command=simpan_ruangan, text_color="black", font=customtkinter.CTkFont("", 14))
   button_kirim.pack(pady=(10,15))
   
def window_ruangan():
   global secondary_window_d
   if secondary_window_a:
      secondary_window_a.destroy()
   if secondary_window_b:
      secondary_window_b.destroy()
   if secondary_window_c:
      secondary_window_c.destroy()
   if secondary_window_d:
      secondary_window_d.destroy()
   secondary_window_d = customtkinter.CTkToplevel()
   secondary_window_d.wm_transient(root)
   secondary_window_d.title("Daftar Ruangan")
   secondary_window_d.iconphoto(False, global_icon_image)
   secondary_window_d.geometry("+%i+%i" % (725, 250))


   btn_tambah_ruangan = customtkinter.CTkButton(secondary_window_d, text="Tambah Ruangan", command=insert_data_ruangan, text_color="black", font=customtkinter.CTkFont("", 14))
   ToolTip(btn_tambah_ruangan, msg="Daftarkan ruangan baru untuk dapat digunakan.")
   btn_tambah_ruangan.pack(anchor="w", padx=10, pady=(15,0))

   
   my_frame = customtkinter.CTkScrollableFrame(secondary_window_d, width=385, height=300)
   my_frame.pack(padx=10, pady=(10,15))

   
   value = [["Kode","Nama Ruangan"]] + ruang_list
   table = CTkTable(my_frame, row=len(ruang_list)+1, column=2, values=value, header_color="SpringGreen3", wraplength=250, font=customtkinter.CTkFont("", 14))

   table.pack(expand=True, fill="both", padx=10, pady=10)


def window_int_dur():
   global secondary_window_a
   if secondary_window_a:
      secondary_window_a.destroy()
   if secondary_window_b:
      secondary_window_b.destroy()
   if secondary_window_c:
      secondary_window_c.destroy()
   if secondary_window_d:
      secondary_window_d.destroy()
   secondary_window_a = customtkinter.CTkToplevel()
   secondary_window_a.wm_transient(root)
   secondary_window_a.title("Durasi & Jeda")
   secondary_window_a.iconphoto(False, global_icon_image)
   secondary_window_a.geometry("+%i+%i" % (380, 330))
   img = customtkinter.CTkImage(light_image=Image.open("static/images/dur_jeda.jpg"), dark_image=Image.open("static/images/dur_jeda.jpg"), size=(900,250))
   label = customtkinter.CTkLabel(secondary_window_a, image=img, text="", text_color="black", font=customtkinter.CTkFont("", 14))
   label.pack(expand=1, fill="both", padx=10, pady=10)
   label.image = img


def window_exp():
   global secondary_window_b
   if secondary_window_a:
      secondary_window_a.destroy()
   if secondary_window_b:
      secondary_window_b.destroy()
   if secondary_window_c:
      secondary_window_c.destroy()
   if secondary_window_d:
      secondary_window_d.destroy()
   secondary_window_b = customtkinter.CTkToplevel()
   secondary_window_b.wm_transient(root)
   secondary_window_b.title("Expires")
   secondary_window_b.iconphoto(False, global_icon_image)
   secondary_window_b.geometry("+%i+%i" % (505, 165))
   img = customtkinter.CTkImage(light_image=Image.open("static/images/expires2.png"), dark_image=Image.open("static/images/expires2.png"), size=(700,500))
   label = customtkinter.CTkLabel(secondary_window_b, image=img, text="", text_color="black", font=customtkinter.CTkFont("", 14))
   label.pack(expand=1, fill="both", padx=10, pady=10)
   label.image = img


def window_tol():
   global secondary_window_c
   if secondary_window_a:
      secondary_window_a.destroy()
   if secondary_window_b:
      secondary_window_b.destroy()
   if secondary_window_c:
      secondary_window_c.destroy()
   if secondary_window_d:
      secondary_window_d.destroy()
   secondary_window_c = customtkinter.CTkToplevel()
   secondary_window_c.wm_transient(root)
   secondary_window_c.title("Threshold")
   secondary_window_c.iconphoto(False, global_icon_image)
   secondary_window_c.geometry("+%i+%i" % (400, 245))
   img = customtkinter.CTkImage(light_image=Image.open("static/images/toleransi.png"), dark_image=Image.open("static/images/toleransi.png"), size=(870,400))
   label = customtkinter.CTkLabel(secondary_window_c, image=img, text="", font=customtkinter.CTkFont("", 14))
   label.pack(expand=1, fill="both", padx=10, pady=10)
   label.image = img


def ambil_data_wajah():
   try_count = 0
   while try_count < 5:
      try:
         print(f"Mengambil data wajah...")
         client = MongoClient(db_url, server_api=ServerApi('1'))
         db = client["face_identification_3"]
         collection_mahasiswa = db["mahasiswa"]
         list_mhs = collection_mahasiswa.find({})
         
         known_face_encodings = []
         name_list = []
         id_mhs_list = []
         nim_list = []
         foto_profil_path_list = []
         
         for res in list_mhs:
            for encode in res["encode_foto_wajah"]:
               known_face_encodings.append(encode)
               nim_list.append(res["nim"])
               name_list.append(res["nama"])
               id_mhs_list.append(str(res["_id"]))
               foto_profil_path_list.append(res["foto_profil_path"])
         
         array_name_list = np.array(name_list)
         array_id_mhs = np.array(id_mhs_list)

         np.save("data/temp/known_face_encodings", known_face_encodings)
         np.save("data/temp/name_list", array_name_list)
         np.save("data/temp/id_mhs_list", array_id_mhs)
         np.save("data/temp/nim_list", nim_list)
         np.save("data/temp/foto_profil_path_list", foto_profil_path_list)

         print(f"Data wajah didapati")
         break
      except Exception as e:
         print("Mengambil data wajah gagal : ", e)
      
      try_count += 1

   # return np.array(known_face_encodings), array_name_list, array_id_mhs, nim_list

def ambil_data_wajah_2(index, kne, nl, iml):
   try_count = 0
   while try_count < 10:
      try:
         try_count += 1
         print(f"Mengambil data wajah Proses {index}...")
         client = MongoClient(db_url, server_api=ServerApi('1'))
         db = client["face_identification_3"]
         collection_mahasiswa = db["mahasiswa"]
         list_mhs = collection_mahasiswa.find({})
         
         known_face_encodings = []
         name_list = []
         id_mhs_list = []
         
         for res in list_mhs:
            for encode in res["encode_foto_wajah"]:
               known_face_encodings.append(encode)
               name_list.append(res["nama"])
               id_mhs_list.append(str(res["_id"]))
         
         array_name_list = np.array(name_list)
         array_id_mhs = np.array(id_mhs_list)

         print(f"Data wajah Proses {index} didapati")

         # np.save("data/temp/known_face_encodings", known_face_encodings)
         # np.save("data/temp/name_list", array_name_list)
         # np.save("data/temp/id_mhs_list", array_id_mhs)
         # np.save("data/temp/nim_list", nim_list)
         return np.array(known_face_encodings), array_name_list, array_id_mhs
      except:
         pass
   print(f"Mengambil data wajah ({index}) gagal.")
   return kne, nl, iml

face_detector = dlib.get_frontal_face_detector()
face_encoder = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")
shape_predictor_68_point = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

def _rect_to_css(rect):
   """
   Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

   :param rect: a dlib 'rect' object
   :return: a plain tuple representation of the rect in (top, right, bottom, left) order
   """
   return rect.top(), rect.right(), rect.bottom(), rect.left()

def _trim_css_to_bounds(css, image_shape):
   """
   Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.

   :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
   :param image_shape: numpy shape of the image array
   :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
   """
   return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

def _raw_face_locations(img, number_of_times_to_upsample=1):
   """
   Returns an array of bounding boxes of human faces in a image

   :param img: An image (as a numpy array)
   :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
   :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                  deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
   :return: A list of dlib 'rect' objects of found face locations
   """
   return face_detector(img, number_of_times_to_upsample)

def face_locate(img, number_of_times_to_upsample=1):
   """
   Returns an array of bounding boxes of human faces in a image

   :param img: An image (as a numpy array)
   :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
   :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                  deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
   :return: A list of tuples of found face locations in css (top, right, bottom, left) order
   """
   return [_trim_css_to_bounds(_rect_to_css(face), img.shape) for face in _raw_face_locations(img, number_of_times_to_upsample)]

def _css_to_rect(css):
   """
   Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object

   :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
   :return: a dlib `rect` object
   """
   return dlib.rectangle(css[3], css[0], css[1], css[2])

def _raw_face_landmarks(face_image, face_locations=None):
   if face_locations is None:
      face_locations = _raw_face_locations(face_image)
   else:
      face_locations = [_css_to_rect(face_location) for face_location in face_locations]
   return [shape_predictor_68_point(face_image, face_location) for face_location in face_locations]

def face_encode(face_image, known_face_locations=None, num_jitters=1):
   """
   Given an image, return the 128-dimension face encoding for each face in the image.

   :param face_image: The image that contains one or more faces
   :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
   :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
   :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
   :return: A list of 128-dimensional face encodings (one for each face in the image)
   """

   raw_landmarks = _raw_face_landmarks(face_image, known_face_locations)

   # print(f"Landmarks: {raw_landmarks[0]}")

   return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for raw_landmark_set in raw_landmarks]

def face_distance(face_encodings, face_to_compare):
   """
   Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
   for each comparison face. The distance tells you how similar the faces are.

   :param face_encodings: List of face encodings to compare
   :param face_to_compare: A face encoding to compare against
   :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
   """
   if len(face_encodings) == 0:
      return np.empty((0))

   return np.linalg.norm(face_encodings - face_to_compare, axis=1)

def compare_faces(known_face_encodings, face_encoding_to_check, tolerance):
   distances = face_distance(known_face_encodings, face_encoding_to_check)
   index = np.argmin(distances)

   if True in tuple(distances <= tolerance):
      return index, distances[index]
   else:
      return False, distances[index]

def list_to_string(items):
   a = []
   for i in items:
      a.append(i.split(" - ")[0])
   if len(a) == 1:
      return a[0]
   elif len(a) == 2:
      return f"{a[0]} & {a[1]}"
   else:
      return f"{', '.join(a[:-1])} & {a[-1]}"

# Upload the file

# Function to handle MongoDB insertions in a separate process
def queue_process(data_queue):
   while True:
      # Get data from the queue
      kode, first, second = data_queue.get()
      # if data == 'STOP':
         # break  # Exit the process if we receive the STOP signal
      # Insert data into MongoDB
      if kode == 1:
         asyncio.run(ambil_jadwal_async(id_ruang=first, ket_ruang=second))
      else:
         upload_gambar(path=first, url=second)
      # if kode == 1:
      #    asyncio.run(insert_aktivitas(False, id_mhs, ruangan, filter, kegiatan, time_now, id_file, path))
      # elif kode == 2:
      #    asyncio.run(insert_aktivitas(True, id_mhs, ruangan, filter, kegiatan, time_now, id_file, path))
      # elif kode == 3:
      #    asyncio.run(ambil_jadwal_async(id_mhs))
      # print(f"Saving data to MongoDB: {id_mhs, name, kegiatan_saat_ini, filter, kegiatan, time_now, index_ruang, expires, saved_image, face_locations, identified_folder}")
      # time.sleep(2)
      # collection.insert_one(data)


async def ambil_jadwal_async(id_ruang, ket_ruang):
   print(f"Mengambil data jadwal di ruang {list_to_string(ket_ruang)}")
   now = datetime.now()
   # Extract the year, month, and day
   year = now.year
   month = f"0{now.month}" if now.month < 10 else now.month 
   day = f"0{now.day}" if now.day < 10 else now.day 

   datetime_object = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d") + timedelta(days=1)

   jadwal_all = []

   for el in id_ruang:
      jadwal = await db_async["jadwal"].find({"ruangan_id": ObjectId(el), "waktu_selesai": {"$gt": now, "$lt": datetime_object}}).to_list(None)

      # result = []
      for el in jadwal:
         # if waktu_sekarang < el["waktu_selesai"]:
         #    result.append(el)
         jadwal_all.append(el)
   

      # jadwal_all.append(result)
   # print("Len jadwal async: ", len(jadwal_all))
   np.save("data/temp/jadwal_all", jadwal_all)
   print(f"Data jadwal di ruang {list_to_string(ket_ruang)} didapati")

   # print("Jadwal all: ", jadwal_all)

async def toggle_ruangan_digunakan(kode_ruangan, boolean):
   for kode in kode_ruangan:
      db_async["ruangan"].update_one({"kode_ruangan": kode}, {"$set": {"sedang_digunakan": boolean}})


async def insert_aktivitas2(wkt, exprs, gmbrpth, mhsid, jdwlid, rngid):
   db_async["aktivitas2"].insert_one({
      "timestamp": wkt,
      "expires": exprs,
      "gambar": gmbrpth,
      "mahasiswa_id": ObjectId(mhsid),
      "ruang_id": ObjectId(rngid),
      "jadwal_id": ObjectId(jdwlid)
   })

async def insert_aktivitas(id_mhs, ruangan, query, kegiatan, time_now, id_file):

   # start_time = time.time()
   # document = await db_async["aktivitas"].find_one(query)
   # end_time = time.time()
   # print(f"Execution find one time: {end_time - start_time} seconds")
   
   # query["gambar"] = [f"{id_file}.jpg"]
   # query["updateAt"] = time_now

   db_async["aktivitas"].insert_one(query)

   # Target URL (Replace with your actual server API)
   # url = "http://127.0.0.1:4000/uploadgambarwajah"

   # # Open the image file
   # files = {"file": open(path, "rb")}  # Change to video.mp4 for videos

   # start_time = time.time()
   # # Send POST request
   # requests.post(url, files=files)
   # end_time = time.time()
   # print(f"Execution insert time: {end_time - start_time} seconds")
   # if up_ins:
      # insert
      # query["waktu"] = [time_now]

      # Print response
      # print(response.json())  # Assumes the server returns JSON
   # else:
   #    # update
   #    db_async["aktivitas"].update_one(query, {"$push": {"waktu": time_now, "gambar": f"{id_file}.jpg"}})

   #    db_async["mahasiswa"].update_one(
   #       {"_id": ObjectId(id_mhs)},
   #       {"$set": {
   #          "aktivitas_terakhir": {
   #             "ruangan": ruangan,
   #             "nama_kegiatan": kegiatan,
   #             "waktu_terakhir": time_now
   #          }
   #       }}
   #    )


   #    url = "http://127.0.0.1:4000/uploadgambarwajah"

   #    # Open the image file
   #    files = {"file": open(path, "rb")}  # Change to video.mp4 for videos

   #    start_time = time.time()
   #    # Send POST request
   #    requests.post(url, files=files)
   #    end_time = time.time()
   #    print(f"Execution update time: {end_time - start_time} seconds")

      # Print response
      # print(response.json())  # Assumes the server returns JSON


async def update_aktivitas(id_mhs, ruangan, query, expires, time_now, id_file):
   db_async["aktivitas"].update_one(query, {"$push": {"waktu": time_now, "gambar": f"{id_file}.jpg", "expires": expires}, "$set": {"updateAt": time_now}})

   # db_async["mahasiswa"].update_one(
   #    {"_id": ObjectId(id_mhs)},
   #    {"$set": {
   #       "aktivitas_terakhir": {
   #          "ruangan": ruangan,
   #          "nama_kegiatan": kegiatan,
   #          "waktu_terakhir": time_now
   #       }
   #    }}
   # )


def save_frame(frame, ruang_id, threshold, jadwal_id, nama_kegiatan, nama_komputer):
   result = db["frame"].insert_one({"frame": frame, "ruangan_id": ruang_id, "threshold": threshold, "jadwal_id": jadwal_id, "nama_kegiatan": nama_kegiatan, "status": "Off", "nama_komputer": nama_komputer})

   return result.inserted_id 

async def save_frame_0(frame, ruang_id, threshold, jadwal_id, nama_kegiatan, frame_id, kamera):
   db_async["frame"].update_one({"_id": ObjectId(frame_id)}, {"$set": {"frame": frame, "ruangan_id": ObjectId(ruang_id), "threshold": threshold, "jadwal_id": jadwal_id, "nama_kegiatan": nama_kegiatan, "status": "Off", "kamera": kamera}})

async def save_frame_1(frame, frame_id, jadwal_id, nama_kegiatan):
   db_async["frame"].update_one({"_id": ObjectId(frame_id)}, 
      {"$set": {"frame": frame, "jadwal_id": jadwal_id, "nama_kegiatan": nama_kegiatan}})
   
async def save_frame_2(locations, distances, frame_id):
   db_async["frame"].update_one({"_id": ObjectId(frame_id)}, 
      {"$set": {"locations": [arr.tolist() for arr in locations], "distances": list(distances), "status": "On"}})
   
async def save_frame_3(face_names, frame_id):
   db_async["frame"].update_one({"_id": ObjectId(frame_id)}, 
      {"$push": {"face_names": {"$each": face_names, "$position": 0}}})
   
async def save_frame_4(frame_id):
   db_async["frame"].update_one({"_id": ObjectId(frame_id)}, 
      {"$set": {"face_names": [], "status": "Off", "locations": [], "distances": []}})
   
async def save_frame_5(frame_ids):
   for el in frame_ids:
      db_async["frame"].delete_one({"_id": ObjectId(el)})

def upload_gambar(path, url):
   # url = "http://127.0.0.1:4000/uploadgambarwajah"
   # Open the image file
   files = {"file": open(path, "rb")}  # Change to video.mp4 for videos
   # start_time = time.time()
   # Send POST request
   requests.post(url, files=files)
   # end_time = time.time()
   # print(f"Execution upload time: {end_time - start_time} seconds")

def is_valid_image(img):
   if img is None:
      return False
   if not isinstance(img, np.ndarray):
      return False
   if img.dtype != np.uint8:
      return False
   if img.ndim == 2:
      return True  # grayscale
   if img.ndim == 3 and img.shape[2] == 3:
      return True  # RGB
   return False

def identifikasi_frame(expires, toleransi, index_ruang, data_queue, frame_id):
   print(f"Menjalankan identifikasi Proses {index_ruang}")
   
   known_face_encodings = np.load("data/temp/known_face_encodings.npy")
   name_list = np.load("data/temp/name_list.npy")
   id_mhs_list = np.load("data/temp/id_mhs_list.npy")

   identified_folder="static/images/identified"
   data_wajah_belum_terupdate = False
   face_names = list()

   # client = MongoClient(db_url, server_api=ServerApi('1'))
   # db = client["face_identification_3"]
   # collection_aktivitas = db["aktivitas"]
   # collection_mahasiswa = db["mahasiswa"]

   offset_width = np.load("data/temp/offset_width.npy")
   offset_width = offset_width[index_ruang]
   offset_height = np.load("data/temp/offset_height.npy")
   offset_height = offset_height[index_ruang]
   url = "http://127.0.0.1:4000/uploadgambarwajah"
   
   # print(f"offset_width  {index_ruang}: ", offset_width)
   # print(f"offset_height  {index_ruang}: ", offset_height)

   not_empty = False

   while True:
      tanggal = datetime.now().strftime("%Y-%m-%d")
      status = [None]

      while status[0] is None:
         try:
            status = np.load("data/temp/status_main.npy")
         except:
            pass


      if bool(status[0]):

         kegiatan_saat_ini = None
         while kegiatan_saat_ini is None:
            try:
               kegiatan_saat_ini = np.load("data/temp/kegiatan_saat_ini.npy", allow_pickle=True)
            except:
               pass
         

         saved_frame = None
         while saved_frame is None:
            try:
               saved_frame = np.load(f"data/temp/frame_{index_ruang}.npy")
            except:
               pass

         # ===== BARU BOLEH KE DLIB =====
         saved_image = Image.fromarray(saved_frame)
         face_locations = face_locate(saved_frame)

         # start_1 = time.time()
         # start_time = time.time()
         # face_locations = face_locate(saved_frame)
         # end_1 = time.time()
         # end_time = time.time()
         # print(f"Execution time: {end_time - start_time} seconds")
         # print("Type face locations: ", type(face_locations))
         # print("Length face locations: ", len(face_locations))
         # print("Face locations: ", face_locations)
         
         if face_locations:
            # face_locations = 
            face_locations_aft = np.array(face_locations).astype(np.float64)

            # print(face_locations_aft)
            face_locations_aft[:, 1::2] *= offset_width
            face_locations_aft[:, 0::2] *= offset_height
            # print(face_locations_aft.astype(int), "\n")
            # face_locations_aft[:, 0::2] *= offset

            # print(face_locations_aft.astype(int))
            
            np.save(f"data/temp/loc_{index_ruang}", face_locations_aft.astype(int))
            
            distances = ["0"] * len(face_locations)
            np.save(f"data/temp/dis_{index_ruang}", np.array(distances))

            # start_2 = time.time()
            face_encodings = face_encode(saved_frame, face_locations)
            # end_2 = time.time()

            # start_3 = time.time()
            index_a = 0
            for i, face_encoding in enumerate(face_encodings):
               matches, dis = compare_faces(known_face_encodings, face_encoding, toleransi)
               
               distances[i] = str(round(dis, 2))
               
               np.save(f"data/temp/dis_{index_ruang}", np.array(distances))

               if matches:
                  name = name_list[matches]
                  id_mhs = id_mhs_list[matches]
                  jadwal_id =  ObjectId(kegiatan_saat_ini[index_ruang][1]) if kegiatan_saat_ini[index_ruang][1] else None
                  filter = {
                     "mahasiswa_id": ObjectId(id_mhs),
                     "ruangan_id": ObjectId(kegiatan_saat_ini[index_ruang][2]),
                     "jadwal_id": jadwal_id,
                     "tanggal": tanggal
                  }

                  time_now = datetime.now()



                  list_aktivitas = None
                  while list_aktivitas is None:
                     try:
                        list_aktivitas = np.load("data/temp/aktivitas.npy", allow_pickle=True)
                     except:
                        pass


                  index_aktivitas = 0
                  aktivitas = {}
                  for i, akt in enumerate(list_aktivitas):
                     if jadwal_id:


                        if str(akt["mahasiswa_id"]) == str(filter["mahasiswa_id"]) and str(akt["ruangan_id"]) == str(filter["ruangan_id"]) and str(akt["jadwal_id"]) == str(filter["jadwal_id"]) and akt["tanggal"] == filter["tanggal"]:
                           aktivitas = akt
                           index_aktivitas = i
                           break
                     else:



                        if str(akt["mahasiswa_id"]) == str(filter["mahasiswa_id"]) and str(akt["ruangan_id"]) == str(filter["ruangan_id"]) and akt["jadwal_id"] == filter["jadwal_id"] and akt["tanggal"] == filter["tanggal"]:
                           aktivitas = akt
                           index_aktivitas = i
                           break

                  if aktivitas:
                     gap = time_now - aktivitas["waktu"][len(aktivitas["waktu"])-1]
                     if gap.seconds > expires:
                        # print("update")
                        id_file = str(uuid.uuid4())

                        aktivitas["waktu"].append(time_now)
                        aktivitas["expires"].append(expires)
                        aktivitas["updateAt"] = time_now
                        aktivitas["gambar"].append([f"{id_file}.jpg"])
                        list_aktivitas[index_aktivitas] = aktivitas
                        np.save("data/temp/aktivitas", list_aktivitas)


                        imgres_1 = saved_image.crop((face_locations[index_a][3], face_locations[index_a][0], face_locations[index_a][1], face_locations[index_a][2]))

                        path = os.path.join(identified_folder, f"{id_file}.jpg")

                        folder = os.path.abspath(path)
                        imgres_1.thumbnail((100, 100))
                        b,g,r = imgres_1.split()
                        imgres_1 = Image.merge("RGB", (r,g,b))
                        imgres_1.save(folder)

                        # print(type(imgres_1))

                        face_names = np.load(f"data/temp/array_face_names_{index_ruang}.npy", allow_pickle=True)
                        face_names_list = list(face_names)
                        face_names_list.insert(0, f"{id_file}&{name}")

                        np.save(f"data/temp/array_face_names_{index_ruang}", np.array(face_names_list))

                        asyncio.run(save_frame_3([f"{id_file}&{name}"], frame_id))

                        data_queue.put((2, path, url))
                        asyncio.run(update_aktivitas("", "", filter, expires, time_now, id_file))

                  
                  else:
                     # aktivitas["waktu"].append(time_now)
                     # print("insert")
                     id_file = str(uuid.uuid4())

                     filter["gambar"] = [f"{id_file}.jpg"]
                     filter["waktu"] = [time_now]
                     filter["expires"] = [expires]
                     filter["updateAt"] = time_now
                     
                     # list_aktivitas.append(filter)
                     np.save("data/temp/aktivitas", np.append(list_aktivitas, filter))


                     imgres_1 = saved_image.crop((face_locations[index_a][3], face_locations[index_a][0], face_locations[index_a][1], face_locations[index_a][2]))

                     path = os.path.join(identified_folder, f"{id_file}.jpg")

                     folder = os.path.abspath(path)
                     imgres_1.thumbnail((100, 100))
                     b,g,r = imgres_1.split()
                     imgres_1 = Image.merge("RGB", (r,g,b))
                     imgres_1.save(folder)

                     face_names = np.load(f"data/temp/array_face_names_{index_ruang}.npy", allow_pickle=True)
                     face_names_list = list(face_names)
                     face_names_list.insert(0, f"{id_file}&{name}")

                     np.save(f"data/temp/array_face_names_{index_ruang}", np.array(face_names_list))

                     asyncio.run(save_frame_3([f"{id_file}&{name}"], frame_id))

                     data_queue.put((2, path, url))

                     # asyncio.run(insert_aktivitas2(time_now, expires, path, id_mhs, jadwal_id, "6803b5198e36c4521cda02a7"))
                     asyncio.run(insert_aktivitas("", "", filter, "", time_now, id_file))
                     # print(f"Execution insert time: {end_time - start_time} seconds")

            
                  # print("\n")
               # distances.append(str(round(dis, 2)))

               index_a += 1

            asyncio.run(save_frame_2(face_locations_aft.astype(int), distances, frame_id))

            not_empty = True

         else:
               if not_empty:
                  np.save(f"data/temp/loc_{index_ruang}", [])
                  np.save(f"data/temp/dis_{index_ruang}", [])

                  asyncio.run(save_frame_2([], [], frame_id))
                  not_empty = False

         if not data_wajah_belum_terupdate:        
            data_wajah_belum_terupdate = True
      elif data_wajah_belum_terupdate:
         data_wajah_belum_terupdate = False

         np.save(f"data/temp/loc_{index_ruang}", [])
         np.save(f"data/temp/dis_{index_ruang}", [])
         np.save(f"data/temp/array_face_names_{index_ruang}", [])

         asyncio.run(save_frame_4(frame_id))

         known_face_encodings, name_list, id_mhs_list = ambil_data_wajah_2(index_ruang, known_face_encodings, name_list, id_mhs_list)

def jalankan_identifikasi(durasi, jeda, expires, toleransi, ruang_kam, ruang, frame_ids, nama_komputer):
   print("Memulai proses identifikasi...")

   # print("ruang: ", ruang)
   # print("ruang kam: ", ruang_kam)

   kne = np.load("data/temp/known_face_encodings.npy", allow_pickle=True)

   # print("kne: ", kne)
   
   if kne.size == 0:
      print("Mengambil ulang data wajah...")
      ambil_data_wajah()
      # ruang = np.load("data/temp/ruang.npy", allow_pickle=True)
   # ambil_data_wajah()
      
   ruang_nama = []
   ruang_ket = []
   ruang_id = []
   ruang_kode = []
   for x,y in ruang_kam:
      for el in ruang:
         if el["kode_ruangan"] == x:
            ruang_nama.append(el["nama_ruangan"])
            ruang_ket.append(f"{el['kode_ruangan']} - {el['nama_ruangan']}")
            ruang_id.append(el["_id"])
            ruang_kode.append(el["kode_ruangan"])

   
   # print("ruang kode: ", ruang_kode)

   identifikasi = False
   identifikasi_old = False

   np.save("data/temp/status_main", np.array([identifikasi]))

   # print("status main saved")

   quit_box = ""
   refresh_cam_box = ""

   def konfirmasi_quit_id():
      nonlocal quit_box
      
      if secondary_window:
         secondary_window.destroy()

      if quit_box:
         quit_box.destroy()

      if refresh_cam_box:
         refresh_cam_box.destroy()

      quit_box = customtkinter.CTkToplevel()
      quit_box.wm_transient(window)
      quit_box.title("Keluar")
      quit_box.iconphoto(False, global_icon_image)

      frame0 = customtkinter.CTkFrame(quit_box, width=300, border_color="yellow", border_width=2)
      icon_warning = TablerIcons.load(OutlineIcon.ALERT_TRIANGLE, size=46, color="#FFF", stroke_width=2.0)
      icon_warning_img = customtkinter.CTkImage(icon_warning)
      customtkinter.CTkLabel(frame0, text="", image=icon_warning_img, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, pady=(5,0))
      label_koneksi_database = customtkinter.CTkLabel(frame0, text="Keluar dari aplikasi ini akan menghentikan proses identifikasi wajah dari setiap kamera yang terhubung. Lanjutkan?", padx=5, wraplength=320, width=300, font=customtkinter.CTkFont("", 14))
      label_koneksi_database.grid(row=1, column=0, sticky=customtkinter.W, padx=10, pady=10)
      frame_button_quit = customtkinter.CTkFrame(quit_box, width=300)
      customtkinter.CTkButton(frame_button_quit, text="Ya", command=quit_id, font=customtkinter.CTkFont("", 14)).grid(row=2, column=0, pady=10, padx=13)
      customtkinter.CTkButton(frame_button_quit, text="Batal", command=quit_box.destroy, font=customtkinter.CTkFont("", 14)).grid(row=2, column=1, pady=10, padx=13)
      frame0.pack(padx=10, pady=(10,5), anchor="w")
      frame_button_quit.pack(padx=10,pady=10, anchor="w")

      x = window.winfo_rootx() + (window.winfo_width()/2 - quit_box.winfo_width()/2) - 130
      y = window.winfo_rooty() + (window.winfo_height()/2 - quit_box.winfo_height()/2) - 25

      quit_box.geometry("+%i+%i" % (x, y))

   def quit_id():
      # Updatte ruangan digunakan
      asyncio.run(toggle_ruangan_digunakan(set(ruang_kode), False))

      stop_event.set()

      for p in processes:
         if p.is_alive():
            p.terminate()
            p.join()

      asyncio.run(save_frame_5(frame_ids))

      # is_empty = False
      # while not data_queue.empty():
      #    if not is_empty:
      #       print("Menunggu antrian selesai...")
      #       is_empty = True

      if px.is_alive():
         px.terminate()
         px.join()

      if secondary_window:
         secondary_window.destroy()

      window.withdraw()
      window.quit()
      window.destroy()
      root.destroy()

      if os.path.exists(identified_folder):
         shutil.rmtree(identified_folder)
         os.mkdir(identified_folder)
      for index, capture in enumerate(captures):
         capture.release()
         np.save(f"data/temp/frame_{index}", [])
         np.save(f"data/temp/loc_{index}", [])
         np.save(f"data/temp/dis_{index}", [])
      np.save("data/temp/ruang", [])
      np.save("data/temp/jadwal_all", [])
      np.save("data/temp/known_face_encodings", [])
      np.save("data/temp/name_list", [])
      np.save("data/temp/id_mhs_list", [])
      np.save("data/temp/nim_list", [])
      np.save("data/temp/foto_profil_path_list", [])

      # print("ACTIVE PROCESSES:", active_children())
      # print("ACTIVE THREADS:", threading.enumerate())

      os._exit(0)

      # Close the SFTP connection
      # sftp.close()
      # transport.close()
   
   # Diff
   # Create a Queue for inter-process communication
   data_queue = Queue()

   asyncio.run(toggle_ruangan_digunakan(set(ruang_kode), True))

   # data_queue.put((3, ruang_kode, True, "", "", "", "", ""))

   got_jadwal = False

   def update_jadwal():
      nonlocal jadwal
      nonlocal got_jadwal
      if not got_jadwal:
         # print("got jadwal!")
         index_ruang = 0
         for rid in ruang_id:
            jadwal_arr = []
            for j in jadwal_all:
               if str(j["ruangan_id"]) == str(rid):
                  jadwal_arr.append(j)
            jadwal[index_ruang] = jadwal_arr
            index_ruang += 1
         got_jadwal = True
         pass
      else:
         index_ruang = 0
         # print("Put update jadwal on data queue")
         data_queue.put((1, set(ruang_id), set(ruang_ket)))
         # for ket in ruang_ket:
         #    jadwal[index_ruang] = ambil_jadwal(ket)
         #    index_ruang += 1
      # print("Jadwal terupdate: ", jadwal)
      # 1 menit
      window.after(60000, update_jadwal)
   
   def open_view_more(index):
      nonlocal secondary_window
      nonlocal identified_folder
      nonlocal pics_in_frame_extra
      nonlocal labels_in_frame_extra
      nonlocal image_id_in_frame_extra

      if quit_box:
         quit_box.destroy()

      if secondary_window:
         secondary_window.destroy()
      
      try:
         array_face_names = np.load(f"data/temp/array_face_names_{index}.npy")
         identified_folder = "static/images/identified"
         
         secondary_window = customtkinter.CTkToplevel()
         secondary_window.title("View more")
         secondary_window.iconphoto(False, global_icon_image)
         secondary_window.wm_transient(window)
         secondary_window.geometry("+%i+%i" % (655, 200))

         pics_frame = customtkinter.CTkFrame(secondary_window)
         pics_frame.columnconfigure(0, weight=1)
         pics_frame.grid(row=0, column=0)

         pics_in_frame_extra = []
         labels_in_frame_extra = []
         image_id_in_frame_extra = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

         pic_1 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_1.grid(row=0, column=0, padx=3, pady=(5, 0))
         label_pic_1 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_1.grid(row=1, column=0, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_1)
         labels_in_frame_extra.append(label_pic_1)

         pic_2 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_2.grid(row=0, column=1, padx=3, pady=(5, 0))
         label_pic_2 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_2.grid(row=1, column=1, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_2)
         labels_in_frame_extra.append(label_pic_2)

         pic_3 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_3.grid(row=0, column=2, padx=3, pady=(5, 0))
         label_pic_3 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_3.grid(row=1, column=2, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_3)
         labels_in_frame_extra.append(label_pic_3)

         pic_4 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_4.grid(row=0, column=3, padx=3, pady=(5, 0))
         label_pic_4 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_4.grid(row=1, column=3, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_4)
         labels_in_frame_extra.append(label_pic_4)

         pic_5 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_5.grid(row=0, column=4, padx=3, pady=(5, 0))
         label_pic_5 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_5.grid(row=1, column=4, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_5)
         labels_in_frame_extra.append(label_pic_5)

         pic_6 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_6.grid(row=0, column=5, padx=3, pady=(5, 0))
         label_pic_6 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_6.grid(row=1, column=5, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_6)
         labels_in_frame_extra.append(label_pic_6)

         pic_7 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_7.grid(row=2, column=0, padx=3, pady=(5, 0))
         label_pic_7 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_7.grid(row=3, column=0, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_7)
         labels_in_frame_extra.append(label_pic_7)

         pic_8 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_8.grid(row=2, column=1, padx=3, pady=(5, 0))
         label_pic_8 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_8.grid(row=3, column=1, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_8)
         labels_in_frame_extra.append(label_pic_8)

         pic_9 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_9.grid(row=2, column=2, padx=3, pady=(5, 0))
         label_pic_9 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_9.grid(row=3, column=2, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_9)
         labels_in_frame_extra.append(label_pic_9)

         pic_10 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_10.grid(row=2, column=3, padx=3, pady=(5, 0))
         label_pic_10 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_10.grid(row=3, column=3, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_10)
         labels_in_frame_extra.append(label_pic_10)

         pic_11 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_11.grid(row=2, column=4, padx=3, pady=(5, 0))
         label_pic_11 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_11.grid(row=3, column=4, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_11)
         labels_in_frame_extra.append(label_pic_11)

         pic_12 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_12.grid(row=2, column=5, padx=3, pady=(5, 0))
         label_pic_12 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_12.grid(row=3, column=5, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_12)
         labels_in_frame_extra.append(label_pic_12)

         pic_13 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_13.grid(row=4, column=0, padx=3, pady=(5, 0))
         label_pic_13 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_13.grid(row=5, column=0, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_13)
         labels_in_frame_extra.append(label_pic_13)

         pic_14 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_14.grid(row=4, column=1, padx=3, pady=(5, 0))
         label_pic_14 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_14.grid(row=5, column=1, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_14)
         labels_in_frame_extra.append(label_pic_14)

         pic_15 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_15.grid(row=4, column=2, padx=3, pady=(5, 0))
         label_pic_15 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_15.grid(row=5, column=2, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_15)
         labels_in_frame_extra.append(label_pic_15)

         pic_16 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_16.grid(row=4, column=3, padx=3, pady=(5, 0))
         label_pic_16 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_16.grid(row=5, column=3, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_16)
         labels_in_frame_extra.append(label_pic_16)

         pic_17 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_17.grid(row=4, column=4, padx=3, pady=(5, 0))
         label_pic_17 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_17.grid(row=5, column=4, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_17)
         labels_in_frame_extra.append(label_pic_17)

         pic_18 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_18.grid(row=4, column=5, padx=3, pady=(5, 0))
         label_pic_18 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_18.grid(row=5, column=5, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_18)
         labels_in_frame_extra.append(label_pic_18)

         pic_19 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_19.grid(row=6, column=0, padx=3, pady=(5, 0))
         label_pic_19 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_19.grid(row=7, column=0, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_19)
         labels_in_frame_extra.append(label_pic_19)

         pic_20 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_20.grid(row=6, column=1, padx=3, pady=(5, 0))
         label_pic_20 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_20.grid(row=7, column=1, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_20)
         labels_in_frame_extra.append(label_pic_20)

         pic_21 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_21.grid(row=6, column=2, padx=3, pady=(5, 0))
         label_pic_21 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_21.grid(row=7, column=2, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_21)
         labels_in_frame_extra.append(label_pic_21)

         pic_22 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_22.grid(row=6, column=3, padx=3, pady=(5, 0))
         label_pic_22 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_22.grid(row=7, column=3, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_22)
         labels_in_frame_extra.append(label_pic_22)

         pic_23 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_23.grid(row=6, column=4, padx=3, pady=(5, 0))
         label_pic_23 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_23.grid(row=7, column=4, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_23)
         labels_in_frame_extra.append(label_pic_23)

         pic_24 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_24.grid(row=6, column=5, padx=3, pady=(5, 0))
         label_pic_24 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_24.grid(row=7, column=5, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_24)
         labels_in_frame_extra.append(label_pic_24)

         pic_25 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_25.grid(row=8, column=0, padx=3, pady=(5, 0))
         label_pic_25 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_25.grid(row=9, column=0, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_25)
         labels_in_frame_extra.append(label_pic_25)

         pic_26 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_26.grid(row=8, column=1, padx=3, pady=(5, 0))
         label_pic_26 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_26.grid(row=9, column=1, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_26)
         labels_in_frame_extra.append(label_pic_26)

         pic_27 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_27.grid(row=8, column=2, padx=3, pady=(5, 0))
         label_pic_27 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_27.grid(row=9, column=2, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_27)
         labels_in_frame_extra.append(label_pic_27)

         pic_28 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_28.grid(row=8, column=3, padx=3, pady=(5, 0))
         label_pic_28 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_28.grid(row=9, column=3, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_28)
         labels_in_frame_extra.append(label_pic_28)

         pic_29 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_29.grid(row=8, column=4, padx=3, pady=(5, 0))
         label_pic_29 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_29.grid(row=9, column=4, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_29)
         labels_in_frame_extra.append(label_pic_29)

         pic_30 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
         pic_30.grid(row=8, column=5, padx=3, pady=(5, 0))
         label_pic_30 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
         label_pic_30.grid(row=9, column=5, padx=3, pady=(0,10))
         pics_in_frame_extra.append(pic_30)
         labels_in_frame_extra.append(label_pic_30)

         index = 0
         index_a = 0
         for name in array_face_names:
            if index >= 20 and index < 50:
               id_file = name.split("&")[0]
               nama_mahasiswa = name.split("&")[1]

               labels_in_frame_extra[index_a].configure(text=nama_mahasiswa.upper())
               img = Image.open(f"{identified_folder}/{id_file}.jpg").resize((87,87), Image.Resampling.LANCZOS)
               # convert to Tkinter image
               photo = ImageTk.PhotoImage(image=img)
               # solution for bug in `PhotoImage`
               pics_in_frame_extra[index_a].photo = photo
               # check if image already exists
               if image_id_in_frame_extra[index_a]:
                  # replace image in PhotoImage on pics_in_frame[index_a]
                  pics_in_frame_extra[index_a].itemconfig(image_id_in_frame_extra[index_a], image=photo, state='normal')
               else:
                  # create first image on pics_in_frame[index_a] and keep its ID
                  image_id_in_frame_extra[index_a] = pics_in_frame_extra[index_a].create_image((45, 45), anchor="center", image=photo)

               index_a += 1

            index += 1
      except Exception:
         pass
    
   def show_cam_id():
      nonlocal image_id
      nonlocal image_id_in_frame
      nonlocal array_face_names_global
      nonlocal extras

      frame = frames[curr_index]
      
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      frame = cv2.resize(frame, (1310, 737))
      try:
         locations = np.load(f"data/temp/loc_{curr_index}.npy")
      except:
         locations = []
      try:
         distances = np.load(f"data/temp/dis_{curr_index}.npy")
      except:
         distances = []

      font_color = (0, 255, 0)
      
      for face, dis in zip(locations, distances):
         x1, y1, x2, y2 = (face[3], face[0], face[1], face[2])
         # print("x1: ", x1, "\ny1: ", y1, "\nx2: ", x2, "\ny2: ", y2)
         # Draw the rectangle on the original image
         if float(dis) == 0.0:
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (180,180,180), 2)
            continue

         if float(dis) > toleransi:
            font_color = (0,120,255)

         frame = cv2.rectangle(frame, (x1, y1), (x2, y2), font_color, 2)

         # Calculate text size to create the rectangle
         # (text_width, text_height), baseline = cv2.getTextSize(dis, cv2.FONT_HERSHEY_SIMPLEX, .6, 2)

         # print("text width ", text_width)
         # print("text height ", text_height)

         # Define the position of the rectangle (top-left and bottom-right corners)
         m1, n1 = x1, y1  # Starting point of the text (x, y)
         m2, n2 = m1 + 47, n1 - 28  # Rectangle size based on text size

         # Draw the rectangle (filled rectangle with background color)
         frame = cv2.rectangle(frame, (m1, n1 - 3), (m2, n2), (255, 255, 255), -1)  # -1 fills the rectangle

         # Put the text on the image inside the rectangle
         frame = cv2.putText(frame, dis, (x1 + 5, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, .5, (0, 0, 0), 1, cv2.LINE_AA)

      # TAMPILKAN FRAME
      x, y, w, h = 0, 0, title_width[curr_index], title_height[curr_index]
      frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), -1)
      frame = cv2.putText(frame, f"{ruang_kam[curr_index][1]} - {ruang_nama[curr_index]} {length_id[curr_index]}", (15, 27), cv2.FONT_HERSHEY_TRIPLEX, 0.6, (220, 220, 0), 1, cv2.LINE_AA)
      
      img = Image.fromarray(frame)
      # print(frame)
      photo = ImageTk.PhotoImage(image=img)
      canvas.photo = photo

      # check if image already exists
      if image_id:       
         # replace image in PhotoImage on canvas
         canvas.itemconfig(image_id, image=photo)
      else:
         # create first image on canvas and keep its ID
         image_id = canvas.create_image((0,0), image=photo, anchor='nw')

      # TAMPILKAN FOTO YANG TERIDENTIFIKASI
      try:
         array_face_names = np.load(f"data/temp/array_face_names_{curr_index}.npy")
      except:
         array_face_names = np.array([])

      # print(array_face_names)

      if not np.array_equal(array_face_names, array_face_names_global[curr_index]):
         array_face_names_global[curr_index] = array_face_names

         # print(array_face_names)

         index = 0

         for label in labels_in_frame:
            label.configure(text="")
            if image_id_in_frame[index]:       
               # replace image in PhotoImage on pics_in_frame[index]
               # pics_in_frame[index].delete("all")
               pics_in_frame[index].itemconfig(image_id_in_frame[index], state='hidden')
            index += 1

         if array_face_names.size == 0:
            value_teridentifikasi.configure(text="-")
         else:
            value_teridentifikasi.configure(text="")
            index = 0
            extra = 0

            for name in array_face_names:
               if index < 20:
                  id_file = name.split("&")[0]
                  nama_mahasiswa = name.split("&")[1]

                  labels_in_frame[index].configure(text=nama_mahasiswa.upper())
                  img = Image.open(f"{identified_folder}/{id_file}.jpg").resize((87,87), Image.Resampling.LANCZOS)
                  # convert to Tkinter image
                  photo = ImageTk.PhotoImage(image=img)
                  # solution for bug in `PhotoImage`
                  pics_in_frame[index].photo = photo
                  # check if image already exists
                  if image_id_in_frame[index]:
                     # replace image in PhotoImage on pics_in_frame[index]
                     pics_in_frame[index].itemconfig(image_id_in_frame[index], image=photo, state='normal')
                  else:
                     # create first image on pics_in_frame[index] and keep its ID
                     image_id_in_frame[index] = pics_in_frame[index].create_image((45, 45), anchor="center", image=photo)
               else:
                  extra += 1
               index += 1

            extras[curr_index] = extra
            if extra:
               if extra > 30:
               # print(f"Extra: {extra}")
                  view_more.configure(text=f"View 30 more", cursor="hand2")
               else:
                  view_more.configure(text=f"View {extra} more", cursor="hand2")
               view_more.bind("<Button-1>", lambda e:open_view_more(curr_index))

      # 0.1 Detik sekali (10 fps)
      window.after(100, show_cam_id)

   def get_all_captures_id():
      # nonlocal captures
      nonlocal length_id
      # nonlocal offset
      nonlocal title_width
      nonlocal title_height

      nonlocal captures_id

      i_ruang_kam = 0

      offset_width = []
      offset_height = []

      for i, x in enumerate(captures):
         # print(f"Checking cap_{i}...")
         if i not in cam_indexes_id:
            x.release()

      for c_index in cam_indexes_id:
         captures_id.append(captures[c_index])

         length_id.append(length[c_index])

         # print(f'offset {i_ruang_kam} : 1310/{length_x[i_ruang_kam]} = {1310/length_x[i_ruang_kam]}')

         offset_width.append(1310/length_x[c_index])
         offset_height.append(737/length_y[c_index])

         (text_width, text_height), baseline = cv2.getTextSize(f"{ruang_kam[i_ruang_kam][1]} {ruang_nama[i_ruang_kam]} {length[c_index]}", cv2.FONT_HERSHEY_SIMPLEX, .6, 1)

         # print(int(text_width * 30/100))

         title_width.append(text_width + 70)
         title_height.append(text_height + 30)

         i_ruang_kam += 1

      # for i, index in enumerate(cam_indexes):
      #    print(f"Menghubungkan kembali kamera {i}..")

      #    capture = cv2.VideoCapture(index)
      #    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
      #    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
      #    captures[i] = capture
      #    ret, frame = capture.read()
      #    length[i] = f"({len(frame)}p)"
      #    offset.append(1310/len(frame[0]))


      #    (text_width, text_height), baseline = cv2.getTextSize(f"{ruang_nama[i]} {length[i]} 10fps", cv2.FONT_HERSHEY_SIMPLEX, .6, 1)

      #    title_width.append(text_width + int(text_width * 15/100))
      #    title_height.append(text_height + 30)

      np.save("data/temp/offset_width", offset_width)
      np.save("data/temp/offset_height", offset_height)

   def get_all_frames_id():
      nonlocal frames
      nonlocal default_frames
      nonlocal length_id
      # np.set_printoptions(threshold=np.inf)
      for index, capture in enumerate(captures_id):
         ret, frame = capture.read()
         if not ret:
            capture = cv2.VideoCapture("static/images/Fix-Windows-10-Camera-not-working_1.mp4")
            # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            ret, frame = capture.read()
            length_id[index] = ""
            # frame = frames[index]
         # print("Type frame: ", type(frame))
         # print("Len frame: ", len(frame))
         # print("Shapes frame: ", frame.shape)
         # print("Frame: ", frame)
         frames[index] = frame
         np.save(f"data/temp/frame_{index}", frame)

      # Khusus pengujian
      window.after(100, get_all_frames_id)

   identified_folder = "static/images/identified"

   secondary_window = False
   pics_in_frame_extra = []
   labels_in_frame_extra = []
   image_id_in_frame_extra = []
   np.save("data/temp/view_more", np.array([False]))
   np.save("data/temp/offset_width", [])
   np.save("data/temp/offset_height", [])

   # print("view more, offset saved")

   title_width = []
   title_height = []

   image_id = None

   frames = []
   default_frames = []
   captures_id = []
   cam_indexes_id = []
   curr_index = 0
   processes = []
   array_face_names_global = []
   jadwal = []
   kegiatan_saat_ini = []

   def ganti_ruang(index_a):
      nonlocal curr_index
      
      if quit_box:
         quit_box.destroy()

      for btn in button_ruang:
         btn.configure(state="normal")
      button_ruang[index_a].configure(state="disabled")
      curr_index = index_a
      value_kegiatan.configure(text=kegiatan_saat_ini[curr_index][0])

      index = 0

      for label in labels_in_frame:
         label.configure(text="")
         if image_id_in_frame[index]:       
            # replace image in PhotoImage on pics_in_frame[index]
            pics_in_frame[index].itemconfig(image_id_in_frame[index], state='hidden')
         index += 1
      

      if not any(array_face_names_global[curr_index]):
         value_teridentifikasi.configure(text="-")
      else:
         value_teridentifikasi.configure(text="")
         index = 0
         extra = 0

         for name in array_face_names_global[curr_index]:
            if index < 20:
               id_file = name.split("&")[0]
               nama_mahasiswa = name.split("&")[1]

               labels_in_frame[index].configure(text=nama_mahasiswa.upper())

               # ERR
               # print("Files in folder:", os.listdir(identified_folder))
               file_path = os.path.join(identified_folder, f"{id_file}.jpg")
               if not os.path.exists(file_path):
                  continue
               img = Image.open(file_path).resize((87,87), Image.Resampling.LANCZOS)
               # convert to Tkinter image
               photo = ImageTk.PhotoImage(image=img)
               # solution for bug in `PhotoImage`
               pics_in_frame[index].photo = photo
               # check if image already exists
               if image_id_in_frame[index]:
                  # replace image in PhotoImage on pics_in_frame[index]
                  pics_in_frame[index].itemconfig(image_id_in_frame[index], image=photo, state='normal')
               else:
                  # create first image on pics_in_frame[index] and keep its ID
                  image_id_in_frame[index] = pics_in_frame[index].create_image((45, 45), anchor="center", image=photo)
            else:
               extra += 1
            index += 1

      if extras[curr_index]:
         if extras[curr_index] > 30:
            view_more.configure(text=f"View 30 more", cursor="hand2")
         else:
            view_more.configure(text=f"View {extras[curr_index]} more", cursor="hand2")
         view_more.bind("<Button-1>", lambda e:open_view_more(curr_index))
      else:
         view_more.configure(text="")
         view_more.unbind("<Button-1")
      if secondary_window:
         secondary_window.destroy()

   window = customtkinter.CTkToplevel(root)
   window.geometry("+%i+%i" % (40, 120))
   window.title(f"Identifikasi Wajah ({nama_komputer})")
   window.iconphoto(False, global_icon_image)
   window.protocol("WM_DELETE_WINDOW", konfirmasi_quit_id)

   # print("window root created")
   
   customtkinter.CTkFrame(window, width=18).grid(row=0, column=0, rowspan=2)

   left_frame = customtkinter.CTkFrame(window)
   left_frame.columnconfigure(0, weight=3)

   first = True
   def get_status_identifikasi():
      nonlocal first
      nonlocal identifikasi
      nonlocal identifikasi_old
      nonlocal time_start
      nonlocal time_stop
      nonlocal kegiatan_saat_ini

      # Perbarui keterangan status identifikasi "OFF Starts in ..." atau "ON Stops in ..."
      if datetime.now() >= time_start and datetime.now() < time_stop:
         identifikasi = True
         gap = time_stop - datetime.now()
         # print(gap.seconds)
         if gap.seconds < 86000:
            value_status.configure(text=f"ON. Stops in.. {str(timedelta(seconds = gap.seconds))}")
         else:
            value_status.configure(text=f"ON. Stops in.. {str(timedelta(seconds = durasi) - timedelta(seconds = 1))}")
      else:
         identifikasi = False
         gap = time_start - datetime.now()
         # print(gap.seconds)
         if gap.seconds < 86000:
            value_status.configure(text=f"OFF. Starts in.. {str(timedelta(seconds = gap.seconds))}")
         else:
            value_status.configure(text=f"OFF. Starts in.. {str(timedelta(seconds = jeda) - timedelta(seconds = 1))}")

      jadwal_list = np.load("data/temp/jadwal_all.npy", allow_pickle=True)

      # print("Jadwal: ", jadwal_list)

      # index_ruang = 0
      waktu_sekarang = datetime.now()
      for i, ruang in enumerate(ruang_id):
         for jadwal in jadwal_list:
            # print(ruang, "and", jadwal["ruangan"], ruang == jadwal["ruangan"])
            # print(waktu_sekarang, ">=", jadwal["waktu_mulai"], waktu_sekarang >= jadwal["waktu_mulai"])
            # print(waktu_sekarang, "<",jadwal["waktu_selesai"], waktu_sekarang < jadwal["waktu_selesai"], "\n")
            if str(ruang) == str(jadwal["ruangan_id"]) and waktu_sekarang >= jadwal["waktu_mulai"] and waktu_sekarang < jadwal["waktu_selesai"]:
               # a_new = {
               #    "id_jadwal": jadwal["_id"],
               #    "nama_kegiatan": jadwal["nama_kegiatan"],
               #    "waktu_mulai": jadwal["waktu_mulai"],
               #    "waktu_selesai": jadwal["waktu_selesai"],
               #    "keterangan": jadwal["keterangan"],
               #    "dosen": str(jadwal["dosen_id"])
               # }
               kegiatan_saat_ini[i] = [jadwal['nama_kegiatan'], str(jadwal["_id"]), ruang_id[i], ruang_ket[i]]
               break
            else:
               kegiatan_saat_ini[i] = ["", False, ruang_id[i], ruang_ket[i]]

            # index_ruang += 1
      
      # print("Kegiatan saat ini:", kegiatan_saat_ini)

      value_kegiatan.configure(text=kegiatan_saat_ini[curr_index][0])
      # print("Kegiatan saat ini: ", kegiatan_saat_ini)
      np.save("data/temp/kegiatan_saat_ini", np.array(kegiatan_saat_ini))

      for index, frame in enumerate(frames):
         # start_1 = time.time()
         success, buffer = cv2.imencode(".jpg", frame)
         # end_1 = time.time()
         # print(f"Execution time: {end_1 - start_1} seconds")
         if success:
            if first:
               # print(type(buffer.tobytes()))
               asyncio.run(save_frame_0(buffer.tobytes(), ruang_id[index], toleransi, ObjectId(kegiatan_saat_ini[index][1]) if kegiatan_saat_ini[index][1] else None, kegiatan_saat_ini[index][0], frame_ids[index], ruang_kam[index][1]))
            else:
               asyncio.run(save_frame_1(buffer.tobytes(), frame_ids[index], ObjectId(kegiatan_saat_ini[index][1]) if kegiatan_saat_ini[index][1] else None, kegiatan_saat_ini[index][0]))
      first = False

      if identifikasi != identifikasi_old:
         if not identifikasi:
            time_start = time_start + timedelta(seconds = jeda) + timedelta(seconds = durasi)
            time_stop = time_stop + timedelta(seconds = jeda) + timedelta(seconds = durasi)
            view_more.configure(text="")
            view_more.unbind("<Button-1>")
         else:
            if os.path.exists(identified_folder):
               shutil.rmtree(identified_folder)
               os.mkdir(identified_folder)
         identifikasi_old = identifikasi
         np.save("data/temp/status_main", np.array([identifikasi]))

      # 1 Detik
      window.after(1000, get_status_identifikasi)


   my_frame = customtkinter.CTkScrollableFrame(left_frame, height=50, width=1034, orientation="horizontal")

   length_id = []
   button_ruang = []
   extras = []
   index_ruang = 0

   # print("ruang id: ", ruang_id)
   # print("ruang kam: ", ruang_kam)
   for x,y in ruang_kam:
      btn = customtkinter.CTkButton(my_frame, text=y, command=partial(ganti_ruang, index_ruang))
      ToolTip(btn, msg=f"{y} - {ruang_nama[index_ruang]} ({x})")
      btn.pack(side="left", padx=10)
      button_ruang.append(btn)
      indd = int(y.split(" ")[1])
      cam_indexes_id.append(indd)
      extras.append(False)
      frames.append(False)
      # length.append("")
      default_frames.append(False)
      np.save(f"data/temp/array_face_names_{index_ruang}", [])
      np.save(f"data/temp/frame_{index_ruang}", [])
      np.save(f"data/temp/loc_{index_ruang}", [])
      np.save(f"data/temp/dis_{index_ruang}", [])
      array_face_names_global.append([False])
      jadwal.append([False])
      # captures_id.append(False)
      kegiatan_saat_ini.append(["", False, ruang_id[index_ruang], ruang_ket[index_ruang], {}])
      p = Process(target=identifikasi_frame, args=(expires, toleransi, index_ruang, data_queue, frame_ids[index_ruang],))
      processes.append(p)
      index_ruang += 1

   # print("cam indexes id: ", cam_indexes_id)
   # print("loop ruang kam done")

   button_ruang[0].configure(state="disabled")

   my_frame.grid(row=1, column=0,sticky="w")
   canvas = customtkinter.CTkCanvas(left_frame, width=1280, height=720)
   canvas.grid(row=2, column=0, pady=10)

   right_frame = customtkinter.CTkFrame(window)
   right_frame_top = customtkinter.CTkFrame(right_frame)
   right_frame_top.columnconfigure(0, weight=1)

   durasi_str = str(timedelta(seconds = durasi))
   jeda_str = str(timedelta(seconds = jeda))

   customtkinter.CTkLabel(
      right_frame_top,
      text=f"Durasi Scan: {durasi_str}",
      width=30,
      height=2, font=customtkinter.CTkFont("", 14)
   ).grid(column=0, row=0, padx=10, pady=10)

   customtkinter.CTkLabel(
      right_frame_top,
      text=f"Jeda Scan: {jeda_str}",
      width=30,
      height=2, font=customtkinter.CTkFont("", 14)
   ).grid(column=1, row=0, padx=10, pady=10)

   customtkinter.CTkLabel(
      right_frame_top,
      text=f"Expires: {expires} detik",
      width=30,
      height=2, font=customtkinter.CTkFont("", 14)
   ).grid(column=0, row=1, padx=10, pady=10)

   customtkinter.CTkLabel(
      right_frame_top,
      text=f"Threshold: {toleransi}",
      width=30,
      height=2, font=customtkinter.CTkFont("", 14)
   ).grid(column=1, row=1, padx=10, pady=10)

   right_frame_bottom = customtkinter.CTkFrame(right_frame)
   right_frame_bottom_top = customtkinter.CTkFrame(right_frame_bottom)
   value_status = customtkinter.CTkLabel(right_frame_bottom_top, text=f"ON", width=233, justify="left", anchor="w", font=customtkinter.CTkFont("", 14))

   customtkinter.CTkLabel(right_frame_bottom_top, text=f"Kegiatan Saat Ini", width=130, justify="left", anchor="w", font=customtkinter.CTkFont("", 14)).grid(column=0, row=0, padx=5)

   customtkinter.CTkLabel(right_frame_bottom_top, text=f":", width=3, font=customtkinter.CTkFont("", 14)).grid(column=1, row=0)

   value_kegiatan = customtkinter.CTkLabel(right_frame_bottom_top, text=kegiatan_saat_ini[0][0], width=233, justify="left", anchor="w", font=customtkinter.CTkFont("", 14))
   value_kegiatan.grid(column=2, row=0, padx=5)

   customtkinter.CTkLabel(right_frame_bottom_top, text=f"Status Scan",  width=130, justify="left", anchor="w", font=customtkinter.CTkFont("", 14)).grid(column=0, row=1, padx=5)

   customtkinter.CTkLabel(right_frame_bottom_top, text=f":", width=3, justify="left", anchor="w", font=customtkinter.CTkFont("", 14)).grid(column=1, row=1)

   value_status.grid(column=2, row=1, padx=5)

   customtkinter.CTkLabel(right_frame_bottom_top, text=f"Teridentifikasi", width=130, justify="left", anchor="w", font=customtkinter.CTkFont("", 14)).grid(column=0, row=2, padx=5)

   customtkinter.CTkLabel(right_frame_bottom_top, text=f":", width=3, font=customtkinter.CTkFont("", 14)).grid(column=1, row=2)

   value_teridentifikasi = customtkinter.CTkLabel(right_frame_bottom_top, text=f"-", width=233, justify="left", anchor="w", font=customtkinter.CTkFont("", 14))
   value_teridentifikasi.grid(column=2, row=2, padx=5)

   right_frame_bottom_top.grid(row=0, column=0, columnspan=3, pady=(10,0))
   
   # print("ambil jadwal")
   jadwal_all = np.load("data/temp/jadwal_all.npy", allow_pickle=True)
   # print("jadwal all: ", jadwal_all)

   # print("update jadwal")
   update_jadwal()
   # print("done update jadwal")

   pics_frame = customtkinter.CTkFrame(right_frame_bottom)
   pics_frame.columnconfigure(0, weight=1)
   pics_frame.grid(row=1, column=0, columnspan=3, pady=(22,0))

   pics_in_frame = []
   labels_in_frame = []
   image_id_in_frame = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

   pic_1 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_1.grid(row=0, column=0, padx=3, pady=(5, 0))
   label_pic_1 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_1.grid(row=1, column=0, padx=3, pady=(0,10))
   pics_in_frame.append(pic_1)
   labels_in_frame.append(label_pic_1)

   pic_2 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_2.grid(row=0, column=1, padx=3, pady=(5, 0))
   label_pic_2 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_2.grid(row=1, column=1, padx=3, pady=(0,10))
   pics_in_frame.append(pic_2)
   labels_in_frame.append(label_pic_2)

   pic_3 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_3.grid(row=0, column=2, padx=3, pady=(5, 0))
   label_pic_3 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_3.grid(row=1, column=2, padx=3, pady=(0,10))
   pics_in_frame.append(pic_3)
   labels_in_frame.append(label_pic_3)

   pic_4 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_4.grid(row=0, column=3, padx=3, pady=(5, 0))
   label_pic_4 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_4.grid(row=1, column=3, padx=3, pady=(0,10))
   pics_in_frame.append(pic_4)
   labels_in_frame.append(label_pic_4)

   pic_5 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_5.grid(row=0, column=4, padx=3, pady=(5, 0))
   label_pic_5 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_5.grid(row=1, column=4, padx=3, pady=(0,10))
   pics_in_frame.append(pic_5)
   labels_in_frame.append(label_pic_5)

   pic_6 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_6.grid(row=2, column=0, padx=3, pady=(5, 0))
   label_pic_6 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_6.grid(row=3, column=0, padx=3, pady=(0,10))
   pics_in_frame.append(pic_6)
   labels_in_frame.append(label_pic_6)

   pic_7 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_7.grid(row=2, column=1, padx=3, pady=(5, 0))
   label_pic_7 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_7.grid(row=3, column=1, padx=3, pady=(0,10))
   pics_in_frame.append(pic_7)
   labels_in_frame.append(label_pic_7)

   pic_8 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_8.grid(row=2, column=2, padx=3, pady=(5, 0))
   label_pic_8 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_8.grid(row=3, column=2, padx=3, pady=(0,10))
   pics_in_frame.append(pic_8)
   labels_in_frame.append(label_pic_8)

   pic_9 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_9.grid(row=2, column=3, padx=3, pady=(5, 0))
   label_pic_9 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_9.grid(row=3, column=3, padx=3, pady=(0,10))
   pics_in_frame.append(pic_9)
   labels_in_frame.append(label_pic_9)

   pic_10 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_10.grid(row=2, column=4, padx=3, pady=(5, 0))
   label_pic_10 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_10.grid(row=3, column=4, padx=3, pady=(0,10))
   pics_in_frame.append(pic_10)
   labels_in_frame.append(label_pic_10)

   pic_11 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_11.grid(row=4, column=0, padx=3, pady=(5, 0))
   label_pic_11 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_11.grid(row=5, column=0, padx=3, pady=(0,10))
   pics_in_frame.append(pic_11)
   labels_in_frame.append(label_pic_11)

   pic_12 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_12.grid(row=4, column=1, padx=3, pady=(5, 0))
   label_pic_12 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_12.grid(row=5, column=1, padx=3, pady=(0,10))
   pics_in_frame.append(pic_12)
   labels_in_frame.append(label_pic_12)

   pic_13 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_13.grid(row=4, column=2, padx=3, pady=(5, 0))
   label_pic_13 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_13.grid(row=5, column=2, padx=3, pady=(0,10))
   pics_in_frame.append(pic_13)
   labels_in_frame.append(label_pic_13)

   pic_14 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_14.grid(row=4, column=3, padx=3, pady=(5, 0))
   label_pic_14 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_14.grid(row=5, column=3, padx=3, pady=(0,10))
   pics_in_frame.append(pic_14)
   labels_in_frame.append(label_pic_14)

   pic_15 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_15.grid(row=4, column=4, padx=3, pady=(5, 0))
   label_pic_15 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_15.grid(row=5, column=4, padx=3, pady=(0,10))
   pics_in_frame.append(pic_15)
   labels_in_frame.append(label_pic_15)

   pic_16 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_16.grid(row=6, column=0, padx=3, pady=(5, 0))
   label_pic_16 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_16.grid(row=7, column=0, padx=3, pady=(0,10))
   pics_in_frame.append(pic_16)
   labels_in_frame.append(label_pic_16)

   pic_17 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_17.grid(row=6, column=1, padx=3, pady=(5, 0))
   label_pic_17 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_17.grid(row=7, column=1, padx=3, pady=(0,10))
   pics_in_frame.append(pic_17)
   labels_in_frame.append(label_pic_17)

   pic_18 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_18.grid(row=6, column=2, padx=3, pady=(5, 0))
   label_pic_18 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_18.grid(row=7, column=2, padx=3, pady=(0,10))
   pics_in_frame.append(pic_18)
   labels_in_frame.append(label_pic_18)

   pic_19 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_19.grid(row=6, column=3, padx=3, pady=(5, 0))
   label_pic_19 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_19.grid(row=7, column=3, padx=3, pady=(0,10))
   pics_in_frame.append(pic_19)
   labels_in_frame.append(label_pic_19)

   pic_20 = customtkinter.CTkCanvas(pics_frame, width=87, height=87, background="SpringGreen3")
   pic_20.grid(row=6, column=4, padx=3, pady=(5, 0))
   label_pic_20 = customtkinter.CTkLabel(pics_frame, width=12, height=2, wraplength=75, font=("", 10), text="")
   label_pic_20.grid(row=7, column=4, padx=3, pady=(0,10))
   pics_in_frame.append(pic_20)
   labels_in_frame.append(label_pic_20)

   view_more = customtkinter.CTkLabel(right_frame_bottom, text="", width=30, height=2, font=customtkinter.CTkFont("", 14))
   view_more.grid(row=2, column=0, columnspan=3, sticky="e", padx=10)

   right_frame_top.grid(row=0, column=0, pady=22)
   right_frame_bottom.grid(row=1, column=0)
   right_frame.grid(column=2, row=1, padx=(10,20), pady=20)
   left_frame.grid(column=1, row=1, padx=(20,10), pady=20)

   # print("get status identifikasi done")

   # print("summon all proses")
   for p in processes:
      p.start()
   # print("all proses summoned")
   
   # Diff
   # Start the process to save data to MongoDB
   px = Process(target=queue_process, args=(data_queue,))
   px.start()

   get_all_captures_id()
   get_all_frames_id()
   show_cam_id()

   time_start = datetime.now() + timedelta(seconds = jeda)
   time_stop = time_start + timedelta(seconds = durasi)
   
   get_status_identifikasi()

   window.mainloop()

def simpan_setup():
   print("Menyimpan setup...\n")

   cek_ruang()

   now2 = datetime.now()
   year2 = now2.year
   month2 = f"0{now2.month}" if now2.month < 10 else now2.month 
   day2 = f"0{now2.day}" if now2.day < 10 else now2.day

   if f"{year2}-{month2}-{day2}" != f"{year}-{month}-{day}":
      print(f"Terdapat perbedaan tanggal saat setup inisiasi dibuka ({year}-{month}-{day}) & disimpannya ({year2}-{month2}-{day2}). Harap coba kembali.")
      p2.join()
      p2.terminate()
      p3.join()
      p3.terminate()
      p4.join()
      p4.terminate()
      root.destroy()
      sys.exit()

   durasi = int(dur_entry.get())
   jeda = int(jeda_entry.get())
   expires = int(exp_entry.get())
   toleransi = float(toleransi_entry.get())
   nama_komputer = nama_entry.get()

   res = check_nama_komputer(nama_komputer)
   if not res:
      nama_entry.delete(0, customtkinter.END)
      button_mulai.configure(state="disabled")
      return CTkMessagebox(title="Info", message=f"Nama komputer '{nama_komputer}' telah ada yang menggunakan.")


   ruang_ls_1 = []
   p2.join()
   p2.terminate()
   p3.join()
   p3.terminate()
   p4.join()
   p4.terminate()

   frame_ids = []

   for el in ruang_ls:
      ruang_ls_1.append(str(el.split("(")[1]).split(")")[0])
      frame_ids.append(save_frame("", "", toleransi, "", "", nama_komputer))



   ruang_kam = list(zip(ruang_ls_1, cam_ls))

   root.withdraw()
   root.quit()
   root.after_cancel(gaf)
   root.after_cancel(sc)
   
   jalankan_identifikasi(durasi, jeda, expires, toleransi, ruang_kam, ruang, frame_ids, nama_komputer)

def on_toleransi_entry_enter(event):
   if button_mulai.cget("state") == "normal":
      simpan_setup()

def get_all_frames():
   global gaf
   global frames
   for cam in cam_indexes:
      index = int(str(cam).split(" ")[1])
      capture = captures[index]
      ret, frame = capture.read()
      # if not ret:
      #    refresh_kamera(my_frame)
      #    break
      frames[index] = frame
   gaf = root.after(100, get_all_frames)

def get_all_captures():
   global captures
   global length
   global length_x
   global length_y
   # indexx = ["interstellar","onceupon","vid_4"]
   for cam in cam_indexes:
      index = int(str(cam).split(" ")[1])
      print(f"Menghubungkan kamera ({index+1}/{len(cam_indexes)})...")
      capture = cv2.VideoCapture(index)
      # capture = cv2.VideoCapture(f"static/images/{indexx[index]}.mp4")
      capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
      capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
      captures[index] = capture
      ret, frame = capture.read()
      height, width = frame.shape[:2]
      aspect_ratio = width / height
      print(f"Resolution: {width}x{height}")
      print(f"Aspect ratio: {aspect_ratio:.2f} (≈ {round(aspect_ratio, 2) * 9}:9)")
      length.append(f"({height}p)")
      length_x.append(width)
      length_y.append(height)

sc = False

def show_cam():
   global image_id
   global sc
   try:
      frame = frames[curr_index]
      # cv2 uses `BGR` but `GUI` needs `RGB
      frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      frame = cv2.resize(frame, (1280, 720))
      x, y, w, h = 0, 0, 300, 50
      cv2.rectangle(frame, (x, x), (x + w, y + h), (0, 0, 0), -1)
      cv2.putText(frame, f"KAMERA {curr_index} {length[curr_index]}", (x + int(w/10), y + int(h/1.6)), cv2.FONT_HERSHEY_COMPLEX, 0.6, (220, 220, 0), 1, cv2.LINE_AA)
      img = Image.fromarray(frame)
      photo = ImageTk.PhotoImage(image=img)
      canvas.photo = photo
      # check if image already exists
      if image_id:       
         # replace image in PhotoImage on canvas
         canvas.itemconfig(image_id, image=photo)
      else:
         # create first image on canvas and keep its ID
         image_id = canvas.create_image((0,0), image=photo, anchor='nw')
   except:
      pass
   sc = root.after(100, show_cam)

def resource_path(relative_path):
   try:
      base_path = sys._MEIPASS  # if bundled by Nuitka or PyInstaller
   except AttributeError:
      base_path = os.path.abspath(".")

   return os.path.join(base_path, relative_path)

def limit_input(P):
    return len(P) <= 10  # Limit to 10 characters


if __name__ == "__main__":   
   # Set OpenCV's log level to fatal only
   freeze_support()
   # Get the current date and time
   now = datetime.now()

   # Extract the year, month, and day
   year = now.year
   month = f"0{now.month}" if now.month < 10 else now.month 
   day = f"0{now.day}" if now.day < 10 else now.day 

   p2 = Process(target=ambil_data_wajah)
   p3 = Process(target=ambil_jadwal_all, args=(f"{year}-{month}-{day}",))
   p4 = Process(target=ambil_aktivitas, args=(str(datetime(year, now.month, now.day)).split(" ")[0],))

   p2.start()
   p3.start()
   p4.start()

   cv2.setLogLevel(1)
   cam_indexes = get_cam_index()
   print(f"Ditemukan {len(cam_indexes)} kamera terhubung")


   customtkinter.set_appearance_mode("light")
   customtkinter.set_default_color_theme("green")

   root = customtkinter.CTk()
   vcmd = (root.register(limit_input), '%P')
   root.title("Pengaturan Identifikasi")

   icon_path = resource_path("facerecognition.png")
   global_icon_image = PhotoImage(file=icon_path)

   ico_icon_path = resource_path("facerecognition.ico")

   root.iconphoto(True, global_icon_image)

   root.iconbitmap(ico_icon_path)

   root.geometry("+%d+%d" % (40, 120))
   root.resizable(False, False)
   root.protocol("WM_DELETE_WINDOW", konfirmasi_quit)

   left_frame = customtkinter.CTkFrame(root, width=300, height=350)
   left_frame.grid(column=0, row=0, sticky="n")
   right_frame = customtkinter.CTkFrame(root, width=300, height=350, bg_color="blue")
   canvas = customtkinter.CTkCanvas(right_frame, width=1280, height=720)
   canvas.grid(row=0, column=0)
   right_frame.grid(column=1, row=0, sticky="n")

   frame0 = customtkinter.CTkFrame(left_frame, width=385, border_color="yellow", border_width=2)
   icon_warning = TablerIcons.load(OutlineIcon.ALERT_TRIANGLE, size=46, color="#FFF", stroke_width=2.0)
   icon_warning_img = customtkinter.CTkImage(icon_warning)
   customtkinter.CTkLabel(frame0, text="", image=icon_warning_img, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, pady=(5,0))
   label_koneksi_database = customtkinter.CTkLabel(frame0, text = "Ambil data ruangan gagal. Coba kembali atau hubungi admin.", padx=5, wraplength=320, width=385, font=customtkinter.CTkFont("", 14))
   label_koneksi_database.grid(row=1, column=0, sticky=customtkinter.W, padx=10, pady=10)
   btn_refresh_db = customtkinter.CTkButton(frame0, text="Coba lagi", command=refresh_cek_db, font=customtkinter.CTkFont("", 14))
   btn_refresh_db.grid(row=2, column=0, pady=(0, 10))
   frame0.grid(column=0, row=0, padx=10,pady=10, sticky="w", columnspan=2)

   retry_window = ""

   frame1_1 = customtkinter.CTkFrame(left_frame)
   frame1_1.grid(row=1, column=0, padx=0, pady=(15,10))

   customtkinter.CTkLabel(frame1_1, text="Max. proses:", justify="center", width=110, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0)

   id_jum_kam_1 = customtkinter.CTkLabel(frame1_1, width=30, text=cpu_count, justify="center", font=customtkinter.CTkFont("", 14))
   ToolTip(id_jum_kam_1, msg="Jumlah maksimal pasangan kamera-ruangan, sesuai jumlah core pada CPU.")
   id_jum_kam_1.grid(row=0, column=1)

   frame1_2 = customtkinter.CTkFrame(left_frame)
   frame1_2.grid(row=1, column=1, ipadx=0, pady=(15, 10))

   customtkinter.CTkLabel(frame1_2, text="Kamera terkoneksi:", justify="center", width=148, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0)

   id_jum_kam = customtkinter.CTkLabel(frame1_2, width=15, text=len(cam_indexes), justify="center", font=customtkinter.CTkFont("", 14))
   id_jum_kam.grid(row=0, column=1, padx=(0, 15))
   icon_refresh = TablerIcons.load(OutlineIcon.REFRESH, size=46, color="#FFF", stroke_width=2.0)
   icon_refresh_img = customtkinter.CTkImage(icon_refresh)
   refresh_kam_btn = customtkinter.CTkButton(frame1_2, image=icon_refresh_img, width=30, text="", command=lambda: refresh_kamera(my_frame), text_color="black", font=customtkinter.CTkFont("", 14))
   ToolTip(refresh_kam_btn, msg="Deteksi ulang kamera yang terhubung")
   refresh_kam_btn.grid(column=2, row=0)

   kode_ruangan_ok = False
   nama_ruangan_ok = False

   kode_ruangan_entry = False
   nama_ruangan_entry = False
   button_kirim = False

   frame2 = customtkinter.CTkFrame(left_frame, width=388)
   ruangan_btn = customtkinter.CTkButton(frame2, text_color="black", text="Daftar Ruangan", command=window_ruangan, font=customtkinter.CTkFont("", 14))
   ToolTip(ruangan_btn, msg="Lihat daftar semua ruangan")
   ruangan_btn.grid(column=0, row=0)

   frame_add = customtkinter.CTkFrame(frame2)
   frame_add.grid(column=1, row=0, padx=(145,0))
   add_btn = customtkinter.CTkButton(frame_add, text="+", width=50, command=tambah_ruangan, text_color="black", font=customtkinter.CTkFont("", 14))
   ToolTip(add_btn, msg="Tambahkan proses identifikasi")
   add_btn.grid(column=0, row=0)
   frame_remove = customtkinter.CTkFrame(frame2)
   frame_remove.grid(column=2, row=0, padx=(20,0))
   remove_btn = customtkinter.CTkButton(frame_remove, text="-", width=50, command=hapus_ruangan, text_color="black", font=customtkinter.CTkFont("", 14))
   ToolTip(remove_btn, msg="Kurangi proses identifikasi")
   remove_btn.grid(column=1, row=0)
   frame2.grid(column=0, row=2, padx=10,pady=5, sticky="w", columnspan=2)


   my_frame = customtkinter.CTkScrollableFrame(left_frame, width=385, height=300)
   my_frame.grid(column=0, row=3, padx=10, pady=(0,10), sticky="w", columnspan=2)


   frame_ruang_kam = customtkinter.CTkFrame(my_frame, width=385)
   customtkinter.CTkLabel(frame_ruang_kam, text="Kamera", text_color="black", font=customtkinter.CTkFont("", 14)).grid(column=0, row=0,  padx=35)
   customtkinter.CTkLabel(frame_ruang_kam, text="Ruangan", text_color="black", font=customtkinter.CTkFont("", 14)).grid(column=1, row=0, padx=100)
   frame_ruang_kam.pack(padx=8,pady=5, anchor="w")


   secondary_window_a = False
   secondary_window_b = False
   secondary_window_c = False
   secondary_window_d = False
   secondary_window_e = False

   frame3 = customtkinter.CTkFrame(left_frame, width=300)
   frame_label_int_durasi = customtkinter.CTkFrame(frame3)
   frame_label_int_durasi.grid(row=0, column=1, sticky="w")
   customtkinter.CTkLabel(frame_label_int_durasi, text="Durasi & Jeda (detik):", anchor="w", justify="left", padx=5, text_color="black", font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, sticky=customtkinter.W, padx=10)
   penjelasan_dur_jed = customtkinter.CTkButton(frame_label_int_durasi, text="?", width=30, command=window_int_dur, text_color="black", font=customtkinter.CTkFont("", 14))
   penjelasan_dur_jed.grid(row=0, column=1, padx=(14,0))
   ToolTip(penjelasan_dur_jed, msg="Lihat penjelasan mengenai durasi & jeda")
   sv_dur = customtkinter.StringVar()
   sv_dur.trace_add("write", check_dur)
   dur_entry = customtkinter.CTkEntry(frame3, width=50, justify="center", textvariable=sv_dur, font=customtkinter.CTkFont("", 14))
   ToolTip(dur_entry, msg="Durasi identifikasi")
   dur_entry.grid(row=0, column=2, padx=(20,10))
   sv_jeda = customtkinter.StringVar()
   sv_jeda.trace_add("write", check_jeda)
   jeda_entry = customtkinter.CTkEntry(frame3, width=50, justify="center", textvariable=sv_jeda, font=customtkinter.CTkFont("", 14))
   ToolTip(jeda_entry, msg="Jeda identifikasi")
   jeda_entry.grid(row=0, column=3)
   frame3.grid(column=0, row=4, padx=(10,0),pady=5, sticky="w", columnspan=2)

   frame4 = customtkinter.CTkFrame(left_frame, width=300)
   frame_expires = customtkinter.CTkFrame(frame4)
   frame_expires.grid(row=0, column=1, sticky="w")
   customtkinter.CTkLabel(frame_expires, text="Expires (detik):", anchor="w", justify="left", padx=5, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, padx=10)
   penjelasan_exp = customtkinter.CTkButton(frame_expires, text="?", width=30, command=window_exp, text_color="black", font=customtkinter.CTkFont("", 14))
   penjelasan_exp.grid(row=0, column=1, padx=(57,0))
   ToolTip(penjelasan_exp, msg="Lihat penjelasan mengenai expires")
   sv_exp = customtkinter.StringVar()
   sv_exp.trace_add("write", check_exp)
   exp_entry = customtkinter.CTkEntry(frame4, width=50, justify="center", textvariable=sv_exp, font=customtkinter.CTkFont("", 14))
   ToolTip(exp_entry, msg="Expires identifikasi")
   exp_entry.grid(row=0, column=2, padx=(20,0))
   frame4.grid(column=0, row=5, padx=10,pady=5, sticky="w", columnspan=2)

   frame5 = customtkinter.CTkFrame(left_frame, width=300)
   frame_toleransi = customtkinter.CTkFrame(frame5)
   frame_toleransi.grid(row=0, column=1, sticky="w")
   customtkinter.CTkLabel(frame_toleransi, text="Threshold (0.0 - 1.0):", anchor="w", justify="left", padx=5, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, padx=10)
   penjelasan_thresh = customtkinter.CTkButton(frame_toleransi, text="?", width=30, command=window_tol, text_color="black", font=customtkinter.CTkFont("", 14))
   penjelasan_thresh.grid(row=0, column=1, padx=(17,0))
   ToolTip(penjelasan_thresh, msg="Lihat penjelasan mengenai threshold")
   sv_toleransi = customtkinter.StringVar()
   sv_toleransi.trace_add("write", check_toleransi)
   toleransi_entry = customtkinter.CTkEntry(frame5, width=50, justify="center", textvariable=sv_toleransi, font=customtkinter.CTkFont("", 14))
   ToolTip(toleransi_entry, msg="Threshold identifikasi")
   toleransi_entry.bind("<Return>", on_toleransi_entry_enter)
   toleransi_entry.grid(row=0, column=2, padx=(20,0))
   frame5.grid(column=0, row=6, padx=10,pady=5, sticky="w", columnspan=2)

   frame6 = customtkinter.CTkFrame(left_frame, width=300)
   frame_nama = customtkinter.CTkFrame(frame6)
   frame_nama.grid(row=0, column=1, sticky="w")
   customtkinter.CTkLabel(frame_nama, text="Nama Komputer:", anchor="w", justify="left", padx=5, font=customtkinter.CTkFont("", 14)).grid(row=0, column=0, padx=10)
   sv_nama = customtkinter.StringVar()
   sv_nama.trace_add("write", check_nama)
   nama_entry = customtkinter.CTkEntry(frame6, width=190, font=customtkinter.CTkFont("", 14), textvariable=sv_nama)
   ToolTip(nama_entry, msg="Nama/identitas komputer yang menjalankan identifikasi.")
   nama_entry.grid(row=0, column=2, padx=(44,0))
   frame6.grid(column=0, row=7, padx=10,pady=5, sticky="w", columnspan=2)

   button_mulai = customtkinter.CTkButton(left_frame, width=100, text="Mulai", state="disabled", command= simpan_setup, text_color="black", font=customtkinter.CTkFont("", 14))
   button_mulai.grid(column=0, row=8, pady=(12,20), columnspan=2)

   image_id = None
   kamera_value = 0

   frames = []
   captures = []
   curr_index = 0
   cam_ls = []
   ruang_ls = []

   gaf = False
   length = []
   length_x = []
   length_y = []

   for cam in cam_indexes:
      frames.append(False)
      captures.append(False)
      cam_ls.append("Kamera 0")

   opsi_ruang_2 = []
   opsi_ruang_3 = []
   opsi_kam_2 = []

   ruang = ambil_ruangan([])

   np.save("data/temp/known_face_encodings", [])
   np.save("data/temp/name_list", [])
   np.save("data/temp/id_mhs_list", [])
   np.save("data/temp/nim_list", [])

   if len(ruang) > 0:
      ruang_indexes = []
      ruang_list = []

      for el in ruang:
         if len(f"{el['kode_ruangan']} - {el['nama_ruangan']}") > 28 :
            ruang_indexes.append(f"{el['nama_ruangan']} ({el['kode_ruangan']})"[:28] + "..")
         else:
            ruang_indexes.append(f"{el['nama_ruangan']} ({el['kode_ruangan']})")
         ruang_list.append([el['kode_ruangan'], el['nama_ruangan']])

      opsi_cam = []
      opsi_ruang = []

      framex_list = []


      for x in range(len(cam_indexes)):
         framex = customtkinter.CTkFrame(my_frame)

         clicked_opsi_kam = customtkinter.StringVar()
         clicked_opsi_kam.set(cam_indexes[0])
         opsi_cam.append(clicked_opsi_kam)
         opsi_2 = customtkinter.CTkOptionMenu(framex, variable=opsi_cam[x], values=cam_indexes, text_color="black", width=115, font=customtkinter.CTkFont("", 14))
         opsi_kam_2.append(opsi_2)
         opsi_2.grid(column=0, row=0)
         opsi_cam[x].trace_add("write", partial(cek_cams2, opsi_cam[x]))
         
         clicked_opsi_ruang = customtkinter.StringVar()
         clicked_opsi_ruang.set(ruang_indexes[0])
         opsi_ruang.append(clicked_opsi_ruang)
         opsi = customtkinter.CTkOptionMenu(framex, variable=opsi_ruang[x], text_color="black", width=242, font=customtkinter.CTkFont("", 14))
         opsix = CTkScrollableDropdown(opsi, values=ruang_indexes, height=450, justify="left", width=265, font=customtkinter.CTkFont("", 14))
         opsi_ruang_2.append(opsi)
         opsi_ruang_3.append(opsix)
         opsi.grid(column=1, row=0, padx=(10,0))
         
         
         framex.pack(padx=5, pady=5)
         framex_list.append(framex)

   cek_database(ruang)

   root.mainloop()