const ws = new WebSocket('ws://localhost:8080/ws');
const accessToken = localStorage.getItem('accessToken') || null;
// const tradingPairsSelect = document.getElementById('trading-pairs');

const fetchLastOrders = async (tradingPair) => {
    let orders = await fetch(
        `http://localhost:8000/orders/last/${tradingPair}`,
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    ).then(response => response.json());
    return orders;
};

const fillLastOrders = (lastOrders) => {
    let buyOrders = document.getElementById('buy-orders');
    let sellOrders = document.getElementById('sell-orders');

    buyOrders.innerHTML = '';
    sellOrders.innerHTML = '';

    lastOrders.buy.forEach(order => {
        let orderElement = document.createElement('div');
        orderElement.className = 'order';
        let priceElement = document.createElement('span');
        priceElement.textContent = order.price;
        let amountElement = document.createElement('span');
        amountElement.textContent = order.initQty - order.executedQty;
        orderElement.appendChild(priceElement);
        orderElement.appendChild(amountElement);
        buyOrders.appendChild(orderElement);
    });

    lastOrders.sell.forEach(order => {
        let orderElement = document.createElement('div');
        orderElement.className = 'order';
        let priceElement = document.createElement('span');
        priceElement.textContent = order.price;
        let amountElement = document.createElement('span');
        amountElement.textContent = order.initQty - order.executedQty;
        orderElement.appendChild(priceElement);
        orderElement.appendChild(amountElement);
        sellOrders.appendChild(orderElement);
    });
};

const fetchLastTrades = async (tradingPair) => {
    let trades = await fetch(
        `http://localhost:8000/trades/last/${tradingPair}`,
        {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }
    ).then(response => response.json());

    let tradesContent = document.getElementById('trades');
    tradesContent.innerHTML = '';

    return trades;
};

const fillLastTrades = (newTrades) => {
    let tradesContent = document.getElementById('trades');
    newTrades.forEach(trade => {
        let tradeElement = document.createElement('div');
        tradeElement.className = 'trade';
        let priceElement = document.createElement('span');
        priceElement.textContent = trade.price;
        let amountElement = document.createElement('span');
        amountElement.textContent = trade.qty;
        tradeElement.appendChild(priceElement);
        tradeElement.appendChild(amountElement);
        tradesContent.appendChild(tradeElement);
    });
};

let ctx = document.getElementById('tickers-chart').getContext('2d');
var chart = new Chart(ctx, {
    // ...
    type: 'line',
    data: {
        labels: [], // Initially, labels (usually representing time) is an empty array
        datasets: [{
            data: [], // Initially, data (usually representing price) is an empty array
            label: "Price",
            borderColor: "#3e95cd",
            fill: false
        }]
    },
    // ...
});

document.getElementById('trading-pairs').addEventListener('change', async (event) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        // Send selected trading pair to server
        ws.send(JSON.stringify({
            type: 'subscribe',
            target: event.target.value
        }));
        console.log(event.target.value);
        let lastOrders = await fetchLastOrders(event.target.value);
        fillLastOrders(lastOrders);
        let lastTrades = await fetchLastTrades(event.target.value);
        fillLastTrades(lastTrades);

        // Clear the chart
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
            
        lastTrades.forEach(trade => {
            addTradeToChart(trade);
        });
        // Update the chart
        chart.update();
    }
});

ws.onopen = function() {
    if (accessToken) {
        ws.send(JSON.stringify({
            type: 'auth',
            token: `Bearer ${accessToken}`
        }));
    }
    tradingPairsSelect.dispatchEvent(new Event('change'));
};

ws.onmessage = function(event) {
    let data = JSON.parse(event.data);
    if (data.type === 'broadcast') {
        if (data.target === "last_orders") {
            fillLastOrders(data.data);
        } else if (data.target === "new_trades") {
            console.log(data.data.newTrades);
            fillLastTrades(data.data.newTrades);
            data.data.newTrades.forEach(trade => {
                    addTradeToChart(trade);
                }
            );
        }
    } else if (data.type === 'update') {
        if (data.target === "balance") {
            console.log(data.data);
            let balance = data.data;
            let balanceElement = document.getElementById(balance.currency);
            balanceElement.textContent = `${balance.currency.toUpperCase()}: ${balance.amount}`;
        }
    }
};

const addTradeToChart = (trade) => {
    // Add the trade time to the labels array
    chart.data.labels.push(trade.createdAt);

    // Add the trade price to the data array
    chart.data.datasets[0].data.push(trade.price);
}
