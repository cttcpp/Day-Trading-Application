# RealTimeNeuralNetworkTrading

### Why this project was created:

         This project was made as a final project for Udacity.com for there Machine Learning 
         Engineer program. This project uses a variety of techniques to create many well 
         known indicators for trading on the stock market, and utilize these within a deep 
         learning setup that uses real time recurrent learning. We use this neural network 
         to predict stock returns for a companies of our choice. 
         
         Due to limitations on acquiring free intraday data, we're currently only able to 
         predict on roughly 50 stocks but if you chose to acquire paid data elsewhere, you 
         could theoretically predict for any amount of companies you wanted. This setup is 
         more based for those who don't have the money to buy lots of data though. 
         
### How this package operates:
         
         The way this package works is first, you create your indicator data using some 
         precalculated dataframes containing high/low/close/typical values for the past 
         several years that were adjusted for dividends and splits and such. Once this is 
         done, you can start training your neural network using this indicator data. This 
         project allows you to choose the indicator attributes of your choice. For each 
         indicator, which there are 12, you also have the ability to use 32 different 
         period lengths. The period length is how much data each indicator uses to 
         calculate itself. So for example, you might only choose to use the smallest 
         period length of 6 minutes, or choose the longest period length of 125 trading 
         days. And you can choose many different options together to get both
         short term and long term data combined. Each indicator has preferred period 
         lengths that work best generally but I encourage you to try to test as much as 
         you can out yourself. 
         
         You probably want to keep the amount of indicators you're using total less than 
         about 250, as more than that amount of attributes can quickly run up memory and 
         cpu usage. For my machine, I ran on a generally small amount of resources using 
         12GB of ram, with an Intel i7-4510U cpu. Much more than than amount of attributes 
         tended to kill my memory, and in the process, kill my cpu time. I tended to train 
         on 230 attributes, using roughly 25000 records at a time. I found this to be useful 
         and provided a good accuracy/limitation ratio. 
         
         Once you've set up all of your indicator and neural network data and everything is
         up to date, you can start using the real-time portion of the project. In particular, 
         the RealTimeCalculator notebook allows for calculating indicators in real-time using 
         data from a Google Finance server that provides us real-time stock data for the 
         stocks of our choice. This allowed us to then calculate highs/lows/closes/typical 
         values which then allowed us to calculate our indicators. Once the indicators had 
         been calculated, our neural network function would be called to make its prediction 
         for us based on our indicators.
         
         This package is set up to train the neural network on the trading off-hours so that 
         during the day we could test only, rather than train and test which would use up a 
         lot more resources. However, eventually, an update will be provided that will give 
         you the option to train on the data in real-time so you could get more accurate 
         predictions. 
         
### For more information or questions/concerns:
         Contact me at jbboltz123@gmail.com
		 
----------------------------------------------------------------------------
		 
# Installation
      1. Ensure you have an IPython Notebook solution such as with 
         Anaconda which installs a variety of applications including
         python, and Ipython solution, and several other helpful
         modules such as Numpy, Pandas, and Pip.
      
      2. Retrieve the 4 python files in this repository and store them
         in the same directory with all of your other repositories. 
        
         For example, with Anaconda, the directory is stored in:
            C:/path/to/user/Anaconda/Lib/site_packages/
        
         RealTimeNN.py, CalcInd.py, and NyseDatesPrds.py are stored as 
         standalone files, while the googlefinance init.py is stored in 
         a folder called googlefinance. The googlefinance is a slightly
         altered version of the googlefinance package written by hongtaocai
            
      3. Install the other modules using pip. For example, cd to the 
         scripts directory at C:/path/to/user/Anaconda/scripts/ , then
         type:
            pip install yahoo_finance
            pip install quandl
            pip install matplotlib
            pip install scipy
            pip install pickle
            pip install pandas
            pip install numpy
            
      4. Once all of your modules have been set up, place the other ipynb
         files from this repository into a directory called Trading/ and 
         place these 6 ipython files into this directory.
            
      5. Retrieve the HLC directory from the repository, within this is
         20 pickled files containing premade dataframes with intraday
         highs, lows, closes, and typical values at a minute by minute
         level. These are provided so you don't have to create them yourself
         using the online repository that was used to create them as it made
         it so you would have to download individually one at a time and adjust
         them yourself. 
            
         This repository contains 14 stocks as well as 6 Exchange Traded Funds, 
         as well as Indexes that are used to help in the prediction process. 
         
         If you choose, you can retrieve more stocks/funds/indexes directly from
         the online server that was used to create these data sources. The site
         is called http://thebonnotgang.com/tbg/historical-data/
         
         Store this repository within your Trading/ directory.
                
