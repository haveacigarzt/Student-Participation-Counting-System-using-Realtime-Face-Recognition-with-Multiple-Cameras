from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, RadioField, FileField, EmailField
from wtforms.validators import DataRequired, Length
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

# db_uri = os.getenv('mongo_uri1')
# db_uri = os.getenv("mongodb_atlas_url")
db_uri = "mongodb+srv://afriandypramana:bczFDLSJSzrATKdP@cluster0.yqmayik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
   client = AsyncIOMotorClient(db_uri, server_api=ServerApi("1"))
   loop = client.get_io_loop()
except Exception:
   print("DB connection failed")
   sys.exit()

class LoginForm(FlaskForm):
   username = StringField(
      "Username", 
      validators=[DataRequired(), Length(min=3, max=15)],
      render_kw={"minlength": 3, "maxlength": 15}
   )
   password = PasswordField(
      "Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   pengguna = RadioField("Login sebagai?", choices=[('mahasiswa', 'Mahasiswa'), ('orang_tua', 'Orang tua'), ('dosen', 'Dosen')], validators=[DataRequired()])
   masuk = SubmitField("Masuk")

class DaftarFormMahasiswa(FlaskForm):
   nama = StringField(
      "Nama", 
      validators = [DataRequired(), Length(min=3, max=40)], 
      render_kw={"minlength": 3, "maxlength": 40}
   )
   nim = StringField(
      "NIM", 
      validators=[DataRequired(), Length(min=7, max=15)],
      render_kw={"minlength": 7, "maxlength": 15}
   )
   email = EmailField(
      "Email", 
      validators=[DataRequired(), Length(min=4)],
      render_kw={"minlength": 4}
   )
   username = StringField(
      "Username", 
      validators=[DataRequired(), Length(min=3, max=15)],
      render_kw={"minlength": 3, "maxlength": 15}
   )
   password = PasswordField(
      "Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   konfirmasi_password = PasswordField(
      "Konfirmasi Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   daftar = SubmitField("Kirim", validators=[DataRequired()])

class DaftarFormDosen(FlaskForm):
   nama = StringField(
      "Nama", 
      validators = [DataRequired(), Length(min=3, max=40)], 
      render_kw={"minlength": 3, "maxlength": 40}
   )
   nip = StringField(
      "NIP", 
      validators=[DataRequired(), Length(min=9, max=20)],
      render_kw={"minlength": 9, "maxlength": 20}
   )
   email = EmailField(
      "Email", 
      validators=[DataRequired(), Length(min=4)],
      render_kw={"minlength": 4}
   )
   username = StringField(
      "Username", 
      validators=[DataRequired(), Length(min=3, max=15)],
      render_kw={"minlength": 3, "maxlength": 15}
   )
   password = PasswordField(
      "Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   konfirmasi_password = PasswordField(
      "Konfirmasi Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   daftar = SubmitField("Kirim")

class DaftarFormOrangTua(FlaskForm):
   nama = StringField("Nama", validators=[DataRequired()])
   email = EmailField(
      "Email", 
      validators=[DataRequired(), Length(min=4)],
      render_kw={"minlength": 4}
   )
   username = StringField(
      "Username", 
      validators=[DataRequired(), Length(min=3, max=15)],
      render_kw={"minlength": 3, "maxlength": 15}
   )
   password = PasswordField(
      "Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   konfirmasi_password = PasswordField(
      "Konfirmasi Password", 
      validators=[DataRequired(), Length(min=3, max=20)],
      render_kw={"minlength": 3, "maxlength": 20}
   )
   daftar = SubmitField("Kirim")

class JadwalForm(FlaskForm):
   submit = SubmitField("Buat")