const reveal_pass_btn = (target) => {
   let button;
   let input;
   let i_tag;

   if (target.localName == "button") {
      i_tag = target.firstElementChild;
      button = target;
      input = target.previousElementSibling;
   } else if (target.localName == "i") {
      i_tag = target;
      button = target.parentElement;
      input = target.parentElement.previousElementSibling;
   }
   if (i_tag.classList.contains("fa-eye-slash")) {
      input.removeAttribute("type", "password")
      input.setAttribute("type", "text")
   } else {
      input.removeAttribute("type", "text")
      input.setAttribute("type", "password")
   }
   i_tag.classList.toggle("fa-eye-slash")
   i_tag.classList.toggle("fa-eye")
}

function active_link_pembuat_jadwal(event) {
   event.target.querySelector("span").style.textDecoration = "underline"
}

function deactive_link_pembuat_jadwal(event) {
   event.target.querySelector("span").style.textDecoration = "none"
}

function ganti_mode(event) {
   let data
   if (event.target.checked) {
      data = "checked";
      document.body.classList.remove("darkmode-")
   } else {
      data = "";
      document.body.classList.add("darkmode-")
   }
   fetch('/ganti_mode', {
      method: 'POST',  // HTTP method
      headers: {
         'Content-Type': 'application/json',  // Indicate that we're sending JSON
      },
      body: JSON.stringify(data),  // Convert the data to a JSON string
   })
      .then(response => response.json())  // Parse the JSON response
      .then(data => console.log('Success:', data))  // Handle the response
      .catch(error => console.error('Error:', error));  // Handle errors
}

function buka_navbar() {
   console.log("navbar dibuka")
}

const pass_input = document.querySelectorAll(".password_input")
const button = document.getElementById("daftar")
const progress_daftar = document.getElementById("progress_daftar")
const konf_pass_input = document.getElementById("konf_pass_input")

if (pass_input.length > 0) {
   const alert = document.getElementById("alert_konfirmasi_password")
   pass_input.forEach(input => {

      input.addEventListener("keyup", () => {
         let data = []
         pass_input.forEach(input => {
            data.push(input.value);
         })

         if (data[1] !== '') {
            if (data[0] != data[1]) {
               alert.classList.remove("d-none")
               konf_pass_input.classList.add("alert-input-danger");
               button.disabled = true
            } else {
               alert.classList.add("d-none")
               konf_pass_input.classList.remove("alert-input-danger");
               button.disabled = false
            }
         } else {
            alert.classList.add("d-none")
            konf_pass_input.classList.remove("alert-input-danger");
            button.disabled = false
         }
      })
   })
}

const url = document.URL.split("/")
let page = url[url.length - 1]

function input_username(target) {
   const alert_username = document.getElementById("alert_username")
   if (target.value.includes(" ")) {
      alert_username.classList.remove("d-none");
      alert_username.classList.add("d-block");
      target.classList.add("alert-input-danger");
      // console.log("String contains a space!");
   } else {
      alert_username.classList.remove("d-block");
      alert_username.classList.add("d-none");
      target.classList.remove("alert-input-danger");

   }
}


const edit_konten_navbar_links = document.querySelectorAll("#main_nav .nav-link")

if (page) {
   edit_konten_navbar_links.forEach(link => {
      if (link.dataset.value == page) {
         link.classList.add("active")
      } else {
         link.classList.remove("active")
      }
   })
}

function loadFile(event) {
   const files = event.target.files
   const form = event.target.parentElement.parentElement;
   const output = form.querySelectorAll('img.output-image');
   const output_row = output[0].parentElement.parentElement;
   const alert_gambar = form.querySelector("#alert_gambar");

   if (files.length > 0) {
      output_row.classList.add("mb-3")
   } else {
      output_row.classList.remove("mb-3")
   }

   for (let i = 0; i < output.length; i++) {
      output[i].parentElement.classList.add("d-none")
      output[i].src = ''
   }

   if (files.length > 3) {
      alert_gambar.classList.remove("d-none")
      button.disabled = true
      output_row.classList.remove("mb-3")
   } else {
      button.disabled = false
      alert_gambar.classList.add("d-none")
      for (let i = 0; i < files.length; i++) {
         output[i].parentElement.classList.remove("d-none")
         output[i].src = URL.createObjectURL(files[i])
      }
   }

};

function loadFileDosen(event) {
   const file = event.target.files[0]
   const form = event.target.parentElement.parentElement;
   const output = form.querySelector('img#output-image');
   const output_row = output.parentElement.parentElement;

   // if (file.size > 1048576) {
   //    alert("File terlalu besar! (Max. 1MB)");
   //    event.target.value = "";
   //    output_row.classList.remove("mb-3")
   //    output.parentElement.classList.add("d-none")
   //    output.src = ""
   //    return false;
   // }

   output_row.classList.add("mb-3")
   output.parentElement.classList.remove("d-none")
   output.src = URL.createObjectURL(file)

};

function loadFileAkunMhs(event) {
   const file = event.target.files[0]
   const output = event.target.parentElement.querySelector('.output-image');

   if (file.size > 5048576) {
      alert("Ukuran file terlalu besar! (Max. 5MB)");
      return false;
   }

   try {
      output.src = URL.createObjectURL(file)
   } catch (error) {
      output.src = ""
   }

};

function tambahFileAkunMhs(event) {
   const file = event.target.files[0]
   const output = event.target.parentElement.querySelector('.output-image');

   if (file.size > 5048576) {
      alert("Ukuran file terlalu besar! (Max. 5MB)");
      return false;
   }

   output.parentElement.parentElement.classList.remove("d-none")

   try {
      output.src = URL.createObjectURL(file)
   } catch (error) {
      output.src = ""
   }

   const containerFotosAkun = document.getElementById("containerFotosAkun");
   const tambah_div_kosong_label = document.getElementById("tambah_div_kosong_label");
   const indexToAppend = containerFotosAkun.childElementCount;
   tambah_div_kosong_label.setAttribute("for", `file_${indexToAppend}`)

};

