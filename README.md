# Stock_DB

This program sets up a database and downloads stock data from Yahoo. It uses a simple web interface built in Flask, where you can download stock history and visualize it. There is no CSRF of flash messages implemented.

Download web_stock_search_db and templates. Make sure you're in the right folder when you run it otherwise the program will not find the database.

First time the program is run it will creat the database stock.db in the same folder as the program. The db has two tables, one for name and length of the time series and one for the data.

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/Picture2.png)

When the program starts it loads a web page with three choices Download Data, Load Data and View Database. 

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/Link_view.png)

Since the db has just been created it needs to be populated, so choose Download Data. It will take you to a new view where you fill out the boxes and hit download. The first box is for the ticker (which must be filled in since this is used for connecting to Yahoo), the second one is the full name (which can be left blank).

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/choose_to_download.png)

Once you hit download and the data is recieved and inserted in the db the table of the db will update.

