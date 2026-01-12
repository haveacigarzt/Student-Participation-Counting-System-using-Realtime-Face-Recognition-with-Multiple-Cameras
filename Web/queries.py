from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
import os
from flask import flash
from bson import ObjectId
import uuid
from flask import flash
from operator import itemgetter

from datetime import datetime, timedelta, time
from utils_face import hitung_wajah, face_encodings, compare_faces_3
from utils import get_hari_dan_tanggal, get_tanggal


atlas_url = "mongodb+srv://afriandypramana:bczFDLSJSzrATKdP@cluster0.yqmayik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

temp_folder = "static/pictures/temp"
foto_profil_folder = "static/pictures/foto_profil"
foto_wajah_folder = "static/pictures/foto_wajah"

client = AsyncIOMotorClient(atlas_url, server_api=ServerApi("1"))
client2 = MongoClient(atlas_url)
loop = client.get_io_loop()

async def find_user_complete(id):
   try:
      db = client["face_identification_3"]
      collection = db["akun"]
      id = ObjectId(id)      
      user =  await collection.find_one({"_id": id })

      if user:
         return user
      return False
   except Exception:
      print("MongoDB: Fail to connect")
      return False

async def find_user(pengguna, username):
   db = client["face_identification_3"]
   collection = db[pengguna]
   
   user =  await collection.find_one({ "username": username })

   if user:
      return [user["password"], str(user["_id"]), str(user["nama"]).title(), str(user["foto_profil_path"])]
   return [False, False, False, False]

async def find_list(tipe, field):
   db = client["face_identification_3"]
   collection = db[tipe]

   myset = set()
   result = collection.find({})

   if field == "username":
      mhs = db["mahasiswa"].find({})
      dos = db["dosen"].find({})
      ortu = db["mahasiswa"].find({})
      for item in await mhs.to_list(length=None):
         myset.add(item["username"].upper())
      for item in await dos.to_list(length=None):
         myset.add(item["username"].upper())
      for item in await ortu.to_list(length=None):
         myset.add(item["username"].upper())
   else:
      for item in await result.to_list(length=None):
         myset.add(item[field].upper())

   return myset

def simpan_data_mahasiswa(data):
   path = os.path.join(foto_profil_folder, "new_user.jpg")

   try:
      db = client2["face_identification_3"]
      mahasiswa_collection = db["mahasiswa"]
      
      mahasiswa_collection.insert_one({
         "nim": str(data["nim"]).upper(),
         "orang_tua_id": None,
         "requested_orang_tua_id": [],
         "foto_wajah_path": [],
         "encode_foto_wajah": [],
         "nama": str(data["nama"]).title(),
         "email": data["email"],
         "username": data["username"],
         "password": generate_password_hash(data["password"]),
         "foto_profil_path": path
      })

   except Exception:
      flash(f"Akun gagal dibuat. Kesalahan dalam basis data.", "danger")
      return False

   return True

def simpan_data_dosen(data):
   path = os.path.join(foto_profil_folder, "new_user.jpg")

   try:
      db = client2["face_identification_3"]
      dosen_collection = db["dosen"]
      
      dosen_collection.insert_one({
         "nip": data["nip"],
         "nama": str(data["nama"]).title(),
         "username": data["username"],
         "email": data["email"],
         "password": generate_password_hash(data["password"]),
         "foto_profil_path": path
      })

   except Exception:
      flash(f"Akun gagal dibuat. Kesalahan dalam basis data.", "danger")
      return False

   return True

def simpan_data_orang_tua(data):
   
   path = os.path.join(foto_profil_folder, "new_user.jpg")
   
   try:
      db = client2["face_identification_3"]
      mahasiswa_collection = db["mahasiswa"]
      orang_tua_collection = db["orang_tua"]

      orang_tua = orang_tua_collection.insert_one({
         "anak_id": None,
         "requested_anak_id": ObjectId(data["akun_anak"]),
         "nama": str(data["nama"]).title(),
         "email": data["email"],
         "username": data["username"],
         "password": generate_password_hash(data["password"]),
         "foto_profil_path": path
      })

      mahasiswa_collection.update_one({"_id": ObjectId(data["akun_anak"])}, {"$push": {"requested_orang_tua_id": orang_tua.inserted_id}})


   except Exception:
      flash(f"Akun gagal dibuat. Kesalahan dalam basis data.", "danger")
      return False

   return True

def ambil_ruangan():
   try:
      db = client2["face_identification_3"]
      collection_ruangan = db["ruangan"]
      ruang = collection_ruangan.find({})
      list_ruang = []
      for el in ruang:
         list_ruang.append(el)
      
      new_list = sorted(list_ruang, key=itemgetter("kode_ruangan"))
      # print("ruangan: ", new_list)
      return new_list
   
   except Exception:
      print("MongoDB: Gagal ambil data!")
      return False

def allowed_file(filename):
   return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}
   
def contains(mylist, filter):
   for x in mylist:
      if filter(x):
         print(x)
      else:
         print("not found")

def get_part_of_day(h):
   return("pagi" if 5 <= h <= 11 else "siang" if 12 <= h <= 14 else "sore" if 15 <= h <= 18 else "malam")

async def ambil_choices_akun_mhs():
   db = client["face_identification_3"]
   collection_mahasiswa = db["mahasiswa"]
   mhs = collection_mahasiswa.find({"orang_tua_id": None})
   
   e = []

   for a in await mhs.to_list(length=1000):
      id = a["_id"]
      nama = a['nama']
      nim = a['nim']
      e.append(tuple([str(id), f"{nama.title()} ({nim})"]))

   return e

async def ambil_choices_akun_mhs_2(id):
   db = client["face_identification_3"]
   collection_mahasiswa = db["mahasiswa"]
   mhs = collection_mahasiswa.find({"orang_tua_id": None})
   mhs_own = await collection_mahasiswa.find_one({"orang_tua_id": ObjectId(id)})
   
   e = []

   if mhs_own:
      id = mhs_own["_id"]
      nama = mhs_own['nama']
      nim = mhs_own['nim']
      e.append([str(id), f"{nama.title()} ({nim})"])

   for a in await mhs.to_list(length=1000):
      id = a["_id"]
      nama = a['nama']
      nim = a['nim']
      e.append([str(id), f"{nama.title()} ({nim})"])

   return e

async def dosen_cari_aktivitas_user(id, pengguna):
   db = client["face_identification_3"]
   collection_aktivitas = db["aktivitas"]
   collection_mahasiswa = db["mahasiswa"]

   events = []
   my_aktivitas = []

   try:
      id = ObjectId(id)
   except:
      return False, "", "", "", ""

   aktivitas = collection_aktivitas.find({"mahasiswa_id": ObjectId(id)})
   aktivitas_terakhir_found = await collection_aktivitas.find_one({"mahasiswa_id": ObjectId(id)}, sort=[("updateAt", DESCENDING)])

   if not aktivitas:
      return False, "", "", "", ""
   
   mahasiswa = await collection_mahasiswa.find_one({"_id": ObjectId(id)}, {"encode_foto_wajah": 0, "email": 0, "password": 0, "username": 0})

   if not mahasiswa:
      return False, "", "", "", ""

   ruangan = await db["ruangan"].find().to_list(None)

   if mahasiswa["orang_tua_id"]:
      orang_tua = await db["orang_tua"].find_one({"_id": ObjectId(mahasiswa["orang_tua_id"])})
      mahasiswa["nama_orang_tua"] = orang_tua["nama"]

   if not mahasiswa:
      return False, "", "", "", ""

   for a in await aktivitas.to_list(length=None):
      tanggal = datetime.strptime(a["tanggal"], "%Y-%m-%d")
      tanggal_baru = format_tanggal(a["tanggal"])

      nama_ruangan = ""

      for ruang in ruangan:
         if str(a["ruangan_id"]) == str(ruang["_id"]):
            nama_ruangan = ruang["nama_ruangan"]
            break

      if not a["jadwal_id"]:
         my_aktivitas.append({
            "nama": "Berada di Kampus",
            "ruangan": nama_ruangan,
            "tanggal": tanggal_baru, 
            "waktu_int": tanggal.day * 24 + tanggal.month * 720 + tanggal.year * 8640,
            "url": f"/dosen/mahasiswa/aktivitas/{a['_id']}"   
         })
         events.append({
            "className": "event-yellow",
            "start": tanggal.strftime("%Y-%m-%dT00:00:00"),
            "description": f'Berada di Kampus',
            "url": f'{id}/berada_di_kampus/{a["tanggal"]}'
         })

      else:
         jadwal = await db["jadwal"].find_one({"_id": ObjectId(a["jadwal_id"])})
         my_aktivitas.append({
            "nama": f'Menghadiri {jadwal["nama_kegiatan"]}',
            "ruangan": nama_ruangan,
            "tanggal": tanggal_baru, 
            "waktu_int": tanggal.day * 24 + tanggal.month * 720 + tanggal.year * 8640,
            "url": f'/dosen/mahasiswa/aktivitas/{a["_id"]}'
         })
         events.append({
            "className": "event-purple",
            "start": tanggal.strftime("%Y-%m-%dT00:00:00"),
            "description": "Menghadiri Kegiatan",
            "url": f'{id}/menghadiri_kegiatan/{a["tanggal"]}'
         })
   
   my_aktivitas = sorted(my_aktivitas, key=lambda d: d["waktu_int"], reverse=True)

   seen = []
   unique_list = []
   for item in my_aktivitas:
      if item not in seen:
         unique_list.append(item)
      seen.append(item)

   my_aktivitas = unique_list

   events = list({item["url"]: item for item in events}.values())

   aktivitas_terakhir = ""
   waktu_sekarang = datetime.now()

   mahasiswa["aktivitas_terakhir_ruangan"] = ""
   
   if aktivitas_terakhir_found:
      ruangan = await db["ruangan"].find_one({"_id": aktivitas_terakhir_found["ruangan_id"]})
      time_gap = str(waktu_sekarang - aktivitas_terakhir_found["updateAt"]).split(" ")
      mahasiswa["aktivitas_terakhir_ruangan"] = ruangan["nama_ruangan"]
      if aktivitas_terakhir_found["jadwal_id"]:
         jadwal =  await db["jadwal"].find_one({"_id": ObjectId(aktivitas_terakhir_found["jadwal_id"])})
         mahasiswa["aktivitas_terakhir_nama_kegiatan"] = f'Menghadiri {jadwal["nama_kegiatan"]}'
      else:
         mahasiswa["aktivitas_terakhir_nama_kegiatan"] = "Berada di Kampus"


      # print(f"time gap: {time_gap}")

      selisih = ""

      if len(time_gap) > 1:
         selisih = f"{time_gap[0]} hari yang lalu"
      else:
         waktu = time_gap[0].split(".")[0]
         jam = waktu.split(":")[0]
         menit = waktu.split(":")[1]
         detik = waktu.split(":")[2]

         # print(jam, menit, detik)

         if jam != "0":
            selisih = f"{int(jam)} jam yang lalu"
         elif menit != "00":
            selisih = f"{int(menit)} menit yang lalu"
         elif detik != "00":
            selisih = f"{int(detik)} detik yang lalu"
      
      aktivitas_terakhir = selisih

   return True, events, aktivitas_terakhir, mahasiswa, my_aktivitas

