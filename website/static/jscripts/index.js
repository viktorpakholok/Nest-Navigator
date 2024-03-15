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
