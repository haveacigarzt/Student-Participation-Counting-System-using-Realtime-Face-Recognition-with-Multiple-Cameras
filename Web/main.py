# Copas dari main, plus pantau identifikasi
from flask import render_template, request, flash, redirect, url_for, make_response, jsonify
from markupsafe import Markup
from werkzeug.security import check_password_hash

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

import sys
import os
from datetime import datetime, timedelta
import time
import base64

import jwt
from jwt.exceptions import ExpiredSignatureError
from functools import wraps

from app import app
from forms import LoginForm, DaftarFormMahasiswa, DaftarFormDosen, JadwalForm, DaftarFormOrangTua
from queries import find_user, find_list, simpan_data_mahasiswa, simpan_data_dosen, find_mahasiswa_complete, tambah_jadwal, tambah_jadwal2, ubah_jadwal, hapus_jadwal, ambil_jadwal, ambil_berada_di_kampus, ambil_berada_di_kampus_by_tanggal_only, cari_aktivitas_user, simpan_data_orang_tua, find_dosen_complete, find_orang_tua_complete, cari_id_anak, cari_req_id_anak, ubah_data_akun, ambil_choices_akun_mhs, ambil_choices_akun_mhs_2, hapus_foto_wajah_mhs, cari_foto_wajah, ambil_jadwal_dan_hasil, cek_akun_anak, cari_semua_mahasiswa, ambil_jadwal_dan_hasil_mhs, ambil_semua_jadwal, ambil_ruangan, ambil_aktivitas_by_id, ambil_menghadiri_kegiatan, dosen_cari_aktivitas_user, ambil_frame, cari_ruangan_aktif, ambil_ruangan_by_id

from utils import verify_akun_umum, get_hari_dan_tanggal, get_tanggal, get_tanggal_2

db_uri = "mongodb+srv://afriandypramana:bczFDLSJSzrATKdP@cluster0.yqmayik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
payload = ""

try:
   client = AsyncIOMotorClient(db_uri, server_api=ServerApi("1"))
   loop = client.get_io_loop()
except Exception:
   print("DB connection failed")
   sys.exit()

user_id = ""

def token_required_mahasiswa(func):
   @wraps(func)
   def decorated(*args, **kwargs):
      global payload
      global user_id
      token = request.cookies.get("token")
      if not token:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      try:
         try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
         except ExpiredSignatureError as error:
            flash(f"Token anda telah kadaluarsa, silahkan login kembali.", "warning")
            return redirect(url_for("login"))
         if (payload["pengguna"] == "dosen"):
            flash(f"Anda tidak login sebagai mahasiswa!", "warning")
            return redirect(url_for("dosen"))
         if (payload["pengguna"] == "orang_tua"):
            flash(f"Anda tidak login sebagai mahasiswa!", "warning")
            return redirect(url_for("orang_tua"))
         user_id = payload["user_id"]
      except:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      return func(*args, **kwargs)
   return decorated

def token_required_dosen(func):
   @wraps(func)
   def decorated(*args, **kwargs):
      global payload
      global user_id
      token = request.cookies.get("token")
      if not token:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      try:
         try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
         except ExpiredSignatureError as error:
            flash(f"Token anda telah kadaluarsa, silahkan login kembali.", "warning")
            return redirect(url_for("login"))
         if (payload["pengguna"] == "mahasiswa"):
            flash(f"Anda tidak login sebagai dosen!", "warning")
            return redirect(url_for("mahasiswa"))
         if (payload["pengguna"] == "orang_tua"):
            flash(f"Anda tidak login sebagai dosen!", "warning")
            return redirect(url_for("orang_tua"))
         user_id = payload["user_id"]
      except:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      return func(*args, **kwargs)
   return decorated

def token_required_orang_tua(func):
   @wraps(func)
   def decorated(*args, **kwargs):
      global payload
      global user_id
      token = request.cookies.get("token")
      if not token:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      try:
         try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
         except ExpiredSignatureError as error:
            flash(f"Token anda telah kadaluarsa, silahkan login kembali.", "warning")
            return redirect(url_for("login"))
         if (payload["pengguna"] == "mahasiswa"):
            flash(f"Anda tidak login sebagai orang tua!", "warning")
            return redirect(url_for("mahasiswa"))
         if (payload["pengguna"] == "dosen"):
            flash(f"Anda tidak login sebagai orang tua!", "warning")
            return redirect(url_for("dosen"))
         user_id = payload["user_id"]
      except:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      return func(*args, **kwargs)
   return decorated