def format_tanggal(string):
   tgl = str(string).split("-")
   return f"{tgl[2]}/{tgl[1]}/{tgl[0]}"

async def cari_aktivitas_user(id, pengguna):
   db = client["face_identification_3"]
   collection_aktivitas = db["aktivitas"]
   collection_jadwal = db["jadwal"]

   events = []
   my_aktivitas = []

   aktivitas = collection_aktivitas.find({"mahasiswa_id": ObjectId(id)})
   aktivitas_terakhir_found = await collection_aktivitas.find_one({"mahasiswa_id": ObjectId(id)}, sort=[("updateAt", DESCENDING)])

   ruangan = await db["ruangan"].find().to_list(None)

   for a in await aktivitas.to_list(length=None):
      nama_ruangan = ""
      nama_ruangan2 = ""
      for ruang in ruangan:
         if str(a["ruangan_id"]) == str(ruang["_id"]):
            nama_ruangan = f"{ruang['nama_ruangan']}"
            nama_ruangan2 = ruang["nama_ruangan"]
            break

      
      tanggal = datetime.strptime(a["tanggal"], "%Y-%m-%d")
      tanggal_baru = format_tanggal(a["tanggal"])

      if not a["jadwal_id"]:
         my_aktivitas.append({
            "nama": "Berada di Kampus",
            "ruangan": nama_ruangan,
            "tanggal": tanggal_baru, 
            "waktu_int": tanggal.day * 24 + tanggal.month * 720 + tanggal.year * 8640,
            "url": f'{pengguna}/aktivitas/{a["_id"]}'
         })
         events.append({
            "className": "event-yellow",
            "start": tanggal.strftime("%Y-%m-%dT00:00:00"),
            "description": f'Berada di Kampus',
            "url": f'{pengguna}/berada_di_kampus/{a["tanggal"]}'
         })

      else:
         jadwal = await collection_jadwal.find_one({"_id": ObjectId(a["jadwal_id"])})
         my_aktivitas.append({
            "nama": f'Menghadiri {jadwal["nama_kegiatan"]}',
            "ruangan": nama_ruangan,
            "tanggal": tanggal_baru, 
            "waktu_int": tanggal.day * 24 + tanggal.month * 720 + tanggal.year * 8640,
            "url": f'{pengguna}/aktivitas/{a["_id"]}'
         })
         events.append({
            "className": "event-purple",
            "start": tanggal.strftime("%Y-%m-%dT00:00:00"),
            "description": "Menghadiri Kegiatan",
            "url": f'{pengguna}/menghadiri_kegiatan/{a["tanggal"]}'
         })

   if my_aktivitas:
      my_aktivitas = sorted(my_aktivitas, key=lambda d: d["waktu_int"], reverse=True)

   seen = []
   unique_list = []
   for item in my_aktivitas:
      if item not in seen:
         unique_list.append(item)
      seen.append(item)

   my_aktivitas = unique_list

   events = list({item["url"]: item for item in events}.values())

   aktivitas_terakhir = [None, None, None]
   waktu_sekarang = datetime.now()
   
   if my_aktivitas:
      time_gap = str(waktu_sekarang - aktivitas_terakhir_found["updateAt"]).split(" ")

      # print(f"time gap: {time_gap}")

      selisih = ""

      if len(time_gap) > 1:
         selisih = f"{time_gap[0]} hari yang lalu"
      else:
         waktu = time_gap[0].split(".")[0]
         jam = waktu.split(":")[0]
         menit = waktu.split(":")[1]
         detik = waktu.split(":")[2]

         # print(jam, menit, detik)

         if jam != "0":
            selisih = f"{int(jam)} jam yang lalu"
         elif menit != "00":
            selisih = f"{int(menit)} menit yang lalu"
         elif detik != "00":
            selisih = f"{int(detik)} detik yang lalu"
      
      aktivitas_terakhir[2] = selisih

      # print(f"Ruangan: {ruangan}")
      if aktivitas_terakhir_found["jadwal_id"]:
         jadwal = await db["jadwal"].find_one({"_id": ObjectId(aktivitas_terakhir_found["jadwal_id"])})
         aktivitas_terakhir[0] = f'Menghadiri {jadwal["nama_kegiatan"]}'
      else:
         aktivitas_terakhir[0] =  "Berada di Kampus"


      aktivitas_terakhir[1] = nama_ruangan2

   if pengguna == "orangtua":
      mahasiswa = await db["mahasiswa"].find_one({"_id": ObjectId(id)}, {"foto_profil_path": 1})
      return events, aktivitas_terakhir, my_aktivitas, mahasiswa["foto_profil_path"]

   return events, aktivitas_terakhir, my_aktivitas
   
async def cari_ruangan_aktif():
   db = client["face_identification_3"]
   ruangan = await db["frame"].find({}).to_list(None)
   return ruangan

async def ambil_ruangan_by_id(id):
   db = client["face_identification_3"]
   ruangan = await db["ruangan"].find_one({"_id": ObjectId(id)})
   return ruangan

async def ambil_aktivitas_by_id(id, user_id, pengguna):
   db = client["face_identification_3"]

   try:
      id = ObjectId(id)
   except:
      return False, False, "", "", "", "", ""

   aktivitas = await db["aktivitas"].find_one({"_id": id})
   mahasiswa = await db["mahasiswa"].find_one({"_id": ObjectId(aktivitas["mahasiswa_id"])})
   ruangan_obj = await db["ruangan"].find_one({"_id": aktivitas["ruangan_id"]})

   if not aktivitas:
      return False, False, "", "", "", "", ""

   if pengguna == "mahasiswa" or pengguna == "orang tua":
      if str(aktivitas["mahasiswa_id"]) != str(user_id):
         return True, False, "Error: Akses tidak diberikan. (401: Unauthorized)", "", "", "", ""
   

   toleransi = timedelta(minutes=15)
   list_waktu = []
   index = 0
   total = timedelta(seconds=aktivitas["expires"][0])

   for el, gam in zip(aktivitas["waktu"], aktivitas["gambar"]):
      list_waktu.append([el.strftime("%H:%M:%S"), gam])
      if index < len(aktivitas["waktu"]) - 1:
         gap = aktivitas["waktu"][index + 1].replace(microsecond=0) - aktivitas["waktu"][index].replace(microsecond=0)
         # print(gap)
         if gap < toleransi:
            total += gap
         else:
            total += timedelta(seconds=aktivitas["expires"][index])
      index += 1

   kegiatan = "-"
   ruangan = f'{ruangan_obj["kode_ruangan"]} - {ruangan_obj["nama_ruangan"]}'
   kode_ruangan = ruangan_obj["kode_ruangan"]
   nama_ruangan = ruangan_obj["nama_ruangan"]
   mulai = "-"
   selesai = "-"
   durasi = "-"
   keterangan = "-"
   id_dosen = "-"
   nama_dosen = "-"
   foto_profil = ""

   if aktivitas["jadwal_id"]:
      
      jadwal = await db["jadwal"].find_one({"_id": ObjectId(aktivitas["jadwal_id"])})
      dosen = await db["dosen"].find_one({"_id": ObjectId(jadwal["dosen_id"])})

      kegiatan = jadwal["nama_kegiatan"]
      mulai = jadwal["waktu_mulai"]
      selesai = jadwal["waktu_selesai"]
      durasi = str(jadwal["waktu_selesai"] - jadwal["waktu_mulai"])
      id_dosen = str(dosen["_id"])
      foto_profil = str(dosen["foto_profil_path"])
      nama_dosen = dosen["nama"]
      keterangan = jadwal["keterangan"]


   keterangan_kegiatan = f'Menghadiri {kegiatan}' if kegiatan != "-" else "Berada di Kampus"
   ket_ruangan = f'di {nama_ruangan}' if kegiatan != "-" else f"{nama_ruangan} ({kode_ruangan})"
   tanggal_baru = datetime.strptime(aktivitas["tanggal"], "%Y-%m-%d")
   hari = get_hari_dan_tanggal(tanggal_baru)

   hours, remainder = divmod(total.seconds, 3600)
   minutes, seconds = divmod(remainder, 60)

   total = f"{hours} jam {minutes} menit {seconds} detik" if hours else f"{minutes} menit {seconds} detik" if minutes else f"{seconds} detik"


   if pengguna == "dosen":
      return True, True, [{"total": total, "waktu": list_waktu}, {"kegiatan": kegiatan, "ruangan": ruangan, "mulai": mulai, "selesai": selesai, "durasi": durasi, "keterangan": keterangan, "id_dosen": id_dosen, "foto_profil": foto_profil, "nama_dosen": nama_dosen, "id_mhs": str(mahasiswa["_id"]), "nama_mhs": mahasiswa["nama"], "ruangan": ruangan}], [f'{keterangan_kegiatan}, {ket_ruangan}', hari], mahasiswa["nama"], mahasiswa["nim"], mahasiswa["foto_profil_path"]
   elif pengguna == "orang tua":
      return True, True, [
         {"total": total, "waktu": list_waktu}, 
         {"kegiatan": kegiatan, "ruangan": ruangan, "mulai": mulai, "selesai": selesai, "durasi": durasi, "keterangan": keterangan, "id_dosen": id_dosen, "foto_profil": foto_profil, "nama_dosen": nama_dosen, "id_mhs": str(mahasiswa["_id"]), "nama_mhs": mahasiswa["nama"], "ruangan": ruangan}
      ], [f'{keterangan_kegiatan}, {ket_ruangan}', hari], mahasiswa["nim"], mahasiswa["foto_profil_path"]
   
   return True, True, [
      {"total": total, "waktu": list_waktu}, 
      {"kegiatan": kegiatan, "ruangan": ruangan, "mulai": mulai, "selesai": selesai, "durasi": durasi, "keterangan": keterangan, "id_dosen": id_dosen, "foto_profil": foto_profil, "nama_dosen": nama_dosen, "id_mhs": str(mahasiswa["_id"]), "nama_mhs": mahasiswa["nama"], "ruangan": ruangan}
   ], [f'{keterangan_kegiatan}, {ket_ruangan}', hari]

