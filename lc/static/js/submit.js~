function submitLink(){
    link = $("#link-field").val();
    $.ajax({
            url: 'link/',
                type: 'POST',
                data: {'link':link},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
		    alert(response.parsed);
                }else{
                    alert(response.error);
                }
            }
        });
    return false;
}