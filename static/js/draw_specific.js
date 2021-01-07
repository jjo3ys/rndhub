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

            let abstract = document.createElement('pre')
            abstract.className = 'abstract-text'
            abstract.innerHTML =  `${data['abstracts']}`

            let detail = document.createElement('div')
        detail.className = 'detail--container'



        let detail_row1 = document.createElement('div')
        detail_row1.className = 'detail--row'

        let detail_title_name = document.createElement('div')
        detail_title_name.className = 'detail--title'
        detail_title_name.innerHTML = 'Publisher:'

        let p_name = document.createElement('div')
        p_name.className = 'detail--value'
        p_name.innerHTML = `${data["researcher_name"]}`


        detail_row1.appendChild(detail_title_name)
        detail_row1.appendChild(p_name)

        

        let detail_row2 = document.createElement('div')
        detail_row2.className = 'detail--row'

        let detail_title_part = document.createElement('div')
        detail_title_part.className = 'detail--title'
        detail_title_part.innerHTML = 'Major part:    '

        let p_part = document.createElement('div')
        p_part.className = 'detail--value'
        p_part.innerHTML = `${data["part"]}`


        detail_row2.appendChild(detail_title_part)
        detail_row2.appendChild(p_part)


        detail.appendChild(detail_row1)
        detail.appendChild(detail_row2)

 


            let a = document.createElement('a')
            a.className = 'btn btn-primary'
            a.innerHTML =  `${data["researcher_email"]}`

            // card_body.appendChild(h5);
            card_body.appendChild(abstract);
            card_body.appendChild(detail);
            card_body.appendChild(a);

            card.appendChild(card_body);
            my_card.appendChild(card);
            cards.appendChild(my_card);
    }

    draw_card(data);
    draw_info(data);
    draw_recommend(_data_recommend)
}