def hms_to_seconds(hms):
   h, m ,s = hms.split(':')
   # trick 33
   # h, m, s = map(int, input_hour.split(':'))
   # use it only if you understand what map does.
   totalSeconds = int(h) * 3600 + int(m) * 60 + int(s)
   return totalSeconds

async def cari_foto_wajah(user_id):
   db = client["face_identification_3"]
   collection_mahasiswa = db["mahasiswa"]

   mahasiswa = await collection_mahasiswa.find_one({"_id": ObjectId(user_id)}, {"foto_wajah_path": 1, "requested_orang_tua_id": 1, "_id": 0})
   
   
   return mahasiswa["foto_wajah_path"], mahasiswa["requested_orang_tua_id"]

async def ubah_data_akun(id, data, files, pengguna):
   print("data: ", data)

   db = client["face_identification_3"]
   collection = db[pengguna]
   is_pp_changed = False
   is_name_chaged = False

   # return True, is_pp_changed, is_name_chaged

   if pengguna == "mahasiswa":
      mahasiswa = await collection.find_one({"_id":  ObjectId(id)})

      setter = {"nama": data["nama"], "email": data["email"], "nim": data["nim"]}

      if str(data["nama"]).upper() != str(mahasiswa["nama"]).upper():
         list_nama = await find_list("mahasiswa", "nama")
         if str(data["nama"]).upper() in list_nama:
            flash("Maaf, nama yang anda masukan sudah terdaftar.", "danger")
         else:
            setter["nama"] = str(data["nama"]).title()
            is_name_chaged = str(data["nama"]).title()

      if "akunortu" in data:
         list_id_req_ortu = [str(x) for x in mahasiswa["requested_orang_tua_id"]]
         print(mahasiswa["requested_orang_tua_id"])
         print(data["akunortu"].split(" ")[0])
         list_id_req_ortu.remove(data["akunortu"].split(" ")[0])
         for el in list_id_req_ortu:
            db["orang_tua"].update_one({"_id":  ObjectId(el)}, {"$set": {"anak_id": None, "requested_anak_id": None}})

         db["orang_tua"].update_one({"_id":  ObjectId(data["akunortu"].split(" ")[0])}, {"$set": {"anak_id": ObjectId(id), "requested_anak_id": None}})
         setter["orang_tua_id"] = ObjectId(data["akunortu"].split(" ")[0])
         setter["requested_orang_tua_id"] = []

      if files:
         if files["foto_profil"].filename != "":
            path = os.path.join(foto_profil_folder, f"{mahasiswa['username']}.jpg")
            folder = os.path.abspath(path)
            files["foto_profil"].save(folder)

            size = os.stat(folder).st_size

            if size > 5048576:
               os.remove(folder)
               flash("Ukuran file foto profil terlalu besar! (Max. 5MB)!", "danger")
            else:
               setter["foto_profil_path"] = path
               is_pp_changed = setter["foto_profil_path"]

            # foto_profil_path = path

         existing_foto_wajah = list(mahasiswa["foto_wajah_path"])
         existing_encode_foto_wajah = list(mahasiswa["encode_foto_wajah"])
         print("len files -1 : ", len(files) -1)
         print("len existing_encode_foto_wajah: ", len(existing_encode_foto_wajah))
         for i in range(len(files) - 1 ):
            try:
               filename = files[f'file_{i}'].filename
               if files[f"file_{i}"].filename != "" and allowed_file(files[f"file_{i}"].filename):
                  file_id = str(uuid.uuid4())
                  path = os.path.join(foto_wajah_folder, f"{mahasiswa['username']}-{file_id}.jpg")
                  # print(f"MENAMBAHKAN: {path}")
                  folder = os.path.abspath(path)

                  files[f"file_{i}"].save(folder)
                  # VERIFIKASI JUMLAH WAJAH > 1 ATAU < 1
                  res_hitung_wajah = hitung_wajah(os.path.abspath(path))
                  # print(f"Res hitung wajah: {res_hitung_wajah[1]}")
                  if res_hitung_wajah[0]:
                     res_hitung_wajah[1].save(folder)
                  else:
                     os.remove(path)
                     flash(f"Vefikasi foto wajah gagal: Pada '{filename}' {res_hitung_wajah[1]}!", "danger")
                     continue
                  
                  # VERIFIKASI KESAMAAN WAJAH DENGAN YANG SUDAH TERSIMPAN
                  encode = face_encodings(res_hitung_wajah[2], res_hitung_wajah[3])[0]
                  if existing_encode_foto_wajah:
                     if not(len(existing_encode_foto_wajah) == 1 and len(files) - 1 == 1):
                        if not compare_faces_3(existing_encode_foto_wajah, encode):
                           os.remove(path)
                           flash(f"Vefikasi foto wajah gagal: Pada '{filename}' terdeteksi wajah yang berbeda!", "danger")
                           continue

                  try:
                     os.remove(existing_foto_wajah[i])
                     existing_foto_wajah[i] = path
                     existing_encode_foto_wajah[i] = encode.tolist()
                  except:
                     existing_foto_wajah.append(path)
                     existing_encode_foto_wajah.append(encode.tolist())
            except:
               break

         existing_foto_wajah = [i for i in existing_foto_wajah if i != None]
            
         # print(f"EXISTING AFTER: {existing_foto_wajah}")

         setter["foto_wajah_path"] = existing_foto_wajah
         setter["encode_foto_wajah"] = existing_encode_foto_wajah
      
      await collection.update_one({"_id": ObjectId(id)}, {"$set": setter})

   elif pengguna == "orang_tua":
      orang_tua = await collection.find_one({"_id": ObjectId(id)})

      setter = {}

      if str(data["nama"]).upper() != str(orang_tua["nama"]).upper():
         list_nama = await find_list("orang_tua", "nama")
         if str(data["nama"]).upper() in list_nama:
            flash("Maaf, nama yang anda masukan sudah terdaftar.", "danger")
         else:
            is_name_chaged = str(data["nama"]).title()
            setter["nama"] = str(data["nama"]).title()

      if data["akun_anak"]:
         db["mahasiswa"].update_one({"_id": ObjectId(data["akun_anak"].split(" ")[0])}, {"$push": {"requested_orang_tua_id": ObjectId(id)}})
         setter["requested_anak_id"] = ObjectId(data["akun_anak"].split(" ")[0])


      # if mahasiswa_target["orang_tua_id"]:
      #    if mahasiswa_target["orang_tua_id"] != orang_tua["_id"]:
      #       flash(f"Akun gagal dibuat. Akun anak yang dipilih sudah terhubung ke Akun Orang Tua lain.", "danger")
      #    else:
      #       setter = {"nama": str(data["nama"]).title(), "email": data["email"]}

      setter["email"] = data["email"]
         
      foto_profil_path = orang_tua["foto_profil_path"]
      if files["foto_profil"].filename != "":
         path = os.path.join(foto_profil_folder, f"{orang_tua['username']}.jpg")
         folder = os.path.abspath(path)
         files["foto_profil"].save(folder)

         size = os.stat(folder).st_size

         if size > 5048576:
            os.remove(folder)
            flash("Ukuran file foto profil terlalu besar! (Max. 5MB)!", "danger")
         else:
            foto_profil_path = path
            is_pp_changed = foto_profil_path

            setter["foto_profil_path"] = foto_profil_path
   
      # if str(data["akun_anak"]) != str(orang_tua["anak_id"]):
      #    db["mahasiswa"].update_one({"_id": ObjectId(orang_tua["anak_id"])}, {"$set": {"orang_tua_id": None}})
      #    db["mahasiswa"].update_one({"_id": ObjectId(data["akun_anak"])}, {"$set": {"orang_tua_id": orang_tua["_id"]}})

      #    setter["anak_id"] = ObjectId(data["akun_anak"])

      await collection.update_one({"_id": ObjectId(id)}, {"$set": setter})


   elif pengguna == "dosen":
      dosen = await collection.find_one({"_id": ObjectId(id)})

      if str(data["nama"]).upper() != str(dosen["nama"]).upper():
         list_nama = await find_list("dosen", "nama")
         if str(data["nama"]).upper() in list_nama:
            flash("Maaf, nama yang anda masukan sudah terdaftar.", "danger")
         else:
            is_name_chaged = str(data["nama"]).title()
      
      foto_profil_path = dosen["foto_profil_path"]
      if files["foto_profil"].filename != "":
         path = os.path.join(foto_profil_folder, f"{dosen['username']}.jpg")
         folder = os.path.abspath(path)
         files["foto_profil"].save(folder)

         size = os.stat(folder).st_size

         if size > 5048576:
            os.remove(folder)
            flash("Ukuran file foto profil terlalu besar! (Max. 5MB)!", "danger")
         else:
            foto_profil_path = path
            is_pp_changed = foto_profil_path
            
      await collection.update_one({"_id": ObjectId(id)}, {"$set": {"nama": str(data["nama"]).title(), "nip": data["nip"], "email": data["email"], "foto_profil_path": foto_profil_path}})
        
   return True, is_pp_changed, is_name_chaged

