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

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/dl_to_db.png)

To go back to main menu hit return. Now that you have some data in the db you can view the db, vhich is essentially the same as the db view in the Download Data, but this page can be built out for e.g. updating the db manually.

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/view_db)

More interesting is the Load Data option. This is used to visualize the timeseries. Before plotting, the data needs to be read from the database and loaded into memory. Use the stock ticker to call up a time series and hit load.

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/choose_to_display.png)

The called up stock will appear in the Loaded Data section

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/load.png)

You can now choose Candle or Line to graph the stock. Tick the Candle radio button and hit Plot.

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/candle.png)

You can also load multiple stocks and plot them in a normalized line graph

![alt text](https://github.com/CJRockball/Stock_DB/blob/main/Images/multi_line_plot)