def token_required(func):
   @wraps(func)
   def decorated(*args, **kwargs):
      global payload
      global user_id
      token = request.cookies.get("token")
      if not token:
         flash(f"Harap login terlebih dahulu.", "warning")
         return redirect(url_for("login"))
      try:
         payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
      except ExpiredSignatureError as error:
         flash(f"Token anda telah kadaluarsa, silahkan login kembali.", "warning")
         return redirect(url_for("login"))
      user_id = payload["user_id"]
      return func(*args, **kwargs)
   return decorated   


@app.route("/", methods=["GET"])
def index():
   global payload
   token = request.cookies.get("token")

   if token:
      try:
         payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
      except ExpiredSignatureError as error:
         return redirect(url_for("login"))
      
      if payload["pengguna"] == "mahasiswa":
         return redirect(url_for("mahasiswa"))
      elif payload["pengguna"] == "dosen":
         return redirect(url_for("dosen"))
      elif payload["pengguna"] == "orang tua":
         return redirect(url_for("orang_tua"))
      else:
         return redirect(url_for("login"))
   else:
      return redirect(url_for("login"))

darkmode = ""

@app.route("/daftar_mahasiswa", methods=["GET", "POST"])
def daftar_mahasiswa():
   form = DaftarFormMahasiswa()

   if request.method == "POST" and form.validate_on_submit():
      
      usernames = loop.run_until_complete(find_list("mahasiswa", "username"))
      names = loop.run_until_complete(find_list("mahasiswa", "nama"))

      verified = verify_akun_umum(request.form["nama"].upper(), names, request.form["username"], usernames,  request.form["password"], request.form["konfirmasi_password"])

      if not verified:
         return redirect(url_for("daftar_mahasiswa"))


      tersimpan = simpan_data_mahasiswa(request.form)

      if not tersimpan:
         return redirect(url_for("daftar_mahasiswa"))

      link = url_for('login')
      flash(Markup(f"Terimakasih akun anda berhasil didaftarkan. Silahkan <a href='{link}' class='link-alert'>login</a>."), "success")
      
      return redirect(url_for("daftar_mahasiswa"))
   
   return render_template("daftar_mahasiswa.html", form=form)
   

@app.route("/daftar_dosen", methods=["GET", "POST"])
def daftar_dosen():
   form = DaftarFormDosen()

   if request.method == "POST" and form.validate_on_submit():
      
      usernames = loop.run_until_complete(find_list("dosen", "username"))
      names = []
      
      verified = verify_akun_umum(request.form["nama"].upper(), names, request.form["username"], usernames,  request.form["password"], request.form["konfirmasi_password"])
      
      if not verified:
         return redirect(url_for("daftar_dosen"))
      
      tersimpan = simpan_data_dosen(request.form)

      if not tersimpan:
         return redirect(url_for("daftar_dosen"))
   
      link = url_for('login')
      flash(Markup(f"Terimakasih akun anda berhasil didaftarkan. Silahkan <a href='{link}' class='link-alert'>login</a>."), "success")
      
      return redirect(url_for("daftar_dosen"))
   
   return render_template("daftar_dosen.html", form=form)

@app.route("/daftar_orang_tua", methods=["GET", "POST"])
def daftar_orang_tua():
   form = DaftarFormOrangTua()

   akun_anak = loop.run_until_complete(ambil_choices_akun_mhs())

   if request.method == "POST" and form.validate_on_submit():
      
      usernames = loop.run_until_complete(find_list("orang tua", "username"))
      names = loop.run_until_complete(find_list("orang tua", "nama"))
      
      verified = verify_akun_umum(request.form["nama"].upper(), names, request.form["username"], usernames,  request.form["password"], request.form["konfirmasi_password"])
      
      if not verified:
         return redirect(url_for("daftar_orang_tua"))
      
      
      hasil_cek_akun_anak = loop.run_until_complete(cek_akun_anak(request.form["akun_anak"]))

      if not hasil_cek_akun_anak:
         flash(f"Akun gagal dibuat. Akun anak yang dipilih sudah terhubung ke satu Akun Orang Tua.", "danger")
         return redirect(url_for("daftar_orang_tua"))
      
      tersimpan = simpan_data_orang_tua(request.form)

      if not tersimpan:
         return redirect(url_for("daftar_orang_tua"))
   
      link = url_for('login')
      flash(Markup(f"Terimakasih akun anda berhasil didaftarkan. Silahkan <a href='{link}' class='link-alert'>login</a>."), "success")
      
      return redirect(url_for("daftar_orang_tua"))
   
   return render_template("daftar_orang_tua.html", form=form, akun_anak=akun_anak)