async def hapus_foto_wajah_mhs(id_akun, file_path, index):
   db = client["face_identification_3"]
   collection_mahasiswa = db["mahasiswa"]

   mhs = await collection_mahasiswa.find_one_and_update({"_id": ObjectId(id_akun)}, {"$pull": {"foto_wajah_path": file_path}})
   os.remove(file_path)

   list_encodes = list(mhs["encode_foto_wajah"])

   list_encodes.pop(int(index))

   collection_mahasiswa.update_one({"_id": ObjectId(id_akun)}, {"$set": {"encode_foto_wajah": list_encodes}})

async def cari_semua_mahasiswa():
   db = client["face_identification_3"]

   mhs = db["mahasiswa"].find({}, {'encode_foto_wajah': 0, 'foto_wajah_path': 0, 'orang_tua': 0, 'username': 0, 'password': 0, 'email': 0})

   ruangan_all = await db["ruangan"].find({}).to_list(None)

   mhs_list = []
   mhs_list_null = []

   for item in await mhs.to_list(length=None):
      # print(item)
      obj = {}
      
      obj["nama"] = item["nama"]
      obj["id"] = str(item["_id"])
      obj["id_mhs"] = str(item["_id"])
      obj["nim"] = item["nim"]
      obj["foto_profil"] = item["foto_profil_path"]

      aktivitas_terakhir = await db["aktivitas"].find_one({"mahasiswa_id": ObjectId(item["_id"])}, sort=[("updateAt", DESCENDING)])

      if not aktivitas_terakhir:
         obj["aktivitas"] = "-"
         obj["tempat"] = "-"
         obj["ts"] = ""
      else:
         for ruangan_obj in ruangan_all:
            nama_ruangan = ""
            if str(aktivitas_terakhir["ruangan_id"]) == str(ruangan_obj["_id"]):
               nama_ruangan = f'{ruangan_obj["kode_ruangan"]} - {ruangan_obj["nama_ruangan"]}'
               break
         # print("aktivitas terakhir: ", aktivitas_terakhir["updateAt"])
         obj["tempat"] = nama_ruangan
         obj["ts"] = aktivitas_terakhir["updateAt"]
         if aktivitas_terakhir["jadwal_id"]:
            jadwal = await db["jadwal"].find_one({"_id": ObjectId(aktivitas_terakhir["jadwal_id"])})
            obj["aktivitas"] = jadwal["nama_kegiatan"]
         else:
            obj["aktivitas"] = "Berada di Kampus"

      if obj["ts"]:
         obj["waktu"] = obj["ts"].strftime("%H:%M:%S")
         obj["tanggal"] = obj["ts"].strftime("%d/%m/%Y")
      else:
         obj["waktu"] = "-"
         obj["tanggal"] = "-"

      if obj["aktivitas"] != "-":
         mhs_list.append(obj)
      else:
         mhs_list_null.append(obj)

   mhs_list.sort(key=lambda d: d["ts"], reverse=True)
   mhs_list = mhs_list + mhs_list_null

   # print(len(mhs_list))

   return mhs_list

async def cari_id_anak(id_akun_orgtua):
   db = client["face_identification_3"]

   collection_mahasiswa = db["mahasiswa"]

   mahasiswa = await collection_mahasiswa.find_one({"orang_tua_id": ObjectId(id_akun_orgtua)})

   if not mahasiswa:
      return False, False

   return mahasiswa["_id"], mahasiswa["nama"]

async def cari_req_id_anak(id_akun_orgtua):
   db = client["face_identification_3"]

   collection_mahasiswa = db["mahasiswa"]

   mahasiswa = await collection_mahasiswa.find_one({"requested_orang_tua_id": ObjectId(id_akun_orgtua)})

   if not mahasiswa:
      return False, False

   return mahasiswa["_id"], mahasiswa["nama"]

def hhmmss_to_seconds(hhmmss):
    h, m, s = map(int, hhmmss.split(':'))
    return h * 3600 + m * 60 + s

async def ambil_berada_di_kampus(id, tanggal, my_bool):
   db = client["face_identification_3"]
   collection_aktivitas = db["aktivitas"]

   # print("id: ", id)

   try:
      id = ObjectId(id)
   except:
      if my_bool:
         return False, "", "", ""
      else:
         return False, "", ""

   aktivitas = await collection_aktivitas.find({"tanggal": tanggal, "mahasiswa_id": ObjectId(id), "jadwal_id": None}, sort=[("updateAt", DESCENDING)]).to_list(None)

   mahasiswa = await db["mahasiswa"].find_one({"_id": ObjectId(id)})

   ruangan = await db["ruangan"].find().to_list(None)

   print("len aktivitas: ", len(aktivitas))
   print("aktivitas: ", aktivitas)

   if my_bool:
      if not aktivitas:
         return False, "", "", ""
      
      toleransi = timedelta(minutes=15)
      berada_di_kampus = []

      
      for a in aktivitas:
         for ruang in ruangan:
            if str(a["ruangan_id"]) == str(ruang["_id"]):
               nama_ruangan = f"{ruang['nama_ruangan']}"
               break
         obj = {"_id": a["_id"], "ruangan": nama_ruangan, "waktu": a["waktu"], "expires": a["expires"], "waktu_terakhir": a["updateAt"].strftime("%H:%M:%S"), "updateAt": a["updateAt"]}

         berada_di_kampus.append(obj)
      # new
      # print("Obj: ", obj, "\n")
      
      # print("BDK : ", len(berada_di_kampus))

      for bdk in berada_di_kampus:
         total = timedelta(seconds=bdk['expires'][0])
         # print("len = ", len(bdk["waktu"]))
         # if len(bdk["waktu"]) == 1:
         #    total = timedelta()
         # print("inisiasi total = ", total)
         for i, waktu in enumerate(bdk["waktu"]):
            if i < len(bdk["waktu"]) - 1:
               gap = bdk["waktu"][i + 1].replace(microsecond=0) - bdk["waktu"][i].replace(microsecond=0)
               # print("Gap : ", gap)
               if gap < toleransi:
                  # print(f"A {total} + {gap} = {total + gap}")
                  total = total + gap
               else:
                  # print(f"B {total} + {bdk['filler'][i+1]} = {total + bdk['filler'][i+1]}")
                  total = total + timedelta(seconds=bdk['expires'][i+1])
            bdk["durasi"] = total
         # print("\n")

      berada_di_kampus = sorted(berada_di_kampus, key=lambda d: d["updateAt"], reverse=True)

      tanggal_baru = datetime.strptime(tanggal, "%Y-%m-%d")
      hari = get_hari_dan_tanggal(tanggal_baru)

      keterangan = hari

      # print(berada_di_kampus)

      return True, mahasiswa["nama"], berada_di_kampus, keterangan
   else:
      if not aktivitas:
         return False, "", ""
      toleransi = timedelta(minutes=15)
      berada_di_kampus = []

      for a in aktivitas:
         for ruang in ruangan:
            if str(a["ruangan_id"]) == str(ruang["_id"]):
               nama_ruangan = f"{ruang['nama_ruangan']}"
               break
         obj = {"_id": a["_id"], "ruangan": nama_ruangan, "waktu": a["waktu"], "expires": a["expires"], "waktu_terakhir": a["updateAt"].strftime("%H:%M:%S"), "updateAt": a["updateAt"]}

         berada_di_kampus.append(obj)
         # print("Obj: ", obj, "\n")
      
      # print("BDK : ", len(berada_di_kampus))

         for bdk in berada_di_kampus:
            total = timedelta(seconds=bdk['expires'][0])
            # print("len = ", len(bdk["waktu"]))
            # if len(bdk["waktu"]) == 1:
            #    total = timedelta()
            # print("inisiasi total = ", total)
            for i, waktu in enumerate(bdk["waktu"]):
               if i < len(bdk["waktu"]) - 1:
                  gap = bdk["waktu"][i + 1].replace(microsecond=0) - bdk["waktu"][i].replace(microsecond=0)
                  # print("Gap : ", gap)
                  if gap < toleransi:
                     # print(f"A {total} + {gap} = {total + gap}")
                     total = total + gap
                  else:
                     # print(f"B {total} + {bdk['filler'][i+1]} = {total + bdk['filler'][i+1]}")
                     total = total + timedelta(seconds=bdk['expires'][i+1])
               bdk["durasi"] = total
            # print("\n")

      berada_di_kampus = sorted(berada_di_kampus, key=lambda d: d["updateAt"], reverse=True)

      tanggal_baru = datetime.strptime(tanggal, "%Y-%m-%d")
      hari = get_hari_dan_tanggal(tanggal_baru)

      keterangan = hari

      # print(berada_di_kampus)

      return True, berada_di_kampus, keterangan

