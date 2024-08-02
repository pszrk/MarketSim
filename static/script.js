
window.onload = function() { getOrderBook();};



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
        //dispatch event that order book was refreshed
        const event = new CustomEvent('bookUpdated');
        window.dispatchEvent(event);
    })
    .catch(error => {console.error('Error fetching order book:', error);});
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