@app.route("/login", methods=["GET", "POST"])
def login():
   global payload
   form = LoginForm()

   token = request.cookies.get("token")
   
   if token:
      try:
         payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
      except ExpiredSignatureError as error:
         respose = make_response(redirect(url_for("login")))
         respose.set_cookie("token", "")
         # flash(f"Token anda telah kadaluarsa, silahkan login kembali.", "warning")
         return respose
      
      
      if payload["pengguna"] == "mahasiswa":
         flash("Anda sudah login.", "warning")
         return redirect(url_for("mahasiswa"))
      elif payload["pengguna"] == "dosen":
         flash("Anda sudah login.", "warning")
         return redirect(url_for("dosen"))
      elif payload["pengguna"] == "orang_tua":
         flash("Anda sudah login.", "warning")
         return redirect(url_for("orang_tua"))
      else:
         pass

   if request.method == "POST" and form.validate_on_submit():
      password, id, nama, foto_profil = loop.run_until_complete(find_user(request.form["pengguna"], request.form["username"]))

      if password:
         if check_password_hash(password, request.form["password"]):
            
            token = jwt.encode({ "username": request.form["username"], "nama": nama, "pengguna": request.form["pengguna"], "user_id": id, "exp": datetime.utcnow() + timedelta(days=1), "foto_profil": foto_profil}, app.config["SECRET_KEY"], algorithm="HS256")

            resp = make_response(redirect(url_for(request.form["pengguna"])))
            
            resp.set_cookie("token", token)
            resp.set_cookie("darkmode", "")
            return resp
         else:
            flash("Username/password salah!", "danger")
      else:
         flash("Username/password salah!", "danger")

   return render_template("login.html", form=form)

@app.route('/logout', methods=[ "POST"])
def logout():
   if request.method == "POST":
      flash(f"Berhasil logout!", "success")
      resp = make_response(redirect(url_for("index")))
      resp.set_cookie("token", "", expires=0)
      resp.set_cookie("darkmode", "", expires=0)
      return resp

@app.route("/dosen", methods=["GET"])
def berada_dosen():
   return redirect(url_for("dosen"))

@app.route("/dosen/jadwal", methods=["GET", "POST"])
@token_required_dosen
def dosen():
   form_jadwal = JadwalForm()

   user = ["dosen", payload["username"], payload["nama"], payload["foto_profil"]]

   if request.method == "POST":
      if form_jadwal.validate_on_submit():

         data = tambah_jadwal(request.form, payload["user_id"], payload["nama"], payload["foto_profil"])

         if data:
            flash(f"Barhasil menambahkan jadwal", "success")

         return redirect(url_for("dosen"))
      
   ruangan = ambil_ruangan()
   for el in ruangan:
      el["_id"] = str(el["_id"])
   
   pengguna = "dosen"

   if request.args.get("tanggal"):
      tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
      tanggal_hari_ini_dt = datetime.strptime(tanggal_hari_ini, "%Y-%m-%d")
      dt = datetime.strptime(request.args.get("tanggal"), "%Y-%m-%d")
      hapus_tombol = dt < tanggal_hari_ini_dt
      hari = get_hari_dan_tanggal(dt)
      tanggal = get_tanggal(dt)
      hari_tgl = [hari, f"{dt.strftime('%Y')}-{dt.strftime('%m')}-{dt.strftime('%d')}", tanggal]
      jadwal_hari_ini = loop.run_until_complete(ambil_jadwal(dt, ruangan))

      darkmode = ""
      if 'darkmode' in request.cookies:
         darkmode = request.cookies["darkmode"]

      return render_template("dosen_2.html", pengguna=pengguna, user=user, hari_tgl=hari_tgl, form_jadwal=form_jadwal, jadwal_hari_ini=jadwal_hari_ini, dt=request.args.get("tanggal"), hapus_tombol=hapus_tombol, ruangan=ruangan, darkmode=darkmode)

   semua_jadwal = loop.run_until_complete(ambil_semua_jadwal())

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("dosen.html", pengguna=pengguna, user=user, form_jadwal=form_jadwal, semua_jadwal=semua_jadwal, ruangan=ruangan, darkmode=darkmode)

