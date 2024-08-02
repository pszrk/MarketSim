const { useState, useEffect } = React;
const { render } = ReactDOM;

function Trades() {
    const [trades, setTrades] = useState([]);

    function getTrades() {
            return fetch('https://pszrk.pythonanywhere.com/trades/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Server response was not ok');
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error('Error fetching trades:', error);
                    return [];
                });
        }

        function handleBookUpdate(event) {
            getTrades().then(fetchedTrades => {
                setTrades(fetchedTrades);
            });
        }

        useEffect(() =>{
            window.addEventListener('bookUpdated', handleBookUpdate);

            return() =>{
                window.removeEventListener('bookUpdated', handleBookUpdate);
            }
        }, []);
        //without dependency array [], useeffect would run after every render of the component
        //with dependency array [] empty, useeffect runs only once when component is first mounted
        // [value] with values in the dependency array, effect runs after initial render and every time one of those values changes

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