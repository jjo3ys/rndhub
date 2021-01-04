window.onload = () => {
    let data = jsonObj["results"]
  
    data.forEach(e => {
      console.log(e)
    });
  
    function drawTable(data){
      let tbl = document.getElementById("myTable");
  
      let tbody = document.createElement('tbody');
      tbl.appendChild(tbody);
  
      for(let i in data){
        let tr = document.createElement('tr');
  
        for(let j in data[i]){
          let td = document.createElement('td');
          td.innerHTML = `${data[i][j]}`
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      }
    }
  
    drawTable(data);
}