@app.route("/dosen/jadwal2", methods=["POST"])
@token_required_dosen
def dosen2():
   data = tambah_jadwal2(request.form, payload["user_id"], payload["nama"], payload["foto_profil"])

   if data:
      flash(f"Barhasil menambahkan jadwal", "success")
   
   return redirect(url_for("dosen", tanggal=request.form["tanggal"]))

@app.route("/dosen/berada_di_kampus", methods=["GET"])
@token_required_dosen
def dosen_berada_di_kampus():
   user = ["dosen", payload["username"], payload["nama"], payload["foto_profil"]]

   ts = time.time()
   dt = datetime.fromtimestamp(ts)

   if request.args.get("tanggal"):
      dt = datetime.strptime(request.args.get("tanggal"), "%Y-%m-%d")

   hari = get_hari_dan_tanggal(dt)
   tanggal = get_tanggal(dt)

   hari_tgl = [hari, f"{dt.strftime('%Y')}-{dt.strftime('%m')}-{dt.strftime('%d')}", tanggal]


   aktivitas = loop.run_until_complete(ambil_berada_di_kampus_by_tanggal_only(str(dt.date())))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("dosen_berada_di_kampus.html", user=user, hari_tgl=hari_tgl, aktivitas=aktivitas, darkmode=darkmode)

@app.route("/dosen/mahasiswa", methods=["GET"])
@token_required_dosen
def dosen_mahasiswa():
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   
   mahasiswa = loop.run_until_complete(cari_semua_mahasiswa())

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("dosen_mahasiswa.html", user=user, mahasiswa=mahasiswa, darkmode=darkmode)

@app.route("/dosen/identifikasi", methods=["GET"])
@token_required_dosen
def dosen_identifikasi():
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   
   ruangan = loop.run_until_complete(cari_ruangan_aktif())

   for el in ruangan:
      result = loop.run_until_complete(ambil_ruangan_by_id(el["ruangan_id"]))

      el["nama_ruangan"] = result["nama_ruangan"]
      el["kode_ruangan"] = result["kode_ruangan"]

   # print(ruangan)

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("dosen_identifikasi.html", user=user, ruangan=ruangan, darkmode=darkmode)

@app.route("/dosen/mahasiswa/<id>", methods=["GET"])
@token_required_dosen
def dosen_mahasiswa_id(id):
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   
   got, events, aktivitas_terakhir, mhs, my_aktivitas = loop.run_until_complete(dosen_cari_aktivitas_user(id, "mahasiswa"))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("dosen"))


   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("dosen_mahasiswa_id.html", user=user, events=events, aktivitas_terakhir=aktivitas_terakhir, mhs=mhs, my_aktivitas=my_aktivitas, darkmode=darkmode)

@app.route("/dosen/mahasiswa/aktivitas/<id>", methods=["GET"])
@token_required_dosen
def dosen_aktivitas(id):
   resp, got, aktivitas, keterangan, nama, nim, pp_path = loop.run_until_complete(ambil_aktivitas_by_id(id, "", "dosen"))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("dosen"))

   user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("mahasiswa_aktivitas_id_dosen.html", user=user, aktivitas=aktivitas, keterangan=keterangan, id_mhs=aktivitas[1]["id_mhs"], nama=nama, nim=nim, darkmode=darkmode, pp_path=pp_path)


@app.route("/dosen/mahasiswa/<id>/berada_di_kampus/<tanggal>", methods=["GET"])
@token_required_dosen
def dosen_mahasiswa_id_berada_di_kampus(id, tanggal):
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   


   got, nama, aktivitas, keterangan = loop.run_until_complete(ambil_berada_di_kampus(id, tanggal, True))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("dosen"))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("mahasiswa_berada_di_kampus_dosen.html", user=user, aktivitas=aktivitas, keterangan=keterangan, nama=nama, id=id, darkmode=darkmode)

@app.route("/dosen/mahasiswa/<id>/menghadiri_kegiatan/<tanggal>", methods=["GET"])
@token_required_dosen
def dosen_mahasiswa_id_menghadiri_kegiatan(id, tanggal):
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   

   got, nama, aktivitas, keterangan = loop.run_until_complete(ambil_menghadiri_kegiatan(id, tanggal, True))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("dosen"))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("mahasiswa_menghadiri_kegiatan_dosen.html", user=user, aktivitas=aktivitas, keterangan=keterangan, nama=nama, id=id, darkmode=darkmode)