function gantiInput(user_1, url, pengguna, url_hapus) {
   const data = JSON.stringify(user_1)
   const form_div = document.getElementById("form_div")
   if (pengguna == "mahasiswa") {
      let foto_row = ``
      let i = 0
      for (let el of user_1['foto']) {
         foto_row += `
         <div class="col-4 col-lg-3">
            <img src="/${el}" style="aspect-ratio: 1/1;" alt="" class="w-100 mb-2" srcset="">
            <div action="${url_hapus}" class="mb-3">
               <button title="Hapus foto" data-bs-toggle="modal" data-bs-target="#delete_wajah_${i}" class="d-block mx-auto btn btn-danger"><i class="fas fa-trash"></i></button>
            </div>
         </div>
         <div class="modal fade" id="delete_wajah_${i}" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-md mx-auto my-4">
               <div class="modal-content px-3 py-2 mx-auto">
                  <div class="modal-body">
                     <h5 class="mb-4 mt-2 pb-1 border-1 border-bottom border-black">Konfirmasi hapus</h5>
                     <div>
                        <img style="aspect-ratio: 1/1;" src="/${el}" alt="" class="w-100 mb-2" srcset="">
                        <p class="text-center">Hapus data wajah ini?</p>
                     </div>
                     <form action="${url_hapus}" method="post" class="mt-2">
                        <input name="file_path" type="hidden" value="${el}">
                        <input name="index" type="hidden" value="${i}">
                        <div class="d-flex justify-content-evenly mt-4">
                           <button type="button" class="btn  btn-secondary px-2 py-1 shadow-sm h5 mb-0" data-bs-dismiss="modal">Batal</button>
                           <button type="submit" class="btn btn-success btn-card px-3 py-1 shadow-sm h5 mb-0">Ya</button>
                        </div>
                     </form>
                  </div>
               </div>
            </div>
         </div>
         `
         i++
      }
      let warning_no_foto = ``
      if (!foto_row) {
         warning_no_foto += `
            <i class="fas fa-triangle-exclamation mt-1 ms-2 text-warning"></i>
         `
      }
      let warning_akun_ortu = ``
      let orang_tua = ``
      if (user_1["orang_tua"]) {
         orang_tua = `
         <p>
            <a href="{{url_for('profil', id=${user_1['id_orang_tua']})}}">
               ${user_1["orang_tua"]}
            </a>
         </p>`

      } else {
         orang_tua = `<p>-</p>`
         if (user_1["req_orang_tua"].length) {
            orang_tua = `<p>- (<i>Menunggu konfirmasi</i>)</p>`
            warning_akun_ortu = `
               <i class="fas fa-triangle-exclamation mt-1 ms-2 text-warning" title="Harap melakukan konfirmasi akun orang tua"></i>
            `
         }
      }
      form_div.innerHTML = `
      <div class="col-11 px-0 px-lg-2">
         <div class="row m-0">
            <div class="col-4">
               <p>Nama</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["nama"]}</p>
            </div>
            <div class="col-4">
               <p>Jenis Pengguna</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["pengguna"]}</p>
            </div>
            <div class="col-4">
               <p>Username</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["username"]}</p>
            </div>
            <div class="col-4">
               <p>Email</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["email"]}</p>
            </div>
            <div class="col-4">
               <p>NIM</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["nim"]}</p>
            </div>
            <div class="col-4">
               <p>Akun Orang Tua ${warning_akun_ortu}</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               ${orang_tua}
            </div>
            <div class="col-4 align-self-center">
               <p>Foto Profil</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <div class="row">
                  <div class="col-7 col-lg-5">
                     <img src="/${user_1['foto_profil']}" alt="" class="w-100 mb-2 cursor-pointer" srcset="" data-bs-toggle="modal" data-bs-target="#modal_profile_pic">
                  </div>
               </div>
            </div>
            <div class="col-4 d-flex">
               <p>Foto Wajah</p>
               ${warning_no_foto}
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               ${warning_no_foto ? "<p>-</p>" : ""}
            </div>
            <div class="row">
               ${foto_row}
            </div>
         </div>
      </div>
      <button class="btn btn-warning shadow col-1 align-self-start p-2" id="button_edit" title="Ubah data" onclick='gantiInput2(${data}, ${JSON.stringify(url)}, ${JSON.stringify(pengguna)}, ${JSON.stringify(url_hapus)})'" ><i class="fa-solid fa-pen-to-square"></i></button>
      <div class="modal fade" id="modal_profile_pic" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
         <div class="modal-dialog modal-dialog-konfirmasi mx-auto my-4">
            <div class="modal-content p-2 mx-auto">
               <div class="modal-body d-flex flex-column">
                  <img src="/${user_1['foto_profil']}">
                  <button type="button" class="btn  btn-secondary px-2 py-1 shadow-sm h5 mb-0 mx-auto mt-2" data-bs-dismiss="modal">Tutup</button>
               </div>
            </div>
         </div>
      </div>
      `
   } else if (pengguna == "dosen") {
      form_div.innerHTML = `
      <div class="col-11 px-0 px-lg-2">
         <div class="row m-0">
            <div class="col-4">
               <p>Nama</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["nama"]}</p>
            </div>
            <div class="col-4">
               <p>Jenis Pengguna</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["pengguna"]}</p>
            </div>
            <div class="col-4">
               <p>Username</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["username"]}</p>
            </div>
            <div class="col-4">
               <p>Email</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["email"]}</p>
            </div>
            <div class="col-4">
               <p>NIP</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["nip"]}</p>
            </div>
            <div class="col-4 align-self-center">
               <p>Foto Profil</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <div class="row">
                  <div class="col-7 col-lg-5">
                     <img src="/${user_1['foto_profil']}" alt="" class="w-100 mb-2 cursor-pointer" srcset="" data-bs-toggle="modal" data-bs-target="#modal_profile_pic">
                  </div>
               </div>
            </div>
         </div>
      </div>
      <button class="btn btn-warning shadow col-1 align-self-start p-2" id="button_edit" title="Ubah data" onclick='gantiInput2(${data}, ${JSON.stringify(url)}, ${JSON.stringify(pengguna)})'" ><i class="fa-solid fa-pen-to-square"></i></button>
      <div class="modal fade" id="modal_profile_pic" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
         <div class="modal-dialog modal-dialog-konfirmasi mx-auto my-4">
            <div class="modal-content p-2 mx-auto">
               <div class="modal-body d-flex flex-column">
                  <img src="/${user_1['foto_profil']}">
                  <button type="button" class="btn  btn-secondary px-2 py-1 shadow-sm h5 mb-0 mx-auto mt-2" data-bs-dismiss="modal">Tutup</button>
               </div>
            </div>
         </div>
      </div>
      `
   } else if (pengguna == "orang_tua") {
      let anakHTML = ""
      let waring_akun_anak = ""
      if (user_1["anak"] != "-") {
         anakHTML = `
         <a href="/profil/mahasiswa/${user_1["id_anak"]}">
            ${user_1["anak"]}
         </a>`;
      } else {
         waring_akun_anak = `<i class="fas fa-triangle-exclamation mt-1 ms-2 text-warning" title="Harap memilih akun anak"></i>`
         if (user_1['req_id_anak']) {
            anakHTML = `
            <i>Menunggu konfirmasi oleh <a href="/profil/mahasiswa/${user_1['req_id_anak']}">${user_1["req_anak"]}</a></i>`
         } else {
            anakHTML = `-`
         }
      }
      form_div.innerHTML = `
      <div class="col-11 px-0 px-lg-2">
         <div class="row m-0">
            <div class="col-4">
               <p>Nama</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["nama"]}</p>
            </div>
            <div class="col-4">
               <p>Jenis Pengguna</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["pengguna"]}</p>
            </div>
            <div class="col-4">
               <p>Username</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["username"]}</p>
            </div>
            <div class="col-4">
               <p>Email</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>${user_1["email"]}</p>
            </div>
            <div class="col-4">
               <p>Akun Anak ${waring_akun_anak}</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <p>
                  ${anakHTML}
               </p>
            </div>
            <div class="col-4 align-self-center">
               <p>Foto Profil</p>
            </div>
            <div class="col-1 px-0 align-self-center">
               <p class="text-end">:</p>
            </div>
            <div class="col-7 align-self-center">
               <div class="row">
                  <div class="col-7 col-lg-5">
                     <img src="/${user_1['foto_profil']}" alt="" class="w-100 mb-2 cursor-pointer" srcset="" data-bs-toggle="modal" data-bs-target="#modal_profile_pic">
                  </div>
               </div>
            </div>
         </div>
      </div>
      <button class="btn btn-warning shadow col-1 align-self-start p-2" id="button_edit" title="Ubah data" onclick='gantiInput2(${data}, ${JSON.stringify(url)}, ${JSON.stringify(pengguna)})'" ><i class="fa-solid fa-pen-to-square"></i></button>
      <div class="modal fade" id="modal_profile_pic" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
         <div class="modal-dialog modal-dialog-konfirmasi mx-auto my-4">
            <div class="modal-content p-2 mx-auto">
               <div class="modal-body d-flex flex-column">
                  <img src="/${user_1['foto_profil']}">
                  <button type="button" class="btn  btn-secondary px-2 py-1 shadow-sm h5 mb-0 mx-auto mt-2" data-bs-dismiss="modal">Tutup</button>
               </div>
            </div>
         </div>
      </div>
      `
   }
};

