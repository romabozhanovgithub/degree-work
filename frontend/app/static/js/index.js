// Trading pairs
let tradingPairs = ["usd-eur", "usd-gbp", "usd-jpy"]

const tradingPairsSelect = document.getElementById('trading-pairs');
tradingPairs.forEach(pair => {
    let option = document.createElement('option');
    option.text = pair.replace('-', '/').toUpperCase();
    option.value = pair;
    tradingPairsSelect.add(option);
});

document.addEventListener('DOMContentLoaded', async function() {
    // Authentication
    let accessToken = localStorage.getItem('accessToken') || null;
    let userData = null;

    if (accessToken) {
        userData = await fetch(
            'http://localhost:5000/user/me',
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            }
        ).then(response => {
            if (response.status === 401) {
                localStorage.removeItem('accessToken');
                return null;
            }
            return response.json();
        });
    }

    let orderForm = document.getElementById('order-form');

    if (userData) {
        document.getElementById('user-details').textContent = `${userData.firstName} ${userData.lastName}`;
        document.getElementById('login').style.display = "none";
        document.getElementById('signup').style.display = "none";


        let balancesContent = document.getElementById('balances-content');
        let balances = userData.balances;
        balances.forEach(balance => {
            let balanceElement = document.createElement('div');
            balanceElement.id = balance.currency;
            balanceElement.textContent = `${balance.currency.toUpperCase()}: ${balance.amount}`;
            balancesContent.appendChild(balanceElement);
        });

        orderForm.style.display = "flex";
        orderForm.addEventListener('submit', async function(e) {
            e.preventDefault();
        
            let symbol = document.getElementById('trading-pairs').value;
            let side = document.getElementById('orderSide').value;
            let initQty = document.getElementById('quantity').value;
            let price = document.getElementById('price').value;
            let type = "limit";
        
            let orderData = {
                symbol, 
                side,
                initQty,
                price,
                type
            };
        
            let response = await fetch('http://localhost:8000/orders/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify(orderData)
            });
        
            let data = await response.json();
        });
    } else {
        document.getElementById('balances').style.display = "none";
        document.getElementById('deposit').style.display = "none";
        orderForm.style.display = "none";
    }
});
