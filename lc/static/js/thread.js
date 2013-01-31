function highlight(){
    id = $(this).attr('id').substring(6);
    $("#com"+id).css("background","white");
}
function removeHighlight(){
    id = $(this).attr('id').substring(6);
    $("#com"+id).css("background","");
}

function toggleComment(id){
    $("#com"+id).toggleClass("comment-hidden");
    if($("#com"+id).hasClass("comment-hidden")){
	$("#togcom"+id).html("[ac]");
    }else{
	$("#togcom"+id).html("[kapa]");
    }
    return false;
}

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
		    appendComment(response.id,tid,id);
                }else{
                    $("#rpllabel"+id).html("bi sorun cikti: "+response.error);
                }

            }
        });
}

function appendComment(cid,tid,pid){
    $.ajax({
            url: '/retrieve/',
                type: 'POST',
                data: {'type':'comment','page':'thread','id':cid,'tid':tid},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    $("#com"+pid).append(response.html);
		    if(!$("#rpl-wrap"+pid).hasClass("dp-none")){
			toggleReply(pid);
		    }
		}else{
                    $("#rpllabel"+pid).html("bi problem cikti: "+response.error);
                }

            }
        });
}