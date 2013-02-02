from time import time

def pretty_time(tm):
    current = int(time())
    sec = (current-tm);

    if(sec < 5):
        return "simdik";
    elif(sec < 10):
        return "bikac sn once";
    elif(sec < 60):
        return "azicik once";

    min = sec / 60;
    if(int(round(min)) == 1):
        return "bi dk once";
    elif(min < 5):
        return "bikac dk once";
    elif(min < 60):
        return str(int(round(min))) + " dk once";

    hour = min / 60;
    if(int(round(hour)) == 1):
        return "bi saat once";
    elif (hour < 24):
        return str(int(round(hour))) + " saat once";
    

    day = hour / 24;
    if (int(round(day)) == 1):
        return "dun";
    elif(int(round(day)) < 7):
        return str(int(round(day))) + " gun once";

    week = day / 7;
    if (int(round(week)) == 1):
        return "gecen hafta";
    elif(int(round(week)) < 5):
        return str(int(round(week))) + " hafta once";

    month = day / 30;
    if (int(round(month)) == 1):
        return "gecen ay";
    elif(month < 12):
        return str(int(round(month))) + " ay once";

    year = month / 12;
    if (int(round(year)) == 1):
        return "bi sene once";
    else:
        return str(int(round(year)))+ " sene once";

    return "acaip uzun sure once";
