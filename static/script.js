console.log("bad")
document.getElementById('search-form').addEventListener('click', function(event) {
    event.preventDefault();
    fetch('/sort_max_price_tag', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.innerHTML),
    });
});