async def ambil_menghadiri_kegiatan(id, tanggal, my_bool):
   db = client["face_identification_3"]

   try:
      id = ObjectId(id)
   except:
      if my_bool:
         return False, "", "", ""
      else:
         return False, "", ""

   mahasiswa = await db["mahasiswa"].find_one({"_id": id})
   aktivitas_list = await db["aktivitas"].find({"tanggal": tanggal, "mahasiswa_id": id, "jadwal_id": { "$ne": None } }).to_list(None)
   ruangan = await db["ruangan"].find().to_list(None)

   if my_bool:
      if not aktivitas_list:
         return False, "", "", ""
         
      toleransi = timedelta(minutes=15)

      for el in aktivitas_list:
         nama_ruangan = ""
         for ruang in ruangan:
            if str(el["ruangan_id"]) == str(ruang["_id"]):
               nama_ruangan = f"{ruang['nama_ruangan']}"
               break
         el["ruangan"] = nama_ruangan
         jadwal = await db["jadwal"].find_one({"_id": el["jadwal_id"]})
         el["nama_kegiatan"] = jadwal["nama_kegiatan"]
         total = timedelta(seconds=el["expires"][0])
         for index, b in enumerate(el["waktu"]):
            if index < len(el["waktu"]) - 1:
               gap = el["waktu"][index + 1].replace(microsecond=0) - b.replace(microsecond=0)
               if gap < toleransi:
                  total = total + gap
               else:
                  total = total + timedelta(seconds=el["expires"][index])

         el["waktu_terakhir"] = el["updateAt"].strftime("%H:%M:%S")
         el["durasi"] = total

      aktivitas_list = sorted(aktivitas_list, key=lambda d: d["updateAt"], reverse=True)

      # print("Aktivitas LIST: ", aktivitas_list)

      tanggal_baru = datetime.strptime(tanggal, "%Y-%m-%d")
      hari = get_hari_dan_tanggal(tanggal_baru)

      keterangan = hari

      return True, mahasiswa["nama"], aktivitas_list, keterangan
   else:
      if not aktivitas_list:
         return False, "", "", ""
      
      toleransi = timedelta(minutes=15)

      for el in aktivitas_list:
         nama_ruangan = ""
         for ruang in ruangan:
            if str(el["ruangan_id"]) == str(ruang["_id"]):
               nama_ruangan = f"{ruang['nama_ruangan']}"
               break
         el["ruangan"] = nama_ruangan
         jadwal = await db["jadwal"].find_one({"_id": ObjectId(el["jadwal_id"])})
         el["nama_kegiatan"] = jadwal["nama_kegiatan"]
         total = timedelta(seconds=el["expires"][0])
         for index, b in enumerate(el["waktu"]):
            if index < len(el["waktu"]) - 1:
               gap = el["waktu"][index + 1].replace(microsecond=0) - b.replace(microsecond=0)
               if gap < toleransi:
                  total = total + gap
               else:
                  total = total + timedelta(seconds=el["expires"][index])

         el["waktu_terakhir"] = el["updateAt"].strftime("%H:%M:%S")
         el["durasi"] = total

      aktivitas_list = sorted(aktivitas_list, key=lambda d: d["updateAt"], reverse=True)
      for el in aktivitas_list:
         print(el["waktu_terakhir"])

      # print("Aktivitas LIST: ", aktivitas_list)

      tanggal_baru = datetime.strptime(tanggal, "%Y-%m-%d")
      hari = get_hari_dan_tanggal(tanggal_baru)

      keterangan = hari

      return True, aktivitas_list, keterangan

async def ambil_berada_di_kampus_by_id(id):
   db = client["face_identification_3"]
   collection_aktivitas = db["aktivitas"]
   collection_mahasiswa = db["mahasiswa"]
   collection_akun = db["akun"]

   aktivitas = await collection_aktivitas.find_one({"_id": ObjectId(id)})
   # print(aktivitas)

   mahasiswa = await collection_mahasiswa.find_one({"_id": ObjectId(aktivitas["id_mhs"])})
   
   akun = await collection_akun.find_one({"_id": ObjectId(mahasiswa["id_akun"])})

   e = []
   total = timedelta(seconds=0)
   filler = timedelta(minutes=2)
   toleransi = timedelta(minutes=15)
   
   index = 0
   for b in aktivitas["waktu"]:
      e.append({
         "waktu": b.strftime("%H:%M:%S")
      })
      if index < len(aktivitas["waktu"]) - 1:
         gap = aktivitas["waktu"][index + 1].replace(microsecond=0) - b.replace(microsecond=0)
         if gap < toleransi:
            total += gap
         else:
            total += filler
      index += 1

   e = sorted(e, key=lambda d: d["waktu"])

   tanggal_baru = datetime.strptime(aktivitas["tanggal"], "%Y-%m-%d")
   hari = get_hari_dan_tanggal(tanggal_baru)

   keterangan = f"Berada di Kampus - {hari} ({aktivitas['ruangan']})"

   nama = [akun["nama"], str(akun["_id"]), akun["foto_profil"]]

   # print(nama)

   return e, keterangan, total, nama

async def ambil_jadwal_dan_hasil(id_jadwal):
   db = client["face_identification_3"]
   collection_aktivitas = db["aktivitas"]
   collection_mahasiswa = db["mahasiswa"]

   try:
      id_jadwal = ObjectId(id_jadwal)
   except:
      return False, "", ""


   jadwal = await db["jadwal"].find_one({"_id": id_jadwal})
   dosen = await db["dosen"].find_one({"_id": jadwal["dosen_id"]})
   ruangan = await db["ruangan"].find_one({"_id": jadwal["ruangan_id"]})


   if not jadwal:
      return False, "", ""
   
   jadwal["nama_dosen"] = dosen["nama"]
   jadwal["foto_profil_path"] = dosen["foto_profil_path"]

   jadwal["ruangan"] = f"{ruangan['kode_ruangan']} - {ruangan['nama_ruangan']}"

   jadwal["tanggal"] = get_tanggal(jadwal["waktu_mulai"])
   jadwal["durasi"] = str(jadwal["waktu_selesai"] - jadwal["waktu_mulai"])
   jadwal["mulai_dt"] = jadwal["waktu_mulai"]
   jadwal["selesai_dt"] = jadwal["waktu_selesai"]
   jadwal["mulai"] = jadwal["waktu_mulai"].strftime("%H:%M")
   jadwal["selesai"] = jadwal["waktu_selesai"].strftime("%H:%M")

   aktivitas = collection_aktivitas.find({"jadwal_id": ObjectId(id_jadwal)})

   hasil = []
   ids = []
   id_aktv = []

   for a in await aktivitas.to_list(length=None):
      this_id = str(a["mahasiswa_id"])
      ids.append(this_id)
      id_aktv.append(str(a["_id"]))
      for b, c in zip(a["waktu"], a["expires"]):
         hasil.append({
            "id_mhs": this_id,
            "ts": b,
            "exp": c
         })

   result = {}

   for id in ids:
      # print("ID: ", id)
      result[id] = []

   hasil.sort(key=lambda d: d["ts"])

   for id in ids:
      for el in hasil:
         if id == el["id_mhs"]:
            result[id].append([el["ts"], el["exp"]])

   final_result = []

   for i, el in enumerate(result):
      toleransi = timedelta(minutes=15)

      mahasiswa = await collection_mahasiswa.find_one({"_id": ObjectId(el)})
      
      # index = 0
      total = timedelta(seconds=result[el][0][1])
      for index, b in enumerate(result[el]):
         if index < len(result[el]) - 1:
            gap = result[el][index + 1][0].replace(microsecond=0) - b[0].replace(microsecond=0)
            if gap < toleransi:
               total += gap
            else:
               total += timedelta(seconds=b[1])
      
      final_result.append({
         "nama": mahasiswa["nama"],
         "id_mhs": mahasiswa["_id"],
         "durasi": total,
         "nim": mahasiswa["nim"],
         "foto_profil": mahasiswa["foto_profil_path"],
         "href": f"/dosen/mahasiswa/aktivitas/{id_aktv[i]}"
      })

   final_result.sort(key=lambda d: d["durasi"], reverse=True)
   return True, jadwal, final_result