@app.route("/dosen/jadwal/<id>", methods=["GET", "POST"])
@token_required_dosen
def jadwal(id):
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]

   if request.method == "POST":
      res = ubah_jadwal(request.form, id)

      if res:
         flash(f"Barhasil mengubah jadwal", "success")
      else:
         flash(f"Gagal mengubah jadwal", "danger")
      return redirect(url_for("jadwal", id=id))
   else:    
      got, jadwal, hasil = loop.run_until_complete(ambil_jadwal_dan_hasil(id))


      if not got:
         flash("URL tidak valid!", "danger")
         return redirect(url_for("dosen"))
   

   is_owner = user[2] == jadwal["nama_dosen"]
   gap = jadwal["mulai_dt"] - datetime.now()
   less_15 = False

   if gap.days < 0:
      less_15 = False
   else:
      less_15 = True

   editable = is_owner and less_15

   # Jika 15 menit
   ruangan = []
   if editable:
      ruangan = ambil_ruangan()
      for el in ruangan:
         del el["sedang_digunakan"]
         el["_id"] = str(el["_id"])

   jadwal["_id"] = str(jadwal["_id"])
   jadwal["dosen_id"] = str(jadwal["dosen_id"])
   jadwal["waktu_mulai"] = str(jadwal["waktu_mulai"])
   jadwal["waktu_selesai"] = str(jadwal["waktu_selesai"])
   jadwal["mulai_dt"] = str(jadwal["mulai_dt"])
   jadwal["tanggal"] = get_tanggal_2(str(jadwal["mulai_dt"]).split(" ")[0])
   jadwal["selesai_dt"] = str(jadwal["selesai_dt"])
   jadwal["ruangan_id"] = str(jadwal["ruangan_id"])
   jadwal["dosen_id"] = str(jadwal["dosen_id"])

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("jadwal.html", jadwal=jadwal, user=user, hasil=hasil, editable=editable, ruangan=ruangan, darkmode=darkmode)

@app.route("/hapus_jadwal/<id>", methods=["POST"])
@token_required_dosen
def hapusjadwal(id):
   data = hapus_jadwal(id)
   if data:
      flash(f"Barhasil menghapus jadwal", "success")
      return redirect(url_for("dosen", tanggal=data))
   else:
      flash(f"Gagal menghapus jadwal", "danger")
      return redirect(url_for("jadwal", id=id))

@app.route("/jadwal/<id>/<id_mhs>", methods=["GET"])
@token_required_dosen
def jadwal_mahasiswa(id, id_mhs):
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   hasil, keterangan = loop.run_until_complete(ambil_jadwal_dan_hasil_mhs(id, id_mhs))

   return render_template("room2.html", user=user, hasil=hasil, keterangan=keterangan)

@app.route("/profil/<pengguna>/<id>", methods=["GET"])
@token_required
def profil(id, pengguna):
   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]
   if pengguna == "mahasiswa":
      profil = loop.run_until_complete(find_mahasiswa_complete(id))
      if not profil:
         flash("URL tidak valid!", "danger")
         return redirect(url_for("mahasiswa"))
   elif pengguna == "dosen":
      profil = loop.run_until_complete(find_dosen_complete(id))
      if not profil:
         flash("URL tidak valid!", "danger")
         return redirect(url_for("dosen"))
   if pengguna == "orangtua":
      profil = loop.run_until_complete(find_orang_tua_complete(id))
      if not profil:
         flash("URL tidak valid!", "danger")
         return redirect(url_for("orang_tua"))


   print("profil: ", profil)
   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("profil.html", user=user, profil=profil, darkmode=darkmode)

@app.route("/mahasiswa", methods=["GET"])
@token_required_mahasiswa
def mahasiswa():
   user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]

   events, aktivitas_terakhir, my_aktivitas = loop.run_until_complete(cari_aktivitas_user(user_id, "mahasiswa"))

   foto_wajah, req_ortu = loop.run_until_complete(cari_foto_wajah(user_id))


   if not foto_wajah:
      link = url_for("mahasiswa_akun")
      flash(Markup(f"Wajah anda belum dapat dikenali oleh sistem! Segera tambahkan Foto Wajah pada halaman <a href='{link}' class='link-alert'>Akun</a>."), "warning")

   if req_ortu:
      link = url_for("mahasiswa_akun")
      flash(Markup(f"Anda memiliki permintaan penghubungan akun orang tua! Segera konfirmasi penerimaan akun orang tua pada halaman <a href='{link}' class='link-alert'>Akun</a>."), "warning")

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]


   return render_template("mahasiswa.html",events=events, user=user, aktivitas_terakhir=aktivitas_terakhir, my_aktivitas=my_aktivitas, darkmode=darkmode, foto_wajah=foto_wajah)

