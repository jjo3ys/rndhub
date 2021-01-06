const contaniner = document.getElementById('main_container');
const loading = document.querySelector('.loading');

let data = jsonObj["results"];

const cards_num = 8;
let min_len_cards = 0;
// let max_len_cards = min_len_cards + cards_num;

addDataToDom(data);

window.addEventListener('scroll', () => {
    const {  scrollHeight, clientHeight } = document.documentElement;
    let scrollTop = this.scrollY;

    if(clientHeight + scrollTop >= scrollHeight + 5){

        
        //loading animation 실행
        showLoading();
    }
})

function showLoading(){
    loading.classList.add('show');

    setTimeout(addDataToDom, 1000, data);
}

// async function getCard() {
//     const postResponse = await fetch(`/ajax`, {
//         method: "POST",
//         credentials: "include",
//         body: JSON.stringify(postdata),
//         cache: "no-cache",
//         headers: new Headers({
//             "content-type": "application/json"
//         })
//     })

//     const postData = await postResponse.json();

//     console.log(postData)
//     const data = {};

//     addDataToDom(data);
// }

function addDataToDom(data) {
    

    for(let i = min_len_cards; i < min_len_cards + cards_num; i++){
        if(i == data_len ){
    
            let done = document.createElement('div');
            done.className = 'done--alert'
            done.innerHTML = "모든 검색 결과를 모두 표시 하였습니다.";

            contaniner.appendChild(done);
            break;
        
        } else if(i > data_len) break;
            
        let my_card = document.createElement('div');
        my_card.className = 'my_card';

        let card = document.createElement('div')
        card.className = 'card'

        let card_body = document.createElement('div')
        card_body.className = 'card-body'


        let a = document.createElement('a');
        a.setAttribute('href', `/specific/${data[i]['idx']}`)

        let h5 = document.createElement('h5')
        h5.className = 'card-title'
        h5.innerHTML = `${data[i]["data_name"]}`

        a.appendChild(h5);

        let abstract = document.createElement('p')
        abstract.className = 'abstract-text'
        abstract.innerHTML = `${data[i]["abstracts"]}`

        // let p_part = document.createElement('p')
        // p_part.className = 'card-text'
        // p_part.innerHTML = `${data[i]["part"]}`

        // let p_name = document.createElement('p')
        // p_name.className = 'card-text'
        // p_name.innerHTML = `${data[i]["researcher_name"]}`



        let detail = document.createElement('div')
        detail.className = 'detail--container'



        let detail_row1 = document.createElement('div')
        detail_row1.className = 'detail--row'

        let detail_title_name = document.createElement('div')
        detail_title_name.className = 'detail--title'
        detail_title_name.innerHTML = 'Publisher:'

        let p_name = document.createElement('div')
        p_name.className = 'detail--value'
        p_name.innerHTML = `${data[i]["researcher_name"]}`


        detail_row1.appendChild(detail_title_name)
        detail_row1.appendChild(p_name)

        

        let detail_row2 = document.createElement('div')
        detail_row2.className = 'detail--row'

        let detail_title_part = document.createElement('div')
        detail_title_part.className = 'detail--title'
        detail_title_part.innerHTML = 'Major part:    '

        let p_part = document.createElement('div')
        p_part.className = 'detail--value'
        p_part.innerHTML = `${data[i]["part"]}`


        detail_row2.appendChild(detail_title_part)
        detail_row2.appendChild(p_part)


        detail.appendChild(detail_row1)
        detail.appendChild(detail_row2)

        h5.setAttribute('data-idx', `${data[i]['idx']}`)
        card_body.appendChild(a);
        card_body.appendChild(abstract);
        card_body.appendChild(detail);
        // card_body.appendChild(p_name);

        // card_body.appendChild(a);

        card.appendChild(card_body);
        my_card.appendChild(card);
        cards.appendChild(my_card);

    }

    loading.classList.remove('show');

    min_len_cards += cards_num;
}
