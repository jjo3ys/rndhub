window.onload = () => {
    let data = jsonObj["results"];
    let current_page = 1;
    let rows = 7;

    const list_element = document.getElementById('cards')
    const pagination_element = document.getElementById('pagination')


    draw(data);

    function draw(data) {
        data_key_list = Object.keys(data);

        DisplayList(data, list_element, rows, current_page);
        SetupPagination(data, pagination_element, rows);
    }

    function DisplayList(items, wrapper, rows_per_page, page) {
        wrapper.innerHTML = "";
        page--;

        let start = rows_per_page * page;
        let end = start + rows_per_page;
        let paginatedItems = data_key_list.slice(start, end);

        for (let i = 0; i < paginatedItems.length; i++) {
            _i = parseInt(paginatedItems[i])


            let my_card = document.createElement('div');
            my_card.className = 'my_card';

            let card = document.createElement('div')
            card.className = 'card'

            let card_body = document.createElement('div')
            card_body.className = 'card-body'


            let a = document.createElement('a');
            a.setAttribute('href', `/specific/${data[_i]['idx']}`)

            let h5 = document.createElement('h5')
            h5.className = 'card-title'
            h5.innerHTML = `${data[_i]["data_name"]}`

            a.appendChild(h5);

            let abstract = document.createElement('p')
            abstract.className = 'abstract-text'
            abstract.innerHTML = `${data[_i]["abstracts"]}`

            let p_part = document.createElement('p')
            p_part.className = 'card-text'
            p_part.innerHTML = `${data[_i]["part"]}`

            let p_name = document.createElement('p')
            p_name.className = 'card-text'
            p_name.innerHTML = `${data[_i]["researcher_name"]}`

            // let data = document.createElement('div')
            // let data_index = document.createAttribute('data-index')
            // data_index.value = _i

            // data.at
            // let a = document.createElement('a')
            // a.className = 'btn btn-primary'
            // a.innerHTML =  `${data[_i]["researcher_email"]}`

            h5.setAttribute('data-idx', `${data[_i]['idx']}`)
            card_body.appendChild(a);
            card_body.appendChild(abstract);
            card_body.appendChild(p_part);
            card_body.appendChild(p_name);

            // card_body.appendChild(a);

            card.appendChild(card_body);
            my_card.appendChild(card);
            cards.appendChild(my_card);

            // h5.addEventListener('click', specific_onclick(this));


        }
    }

    function SetupPagination(items, wrapper, rows_per_page) {
        wrapper.innerHTML = "";

        let page_count = Math.ceil(items.length / rows_per_page);

        for (let i = 1; i < page_count + 1; i++) {
            let btn = PaginationButton(i, items);
            wrapper.appendChild(btn);
        }
    }


    function PaginationButton(page, items) {
        let button = document.createElement('li');
        button.className = 'page-item';

        let a = document.createElement('a');
        a.className = 'page-link'

        button.appendChild(a);

        a.innerText = page;

        if (current_page == page) button.classList.add('active');

        a.addEventListener('click', function () {
            current_page = page;

            DisplayList(items, list_element, rows, current_page);

            let current_btn = document.querySelector('.pagination li.active');
            current_btn.classList.remove('active');

            button.classList.add('active');
        });

        return button;
    }
}

// function specific_onclick(this) {

//         d = h5.data('idx')
//         let form = document.createElement('form');

//         form.action = '/specific';
//         form.method = "POST";

//         form.setAttribute('data-idx', `${data[_i]['idx']}`);

//         console.log(d)

// }

function search_ajax() {
    let input_word = document.getElementById('form-search');

    let postdata = {
        data: input_word.value,
    };




    fetch(`${window.location.href}`, {
            method: "POST",
            credentials: "include",
            body: JSON.stringify(postdata),
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        })
        .then(function (response) {
            if (response.status !== 200) {
                console.log('fuck')
                return;
            }
            else console.log('success')
                // let _data = JSON.parse(data)
                // console.log(_data)
                // a = _data["results"];
                // console.log(a);

                // window.history.pushState(null, null, `/search_page/${input_word}`)
            });
     

}