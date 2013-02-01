function sendComment(id){
    text = $("#qcf"+id).val();
    if(text.trim() == ""){
        return false;
    }
    $("#qcf"+id).val('');
    $("#qclabel"+id).removeClass("dp-none");
    $("#qclabel"+id).html("yollaniyo...");
    $.ajax({
            url: '/scribe/',
                type: 'POST',
                data: {'text':text,'tid':id},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    $("#qclabel"+id).html("yorumun eklendi");
                    getNewSubthread(response.id,id);
                }else{
                    $("#qclabel"+id).html("bi problem cikti: "+response.error);
                }

            }
        });
}

function getNewSubthread(cid,tid){
    $.ajax({
            url: '/retrieve/',
                type: 'POST',
                data: {'type':'comment','page':'thread','new':1,'id':cid,'tid':tid},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    $("#subthread-wrap").prepend(response.html);
                }else{
                    $("#qclabel"+tid).html("bi problem cikti: "+response.error);
                }

            }
        });
}

function upvote(id){
    c = 0;
    // check if already upvoted
    if($("#up"+id).hasClass("up-voted")){
	vote = 0;
	c = -1;
    }else{
	vote = 1;
	c = 1;
    }
    $("#up"+id).toggleClass("up-voted");
    if($("#down"+id).hasClass("down-voted")){
	$("#down"+id).removeClass("down-voted");
	c = c+1;
    }
    $.ajax({
            url: '/vote/',
                type: 'POST',
                data: {'cid':id,'vote':vote},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){

                }else{
		    alert(response.error);
                }
            }
        });
    changeCount(id,c);
}

function downvote(id){
    c = 0;
    // check if already downvoted                                                                                                                                                
    if($("#down"+id).hasClass("down-voted")){
        vote = 0;
	c = 1;
    }else{
        vote = -1;
	c = -1;
    }
    $("#down"+id).toggleClass("down-voted");
    if($("#up"+id).hasClass("up-voted")){
	$("#up"+id).removeClass("up-voted");//just-in-case
	c = c-1;
    }
    $.ajax({
            url: '/vote/',
                type: 'POST',
                data: {'cid':id,'vote':vote},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){

                }else{
		    alert(response.error);
                }
            }
        });
    changeCount(id,c);
}

function changeCount(id,c){
    vraw = $("#comvote"+id).html();
    v = parseInt(vraw.substring(1,vraw.length-1));
    v = v +c ;
    $("#comvote"+id).html('['+v+']');
}

function highlightComment(id){
    offset = $("#comuser"+id).offset();
    $("html,body").animate({
	    scrollTop: offset.top,
		scrollLeft: offset.left
		});
    $("#comtext"+id).css("color","royalblue");
    $("#comuser"+id).css("color","royalblue");
}

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
                data: {'type':'comment','page':'thread','new':0,'id':cid,'tid':tid},
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