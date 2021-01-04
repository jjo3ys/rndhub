window.onload = () => {
    let data = jsonObj["results"];

        
    function draw_cards(data) {
        let cards = document.getElementById("cards");

        for(let i in data) {
            let my_card = document.createElement('div');
            my_card.className = 'my_card';
            
            let card = document.createElement('div')
            card.className = 'card'

            let card_body = document.createElement('div')
            card_body.className = 'card-body'
         


            let h5 = document.createElement('h5')
            h5.className = 'card-title'
            h5.innerHTML =  `${data[i]["data_name"]}`

            let abstract = document.createElement('p')
            abstract.className = 'abstract-text'
            abstract.innerHTML =  `${data[i]["abstract"]}`

            let p_part = document.createElement('p')
            p_part.className = 'card-text'
            p_part.innerHTML =  `${data[i]["part"]}`

            let p_name = document.createElement('p')
            p_name.className = 'card-text'
            p_name.innerHTML =  `${data[i]["researcher_name"]}`

            let a = document.createElement('a')
            a.className = 'btn btn-primary'
            a.innerHTML =  `${data[i]["researcher_email"]}`

            card_body.appendChild(h5);
            card_body.appendChild(abstract);
            card_body.appendChild(p_part);
            card_body.appendChild(p_name);
            card_body.appendChild(a);

            card.appendChild(card_body);
            my_card.appendChild(card);
            cards.appendChild(my_card);
        }
    }

    draw_cards(data);
}