@app.route("/orangtua", methods=["GET"])
@token_required_orang_tua
def orang_tua():
   id_anak, nama_anak = loop.run_until_complete(cari_id_anak(user_id))

   if not id_anak:
      user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"]]
      req_id_anak, req_nama_anak = loop.run_until_complete(cari_req_id_anak(user_id))
      darkmode = ""
      if 'darkmode' in request.cookies:
         darkmode = request.cookies["darkmode"]
      if not req_id_anak:
         return render_template("orang_tua_reject.html", user=user, darkmode=darkmode)

      return render_template("orang_tua_pending.html", user=user, darkmode=darkmode, req_nama_anak=req_nama_anak, req_id_anak=req_id_anak)
      

   user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"], nama_anak, id_anak]

   events, aktivitas_terakhir, my_aktivitas, pp_path = loop.run_until_complete(cari_aktivitas_user(id_anak, "orangtua"))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("orang_tua.html",events=events, user=user, aktivitas_terakhir=aktivitas_terakhir, my_aktivitas=my_aktivitas, darkmode=darkmode, pp_path=pp_path)

@app.route("/mahasiswa/berada_di_kampus/<tanggal>", methods=["GET"])
@token_required_mahasiswa
def mahasiswa_berada_di_kampus(tanggal):
   user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]

   got, aktivitas, keterangan = loop.run_until_complete(ambil_berada_di_kampus(user_id, tanggal, False))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("mahasiswa"))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("mahasiswa_berada_di_kampus.html", user=user, aktivitas=aktivitas, keterangan=keterangan, darkmode=darkmode)

@app.route("/orangtua/berada_di_kampus/<tanggal>", methods=["GET"])
@token_required_orang_tua
def orangtua_berada_di_kampus(tanggal):
   id_anak, nama_anak = loop.run_until_complete(cari_id_anak(user_id))

   user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"], nama_anak]

   got, aktivitas, keterangan = loop.run_until_complete(ambil_berada_di_kampus(id_anak, tanggal, False))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("orang_tua"))


   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("orang_tua_berada_di_kampus.html", user=user, aktivitas=aktivitas, keterangan=keterangan, nama_anak=nama_anak, darkmode=darkmode)

@app.route("/mahasiswa/menghadiri_kegiatan/<tanggal>", methods=["GET"])
@token_required_mahasiswa
def mahasiswa_menghadiri_kegiatan(tanggal):
   user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]

   got, aktivitas, keterangan = loop.run_until_complete(ambil_menghadiri_kegiatan(user_id, tanggal, False))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("mahasiswa"))


   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("mahasiswa_menghadiri_kegiatan.html", user=user, aktivitas=aktivitas, keterangan=keterangan, darkmode=darkmode)

@app.route("/orangtua/menghadiri_kegiatan/<tanggal>", methods=["GET"])
@token_required_orang_tua
def orangtua_menghadiri_kegiatan(tanggal):
   id_anak, nama_anak = loop.run_until_complete(cari_id_anak(user_id))

   user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"], nama_anak]

   got, aktivitas, keterangan = loop.run_until_complete(ambil_menghadiri_kegiatan(id_anak, tanggal, False))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("orang_tua"))


   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("orang_tua_menghadiri_kegiatan.html", user=user, aktivitas=aktivitas, keterangan=keterangan, nama_anak=nama_anak, darkmode=darkmode)

@app.route("/mahasiswa/aktivitas/<id>", methods=["GET"])
@token_required_mahasiswa
def mahasiswa_aktivitas(id):
   got, resp, aktivitas, keterangan = loop.run_until_complete(ambil_aktivitas_by_id(id, payload["user_id"], "mahasiswa"))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("mahasiswa"))

   if not resp:
      flash(aktivitas, "danger")
      return redirect(url_for("mahasiswa"))

   user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("mahasiswa_aktivitas_id.html", user=user, aktivitas=aktivitas, keterangan=keterangan, darkmode=darkmode)

