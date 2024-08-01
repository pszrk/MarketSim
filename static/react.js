const { useState, useEffect } = React;
const { render } = ReactDOM;

function Trades() {
    const [trades, setTrades] = useState([]);

    useEffect(() => {
        function getTrades() {
            fetch('https://pszrk.pythonanywhere.com/trades/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Server response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    updateTradesUI(data);
                })
                .catch(error => {
                    console.error('Error fetching trades:', error);
                });
        }

        getTrades();
    });

    return (
        <div>
            <h2>Trades</h2>
            <table id="tsTable">
                <thead>
                    <tr>
                        <th>Trade</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {trades.map(trade => (
                        <tr key={trade.id}>
                            <td>{`${trade.quantity} @ ${trade.price}`}</td>
                            <td>{trade.time}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

render(<Trades />, document.getElementById('tsContainer'));