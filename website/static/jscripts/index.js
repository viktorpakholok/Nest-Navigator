$(document).ready(function() {
    $('#region').select2({
        placeholder: "Виберіть район",
        allowClear: true
    });
});

// window.addEventListener("load", () => {

//     const loader = document.querySelector(".loader");

//     loader.classList.add("loader-hidden");

//     loader.addEventListener("transitionend", () => {
//         if (document.querySelector(".loader")){
//             loader.parentNode.removeChild(loader)
//         }
//     })
// })

function next(t){
    var elm = t.parentElement.children[1].children[0];
    var item = elm.getElementsByClassName('item');
    elm.append(item[0])
    console.log('what')
}

function prev(t){
    var elm = t.parentElement.children[1].children[0];
    var item = elm.getElementsByClassName('item');
    elm.prepend(item[item.length - 1]);
}
