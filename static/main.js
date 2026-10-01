// MOBILE MENU

const menuBtn = document.getElementById("menu-btn");
const navbar = document.getElementById("navbar");

menuBtn.addEventListener("click", () => {
    navbar.classList.toggle("active");
});

// CLOSE MENU AFTER CLICKING LINK

const navLinks = document.querySelectorAll(".navbar a");

navLinks.forEach(link => {
    link.addEventListener("click", () => {
        navbar.classList.remove("active");
    });
});

// HEADER SHADOW ON SCROLL

const header = document.querySelector(".header");

window.addEventListener("scroll", () => {

    if(window.scrollY > 50){
        header.style.boxShadow = "0 5px 20px rgba(0,0,0,0.12)";
    }
    else{
        header.style.boxShadow = "0 2px 20px rgba(0,0,0,0.08)";
    }

});

// ACTIVE MENU HIGHLIGHT

const sections = document.querySelectorAll("section");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {

        const sectionTop = section.offsetTop - 120;
        const sectionHeight = section.clientHeight;

        if(window.scrollY >= sectionTop){
            current = section.getAttribute("id");
        }

    });

    navLinks.forEach(link => {

        link.classList.remove("active-link");

        if(link.getAttribute("href") === "#" + current){
            link.classList.add("active-link");
        }

    });

});

// SMOOTH SCROLL OFFSET

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function(e){

        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));

        window.scrollTo({
            top: target.offsetTop - 80,
            behavior: "smooth"
        });

    });

});

// SCROLL TO TOP WHEN PAGE RELOADS

window.onbeforeunload = function () {
    window.scrollTo(0, 0);
};


// LOGIN DROPDOWN