function gantiInput2(user_1, url, pengguna, url_hapus) {
   const data = JSON.stringify(user_1)
   const form_div = document.getElementById("form_div")
   if (pengguna == "mahasiswa") {
      let foto_row = ``
      let i = 0
      for (let el of user_1['foto']) {
         foto_row += `
         <div class="col-4 col-lg-3 pb-3">
            <div class="container-foto-akun pb-1">
               <img src="/${el}" style="aspect-ratio: 1/1;" alt="" class="w-100 display-foto-akun output-image" srcset="">
               <label for="file_${i}" class="label-foto-akun">Ganti</label>
               <input accept="image/jpeg" value="${el}" type="file" name="file_${i}" id="file_${i}" class="input-foto-akun" onchange="loadFileAkunMhs(event)">
            </div>
         </div>
      `
         i++
      }
      ortuHTML = ``
      if (user_1["orang_tua"]) {
         ortuHTML = ``
      }
      else if (user_1["req_orang_tua"].length) {
         let ortuindex = 1
         ortuHTML_in = `
            <div class="form-check">
               <input class="form-check-input" type="radio" name="akunortu" id="akunortu0" value="" checked>
               <label class="form-check-label" for="akunortu0">
                  Abaikan
               </label>
            </div>`
         for (const el of user_1["req_orang_tua"]) {
            ortuHTML_in += `
            <div class="form-check">
               <input class="form-check-input" type="radio" name="akunortu" id="akunortu${ortuindex}" value="${el['_id']} ${el['nama']}">
               <label class="form-check-label" for="akunortu${ortuindex}">
                  Konfirmasi: ${el["nama"]} (<a href="/profil/orangtua/${el['_id']}">lihat</a>)
               </label>
            </div>
            `
            ortuindex += 1;
         }
         ortuHTML = `
         <div class="border border-1 rounded mb-3 py-2">
            <div class="mb-2">
               <label for="akun_ortu" class="form-label mb-0">Pengajuan Akun Orang Tua</label>
            </div>
            ${ortuHTML_in}
         </div>
         `
      }
      form_div.innerHTML = `
      <div class="col-11 px-0 px-lg-2">
         <form action="${url}" id="form_mhs" method="post" class="row m-0 align-items-center" onsubmit="return submitAkunMahasiswa(event)" enctype="multipart/form-data">
            <div class="col-4 mb-3">
               <label for="akun_nama" class="form-label mb-0">Nama</label>
            </div>
            <div class="col-8 mb-3">
               <input required type="text" class="form-control" id="akun_nama" name="nama" value="${user_1['nama']}">
            </div>
            <div class="col-4 mb-3">
               <label for="email_pengguna" class="form-label mb-0">Email</label>
            </div>
            <div class="col-8 mb-3">
               <input type="email" name="email" class="form-control" id="email_pengguna" value="${user_1['email']}">
            </div>
            <div class="col-4 mb-3">
               <label for="akun_nim" class="form-label mb-0">NIM</label>
            </div>
            <div class="col-8 mb-3">
               <input required type="text" class="form-control" id="akun_nim" name="nim" value="${user_1['nim']}">
            </div>
            ${ortuHTML}
            <div class="col-4">
               <p>Foto Profil <br><small>(.jpg/.jpeg max. 5MB)</small></p>
            </div>
            <div class="col-8 mb-3">
               <div class="row">
                  <div class="col-7 col-lg-5">
                     <div class="container-foto-akun pb-1 d-flex">
                        <img src="/${user_1['foto_profil']}" alt="" class="w-100 display-foto-akun output-image" srcset="">
                        <label for="foto_profil" class="btn btn-secondary align-self-center ms-3" title="Ganti foto profil">Ganti</label>
                        <input accept="image/jpeg" type="file" name="foto_profil" id="foto_profil" class="input-foto-akun" onchange="loadFileAkunMhs(event)">
                     </div>
                  </div>
               </div>
            </div>
            <div class="col-4 mb-3">
               <p class="mb-0">Foto Wajah <br><small>(.jpg/.jpeg max. 5MB)</small></p>
            </div>
            <div class="col-7 mb-3">
               <label id="tambah_div_kosong_label" for="file_${i}" class="btn btn-secondary" onclick="tambahDivKosong()" title="Tambah foto wajah">
                  <i class="fas fa-plus"></i>
               </label>
            </div>
            <div class="row" id="containerFotosAkun">
               ${foto_row}
            </div>
            <div class="d-flex justify-content-center mt-3">
               <button type="submit" class="btn btn-primary mb-2 ms-3">Simpan</button>
            </div>
         </form>
      </div>
      <button class="btn btn-danger shadow col-1 align-self-start p-2" id="button_exit" title="Batal" onclick='gantiInput(${data}, ${JSON.stringify(url)}, ${JSON.stringify(pengguna)}, ${JSON.stringify(url_hapus)})'><i class="fas fa-times"></i></button>
      `
   } else if (pengguna == "dosen") {
      form_div.innerHTML = `
      <div class="col-11 px-0 px-lg-2">
         <form action="${url}" method="post" class="row m-0 align-items-center" enctype="multipart/form-data">
            <div class="col-4 mb-3">
               <label for="akun_nama" class="form-label mb-0">Nama</label>
            </div>
            <div class="col-8 mb-3">
               <input required type="text" class="form-control" id="akun_nama" name="nama" value="${user_1['nama']}">
            </div>
            <div class="col-4 mb-3">
               <label for="email_pengguna" class="form-label mb-0">Email</label>
            </div>
            <div class="col-8 mb-3">
               <input type="email" name="email" class="form-control" id="email_pengguna" value="${user_1['email']}">
            </div>
            <div class="col-4 mb-3">
               <label for="akun_nip" class="form-label mb-0">NIP</label>
            </div>
            <div class="col-8 mb-3">
               <input required type="text" class="form-control" id="akun_nip" name="nip" value="${user_1['nip']}">
            </div>
            <div class="col-4">
               <p>Foto Profil</p>
            </div>
            <div class="col-8 mb-3">
               <div class="row">
                  <div class="col-7 col-lg-5">
                     <div class="container-foto-akun pb-1 d-flex">
                        <img src="/${user_1['foto_profil']}" alt="" class="w-100 display-foto-akun output-image" srcset="">
                        <label for="foto_profil" class="btn btn-secondary align-self-center ms-3" title="Ganti foto profil">Ganti</label>
                        <input accept="image/jpeg" type="file" name="foto_profil" id="foto_profil" class="input-foto-akun" onchange="loadFileAkunMhs(event)">
                     </div>
                  </div>
               </div>
            </div>
            <div class="d-flex justify-content-center mt-3">
               <button type="submit" class="btn btn-primary mb-2 ms-3">Simpan</button>
            </div>
         </form>
      </div>
      <button class="btn btn-danger shadow col-1 align-self-start p-2" id="button_exit" title="Batal" onclick='gantiInput(${data}, ${JSON.stringify(url)}, ${JSON.stringify(pengguna)})'><i class="fas fa-times"></i></button>
      `
   } else if (pengguna == "orang_tua") {
      let optionHTML = ``
      let option_list = ``
      if (user_1["anak"] == "-" && user_1["req_anak"] == "") {
         // console.log(user_1["req_anak"].toLowerCase())
         option_list += `
            <option value="">-</option>
         `
         for (let el of user_1["anak_select"]) {
            option_list += `
               <option value="${el[0]} ${el[1]}" >${el[1]}</option>
            `
         }
         optionHTML = `
            <div class="col-4 mb-3">
               <label for="akun_anak" class="form-label mb-0">Akun Anak</label>
            </div>
            <div class="col-8 mb-3">
               <select name="akun_anak" class="form-select" id="akun_anak">
                  ${option_list}
               </select>
            </div>`;
      }

      form_div.innerHTML = `
      <div class="col-11 px-0 px-lg-2">
         <form action="${url}" id="form_ortu" method="post" class="row m-0 align-items-center" enctype="multipart/form-data" onsubmit="return submitAkunOrtu(event)">
            <div class="col-4 mb-3">
               <label for="akun_nama" class="form-label mb-0">Nama</label>
            </div>
            <div class="col-8 mb-3">
               <input required type="text" class="form-control" id="akun_nama" name="nama" value="${user_1['nama']}">
            </div>
            <div class="col-4 mb-3">
               <label for="email_pengguna" class="form-label mb-0">Email</label>
            </div>
            <div class="col-8 mb-3">
               <input type="email" name="email" class="form-control" id="email_pengguna" value="${user_1['email']}">
            </div>
            ${optionHTML}
            <div class="col-4">
               <p>Foto Profil</p>
            </div>
            <div class="col-8 mb-3">
               <div class="row">
                  <div class="col-7 col-lg-5">
                     <div class="container-foto-akun pb-1 d-flex">
                        <img src="/${user_1['foto_profil']}" alt="" class="w-100 display-foto-akun output-image" srcset="">
                        <label for="foto_profil" class="btn btn-secondary align-self-center ms-3" title="Ganti foto profil">Ganti</label>
                        <input accept="image/jpeg" type="file" name="foto_profil" id="foto_profil" class="input-foto-akun" onchange="loadFileAkunMhs(event)">
                     </div>
                  </div>
               </div>
            </div>
            <div class="d-flex justify-content-center mt-3">
               <button type="submit" class="btn btn-primary mb-2 ms-3">Simpan</button>
            </div>
         </form>
      </div>
      <button class="btn btn-danger shadow col-1 align-self-start p-2" id="button_exit" title="Batal" onclick='gantiInput(${data}, ${JSON.stringify(url)}, ${JSON.stringify(pengguna)})'><i class="fas fa-times"></i></button>
      `
   }
};

