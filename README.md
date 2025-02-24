# MarketSim
A project simulating a centralized exchange with Level II order flow.  
The exchange is implemented using a Python backend that exposes a RESTful api.  
Clients interact with the API to send orders and view the orderbook.  
The Python backend connects to a MySQL server to store and manage the current state of the orderbook (bids/asks and quantities).  

<b>technologies used:</b>   
Python - backend development  
Flask - Web framework for building the API endpoints  
SQLAlchemy - ORM for interacting with the database  
MySQL: database used to store orderbook data  
HTML/JavaScript/CSS: demo frontend webpage to interact with the API via a graphical interface

<b>usage instructions:</b>   
the exchange server is hosted on the cloud.  
there is a webpage for viewing the exchange and submitting orders, accessible at  
https://pszrk.pythonanywhere.com/  

alternatively, you can make direct HTTP requests to the API endpoints.  
to submit a simulated order, you can send POST requests to the endpoint  
/submit/  
currently hosted at https://pszrk.pythonanywhere.com/submit/    
with a JSON payload containing: price(float), qty(int), and side("bid" or "ask"):   
```
{  
    "price": 100,  
    "qty": 10,  
    "side": "ask"  
}
```  
  
to get the orderbook, send a GET request to the endpoint  
/orderbook/   
currently hosted at https://pszrk.pythonanywhere.com/orderbook/  

<br>
<br>
<br>
<br>
  
  
[![License: CC BY-NC-ND 4.0](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-nd/4.0/)