async def ambil_jadwal_dan_hasil_mhs(id_jadwal, id_mhs):
   db = client["face_identification_3"]
   collection_aktivitas = db["aktivitas"]
   collection_mahasiswa = db["mahasiswa"]
   collection_jadwal = db["jadwal"]
   collection_akun = db["akun"]

   jadwal = await collection_jadwal.find_one({"_id": ObjectId(id_jadwal)})

   aktivitas = await collection_aktivitas.find_one({"id_jadwal": ObjectId(id_jadwal), "id_mhs": ObjectId(id_mhs)})

   mahasiswa = await collection_mahasiswa.find_one({"_id": ObjectId(id_mhs)})
   akun = await collection_akun.find_one({"_id": ObjectId(mahasiswa["id_akun"])})

   keterangan = []
   keterangan.append(str(akun["_id"]))
   keterangan.append(akun["nama"])
   keterangan.append(akun["foto_profil"])

   hasil = []

   total = timedelta(seconds=0)
   filler = timedelta(minutes=2)
   toleransi = timedelta(minutes=15)

   # for a in await aktivitas.to_list(length=1000):
   index = 0
   for b in aktivitas["waktu"]:
      hasil.append({
         "waktu": b.strftime("%H:%M:%S"),
         "ts": b
      })
      
      if len(aktivitas["waktu"]) == 1:
         total = filler
      elif index < len(aktivitas["waktu"]) - 1:
         gap = aktivitas["waktu"][index + 1].replace(microsecond=0) - b.replace(microsecond=0)
         if gap < toleransi:
            total += gap
         else:
            total += filler
      index += 1

   keterangan.append(total)

   tanggal_baru = datetime.strptime(aktivitas['tanggal'], "%Y-%m-%d")
   hari = get_hari_dan_tanggal(tanggal_baru)

   if jadwal["kegiatan"] == "Konsultasi Akademik":
      keterangan.append(f"Melakukan Konsultasi Akademik - {hari} (Ruang Dosen)")
   else:
      keterangan.append(f"Menghadiri {jadwal['kegiatan']} - {hari} ({jadwal['ruangan']})")

   # result = {}

   # for id in ids:
   #    result[id] = []

   # hasil.sort(key=lambda d: d["ts"])

   # for id in ids:
   #    for el in hasil:
   #       if id == el["id_mhs"]:
   #          result[id].append(el["ts"])

   # final_result = []

   # for el in result:
   #    total = timedelta(seconds=0)
   #    filler = timedelta(minutes=2)
   #    toleransi = timedelta(minutes=15)

   #    akun = await collection_akun.find_one({"_id": ObjectId(el)})
   #    mahasiswa = await collection_mahasiswa.find_one({"id_akun": ObjectId(el)})
      
   #    index = 0
   #    for b in result[el]:
   #       if len(result[el]) == 1:
   #          total = filler
   #       elif index < len(result[el]) - 1:
   #          gap = result[el][index + 1].replace(microsecond=0) - b.replace(microsecond=0)
   #          if gap < toleransi:
   #             total += gap
   #          else:
   #             total += filler
   #       index += 1
      
   #    final_result.append({
   #       "nama": str(akun["nama"]).upper(),
   #       "id_mhs": el,
   #       "durasi": total,
   #       "nim": mahasiswa["nim"],
   #       "foto_profil": akun["foto_profil"],
   #       "href": f"/jadwal/{id_jadwal}/{str(mahasiswa['_id'])}"
   #    })

   # print(final_result)


   # print(ids)
   # print(result)


   hasil.sort(key=lambda d: d["ts"], reverse=True)
   # print(hasil)

   # print(jadwal, hasil_sorted)

   # keterangan = f"Berada di Kampus - {tanggal} ({', '.join(ruangan)})"

   return hasil, keterangan

async def ambil_berada_di_kampus_by_tanggal_only(tanggal):
   db = client["face_identification_3"]

   aktivitas = db["aktivitas"].find({"tanggal": tanggal, "jadwal_id": None})

   mahasiswa_list = await db["mahasiswa"].find().to_list(None)
   ruangan = await db["ruangan"].find().to_list(None)

   e = []

   toleransi = timedelta(minutes=15)

   for a in await aktivitas.to_list(length=None):
      for mahasiswa in mahasiswa_list:
         if str(a["mahasiswa_id"]) == str(mahasiswa["_id"]):
            a["nama_mahasiswa"] = mahasiswa["nama"]
            a["foto_profil_path"] = mahasiswa["foto_profil_path"]
            a["nim"] =  mahasiswa["nim"]
            break
      for ruang in ruangan:
         if str(a["ruangan_id"]) == str(ruang["_id"]):
            a["ruangan"] = f'{ruang["kode_ruangan"]} - {ruang["nama_ruangan"]}'
            break
      a["waktu_terakhir"] = str(a["waktu"][len(a["waktu"]) - 1]).split(" ")[1].split(".")[0]

      total = timedelta(seconds=a["expires"][0])
      for index, el in enumerate(a["expires"]):
         if index < len(a["waktu"]) - 1:
            gap = a["waktu"][index + 1].replace(microsecond=0) - a["waktu"][index].replace(microsecond=0)
            # print(gap)
            if gap < toleransi:
               total += gap
            else:
               total += timedelta(seconds=el)
      a["durasi"] = total
      e.append(a)

      # mhs_set.add(a["mahasiswa"]["id_mahasiswa"])
      # ruang_set.add(a["ruangan"])

   # akt_group = []

   # for mhs in mhs_set:
      
   #    mahasiswa = await collection_mahasiswa.find_one({"_id": mhs}) 

      # obj = {"nama": , "username": mahasiswa["akun"]["username"], "foto_profil": mahasiswa["akun"]["foto_profil_path"], "id_mhs": mahasiswa["_id"], "nim": mahasiswa["nim"]}

      # bdk, ket = await ambil_berada_di_kampus(mhs, tanggal, True)

      # print("bdk: ", bdk)
      
      # for el in bdk:
      #    el["nama"] = mahasiswa["akun"]["nama"]
      #    el["foto_profil"] = mahasiswa["akun"]["foto_profil_path"]
      #    el["id_mhs"] = mahasiswa["_id"]
      #    el["nim"] = mahasiswa["nim"]
      #    el["mhs_id"] = mahasiswa['_id']
      #    e.append(el)
      # collection_aktivitas.find({"tanggal": tanggal, "jadwal": {}, "mahasiswa.id_mahasiswa": ObjectId(mhs), "ruangan": ruang})

   e.sort(key=lambda d: d["waktu_terakhir"], reverse=True)

   return e
   
async def find_mahasiswa_complete(id):
   try:
      id = ObjectId(id)
   except:
      return False
   
   db = client["face_identification_3"]
   collection_mahasiswa = db["mahasiswa"]
   collection_aktivitas = db["aktivitas"]
   collection_orang_tua = db["orang_tua"]

   mahasiswa = await collection_mahasiswa.find_one({"_id": ObjectId(id) })

   if not mahasiswa:
      return False
   
   req_orang_tua = []
   
   if mahasiswa["orang_tua_id"]:
      orang_tua = await collection_orang_tua.find_one({"_id": ObjectId(mahasiswa["orang_tua_id"])})
   else:
      a = collection_orang_tua.find({"requested_anak_id": ObjectId(mahasiswa["_id"])})
      for el in await a.to_list(length=100):
         el["_id"] = str(el["_id"])
         el["requested_anak_id"] = str(el["requested_anak_id"])
         el["anak_id"] = str(el["anak_id"])
         req_orang_tua.append(el)

   aktivitas_terakhir_ex = ["", "", ""]
   aktivitas_terakhir = await collection_aktivitas.find_one({"mahasiswa_id": ObjectId(id)}, sort=[("updateAt", DESCENDING)])
   waktu_sekarang = datetime.now()
   
   if aktivitas_terakhir:
      time_gap = str(waktu_sekarang - aktivitas_terakhir["updateAt"]).split(" ")

      selisih = ""

      if len(time_gap) > 1:
         selisih = f"{time_gap[0]} hari yang lalu"
      else:
         waktu = time_gap[0].split(".")[0]
         jam = waktu.split(":")[0]
         menit = waktu.split(":")[1]
         detik = waktu.split(":")[2]

         if jam != "0":
            selisih = f"{jam} jam yang lalu"
         elif menit != "00":
            if menit.split("0")[0] == "0":
               selisih = f"{menit.split('0')[1]} menit yang lalu"
            else:
               selisih = f"{menit} menit yang lalu"
         elif detik != "00":
            if detik.split("0")[0] == "0":
               selisih = f"{detik.split('0')[1]} detik yang lalu"
            else:
               selisih = f"{detik} detik yang lalu"
      
      aktivitas_terakhir_ex[2] = selisih

      ruangan = await db["ruangan"].find_one({"_id": ObjectId(aktivitas_terakhir["ruangan_id"])})
      aktivitas_terakhir_ex[1] = ruangan["nama_ruangan"]

      if not aktivitas_terakhir["jadwal_id"]:
         aktivitas_terakhir_ex[0] = "Berada di Kampus"
      else:
         jadwal = await db["jadwal"].find_one({"_id": ObjectId(aktivitas_terakhir["jadwal_id"])})
         aktivitas_terakhir_ex[0] = jadwal["nama_kegiatan"]

   user = {
      "id": str(mahasiswa["_id"]),
      "nama": mahasiswa["nama"],
      "username": mahasiswa["username"],
      "pengguna": "MAHASISWA",
      "nim": mahasiswa["nim"],
      "email": mahasiswa["email"],
      "foto": [item for item in mahasiswa["foto_wajah_path"] if item != None],
      "orang_tua": orang_tua["nama"] if mahasiswa['orang_tua_id'] else "",
      "id_orang_tua": str(mahasiswa['orang_tua_id']),
      "aktivitas_terakhir": aktivitas_terakhir_ex,
      "foto_profil": mahasiswa["foto_profil_path"] if mahasiswa["foto_profil_path"] != None else "",
      "req_orang_tua": req_orang_tua
   }

   if mahasiswa:
      # print(user)
      return user
   