#### Given files, packages, and directory:
        ProgramInfoAndCreation.ipynb
        IndicatorCreation.ipynb
        CalculateAndAddMissingData.ipynb
        DividendAndSplitUpdate.ipynb
        RealTimeCalculator.ipynb
        RealTimeNeuralNetwork.ipynb
        RealTimeNN.py
        CalcInd.py
        NyseDatesPrds.py
        googlefinance package
        HLC directory

#### Imported packages:
        yahoo_finance package
        quandl package
        matplotlib package
        scipy package
        pickle package
        pandas package
        numpy package
        
--------------------------------------------------------------------

# Usage

      1. First cd to your Trading/ directory, then first call:
            ipython notebook ProgramInfoAndCreation.ipynb
         
         Further instructions on how to view information and create
         your initial files are within this file.
        
      2. After everything is setup using that file, open:
            DividendAndSplitUpdate.ipynb
            
         This file will allow you to add the data since the intraday data
         was put up, and then adjust for any splits and/or dividends that 
         have happened since the hlc dictionary was put online. Follow the 
         instructions within this file for more information.
        
      3. After your hlc dictionary is updated for added data and dividend/
         stock adjustments, you'll now create the indicators for each 
         company. To do this, open:
            IndicatorCreation.ipynb
            
         For more information, look within the file.
        
      4. Now that your indicators and intraday data are up to date, you 
         can open:
            RealTimeCalculor.ipynb
            
         This file has everything you need to acquire real-time stock data
         so as to calculate real-time indicator values as well as use these
         values to create you're predictions. For more information, look 
         within the file.
            
      5. Finally, you'll open:
            RealTimeNeuralNetwork.ipynb
        
         This file is used to calculate the neural networks for any companies
         that you choose. This file is typically run on trading off-hours because
         it is processor and memory intensive, and it allows you to create/update
         a neural network that once created/updated can be saved and then will be
         used throughout the next trading day to make our predictions. Eventually 
         this will be set up to continuously update throughout the training day for
         more accurate results, but for now, it's set up to give you a neural netwrk
         that you will just use to predict and only update after the trading day is
         done.
            
### Note:
#### If no dividends/splits since last update:
         If for any reason, you miss some trading day's data by not using the 
         RealTimeCalculator.ipynb file, you can update everything back to normal by
         opening:
            CalculateAndAddMissingData.ipynb
            
         This file allows you to retrieve missed intraday data from our intraday 
         data source and update up to present. 
         