@app.route("/orangtua/aktivitas/<id>", methods=["GET"])
@token_required_orang_tua
def orangtua_aktivitas(id):
   id_anak, nama_anak = loop.run_until_complete(cari_id_anak(user_id))

   got, resp, aktivitas, keterangan, nim, pp_path = loop.run_until_complete(ambil_aktivitas_by_id(id, id_anak, "orang tua"))

   if not got:
      flash("URL tidak valid!", "danger")
      return redirect(url_for("orang_tua"))

   if not resp:
      flash(aktivitas, "danger")
      return redirect(url_for("orang_tua"))

   user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"], nama_anak]

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("orangtua_aktivitas_id.html", user=user, aktivitas=aktivitas, keterangan=keterangan, nama_anak=nama_anak, darkmode=darkmode, pp_path=pp_path, nim=nim)


@app.route("/dosen/akun", methods=["GET", "POST"])
@token_required_dosen
def dosen_akun():
   if request.method == "POST":
      res_ubah, foto_profil_path, nama = loop.run_until_complete(ubah_data_akun(user_id, request.form, request.files, "dosen"))

      user = ["dosen", payload["username"], payload["nama"], payload["foto_profil"]]
      user_1 = loop.run_until_complete(find_dosen_complete(payload["user_id"]))

      darkmode = ""
      if 'darkmode' in request.cookies:
         darkmode = request.cookies["darkmode"]

      if res_ubah:
         flash(f"Data akun berhasil diubah.", "success")
      else:
         flash(f"Data akun gagal diubah.", "danger")

      resp = make_response(render_template("akun.html", user=user, user_1=user_1, darkmode=darkmode))

      if foto_profil_path:
         token_dict =  jwt.decode(request.cookies["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
         token_dict["foto_profil"] = foto_profil_path
         token_new = jwt.encode(token_dict, app.config["SECRET_KEY"], algorithm="HS256")
         resp.set_cookie("token", token_new)

      if nama:
         token_dict =  jwt.decode(request.cookies["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
         token_dict["nama"] = nama
         token_new = jwt.encode(token_dict, app.config["SECRET_KEY"], algorithm="HS256")
         resp.set_cookie("token", token_new)
      
      return resp

   user = ["dosen", payload["username"], payload["nama"], payload["foto_profil"]]
   user_1 = loop.run_until_complete(find_dosen_complete(payload["user_id"]))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("akun.html", user=user, user_1=user_1, darkmode=darkmode)


@app.route("/mahasiswa/akun", methods=["GET", "POST"])
@token_required_mahasiswa
def mahasiswa_akun():
   if request.method == "POST":
      res_ubah, foto_profil_path, nama = loop.run_until_complete(ubah_data_akun(user_id, request.form, request.files, "mahasiswa"))

      user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]
      user_1 = loop.run_until_complete(find_mahasiswa_complete(payload["user_id"]))

      user_1.pop("aktivitas_terakhir")

      darkmode = ""
      if 'darkmode' in request.cookies:
         darkmode = request.cookies["darkmode"]

      if res_ubah:
         flash(f"Data akun berhasil diubah.", "success")
      else:
         flash(f"Data akun gagal diubah.", "danger")

      resp = make_response(render_template("akun.html", user=user, user_1=user_1, darkmode=darkmode))

      if foto_profil_path:
         token_dict =  jwt.decode(request.cookies["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
         token_dict["foto_profil"] = foto_profil_path

         token_new = jwt.encode(token_dict, app.config["SECRET_KEY"], algorithm="HS256")
         resp.set_cookie("token", token_new)

      if nama:
         token_dict =  jwt.decode(request.cookies["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
         token_dict["nama"] = nama
         token_new = jwt.encode(token_dict, app.config["SECRET_KEY"], algorithm="HS256")
         resp.set_cookie("token", token_new)

      return resp

   user = ["mahasiswa", payload["username"], payload["nama"], payload["foto_profil"]]
   user_1 = loop.run_until_complete(find_mahasiswa_complete(payload["user_id"]))

   user_1.pop("aktivitas_terakhir")

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]
   
   return render_template("akun.html", user=user, user_1=user_1, darkmode=darkmode, url=url_for("mahasiswa_akun"))


@app.route("/mahasiswa/hapus_foto_wajah", methods=["POST"])
@token_required_mahasiswa
def hapus_foto_wajah():
   loop.run_until_complete(hapus_foto_wajah_mhs(user_id, request.form["file_path"], request.form["index"]))
   flash(f"Foto wajah berhasil dihapus.", "success")
   return redirect(url_for("mahasiswa_akun"))


@app.route("/orangtua/akun", methods=["GET", "POST"])
@token_required_orang_tua
def orang_tua_akun():
   if request.method == "POST":
      res_ubah, foto_profil_path, nama = loop.run_until_complete(ubah_data_akun(user_id, request.form, request.files, "orang_tua"))

      user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"]]
      user_1 = loop.run_until_complete(find_orang_tua_complete(payload["user_id"]))

      user_1["anak_select"] = loop.run_until_complete(ambil_choices_akun_mhs_2(payload["user_id"]))

      darkmode = ""
      if 'darkmode' in request.cookies:
         darkmode = request.cookies["darkmode"]

      if res_ubah:
         flash(f"Data akun berhasil diubah.", "success")
      else:
         flash(f"Data akun gagal diubah.", "danger")
      
      resp = make_response(render_template("akun.html", user=user, user_1=user_1, darkmode=darkmode))

      if foto_profil_path:
         token_dict =  jwt.decode(request.cookies["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
         token_dict["foto_profil"] = foto_profil_path
         # jwt.decode()
         token_new = jwt.encode(token_dict, app.config["SECRET_KEY"], algorithm="HS256")
         resp.set_cookie("token", token_new)

      if nama:
         token_dict =  jwt.decode(request.cookies["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
         token_dict["nama"] = nama
         token_new = jwt.encode(token_dict, app.config["SECRET_KEY"], algorithm="HS256")
         resp.set_cookie("token", token_new)

      return resp

   user = ["orang_tua", payload["username"], payload["nama"], payload["foto_profil"]]
   user_1 = loop.run_until_complete(find_orang_tua_complete(payload["user_id"]))
   print("user_1: ", user_1)
   user_1["anak_select"] = loop.run_until_complete(ambil_choices_akun_mhs_2(payload["user_id"]))

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]


   return render_template("akun.html", user=user, user_1=user_1, darkmode=darkmode)

@app.route("/uploadgambarwajah", methods=["POST"])
def uploadgambarwajah():
   if 'file' not in request.files:
      return jsonify({"error": "No file uploaded"}), 400

   file = request.files['file']
   
   if file.filename == '':
      return jsonify({"error": "No file selected"}), 400

   # Save file to the uploads folder
   file_path = os.path.join("static/pictures/identified", file.filename)
   file.save(file_path)

   return jsonify({"message": "Upload successful", "filename": file.filename, "path": file_path})

@app.route("/frame/<frame_id>", methods=["GET"])
def frame(frame_id):
   frame = loop.run_until_complete(ambil_frame(frame_id))
   if not frame:
      frame = {"frame": "", "ruangan_id": ""}
   frame["frame"] = base64.b64encode(frame["frame"]).decode("utf-8")
   frame["ruangan_id"] = str(frame["ruangan_id"])
   frame["jadwal_id"] = str(frame["jadwal_id"]) if frame["jadwal_id"] else ""
   frame["_id"] = str(frame["_id"])
   # print("frame: ", type(frame["frame"]))
   return jsonify(frame)
   # return Response(frame)

@app.route("/dosen/identifikasi/<frame_id>", methods=["GET"])
@token_required_dosen
def show_frame(frame_id):
   frame = loop.run_until_complete(ambil_frame(frame_id))
   if not frame:
      frame = {"frame": "", "ruangan_id": ""}
      ruangan = {}
   else:
      ruangan = loop.run_until_complete(ambil_ruangan_by_id(frame["ruangan_id"]))
      frame["frame"] = base64.b64encode(frame["frame"]).decode("utf-8")
      frame["ruangan_id"] = str(frame["ruangan_id"])
      frame["jadwal_id"] = str(frame["jadwal_id"]) if frame["jadwal_id"] else ""
      frame["_id"] = str(frame["_id"])

   user = [payload["pengguna"], payload["username"], payload["nama"], payload["foto_profil"]]

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template("frame.html", user=user,  darkmode=darkmode, frame=frame, ruangan=ruangan)


@app.errorhandler(404)
def page_not_found(e):

   darkmode = ""
   if 'darkmode' in request.cookies:
      darkmode = request.cookies["darkmode"]

   return render_template('404.html', darkmode=darkmode), 404

if __name__ == "__main__":
   app.run(debug=True, port=4000)