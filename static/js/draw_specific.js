window.onload = () => {
    let _data = jsonObj["results"];
    let _data_recommend = jsonObj_recommend["results"];
    let data = _data[0]
    

    function draw_recommend(data) {
        let recommend_data_name = document.querySelector('.my--recommend');
        let max_len = 5;

        for(let i = 0; i < max_len; i++){
            let data_name = document.querySelector('.my--recommend .recommend_data_name')

            let list_name = document.createElement('li');
            list_name.className = 'list-group-item';

            let a = document.createElement('a');
            a.setAttribute('href', `/specific/${data[i]['idx']}`)
            a.innerHTML = data[i]['data_name'];

            list_name.appendChild(a);
            data_name.appendChild(list_name);


            // let data_researcher = document.querySelector('.my--recommend .recommend_data_researcher')

            // let list_researcher = document.createElement('li');
            // list_researcher.className = 'nav-item';
            // list_researcher.innerHTML = data[i]['researcher_name'];

            // data_researcher.appendChild(list_researcher);

            
        }
    }

    function draw_info(data) {
        let my_table = document.getElementById('my_table');
        
        let title = document.getElementById('title');
        
        let h5 = document.createElement('h5');
        h5.className = 'card-title';
        h5.innerHTML = `${data['data_name']}`

        title.appendChild(h5)

        let tbody = document.querySelector('#my_table tbody');
        


        for(let i = 3; i < Object.keys(data).length; i++) {

            let tr = document.createElement('tr')

            let th = document.createElement('th')
            th.setAttribute('scope', 'row')
            th.innerHTML = Object.keys(data)[i];
            
            let td = document.createElement('td')
            td.innerHTML = data[Object.keys(data)[i]];

            tr.appendChild(th)
            tr.appendChild(td)

            tbody.appendChild(tr)
        }
        
   
        my_table.appendChild(tbody);


    }

    function draw_card(data) {
        
        let my_card = document.createElement('div');
            my_card.className = 'my_card';
            
            let card = document.createElement('div')
            card.className = 'card'

            let card_body = document.createElement('div')
            card_body.className = 'card-body'
         


            // let h5 = document.createElement('h5')
            // h5.className = 'card-title'
            // h5.innerHTML =  `${data['data_name']}`

            let abstract = document.createElement('p')
            abstract.className = 'abstract-text'
            abstract.innerHTML =  `${data['abstracts']}`

            let p_part = document.createElement('p')
            p_part.className = 'card-text'
            p_part.innerHTML =  `${data['part']}`

            let p_name = document.createElement('p')
            p_name.className = 'card-text'
            p_name.innerHTML =  `${data['researcher_name']}`

            let a = document.createElement('a')
            a.className = 'btn btn-primary'
            a.innerHTML =  `${data["researcher_email"]}`

            // card_body.appendChild(h5);
            card_body.appendChild(abstract);
            card_body.appendChild(p_part);
            card_body.appendChild(p_name);
            card_body.appendChild(a);

            card.appendChild(card_body);
            my_card.appendChild(card);
            cards.appendChild(my_card);
    }

    draw_card(data);
    draw_info(data);
    draw_recommend(_data_recommend)
}