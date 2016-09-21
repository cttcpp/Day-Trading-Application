from sys import stdout
from dateutil import rrule 
import cPickle as pickle
import pandas as pd
import numpy as np
import datetime
import time
import os

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
########################################################################

def create_prd_lst2(highlowclose, prd_lst, prd_lst_nums, 
                    prd_lst_nums2, prd_lst_nums3):
    """
    There are three different lists for each company because the different indicators have
    different starting values and more periods. For example, the first lst is the base and 
    is used for almost all the indicators, but the third one is used for MAC indicators. For 
    those, there are 3 extra, 2 at the beginning, 6 and 8, and one at the end, 350.
    """
    prd_dict  = {}
    for name in highlowclose.keys():
        close = highlowclose[name]['Closes']
        
        len_p, all_l = [], []
        for each in prd_lst[name]:
            len_p.append(len(close[each:]))
            
        lst1 = prd_lst_nums  + len_p
        lst2 = prd_lst_nums2 + len_p
        lst3 = prd_lst_nums3 + len_p
        
        all_l.append(lst1)
        all_l.append(lst2)
        all_l.append(lst3)
        
        prd_dict[name] = all_l
    return prd_dict