function gantiInput3(mydata, ruangan) {
   console.log(mydata)
   console.log(ruangan)

   const data = JSON.stringify(mydata)
   const ruangs = JSON.stringify(ruangan)
   const form_div = document.getElementById("form_div")
   const button_div = document.getElementById("button_div")
   const title_jadwal_kegiatan = document.getElementById("title_jadwal_kegiatan")

   title_jadwal_kegiatan.textContent = "Ubah Jadwal Kegiatan"

   let mulai_dt = new Date(mydata["mulai_dt"])
   mulai_dt = String(mydata["mulai_dt"]).split(" ").join("T")
   let selesai_dt = new Date(mydata["selesai_dt"])
   selesai_dt = String(mydata["selesai_dt"]).split(" ").join("T")


   button_div.innerHTML = `<button class="btn btn-secondary shadow-sm m-1" id="button_exit" title="Batal" onclick='gantiInput4(${data}, ${ruangs})'><i class="fas fa-times"></i></button>`

   let options_ruang = ""

   for (const ruang of ruangan) {
      const ruang_str = `${ruang["kode_ruangan"]} - ${ruang["nama_ruangan"]}`
      if (mydata["ruangan"] == ruang_str) {
         options_ruang += `<option value="${ruang['kode_ruangan']} - ${ruang['nama_ruangan']}" selected>${ruang['kode_ruangan']} - ${ruang['nama_ruangan']}</option>`
      } else {
         options_ruang += `<option value="${ruang['kode_ruangan']} - ${ruang['nama_ruangan']}">${ruang['kode_ruangan']} - ${ruang['nama_ruangan']}</option>`
      }
   }

   console.log(options_ruang)


   form_div.innerHTML = `
      <form action="/dosen/jadwal/${mydata["_id"]}" method="post" class="row m-0 px-0 align-items-center">
         <div class="col-4 mb-3">
            <label for="nama_kegiatan" class="form-label mb-0">Kegiatan</label>
         </div>
         <div class="col-8 mb-3">
            <input type="text" class="form-control" id="nama_kegiatan" name="nama_kegiatan" required value="${mydata['nama_kegiatan']}">
         </div>
         <div class="col-4 mb-3">
            <label for="ruangan_kegiatan" class="form-label mb-0">Ruangan</label>
         </div>
         <div class="col-8 mb-3">
            <select class="form-select" id="ruangan_kegiatan" name="ruangan_kegiatan" aria-label="Default select example" required onchange="ganti_ruangan(event)">
               ${options_ruang}
            </select>
         </div>
         <div class="col-4 mb-3">
            <label for="waktu_mulai" class="form-label mb-0">Waktu Mulai</label>
         </div>
         <div class="col-8 mb-3">
            <input type="datetime-local" class="form-control" id="waktu_mulai" name="waktu_mulai" required onchange="cek_waktu_selesai_2(event)" value="${mulai_dt}">
            <input type="datetime-local" class="d-none form-control" name="waktu_mulai_old" required value="${mulai_dt}">
         </div>
         <div class="col-4 mb-3">
            <label for="waktu_selesai" class="form-label mb-0">Waktu Selesai</label>
         </div>
         <div class="col-8 mb-3">
            <input type="datetime-local" class="form-control" id="waktu_selesai" name="waktu_selesai" required onchange="cek_waktu_mulai_2(event)" value="${selesai_dt}">
         </div>
         <div class="col-4 mb-3">
            <label for="keterangan" class="form-label mb-0 for="keterangan"">Keterangan</label>
         </div>
         <div class="col-8 mb-3">
            <textarea required type="text" class="form-control" name="keterangan" id="keterangan">${mydata["keterangan"]}</textarea>
         </div>
         <div class="d-flex justify-content-center mt-2">
            <button type="submit" id="button_submit" class="btn btn-primary">Simpan</button>
         </div>
      </form>
      <div class="d-flex justify-content-center py-3">
         <button type="button" data-bs-toggle="modal" data-bs-target="#delete_jadwal" class="btn btn-danger">Hapus</button>
      </div>
      <form method="post" id="form_hapus_jadwal" class="py-3">
      </form>
      <div class="modal fade" id="delete_jadwal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
         <div class="modal-dialog modal-md mx-auto my-4">
            <div class="modal-content px-3 py-2 mx-auto">
               <div class="modal-body">
                  <h5 class="mb-4 mt-2 pb-1 border-1 border-bottom border-black">Konfirmasi hapus</h5>
                  <div>
                     <p class="text-center">Hapus data jadwal ini?</p>
                  </div>
                  <form action="/hapus_jadwal/${mydata["_id"]}" method="post" class="mt-2">
                     <div class="d-flex justify-content-evenly mt-4">
                        <button type="button" class="btn  btn-secondary px-2 py-1 shadow-sm h5 mb-0" data-bs-dismiss="modal">Batal</button>
                        <button type="submit" class="btn btn-success btn-card px-3 py-1 shadow-sm h5 mb-0">Ya</button>
                     </div>
                  </form>
               </div>
            </div>
         </div>
      </div>
   `
};

