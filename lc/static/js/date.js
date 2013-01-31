function getPrettyDate(time){
    now = new Date().getTime();

    sec = (now-time);

    if(sec < 10){
	return "bikac saniye once";
    }else if(sec < 60){
	return "bi dakika once";
    }
    
    min = sec / 60;
    if(Math.round(min) == 1){
	return "bi dakika once";
    }else if(min < 5){
	return "bikac dakika once";
    }else if(min < 60){
	return Math.round(min) + " dakika once";
    }
    
    hour = min / 60;
    if(Math.round(hour) == 1){
	return "bi saat once";
    }else if (hour < 24){
	return Math.round(hour) + " saat once";
    }

    day = hour / 24;
    if (Math.round(day) == 1){
	return "dun";
    }else if(Math.round(day) < 7){
	return Math.round(day)+ " gun once";
    }

    week = day / 7;
    if (Math.round(week) == 1){
	return "gecen hafta";
    }else if(Math.round(week) < 5){
	return Math.round(week)+ " hafta once";
    }
    
    month = day / 30;
    if (Math.round(month) == 1){
	return "gecen ay";
    }else if(month < 12){
	return Math.round(month)+ " ay once";
    }

    year = month / 12;
    if (Math.round(year) == 1){
	return "bi sene once";
    }else{
	return Math.round(year)+ " sene once";
    }

    return "acaip uzun sure once";
}