#### If dividends/splits since last update:   
         Make sure there have been no dividends or stock splits on any of your stocks 
         since you last updated everything as if this did happen, rather than call the 
         above file, you'll instead open:
            DividendAndSplitUpdate.ipynb
         
         where you'll update your intraday data dataframes for the div/splits. This will
         leave you with a new pickle file called onlyupdatedintra.pickle, that contains 
         only the company highs/lows/closes/typicals that have been adjusted. Following
         this adjustment, all of the indicators for these companies need to be reupdated, 
         rather than soley adding the indicator values since you last updated(which you'll
         do for the other companies that don't need to be fully updated). Now open:
            IndicatorCreation.ipynb
            
         And update the companies that recieved the dividend/split to reupdate all of the 
         indicators for those stocks. Then open:
            CalculateAndAddMissingData.ipynb
            
         Where you'll add the missing indicator data for the companies that don't need to
         be fully updated. This will just append the new data to your already created 
         indicator dataframes.
         
--------------------------------------------------------------------------------------------------------

# Credits

    1. Following functions thanks to https://gist.github.com/jckantor/d100a028027c5a6b8340:
          - NYSE_tradingdays()
          - NYSE_holidays()
          - NYSE_tradingdays2()
          - NYSE_holidays2()
       
       This set of functions is used to calculate past and future trading days, making sure 
       to adjust for trading holidays and such. The first set of functions, NYSE_tradingdays() 
       and NYSE_holidays() is the original functions as was created entirely by jckantor, 
       while the second set was altered by me to adjust for a specific requirement I needed, 
       but was based entirely off the original so thanks to jckantor for providing this set 
       of extremley helpful trading functions!!
       
    2. Following package thanks to https://github.com/hongtaocai/googlefinance:
          - googlefinance
          
       This package allowed for retrieving real-time stock data from Google's finance servers 
       that allowed this project to calculate real-time indicators. It also allowed for 
       getting year's worth of news data for those companies up to present. Thanks again, 
       this project wouldn't exist if it weren't for them!
       
    3. Following package thanks to https://github.com/lukaszbanasiak/yahoo-finance:
          - yahoofinance
          
       This package allowed for providing information for each company when deciding which 
       companies to track. Thanks to lukaszbanasiak for making this package public!
       
    4. Following package thanks to https://github.com/quandl/quandl-python:
          - quandl
          
       Quandl provides all kinds of data that is both free and pay. They are one of the 
       leading trading data providers out there, so check them out if interested. For my 
       portion of the project, I utilize there adjusted closing prices for use if a 
       company has a dividend or stock split you need to adjust for. Thanks to them for 
       providing that useful free data!
       
    5. Following functions thanks to Dennis Atabay at https://pyrenn.readthedocs.io/en/latest/:
          - create_neural_network()
          - create_weight_vector()
          - convert_matrices_to_vector()
          - convert_vector_to_matrices()
          - get_network_output()
          - RTRL()
          - prepare_data()
          - train_LM()
          - calc_error()
          - NNOut()
          
       These functions allowed for utilizing real-time recurrent learning of neural nets. 
       These were out of a package called Pyrenn. There is a lot more functionality from 
       that package so check it out. These functions have been altered to use more 
       descriptive naming of variables and functions, for both learning purposes and for 
       anyone checking out this package who wanted a little easier to follow group of 
       functions.
       
       One major change was in RTRL(), the dictionaries 
       deriv_layer_outputs_respect_weight_vect, and sensitivity_matrix. These 
       dictionaries started to cause issues when training on more than 10,000 data 
       records at a time. Due to the way they were set up, these functions would 
       continuously add key/values to there dictionaries after calculating those 
       particular values. The issue arose because the function only needed to keep enough 
       to calculate up to the largest delay. What this meant was that rather than keeping 
       tens of thousands of data keys/values in a dictionary these dictionaries, we could 
       just keep, for example, the previous 5 key/value pairs that were needed for 
       calculating with delays but no more. What resulted was massive performance rewards 
       in terms of memory consumption, and as a result of significantly less memory 
       consumption, computing time as well. That being said, this project wouldn't have 
       been possible if not for them, so thanks again!!
       
    6. Finally, thanks to everyone at http://thebonnotgang.com/tbg/ for providing FREE 
       INTRADAY DATA!!!! This was probably the most amazing find of this project. Prior 
       to this, I was working on daily stock values, rather than intraday, so when I 
       found these guys, I couldn't have been happier. Please Please Please check out 
       there site, they provide apps, and all sorts of help. These guys were a lifesaver 
       so show them some love! They are the only guys I was able to find on here who 
       provided free intraday data, so if you're poor like me and ever need intraday 
       data, check them out!