function gantiInput4(mydata, ruangan) {
   const data = JSON.stringify(mydata)
   const ruangs = JSON.stringify(ruangan)
   const form_div = document.getElementById("form_div")
   const button_div = document.getElementById("button_div")
   const title_jadwal_kegiatan = document.getElementById("title_jadwal_kegiatan")

   // console.log("mydata: ", mydata)

   title_jadwal_kegiatan.textContent = "Jadwal Kegiatan"
   console.log(mydata["_id"], data, form_div)
   button_div.innerHTML = `<button class="btn btn-warning shadow-sm m-1" onclick='gantiInput3(${data}, ${ruangs})' title='Ubah Jadwal'><i class="fa-solid fa-pen-to-square"></i></button>`
   form_div.innerHTML = `
      <div class="col-5 col-lg-4 form-div-top-left">Kegiatan</div>
      <div class="col-7 col-lg-8 form-div-top-right">${mydata["nama_kegiatan"]}</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Ruangan</div>
      <div class="col-7 col-lg-8 form-div-mid-right">${mydata["ruangan"]}</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Tanggal</div>
      <div class="col-7 col-lg-8 form-div-mid-right">${mydata["tanggal"]}</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Waktu Mulai</div>
      <div class="col-7 col-lg-8 form-div-mid-right">${mydata["mulai"]} WIB</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Waktu Selesai</div>
      <div class="col-7 col-lg-8 form-div-mid-right">${mydata["selesai"]} WIB</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Durasi Kegiatan</div>
      <div class="col-7 col-lg-8 form-div-mid-right">${mydata["durasi"]} (J:MM:DD)</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Keterangan</div>
      <div class="col-7 col-lg-8 form-div-mid-right">${mydata["keterangan"]}</div>
      <div class="col-5 col-lg-4 form-div-mid-left">Pembuat Jadwal</div>
      <div class="col-7 col-lg-8 form-div-mid-right">
         <a href="/profil/dosen/${mydata["dosen_id"]}" class="link-pembuat-jadwal" onmouseenter="active_link_pembuat_jadwal(event)" onmouseleave="deactive_link_pembuat_jadwal(event)">
            <img src="/${mydata['foto_profil_path']}" style="border-radius: 50%; object-fit:cover; width:30px; height:30px; margin-right: 2px;" alt="">
            <span>
               ${mydata["nama_dosen"]}
            </span>
         </a>
      </div>
   `
}

