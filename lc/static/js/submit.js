var displaying_response = 0;

function submitLink(){
    link = $("#link-field").val();
    $.ajax({
            url: 'link/',
                type: 'POST',
                data: {'link':link},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
		    if(displaying_response == 0){
			$("#submit-container").append(response.html);
			displaying_response = 1;
		    }else{
			$("#parsed-url").remove();
			$("#submit-container").append(response.html);
		    }
		}else{
                    alert(response.error);
                }
            }
        });
    return false;
}