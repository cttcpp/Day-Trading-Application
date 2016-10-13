from sys import stdout
from dateutil import rrule 
import cPickle as pickle
import pandas as pd
import numpy as np
import datetime
import urllib
import time
import os

def get_short_index(short):
    """
    Get the second the earliest and latest dates so you can update the shortened dictionary
    after each trading day to adjust for the new days data and still be the same length.
    """
    short_dict = {}
    # For each stock
    for key, value in short.iteritems():
        # Get the stock index and get the first and last date in yyyy-mm-dd format
        index  = value.index
        start  = datetime.datetime.strptime((str(index[0])[:10]), '%Y-%m-%d').date()
        end    = datetime.datetime.strptime((str(index[-1])[:10]), '%Y-%m-%d').date()
        # Call our trading days function to get the dates between those days
        rs2    = NYSE_tradingdays2(start, end)
        # Number of stock days within those dates
        length = len(rs2[:])
        # The second to earliest date
        new_date = str(rs2[1])[:10]
        # The second to latest date
        new_end  = str(rs2[length-2])[:10]
        short_dict[key] = [new_date, new_end]
    return short_dict

def resample_intraday(hlc):
    """
    Make the indexes the same for each company, meaning we resample the times to be at the 
    beginning of each minute, rather than sometime during that minute.
    """
    new_hlc, count = {}, 0
    for key, value in hlc.iteritems():
        new_df = pd.DataFrame()

        # Ensure we don't have duplicate rows that curiously occurred several times
        value  = value.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
        # Take our index from our dataframe and convert the first and last timestamps
        # to yyyy-mm-dd format getting rid of the time after the date
        index  = value.index
        start  = datetime.datetime.strptime((str(index[0])[:10]), '%Y-%m-%d').date()
        end    = datetime.datetime.strptime((str(index[-1])[:10]), '%Y-%m-%d').date()
        # Call our trading days function that will give us a list of trading days 
        # between our two given dates we feed it.
        rs2    = NYSE_tradingdays2(start, end)
        # How many trading days between the two dates
        length = len(rs2[:])

        for x in range(length):
            # For each trading timestamp, first convert to date only in str format instead
            # of both date and time which is given as 00:00:00
            date   = str(rs2[x])[:10]
            # Retrieve that date's values from our dataframe
            day    = value[date]
            # Resample each day, setting the time value to be the top of every minute
            # This was done to match datetimes since dataframes usually were a second 
            # or two off between companies which meant it was harder to call a datetime
            # for one or more companies at once.
            reday  = day.resample('T').pad().fillna(method='bfill')
            # Series are mutable, so we need to create a new dataframe with this new series
            new_df = new_df.append(reday)  

        new_hlc[key] = new_df
        stdout.write("\r%d" % count)
        stdout.flush() 
        count += 1
    return new_hlc

#### # Credit to https://gist.github.com/jckantor/d100a028027c5a6b8340 ######
def NYSE_holidays(a = datetime.date.today() - datetime.timedelta(days=372), 
                  b = datetime.date.today() + datetime.timedelta(days=365)): 
    
    # Generate ruleset for holiday observances on the NYSE 
    rs = rrule.rruleset()
    
    # Include all potential holiday observances 
    ###############################################
    
    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=31, 
                         byweekday=rrule.FR))               
    # New Years Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=1))                                    
    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=2, 
                         byweekday=rrule.MO))                   
    # MLK Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,
                         byweekday=rrule.MO(3)))                            
    # Washington's Bday
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=2,
                         byweekday=rrule.MO(3)))                          
    # Good Friday 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,byeaster=-2)) 
    # Memorial Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=5, 
                         byweekday=rrule.MO(-1)))                        
    # Independence Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=3, 
                         byweekday=rrule.FR))              
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=4))                                   
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=5, 
                         byweekday=rrule.MO))               
    # Labor Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=9, 
                         byweekday=rrule.MO(1)))                          
    # Thanksgiving Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=11, 
                         byweekday=rrule.TH(4)))                          
    # Christmas 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=24, 
                         byweekday=rrule.FR))                
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=25))                                     
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=26, 
                         byweekday=rrule.MO))                
    ######################################################

    # Exclude potential holidays that fall on weekends 
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,until=b,
                          byweekday=(rrule.SA,rrule.SU))) 
    return rs 