function submitAkunMahasiswa(event) {
   const akunortu = event.target.querySelector('input[name="akunortu"]:checked');
   if (akunortu) {
      if (akunortu.value) {
         event.preventDefault(); // Prevent default form submission
         const text_modalKonfirmasiAkunOrtu = document.getElementById("text_modalKonfirmasiAkunOrtu")
         let nama = akunortu.value.split(" ")
         nama.shift()
         nama = nama.join(" ")
         text_modalKonfirmasiAkunOrtu.textContent = `Apakah anda yakin untuk mengonfirmasi penerimaan akun orang tua atas nama ${nama}? (Perubahan ini hanya dapat dilakukan sekali)`
         const modalEl = document.getElementById("modalKonfirmasiAkunOrtu");
         const modal = new bootstrap.Modal(modalEl);
         modal.show();
      }
   }

}

function submitAkunOrtu(event) {
   const akun_anak = event.target.querySelector('select[name="akun_anak"]');
   if (akun_anak) {
      if (akun_anak.value) {
         event.preventDefault(); // Prevent default form submission
         // console.log(akun_anak.value)
         // const text_modalKonfirmasiAkunOrtu = document.getElementById("text_modalKonfirmasiAkunOrtu")
         let nama = akun_anak.value.split(" ")
         nama.shift()
         nama = nama.join(" ")
         console.log(nama)
         text_modalKonfirmasiAkunAnak.textContent = `Apakah anda yakin untuk mengirimkan pengajuan akun anak kepada ${nama}? (Perubahan ini hanya dapat dilakukan sekali)`
         const modalEl = document.getElementById("modalKonfirmasiAkunAnak");
         const modal = new bootstrap.Modal(modalEl);
         modal.show();
      }
   }

}

function submitFormAkun(event) {
   event.preventDefault();
   const form = document.getElementById("form_mhs")
   console.log(form)
   form.submit()
}

function submitFormAkun2(event) {
   event.preventDefault();
   const form = document.getElementById("form_ortu")
   console.log(form)
   form.submit()
}

function tambahDivKosong() {
   const containerFotosAkun = document.getElementById("containerFotosAkun").children;
   let add_div = true
   for (const item of containerFotosAkun) {
      if (item.classList.contains("d-none")) {
         add_div = false
         break
      }
   }
   if (add_div) {
      tambahFotoWajah()
   }
}

function bdk_in(event) {
   const tds = event.target.parentElement.querySelectorAll("td");
   tds.forEach(element => {
      element.style = "color: rgb(53, 174, 91);"
   });
}

function bdk_out(event) {
   const tds = event.target.parentElement.querySelectorAll("td");
   tds.forEach(element => {
      element.style = "color: rgb(0, 0, 0);"
   });
}

function hapusFileAkunMhs(event) {
   let parent = event.target.parentElement;
   if (event.target.tagName == "I") {
      parent = event.target.parentElement.parentElement;
   }
   parent.remove()
   // const containerFotosAkun = document.getElementById("containerFotosAkun").children;
   // let i = 0
   // for (let item of containerFotosAkun) {
   //    const label = item.getElementsByTagName("label")
   //    const input = item.getElementsByTagName("input")
   //    label[0].setAttribute("for", `file_${i}`)
   //    input[0].setAttribute("id", `file_${i}`)
   //    input[0].setAttribute("name", `file_${i}`)
   //    i++
   //    console.log(item)
   // }
}