async def find_dosen_complete(id):
   try:
      id = ObjectId(id)
   except:
      return False

   db = client["face_identification_3"]
   collection_dosen = db["dosen"]

   dosen = await collection_dosen.find_one({"_id": ObjectId(id) })

   if not dosen:
      return False

   user = {
      "nama": dosen["nama"],
      "username": dosen["username"],
      "pengguna": "DOSEN",
      "email": dosen["email"],
      "nip": dosen["nip"],
      "foto_profil": dosen["foto_profil_path"]
   }

   if dosen:
      return user
      
async def find_orang_tua_complete(id):
   try:
      id = ObjectId(id)
   except:
      return False
   db = client["face_identification_3"]
   collection_orang_tua = db["orang_tua"]
   collection_mahasiswa = db["mahasiswa"]

   id = ObjectId(id)

   orang_tua = await collection_orang_tua.find_one({"_id": ObjectId(id) })
   if not orang_tua:
      return False
   anak = await collection_mahasiswa.find_one({"_id": ObjectId(orang_tua["anak_id"])})
   
   if not anak:
      req_anak = await collection_mahasiswa.find_one({"_id": ObjectId(orang_tua["requested_anak_id"])})
      if not req_anak:
         user = {
            "nama": orang_tua["nama"],
            "username": orang_tua["username"],
            "pengguna": "ORANG TUA",
            "email": orang_tua["email"],
            "anak": "-",
            "id_anak": "-",
            "req_anak": "",
            "req_id_anak": "",
            "foto_profil": orang_tua["foto_profil_path"]
         }
      else:
         user = {
            "nama": orang_tua["nama"],
            "username": orang_tua["username"],
            "pengguna": "ORANG TUA",
            "email": orang_tua["email"],
            "anak": "-",
            "id_anak": "-",
            "req_anak": req_anak["nama"],
            "req_id_anak": str(req_anak["_id"]),
            "foto_profil": orang_tua["foto_profil_path"]
         }
   else:
      user = {
         "nama": orang_tua["nama"],
         "username": orang_tua["username"],
         "pengguna": "ORANG TUA",
         "email": orang_tua["email"],
         "anak": f'{anak["nama"]} ({anak["nim"]})',
         "id_anak": str(anak["_id"]),
         "foto_profil": orang_tua["foto_profil_path"]
      }

   return user
   
async def cek_akun_anak(id_mhs):
   db = client["face_identification_3"]
   mahasiswa_collection = db["mahasiswa"]
   mahasiswa = await mahasiswa_collection.find_one({"_id": ObjectId(id_mhs)})

   if mahasiswa["orang_tua_id"]:
      # print("akun anak sudah occupied")
      return False

   return True

async def verify_jadwal(ruangan, waktu_mulai, waktu_selesai):
   db = client["face_identification_3"]
      
   jadwal_collection = db["jadwal"]
   jadwal = jadwal_collection.find({"ruangan_id": ObjectId(ruangan)})
   
   for el in await jadwal.to_list(length=100):
      a = waktu_mulai >= el["waktu_mulai"] and waktu_mulai <= el["waktu_selesai"]
      b = waktu_selesai >= el["waktu_mulai"] and waktu_selesai <= el["waktu_selesai"]
      c = el["waktu_mulai"] >= waktu_mulai and el["waktu_mulai"] <= waktu_selesai
      d = el["waktu_selesai"] >= waktu_mulai and el["waktu_selesai"] <= waktu_selesai
      if a or b or c or d:
         return False


   return True

async def verify_ubah_jadwal(ruangan, waktu_mulai, waktu_selesai, id):
   db = client["face_identification_3"]
      
   jadwal_collection = db["jadwal"]
   jadwal = jadwal_collection.find({"ruangan": ruangan})
   
   id = ObjectId(id)

   for el in await jadwal.to_list(length=100):
      if id != el["_id"]:
         if(waktu_mulai >= el["waktu_mulai"] and waktu_mulai <= el["waktu_selesai"]) or (waktu_selesai >= el["waktu_mulai"] and waktu_selesai <= el["waktu_selesai"]):
            return False


   return True

def tambah_jadwal(data, id, nama, foto_profil):
   db = client2["face_identification_3"]
   
   jadwal_collection = db["jadwal"]

   waktu_mulai = datetime.strptime(data["waktu_mulai"], "%Y-%m-%dT%H:%M")
   waktu_selesai = datetime.strptime(data["waktu_selesai"], "%Y-%m-%dT%H:%M")

   if waktu_mulai >= waktu_selesai:
      flash(f"Gagal menambahkan jadwal. Waktu selesai < waktu mulai!", "danger")
      return False


   if waktu_selesai.day > waktu_mulai.day:
      flash(f"Gagal menambahkan jadwal. Waktu mulai dan waktu selesai di hari yang berbeda tidak diperbolehkan.", "danger")
      return False
   

   gap = waktu_mulai - datetime.now()

   if gap.days < 0:
      flash(f"Gagal menambahkan jadwal. Waktu mulai jadwal melewati waktu saat jadwal dibuat.", "danger")
      return False

   ket_ruangan = data["ruangan_kegiatan"].split("___")[0]


   # Verify jadwal baru (jadwal tabrakan)
   if not loop.run_until_complete(verify_jadwal(ket_ruangan, waktu_mulai, waktu_selesai)):
      flash(f"Gagal menambahkan jadwal. Terjadi bentrok antar jadwal.", "danger")
      return False

   jadwal_collection.insert_one({
      "nama_kegiatan": data["nama_kegiatan"][:20].title(),
      "waktu_mulai": waktu_mulai,
      "waktu_selesai": waktu_selesai,
      "keterangan": data["keterangan_kegiatan"][:300],
      "dosen_id": ObjectId(id),
      "ruangan_id": ObjectId(ket_ruangan)
   })

   return True

def tambah_jadwal2(data, id, nama, foto_profil):
   db = client2["face_identification_3"]

   jadwal_collection = db["jadwal"]

   waktu_mulai = f'{data["tanggal"]}T{data["waktu_mulai"]}'
   waktu_selesai = f'{data["tanggal"]}T{data["waktu_selesai"]}'

   waktu_mulai = datetime.strptime(waktu_mulai, "%Y-%m-%dT%H:%M")
   waktu_selesai = datetime.strptime(waktu_selesai, "%Y-%m-%dT%H:%M")

   if waktu_mulai >= waktu_selesai:
      flash(f"Gagal menambahkan jadwal. Waktu selesai < waktu mulai!", "danger")
      return False

   if waktu_selesai.day > waktu_mulai.day:
      flash(f"Gagal menambahkan jadwal. Waktu mulai dan waktu selesai di hari yang berbeda tidak diperbolehkan.", "danger")
      return False

   gap = waktu_mulai - datetime.now()

   if gap.days < 0:
      flash(f"Gagal menambahkan jadwal. Waktu mulai jadwal melewati waktu saat jadwal dibuat.", "danger")
      return False

   ket_ruangan = data["ruangan_kegiatan"].split("___")[0]

   # Verify jadwal baru (jadwal tabrakan)
   if not loop.run_until_complete(verify_jadwal(ket_ruangan, waktu_mulai, waktu_selesai)):
      flash(f"Gagal menambahkan jadwal. Terjadi bentrok antar jadwal.", "danger")
      return False
   

   jadwal_collection.insert_one({
      "nama_kegiatan": data["nama_kegiatan"][:20].title(),
      "waktu_mulai": waktu_mulai,
      "waktu_selesai": waktu_selesai,
      "keterangan": data["keterangan_kegiatan"][:300],
      "dosen_id": ObjectId(id),
      "ruangan_id": ObjectId(ket_ruangan)
   })

   return True

def ubah_jadwal(data, id):
   db = client2["face_identification_3"]
   
   jadwal_collection = db["jadwal"]

   waktu_mulai = datetime.strptime(data["waktu_mulai"], "%Y-%m-%dT%H:%M")
   waktu_selesai = datetime.strptime(data["waktu_selesai"], "%Y-%m-%dT%H:%M")
   waktu_mulai_old = datetime.strptime(data["waktu_mulai_old"], "%Y-%m-%dT%H:%M")

   gap = waktu_mulai_old - datetime.now()

   if gap.days < 0:
      flash(f"Jadwal yang ingin diubah telah dimulai.", "danger")
      return False
   
   if waktu_mulai >= waktu_selesai:
      flash(f"Gagal menambahkan jadwal. Waktu selesai < waktu mulai!", "danger")
      return False


   if waktu_selesai.day > waktu_mulai.day:
      flash(f"Gagal menambahkan jadwal. Waktu mulai dan waktu selesai di hari yang berbeda tidak diperbolehkan.", "danger")
      return False

   gap = waktu_mulai - datetime.now()
   # print(gap.seconds)
   if gap.days < 0:
      flash(f"Waktu mulai jadwal melewati waktu saat jadwal dibuat.", "danger")
      return False

   # Verify jadwal baru (jadwal tabrakan)
   if not loop.run_until_complete(verify_ubah_jadwal(data["ruangan_kegiatan"], waktu_mulai, waktu_selesai, id)):
      flash(f"Terjadi bentrok antar jadwal.", "danger")
      return False
   

   jadwal_collection.update_one({"_id": ObjectId(id)}, {"$set": {
      "nama_kegiatan": data["nama_kegiatan"],
      "ruangan": data["ruangan_kegiatan"],
      "waktu_mulai": waktu_mulai,
      "waktu_selesai": waktu_selesai,
      "keterangan": data["keterangan"],
   }})

   return True

