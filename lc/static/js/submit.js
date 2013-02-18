var selected_link;
var suggested_title;
var domain;

function submitLink(){
    link = $("#link-field").val();
    selected_link = link;
    $.ajax({
            url: '/link/',
                type: 'POST',
                data: {'link':link},
                success: function(response) {
                response = JSON.parse(response);
                if(response.html){
		    $("#submit-container").html(response.html);
		    suggested_title = $("#title-field").val();
		    domain = $("#domain-label").html();
            domain = domain.substr(1,domain.length-2)
            }else if(response.error=='check url'){
             if($("#error-label").hasClass("dp-none")){
             $("#error-label").removeClass("dp-none");}
            $("#error-label").html("urlde sorun var, baska link dene");
            }else if(response.error=='not authed'){
             if($("#error-label").hasClass("dp-none")){
             $("#error-label").removeClass("dp-none");}
            $("#error-label").html("uye girisi gerekli");
            }else{
             if($("#error-label").hasClass("dp-none")){
             $("#error-label").removeClass("dp-none");}
            $("#error-label").html("olmadi :( bir daha dene");
            }
            }
        });
    return false;
}

function createThread(){
    title = $("#title-field").val();
    summary = $("#summary-field").val();
    if(summary.length > 250){
	summary = summary.substring(0,247)+"...";
    }
    $.ajax({
            url: '/create/',
                type: 'POST',
                data: {'link':selected_link,'summary':summary,'title':title,'suggested':suggested_title,'domain':domain},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    window.location = '/t/'+response.tid;
                }else if(response.error=='texists'){
                    if($("#thlink").hasClass("dp-none")){
                    $("#thlink").removeClass("dp-none");}
                    $("#thlink").attr("href", "/t/"+response.tid)
                }else{
                    alert(response.error);
                }
            }
        });
    return false;
}