function tambahFotoWajah() {
   const containerFotosAkun = document.getElementById("containerFotosAkun");
   const tambah_div_kosong_label = document.getElementById("tambah_div_kosong_label");
   const indexToAppend = containerFotosAkun.childElementCount;
   tambah_div_kosong_label.setAttribute("for", `file_${indexToAppend}`)

   const parent_node = document.createElement("div")
   parent_node.classList.add("d-none", "col-4", "col-lg-3", "pb-3")

   const node = document.createElement("div")
   node.classList.add("container-foto-akun", "pb-1")

   const imageNode = document.createElement("img")
   imageNode.classList.add("w-100", "display-foto-akun", "output-image")

   const labelNode = document.createElement("label")
   labelNode.setAttribute("for", `file_${indexToAppend}`)
   labelNode.classList.add("label-foto-akun")
   labelNode.textContent = "Ganti"

   const inputNode = document.createElement("input")
   inputNode.setAttribute("type", "file")
   inputNode.setAttribute("name", `file_${indexToAppend}`)
   inputNode.setAttribute("id", `file_${indexToAppend}`)
   inputNode.setAttribute("accept", "image/jpeg")
   inputNode.setAttribute("onchange", "tambahFileAkunMhs(event)")
   inputNode.classList.add("input-foto-akun")


   node.appendChild(imageNode)
   node.appendChild(labelNode)
   node.appendChild(inputNode)

   parent_node.appendChild(node)

   containerFotosAkun.appendChild(parent_node)
}

window.addEventListener("load", () => {
   const spinner_container = document.getElementById("spinner_container")
   spinner_container.classList.add("spinner--hidden")
   spinner_container.addEventListener("transitionend", () => {
      spinner_container.remove()
   })
})

// window.onload = function () {
//    const socket = io();
//    socket.connect("https://localhost:5000");
//    socket.on("connect", function () {
//       console.log("Connected")
//    });
//    const form = document.getElementById("form_daftar_mahasiswa")
//    if (form) {
//       form.addEventListener("submit", (e) => {
//          progress_daftar.classList.remove("d-none");
//          return true;
//       })
//    }

//    const progress_bar = document.getElementById("progress_bar")

//    socket.on("update progress", (percent) => {
//       console.log(percent)
//       progress_bar.style.width = `${percent[0]}%`
//       progress_bar.textContent = `${percent[1]}`
//    })
// }

let table1 = new DataTable('#tableHasil');
let table_buffer = new DataTable('#table_buffer', {
   "lengthChange": false, "searching": false, "paging": false, "info": false, order: []
});

if (table_buffer) {
   table_buffer.rows().every(function () {
      const rowNode = this.node(); // actual DOM element
      rowNode.addEventListener('click', () => {
         var url = rowNode.getAttribute('data-url');
         if (url) {
            // Redirect to the URL
            window.location.href = url;
         }
      });
   });
}

const mytable6 = document.getElementById('table_history_aktivitas');
let table6 = new DataTable('#table_history_aktivitas', { "order": [] });
if (mytable6) {
   table6
      .on('order.dt search.dt', function () {
         let i = 1;

         table6
            .cells(null, 0, { search: 'applied', order: 'applied' })
            .every(function (cell) {
               this.data(i++);
            });
      })
      .draw();

   table6.rows().every(function () {
      const rowNode = this.node(); // actual DOM element
      rowNode.addEventListener('click', () => {
         var url = rowNode.getAttribute('data-url');
         if (url) {
            // Redirect to the URL
            window.location.href = url;
         }
      });
   });
}

let table7 = new DataTable('#table_aktivitas', {
   "order": [[0, 'desc']], "dom": "lrtip", "pageLength": 3, "lengthMenu": [[3, 5, 10, 25, 50], [3, 5, 10, 25, 50]]
});

let table2 = $('#tableHasil_profile').DataTable({
   "columnDefs": [
      { "width": "0px", "targets": 1 }
   ],
});

const mytable3 = document.getElementById('table_berada_di_kampus');

let table3 = new DataTable('#table_berada_di_kampus', {
   columnDefs: [
      {
         searchable: false,
         orderable: false,
         targets: 0
      }
   ]
})

let mytable3_row = ""

if (mytable3) {
   table3
      .on('order.dt search.dt', function () {
         let i = 1;

         table3
            .cells(null, 0, { search: 'applied', order: 'applied' })
            .every(function (cell) {
               this.data(i++);
            });
      })
      .draw();

   // mytable3_row = mytable3.querySelectorAll('tbody tr'); // Get all rows in the table

   table3.rows().every(function () {
      // Get the current row node
      const row = this.node();

      // Add a click event listener to the row
      row.addEventListener('click', function () {
         // Get the URL from the data-url attribute
         var url = row.getAttribute('data-url');
         if (url) {
            // Redirect to the URL
            window.location.href = url;
         }
      });
   });

   // Log all rows
   // console.log('All rows:', allRows);
   // console.log('All rows js:', mytable3_row);

   // mytable3_row.forEach(row => {
   //    row.addEventListener('click', function () {
   //       // Get the URL from the data-url attribute
   //       var url = row.getAttribute('data-url');
   //       if (url) {
   //          // Redirect to the URL
   //          window.location.href = url;
   //       }
   //    });
   // });
}

// const button_pagination_mytable3 = document.querySelectorAll(".paginate_button")
// if (button_pagination_mytable3) {
//    console.log(button_pagination_mytable3)
//    button_pagination_mytable3.forEach(btn => {
//       btn.addEventListener("click", function () {
//          console.log(btn)
//       })
//    })
// }


const mytable5 = document.getElementById('table_dosen_mahasiswa');

let table5 = new DataTable('#table_dosen_mahasiswa', {
   columnDefs: [
      {
         searchable: false,
         orderable: false,
         targets: 0
      }
   ]
})