def hapus_jadwal(id):
   db = client2["face_identification_3"]
   
   jadwal_collection = db["jadwal"]
   jadwal = jadwal_collection.find_one({"_id": ObjectId(id)})
   tanggal = jadwal['waktu_mulai'].strftime("%Y-%m-%d")
   try:
      jadwal_collection.delete_one({"_id": ObjectId(id)})
   except:
      return False
   return tanggal

async def ambil_jadwal(date_time, ruangan):
   # try:

   db = client["face_identification_3"]
   
   start = datetime.combine(date_time, time.min)
   end = datetime.combine(date_time, time.max)

   res = db["jadwal"].find({"waktu_mulai": {"$gte": start, "$lt": end}})
   dosen = await db["dosen"].find({}).to_list(None)

   jadwal = []
   now = datetime.now()

   for a in await res.to_list(length=None):
      for dos in dosen:
         if a["dosen_id"] == dos["_id"]:
            a["id_dosen"] = dos["nama"]
            for ruang in ruangan:
               # print("ruangan_id", a["ruangan_id"])
               if str(a["ruangan_id"]) == str(ruang["_id"]):
                  print("matched")
                  a["ruangan"] = ruang["nama_ruangan"]
                  a["kode_ruangan"] = ruang["kode_ruangan"]
                  break
            break
      a["_id"] = str(a["_id"])
      a["resolved"] = 0
      if a["waktu_mulai"] <= now <= a["waktu_selesai"]:
         a["resolved"] = 1
      elif now >= a["waktu_selesai"]:
         a["resolved"] = 2
      a["mulai_selesai_str"] = [a["waktu_mulai"].strftime("%H:%M"), a["waktu_selesai"].strftime("%H:%M")]

      jadwal.append(a)

   jadwal_sorted = sorted(jadwal, key=lambda x: x['waktu_mulai'])

   return jadwal_sorted
   
async def ambil_semua_jadwal():
   db = client["face_identification_3"]
   jadwal_collection = db["jadwal"]

   semua_jadwal =  jadwal_collection.find({})
   tanggal_set = set()
   for a in await semua_jadwal.to_list(length=None):
      tanggal = a["waktu_mulai"].strftime("%Y-%m-%d")
      tanggal_set.add(tanggal)

   return tanggal_set

async def ambil_frame(frame_id):
   db = client["face_identification_3"]
   frame_collection = db["frame"]
   try:
      ObjectId(frame_id)
   except:
      return False

   frame =  await frame_collection.find_one({"_id": ObjectId(frame_id)})

   return frame


def to_integer(current_date):
   return current_date.year * 10000000000 + current_date.month * 100000000 + current_date.day * 1000000 + current_date.hour*10000 + current_date.minute*100 + current_date.second


async def temp2():
   db = client["face_identification_3"]
   aktivitas_collection = db["aktivitas"]
   mahasiswa_collection = db["mahasiswa"]

   semua_aktivitas =  aktivitas_collection.find({})
   for a in await semua_aktivitas.to_list(length=None):
      mahasiswa = await mahasiswa_collection.find_one({"_id": a["mahasiswa"]["id_mahasiswa"]}, {"akun.foto_profil_path": 1})
      print(mahasiswa["akun"]["foto_profil_path"])
      await aktivitas_collection.update_one({"_id": a["_id"]}, {"$set": {"mahasiswa.foto_profil_path": mahasiswa["akun"]["foto_profil_path"]}})

async def temp3():
   db = client["face_identification_3"]
   aktivitas_collection = db["aktivitas"]

   await aktivitas_collection.update_many({}, {'$rename': {"filler": "expires"}})
   # return tanggal_set

async def temp4():
   db = client["face_identification_3"]
   ruangan_collection = db["ruangan"]

   await ruangan_collection.update_many({}, {'$set': {"digunakan": False}})

async def temp5():
   db = client["face_identification_3"]

   semua_aktivitas =  db["aktivitas"].find({})
   count = 0
   for a in await semua_aktivitas.to_list(length=None):
      count += 1
   # print("Before ", count)
   await db["aktivitas"].delete_many({"tanggal": "2025-03-27"})
   semua_aktivitas =  db["aktivitas"].find({})
   count = 0
   for a in await semua_aktivitas.to_list(length=None):
      count += 1
   # print("After ", count)

async def temp6():
   db = client["face_identification_3"]

   ruangan = db["ruangan"].find({"digunakan": True})

   alll = []
   for a in await ruangan.to_list(length=None):
      alll.append(a)
   # print("Ruangan digunakan saat ini:  ", alll)

async def temp7():
   db = client["face_identification_3"]

   await db["ruangan"].update_one({"_id": ObjectId('67bca28267cb298398e8ab29')}, {"$set": {"digunakan": False}})

async def temp8():
   db = client["face_identification_3"]

   dosen = db["dosen"].find({})
   for d in await dosen.to_list(length=None):
      await db["jadwal"].update_many({"dosen.id_dosen": ObjectId(d["_id"])}, {"$set": {"dosen.foto_profil_path": d["akun"]["foto_profil_path"]}})
      await db["aktivitas"].update_many({"jadwal.dosen.id_dosen": ObjectId(d["_id"])}, {"$set": {"jadwal.dosen.foto_profil_path": d["akun"]["foto_profil_path"]}})


async def temp9():
   db = client["face_identification_3"]

   await db["ruangan"].update_many({}, {"$set": {"digunakan": False}})


   # alll = []
   # for a in await ruangan.to_list(length=None):
   #    alll.append(a)
   # print("Ruangan digunakan saat ini:  ", alll)

async def temp10():
   db = client["face_identification_3"]

   nims = ["123", "D1041181025", "D1041181002", "D1041181017"]

   for nim in nims:
      mahasiswa = await db["mahasiswa"].find_one({"nim": nim})
      setter = {
         "nama": mahasiswa["akun"]["nama"],
         "email": mahasiswa["akun"]["email"],
         "username": mahasiswa["akun"]["username"],
         "password": mahasiswa["akun"]["password"],
         "foto_profil_path": mahasiswa["akun"]["foto_profil_path"],
         "orang_tua_id": None
      }
      await db["mahasiswa"].update_one({"nim": nim}, {"$set": setter})
      unsetter = {"akun": "", "orang_tua": "", "aktivitas_terakhir": ""}
      await db["mahasiswa"].update_one({"nim": nim}, {"$unset": unsetter})

async def temp11():
   db = client["face_identification_3"]

   dosen = await db["dosen"].find_one({"nip": "198611132020121005"})
   setter = {
      "nama": dosen["akun"]["nama"],
      "email": dosen["akun"]["email"],
      "username": dosen["akun"]["username"],
      "password": dosen["akun"]["password"],
      "foto_profil_path": dosen["akun"]["foto_profil_path"]
   }
   await db["dosen"].update_one({"nip": "198611132020121005"}, {"$set": setter})
   unsetter = {"akun": ""}
   await db["dosen"].update_one({"nip": "198611132020121005"}, {"$unset": unsetter})

async def temp12():
   db = client["face_identification_3"]

   # await db["aktivitas2"].insert_one({
   #    "timestamp": datetime.now(),
   #    "expires": 30,
   #    "gambar": "xasasa",
   #    "mahasiswa_id": ObjectID(),
   #    "ruang_id": ObjectID(),
   #    "jadwal_id": ObjectID()
   # })

async def temp13():
   db = client["face_identification_3"]

   # await db["aktivitas2"].insert_one({
   #    "timestamp": datetime.now(),
   #    "expires": 30,
   #    "gambar": "xasasa",
   #    "mahasiswa_id": ObjectID(),
   #    "ruang_id": ObjectID(),
   #    "jadwal_id": ObjectID()
   # })

   now = datetime.now()
   start_of_today = datetime(now.year, now.month, now.day)
   start_of_tomorrow = start_of_today + timedelta(days=1)

   # Delete documents where createdAt is within today
   result = db["aktivitas"].delete_many({
      "expires": [40]
   })

   print(result)

async def temp14():
   db = client["face_identification_3"]

   # await db["aktivitas2"].insert_one({
   #    "timestamp": datetime.now(),
   #    "expires": 30,
   #    "gambar": "xasasa",
   #    "mahasiswa_id": ObjectID(),
   #    "ruang_id": ObjectID(),
   #    "jadwal_id": ObjectID()
   # })

   # Delete documents where createdAt is within today
   db["mahasiswa"].delete_one({
      "_id": ObjectId("6805318693165d7931a85a8f")
   })
   db["aktivitas"].delete_many({
      "mahasiswa_id": ObjectId("6805318693165d7931a85a8f")
   })

async def temp15():
   db = client["face_identification_3"]

   # await db["aktivitas2"].insert_one({
   #    "timestamp": datetime.now(),
   #    "expires": 30,
   #    "gambar": "xasasa",
   #    "mahasiswa_id": ObjectID(),
   #    "ruang_id": ObjectID(),
   #    "jadwal_id": ObjectID()
   # })

   # Delete documents where createdAt is within today
   db["mahasiswa"].update_many({}, {
      "$set": {"requested_orang_tua_id": []}
   })

   print("done")


# loop.run_until_complete(temp15())