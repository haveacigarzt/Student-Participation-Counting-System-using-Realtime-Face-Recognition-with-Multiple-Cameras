from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from bson import ObjectId
from statistics import mean

# atlas_url = "mongodb://localhost:27017"

# temp_folder = "static/pictures/temp"
# foto_profil_folder = "static/pictures/foto_profil"
# foto_wajah_folder = "static/pictures/foto_wajah"

atlas_url = "mongodb+srv://afriandypramana:bczFDLSJSzrATKdP@cluster0.yqmayik.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(atlas_url, server_api=ServerApi("1"))
client2 = MongoClient(atlas_url)
loop = client.get_io_loop()

db = client2["face_identification_2"]
collection_aktivitas = db["aktivitas"]
collection_mahasiswa = db["mahasiswa"]

# collection_mahasiswa.update_many({}, {"$set": {"akun.email": "test@email.com"}})

# print(type(aktivitas["filler"]))

# aktivitas = collection_aktivitas.update_many({}, {"$set": {"filler": 20}})
berada_di_kampus = [0.058, 0.03, 0.068, 0.053, 0.043, 0.115, 0.111]
menghadiri_kegiatan = [0.016, 0.053, 0.0, 0.01, 0.012, 0.022, 0.02, 0.02]
res = []

# for x in range(8):
# while True:
#    a = float(input("A: "))
#    b = float(input("B: "))

#    c = abs(a - b)
#    print("c ", c)

#    d = (a + b) / 2
#    print("d ", d)
#    result = c / d

#    print(round(result, 3),"\n")

#    res.append(round(result, 3))

# print(res)

# li_1 = [5.832, 3.097, 6.366, 5.479, 4.259, 11.64, 11.053]
# li_2 = [1.796, 5.247, 0, 0.97, 1.227, 2.299, 2.062, 1.961]

# m_li_1 = round(mean([0.068, 0.019]), 3)
# m_li_2 = round(mean(li_2), 3)
# print(m_li_1)
# print(m_li_2)
# print(round(mean([m_li_1, m_li_2]), 3))
# print(round(mean([6.818, 1.954]), 3))

