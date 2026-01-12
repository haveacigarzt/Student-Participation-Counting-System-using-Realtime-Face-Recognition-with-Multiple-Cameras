const nav_link = document.querySelectorAll(".nav-link")
const current_url = window.location.href;
const current_url_list = current_url.split("/")


function set_navbar_active(nav_link, value) {
   for (el of nav_link) {
      if (el.dataset.value) {
         if (el.dataset.value == value) {
            el.classList.add("active")
         } else {
            el.classList.remove("active")
         }
      }
   }
}

function set_navbar_active2(nav_link, value) {
   for (el of nav_link) {
      if (el.dataset.value) {
         if (el.dataset.value == value) {
            el.classList.add("active")
         }
      }
   }
}


if (current_url_list[3].split("_")[0] == "daftar") {
   set_navbar_active2(nav_link, "daftar")
} else if (current_url_list[3] == "login" || current_url_list[3] == "login#") {
   set_navbar_active(nav_link, "login")
} else if (current_url_list[3] == "dosen" && (current_url_list[4].split("?")[0] == "jadwal" || current_url_list[4].split("?")[0] == "berada_di_kampus")) {
   set_navbar_active(nav_link, "dosen")
} else if (current_url_list[3] == "dosen" && current_url_list[4].split("?") == "mahasiswa") {
   set_navbar_active(nav_link, "dosen_mahasiswa")
} else if (current_url_list[3] == "dosen" && current_url_list[4].split("?") == "identifikasi") {
   set_navbar_active(nav_link, "dosen_identifikasi")
}