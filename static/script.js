
window.onload = function() { getOrderBook(); getTrades()};

newestTradeId = 0;

const priceDiv = document.getElementById('price');
/*priceDiv.addEventListener('animationend', () => {
    priceDiv.classList.remove('fade-in');
});*/
const bidsDiv = document.getElementById('bids-data');
const asksDiv = document.getElementById('asks-data');        
const bidaskDiv = document.getElementById('bidask');
const bidDiv = document.getElementById('bid-price');
const askDiv = document.getElementById('ask-price');

function updateOrderBookUI(bookdata){
    let bids = [];
    for(const bidOrder of bookdata.bids){
            const order = {
                price: bidOrder.price,
                qty: bidOrder.quantity,
            };
            bids.push(order);
        }
        bids.sort((a,b) => b.price - a.price); 
        bidTableBody.innerHTML = ''; 
        for(bid of bids){
            const row = document.createElement('tr');
            row.innerHTML = `<td>${bid.qty}</td><td>${bid.price.toFixed(2)}</td>`;
            bidTableBody.appendChild(row);                  
        }

        let asks = [];                
        for(const askOrder of bookdata.asks){
            const order = {
                price: askOrder.price,
                qty: askOrder.quantity,
            };
            asks.push(order);
        }
        asks.sort((a,b) => b.price - a.price);  
        askTableBody.innerHTML = '';  
        for(ask of asks){
            const row = document.createElement('tr');
            row.innerHTML = `<td>${ask.price.toFixed(2)}</td><td>${ask.qty}</td>`;
            askTableBody.appendChild(row);
        }
}

function getOrderBook(){
    fetch('https://pszrk.pythonanywhere.com/orderbook/')
    .then(response => {
        if (!response.ok) {throw new Error('server response was not ok');}
        return response.json();
    })
    .then(data => {
        // update ui with order book data
        updateOrderBookUI(data);
    })
    .catch(error => {console.error('Error fetching order book:', error);});
}

function getTrades(){
    fetch('https://pszrk.pythonanywhere.com/trades/')
    .then(response => {
        if (!response.ok) {throw new Error('server response getting trades trades was not ok');}
        return response.json();
    })
    .then(data => {
        // update ui with trades data
        updateTradesUI(data);
    })
    .catch(error => {console.error('Error fetching order book:', error);});
}

function updateTradesUI(data){
    const tradesTable = document.getElementById('tsTable');
    const tbody = tradesTable.querySelector('tbody');

    data.forEach(trade => {
        if(trade.id > newestTradeId){
            newestTradeId = trade.id;
            const row = tbody.insertRow(0);
            const c1 = row.insertCell(0);
            const c2 = row.insertCell(1);
            c1.textContent = `${trade.quantity} @ ${trade.price}`;
            c2.textContent = `${trade.time}`;
        }
    });
}


function submitOrder() {
    const price = document.getElementById('submitprice').value;
    const amount = document.getElementById('submitamount').value;
    const side = document.getElementById('submitside').value;

    const orderData = {
        price: price,
        qty: amount,
        side: side
    }            
    fetch('https://pszrk.pythonanywhere.com/submit/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
    })
    .then(response => {
        if (!response.ok) {throw new Error('server response was not ok when submitting order');} 
        return response.json();
    })
    .then(data => {
        getOrderBook();
        getTrades();
    })
    .catch(error => {console.error('Error submitting order:', error);                
    });
}

function submitRandomOrder() {
    const orderData = {
        price: 100,
        qty: 10,
        side: "ask"
    }
}