def NYSE_tradingdays(a = datetime.date.today() - datetime.timedelta(days=372), 
                     b = datetime.date.today() + datetime.timedelta(days=365)): 
    # Generate ruleset for NYSE trading days 
    rs = rrule.rruleset() 
    rs.rrule(rrule.rrule(rrule.DAILY,dtstart=a,until=b)) 
    
    # Exclude weekends and holidays 
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,byweekday=(rrule.SA,rrule.SU)))
    rs.exrule(NYSE_holidays(a, b)) 
    
    return rs 

def NYSE_holidays2(a, b): 
    # Generate ruleset for holiday observances on the NYSE 
    rs = rrule.rruleset()
     
    # Include all potential holiday observances 
    ###############################################

    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=31, 
                         byweekday=rrule.FR))   
    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=1))  
    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=2, 
                         byweekday=rrule.MO))               
    # MLK Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,
                         byweekday=rrule.MO(3)))         
    # Washington's Bday
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=2,
                         byweekday=rrule.MO(3)))   
    # Good Friday
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,byeaster=-2)) 
    # Memorial Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=5, 
                         byweekday=rrule.MO(-1)))         
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=3, 
                         byweekday=rrule.FR))       
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=4))  
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=5, 
                         byweekday=rrule.MO))   
    # Labor Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=9, 
                         byweekday=rrule.MO(1)))   
    # Thanksgiving Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=11, 
                         byweekday=rrule.TH(4))) 
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=24, 
                         byweekday=rrule.FR))  
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=25))  
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=26, 
                         byweekday=rrule.MO))                

    ######################################################
    # Exclude potential holidays that fall on weekends
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,until=b,
                          byweekday=(rrule.SA,rrule.SU))) 
    return rs 

def NYSE_tradingdays2(a, b): 
    # Generate ruleset for NYSE trading days 
    rs = rrule.rruleset() 
    rs.rrule(rrule.rrule(rrule.DAILY,dtstart=a,until=b)) 
    
    # Exclude weekends and holidays 
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,byweekday=(rrule.SA,rrule.SU)))
    rs.exrule(NYSE_holidays2(a, b)) 
    
    return rs
	
def NYSE_holidays3(a = datetime.date.today() - datetime.timedelta(days=390), 
                  b = datetime.date.today() + datetime.timedelta(days=365)): 
    
    # Generate ruleset for holiday observances on the NYSE 
    rs = rrule.rruleset()
    
    # Include all potential holiday observances 
    ###############################################
    
    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=31, 
                         byweekday=rrule.FR))               
    # New Years Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=1))
    # New Years Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=2, 
                         byweekday=rrule.MO))                   
    # MLK Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,
                         byweekday=rrule.MO(3)))                            
    # Washington's Bday
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=2,
                         byweekday=rrule.MO(3)))                          
    # Good Friday 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,byeaster=-2)) 
    # Memorial Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=5, 
                         byweekday=rrule.MO(-1)))                        
    # Independence Day 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=3, 
                         byweekday=rrule.FR))              
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=4))
    # Independence Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=5, 
                         byweekday=rrule.MO))               
    # Labor Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=9, 
                         byweekday=rrule.MO(1)))                          
    # Thanksgiving Day
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=11, 
                         byweekday=rrule.TH(4)))                          
    # Christmas 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=24, 
                         byweekday=rrule.FR))                
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=25))
    # Christmas
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=26, 
                         byweekday=rrule.MO))                
    ######################################################

    # Exclude potential holidays that fall on weekends 
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,until=b,
                          byweekday=(rrule.SA,rrule.SU))) 
    return rs 

