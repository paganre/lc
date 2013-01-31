function toggleReply(id){
    $("#rpl-wrap"+id).toggleClass("dp-none");
    if($("#rpl-wrap"+id).hasClass("dp-none")){
	$("#rpl"+id).html("cevap-yaz");
    }else{
	$("#rpl"+id).html("salla");
    }
}

function sendReply(tid,id){
    text = $("#rpl-field"+id).val().trim();
    if(text == ""){
	return false;
    }
    $("#rpl-field"+id).val('');
    $("#rpllabel"+id).removeClass("dp-none");
    $("#rpllabel"+id).html("yollaniyo...");
    $.ajax({
            url: '/scribe/',
                type: 'POST',
                data: {'text':text,'tid':tid,'parent':id},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    $("#rpllabel"+id).html("cevap eklendi");
                    
                }else{
                    $("#rpllabel"+id).html("bi sorun cikti: "+response.error);
                }

            }
        });
}