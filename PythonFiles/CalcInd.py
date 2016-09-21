from dateutil import rrule  
from sys import stdout
import pandas as pd
import numpy as np
import datetime
import urllib
import cPickle as pickle

def get_short_index(short):
    short_dict = {}
    for key, value in short.iteritems():
        index = value.index
        start  = datetime.datetime.strptime((str(index[0])[:10]), '%Y-%m-%d').date()
        end    = datetime.datetime.strptime((str(index[-1])[:10]), '%Y-%m-%d').date()
        rs2    = NYSE_tradingdays2(start, end)
        length = len(rs2[:])
        new_date = str(rs2[1])[:10]
        new_end  = str(rs2[length-2])[:10]
        short_dict[key] = [new_date, new_end]
    return short_dict

def resample_intraday(hlc):
    new_hlc, count = {}, 0
    for key, value in hlc.iteritems():
        new_df = pd.DataFrame()

        value  = value.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
        index  = value.index
        start  = datetime.datetime.strptime((str(index[0])[:10]), '%Y-%m-%d').date()
        end    = datetime.datetime.strptime((str(index[-1])[:10]), '%Y-%m-%d').date()
        rs2    = NYSE_tradingdays2(start, end)
        length = len(rs2[:])

        for x in range(length):
            date   = str(rs2[x])[:10]
            day    = value[date]
            reday  = day.resample('T').pad().fillna(method='bfill')
            new_df = new_df.append(reday)  

        new_hlc[key] = new_df
        stdout.write("\r%d" % count)
        stdout.flush() 
        count += 1
    return new_hlc

def NYSE_holidays2(a, b): 
    rs = rrule.rruleset()
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=31, 
                         byweekday=rrule.FR))   
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=1))  
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,bymonthday=2, 
                         byweekday=rrule.MO))               
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=1,
                         byweekday=rrule.MO(3)))         
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=2,
                         byweekday=rrule.MO(3)))   
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,byeaster=-2)) 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=5, 
                         byweekday=rrule.MO(-1)))         
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=3, 
                         byweekday=rrule.FR))       
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=4))  
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=7,bymonthday=5, 
                         byweekday=rrule.MO))   
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=9, 
                         byweekday=rrule.MO(1)))   
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=11, 
                         byweekday=rrule.TH(4))) 
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=24, 
                         byweekday=rrule.FR))  
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=25))  
    rs.rrule(rrule.rrule(rrule.YEARLY,dtstart=a,until=b,bymonth=12,bymonthday=26, 
                         byweekday=rrule.MO))                
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,until=b,
                          byweekday=(rrule.SA,rrule.SU))) 
    return rs 
def NYSE_tradingdays2(a, b): 
    rs = rrule.rruleset() 
    rs.rrule(rrule.rrule(rrule.DAILY,dtstart=a,until=b)) 
    rs.exrule(rrule.rrule(rrule.WEEKLY,dtstart=a,byweekday=(rrule.SA,rrule.SU)))
    rs.exrule(NYSE_holidays2(a, b)) 
    return rs