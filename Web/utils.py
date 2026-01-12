from flask import flash
from datetime import datetime

def verify_akun_umum(nama, list_nama, username, usernames, password, konfirmasi_password):
   if nama in list_nama:
      flash("Maaf, nama yang anda masukan sudah terdaftar.", "danger")
      return False
   
   if username.upper() in usernames:
      flash("Maaf, username yang anda pilih telah terdaftar. Coba gunakan username lain.", "danger")
      return False

   if password != konfirmasi_password:
      flash("Password & konfirmasinya tidak sesuai!", "danger")
      return False
   
   return True


def get_hari_dan_tanggal(tanggal):

   day_name = tanggal.strftime("%A")

   if day_name == "Monday":
      nama_hari = "Senin" 
   elif day_name == "Tuesday":
      nama_hari = "Selasa"
   elif day_name == "Wednesday":
      nama_hari = "Rabu"
   elif day_name == "Thursday":
      nama_hari = "Kamis"
   elif day_name == "Friday":
      nama_hari = "Jumat"
   elif day_name == "Saturday":
      nama_hari = "Sabtu"
   elif day_name == "Sunday":
      nama_hari = "Minggu"

   nomor_bulan = tanggal.strftime("%m")

   if nomor_bulan == "01":
      nama_bulan = "Januari" 
   elif nomor_bulan == "02":
      nama_bulan = "Februari"
   elif nomor_bulan == "03":
      nama_bulan = "Maret"
   elif nomor_bulan == "04":
      nama_bulan = "April"
   elif nomor_bulan == "05":
      nama_bulan = "Mei"
   elif nomor_bulan == "06":
      nama_bulan = "Juni"
   elif nomor_bulan == "07":
      nama_bulan = "Juli"
   elif nomor_bulan == "08":
      nama_bulan = "Agustus"
   elif nomor_bulan == "09":
      nama_bulan = "September"
   elif nomor_bulan == "10":
      nama_bulan = "Oktober"
   elif nomor_bulan == "11":
      nama_bulan = "November"
   elif nomor_bulan == "12":
      nama_bulan = "Desember"

   if datetime.now().date() == tanggal.date():
      result = f"Hari ini, {nama_hari} {int(tanggal.strftime('%d'))} {nama_bulan} {tanggal.strftime('%Y')}"
   else:
      result = f"{nama_hari} {int(tanggal.strftime('%d'))} {nama_bulan} {tanggal.strftime('%Y')}"

   return result


def get_tanggal(tanggal):

   nomor_bulan = tanggal.strftime("%m")

   if nomor_bulan == "01":
      nama_bulan = "Januari" 
   elif nomor_bulan == "02":
      nama_bulan = "Februari"
   elif nomor_bulan == "03":
      nama_bulan = "Maret"
   elif nomor_bulan == "04":
      nama_bulan = "April"
   elif nomor_bulan == "05":
      nama_bulan = "Mei"
   elif nomor_bulan == "06":
      nama_bulan = "Juni"
   elif nomor_bulan == "07":
      nama_bulan = "Juli"
   elif nomor_bulan == "08":
      nama_bulan = "Agustus"
   elif nomor_bulan == "09":
      nama_bulan = "September"
   elif nomor_bulan == "10":
      nama_bulan = "Oktober"
   elif nomor_bulan == "11":
      nama_bulan = "November"
   elif nomor_bulan == "12":
      nama_bulan = "Desember"

   return f"{tanggal.strftime('%d')} {nama_bulan} {tanggal.strftime('%Y')}"

def get_tanggal_2(tanggal):

   li_tgl = tanggal.split("-")

   nomor_bulan = li_tgl[1]

   if nomor_bulan == "01":
      nama_bulan = "Januari" 
   elif nomor_bulan == "02":
      nama_bulan = "Februari"
   elif nomor_bulan == "03":
      nama_bulan = "Maret"
   elif nomor_bulan == "04":
      nama_bulan = "April"
   elif nomor_bulan == "05":
      nama_bulan = "Mei"
   elif nomor_bulan == "06":
      nama_bulan = "Juni"
   elif nomor_bulan == "07":
      nama_bulan = "Juli"
   elif nomor_bulan == "08":
      nama_bulan = "Agustus"
   elif nomor_bulan == "09":
      nama_bulan = "September"
   elif nomor_bulan == "10":
      nama_bulan = "Oktober"
   elif nomor_bulan == "11":
      nama_bulan = "November"
   elif nomor_bulan == "12":
      nama_bulan = "Desember"

   return f"{int(li_tgl[2])} {nama_bulan} {li_tgl[0]}"

def allowed_file(filename):
   return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}
