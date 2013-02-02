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
		}else{
                    alert(response.error);
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
                }else{
                    alert(response.error);
                }
            }
        });
    return false;
}