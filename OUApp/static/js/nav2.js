var nav = document.querySelector('nav');
var btnBook = nav.querySelector('.btn-on-nav');
var logo = nav.querySelector('.navbar-brand').querySelector('img')

nav.classList.add("bg-white")
nav.classList.remove("bg-nav", "navbar-dark")
btnBook.classList.remove("text-white")
logo.src = "/static/src/logo_black.png"