if (mytable5) {
   table5
      .on('order.dt search.dt', function () {
         let i = 1;

         table5
            .cells(null, 0, { search: 'applied', order: 'applied' })
            .every(function (cell) {
               this.data(i++);
            });
      })
      .draw();

   table5.rows().every(function () {
      const rowNode = this.node(); // actual DOM element
      const mytds = rowNode.querySelectorAll(".mytd");

      mytds.forEach(mytd => {
         mytd.addEventListener("click", () => {
            // console.log("mytd: ", mytd)
            var url = mytd.getAttribute('data-url');
            // console.log('Clicked url:', url);
            if (url) {
               // Redirect to the URL
               window.location.href = url;
            }
         })
      })
   });
}


let table4 = new DataTable('#table_dosen_jadwal', {
   columnDefs: [
      {
         searchable: false,
         orderable: false,
         targets: 0
      }
   ]
})

if (table4) {
   table4
      .on('order.dt search.dt', function () {
         let i = 1;

         table4
            .cells(null, 0, { search: 'applied', order: 'applied' })
            .every(function (cell) {
               this.data(i++);
            });
      })
      .draw();

   table4.rows().every(function () {
      const rowNode = this.node(); // actual DOM element
      rowNode.addEventListener('click', () => {
         var url = rowNode.getAttribute('data-url');
         if (url) {
            // Redirect to the URL
            window.location.href = url;
         }
      });
   });
}



// $('#tableHasil_profile').on('click', 'tbody tr', function () {
//    window.location.href = $(this).data('href');
// });



// $('#table_dosen_jadwal').on('click', 'tbody tr', function () {
//    window.location.href = $(this).data('href');
// });

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
   return new bootstrap.Tooltip(tooltipTriggerEl)
})

function change_url(event) {
   // event.preventDefault()
   const tanggal_baru = event.target.elements["tanggal"].value
   event.target.action = event.target.action + `?tanggal=${tanggal_baru}`
   // console.dir(event.target)
}

function open_daftar_dropdown() {
   const dropdown_menu = document.getElementById("dropdown_menu")
   dropdown_menu.classList.add("show")
   dropdown_menu.style = "position: absolute; inset: 0px 0px auto auto; margin: 0px; transform: translate3d(-35px, 45px, 0px);"
}

function ganti_ruangan(event) {
   const value = event.target.value
   const options = event.target.parentElement.parentElement.parentElement.querySelector("#nama_kegiatan");
   if (value == "Ruang Kelas") {
      console.log(1)
      options.innerHTML = `
         <option value="Perkuliahan">Perkuliahan</option>
      `
   } else if (value == "Ruang Sidang") {
      options.innerHTML = `
         <option value="Seminar Proposal">Seminar Proposal</option>
         <option value="Sidang Terbuka">Sidang Akhir</option>
      `
      console.log(2)

   } else if (value == "Ruang Dosen") {
      console.log(3)
      options.innerHTML = `
         <option value="Konsultasi Akademik">Konsultasi Akademik</option>
      `
   }
}



const coll = document.getElementsByClassName("collapsible");
let i;

for (i = 0; i < coll.length; i++) {
   coll[i].addEventListener("click", function () {
      this.classList.toggle("active");
      var content = this.nextElementSibling;
      if (content.style.maxHeight) {
         this.children[0].classList.remove("fa-chevron-up")
         this.children[0].classList.add("fa-chevron-down")
         content.style.maxHeight = null;
      } else {
         this.children[0].classList.remove("fa-chevron-down")
         this.children[0].classList.add("fa-chevron-up")
         content.style.maxHeight = content.scrollHeight + "px";
      }
   });
}

function timeToSeconds(timeString) {
   const [hours, minutes] = timeString.split(":").map(Number);
   return hours * 3600 + minutes * 60
}

function cek_waktu_mulai(event, just_time = false) {
   const waktu_mulai = event.target.parentElement.parentElement.previousElementSibling.querySelector("input").value;
   const waktu_selesai = event.target.value;
   const button_submit = document.getElementById("button_submit")
   console.log(waktu_mulai)
   console.log(waktu_selesai)

   if (waktu_mulai && waktu_selesai) {
      let a = ""
      let b = ""
      if (just_time) {
         a = timeToSeconds(waktu_mulai)
         b = timeToSeconds(waktu_selesai)
      } else {
         a = new Date(waktu_mulai)
         b = new Date(waktu_selesai)
      }
      if (a >= b) {
         button_submit.disabled = true
      } else {
         button_submit.disabled = false
      }
   }
}

function cek_waktu_selesai(event, just_time = false) {
   const waktu_selesai = event.target.parentElement.parentElement.nextElementSibling.querySelector("input").value;
   const waktu_mulai = event.target.value;
   const button_submit = document.getElementById("button_submit")

   if (waktu_mulai && waktu_selesai) {
      let a = ""
      let b = ""
      if (just_time) {
         a = timeToSeconds(waktu_mulai)
         b = timeToSeconds(waktu_selesai)
      } else {
         a = new Date(waktu_mulai)
         b = new Date(waktu_selesai)
      }
      if (a >= b) {
         button_submit.disabled = true
      } else {
         button_submit.disabled = false
      }
   }
}

function cek_waktu_mulai_2(event) {
   const waktu_mulai = event.target.parentElement.previousElementSibling.previousElementSibling.querySelector("input").value;
   const waktu_selesai = event.target.value;
   const button_submit = document.getElementById("button_submit")

   if (waktu_mulai && waktu_selesai) {
      const a = new Date(waktu_mulai)
      const b = new Date(waktu_selesai)
      if (a >= b) {
         button_submit.disabled = true
      } else {
         button_submit.disabled = false
      }
   }
}

function cek_waktu_selesai_2(event) {
   const waktu_selesai = event.target.parentElement.nextElementSibling.nextElementSibling.querySelector("input").value;
   const waktu_mulai = event.target.value;
   const button_submit = document.getElementById("button_submit")

   if (waktu_mulai && waktu_selesai) {
      const a = new Date(waktu_mulai)
      const b = new Date(waktu_selesai)
      if (a >= b) {
         button_submit.disabled = true
      } else {
         button_submit.disabled = false
      }
   }
}

function show_frame(frame) {
   console.log("frame")
   console.log(frame)
}