def NYSE_tradingdays3(a = datetime.date.today() - datetime.timedelta(days=390), 
                     b = datetime.date.today() + datetime.timedelta(days=365)): 
    # Generate ruleset for NYSE trading days 
    rs = rrule.rruleset() 
    rs.rrule(rrule.rrule(rrule.DAILY,dtstart=a,until=b)) 
    
    # Exclude weekends and holidays 
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,byweekday=(rrule.SA,rrule.SU)))
    rs.exrule(NYSE_holidays3(a, b)) 
    
    return rs
########################################################################

def create_prd_lst(highlowclose, prd_lst, prd_lst_nums, 
                    prd_lst_nums2, prd_lst_nums3, prd_lst_nums4):
    """
    Each company has it's own period list which is how many minutes encompass each
    different period length. There are differences between companies because of about
    20 missing days worth of data in the past 3 years that several companies have and 
    this is meant to adjust for those differences by getting the length of the period
    between each date range that have been already adjusted for the missing days for that 
    company. 
    
    We then are left with the length of, for example, a 30 day period, which adjusted
    for missing days may mean we take the length between 31 days worth of period, that
    because of the missing data is then the correct 30 day period length. We do this for
    each length and then combine these lengths onto the three day length lists which are
    already set up. 
    
    There are four different lists for each company because the different indicators have
    different starting values and more periods. For example, the first lst is the base and 
    is used for almost all the indicators, but the third one is used for MAC indicators. For 
    those, there are 3 extra, 2 at the beginning, 6 and 8, and one at the end, 350. The last
    lst is used for return values.
    """
    prd_dict  = {}
    # For each stock
    for name in highlowclose.keys():
        # Get the closing prices series to use for calculating lengths
        close = highlowclose[name]['Closes']
        
        len_p  = []
        all_l  = []
        # For each in the period list dictionary, use that date to calculate the 
        # length in stock minutes from that date to present, appending each to a
        # list, and then add that to each of the 4 different stock minute lists
        for each in prd_lst[name]:
            len_p.append(len(close[each:]))

        lst1 = prd_lst_nums  + len_p
        lst2 = prd_lst_nums2 + len_p
        lst3 = prd_lst_nums3 + len_p
        lst4 = prd_lst_nums4 + len_p
        
        # Append each of our lists together and store this in our period dictionary
        # using the stock symbol as the key
        all_l.append(lst1)
        all_l.append(lst2)
        all_l.append(lst3)
        all_l.append(lst4)
        
        prd_dict[name] = all_l
    return prd_dict

def create_prd_lst2(highlowclose, prd_lst, prd_lst_nums, 
                    prd_lst_nums2, prd_lst_nums3):
    """
    There are three different lists for each company because the different indicators have
    different starting values and more periods. For example, the first lst is the base and 
    is used for almost all the indicators, but the third one is used for MAC indicators. For 
    those, there are 3 extra, 2 at the beginning, 6 and 8, and one at the end, 350.
    """
    prd_dict  = {}
    # For each stock
    for name in highlowclose.keys():
        # Get the closing prices series to use for calculating lengths
        close = highlowclose[name]['Closes']

        len_p, all_l = [], []
        # For each in the period list dictionary, use that date to calculate the 
        # length in stock minutes from that date to present, appending each to a
        # list, and then add that to each of the 3 different stock minute lists
        for each in prd_lst[name]:
            len_p.append(len(close[each:]))

        lst1 = prd_lst_nums  + len_p
        lst2 = prd_lst_nums2 + len_p
        lst3 = prd_lst_nums3 + len_p

        # Append each of our lists together and store this in our period dictionary
        # using the stock symbol as the key
        all_l.append(lst1)
        all_l.append(lst2)
        all_l.append(lst3)
        
        prd_dict[name] = all_l
    return prd_dict