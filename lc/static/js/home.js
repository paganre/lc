function sendQuickComment(id){
    text = $("#qcf"+id).val();
    if(text.trim() == ""){
	return false;
    }
    $("#qcf"+id).val('');
    $("#qclabel"+id).removeClass("dp-none");
    $("#qclabel"+id).html("Sending comment...");
    $.ajax({
            url: 'scribe/',
                type: 'POST',
                data: {'text':text,'tid':id},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    $("#qclabel"+id).html("Your comment added");
		    getNewComment(response.id,id);
                }else{
                    $("#qclabel"+id).html("There was an error: "+response.error);
                }

            }
        });
}

function getNewComment(cid,tid){
    // see if the thread has a panel
    has_panel = 1;
    if($("#cp"+tid).length == 0){
	has_panel = 0;
    }
    $.ajax({
            url: 'retrieve/',
                type: 'POST',
                data: {'type':'comment','page':'home','has_panel':has_panel,'id':cid,'tid':tid},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    if(has_panel == 1){
			$("#cmore"+tid).prepend(response.html);
		    }else{
			$("#qcparent"+tid).prepend(response.html);
		    }
                }else{
                    $("#qclabel"+tid).html("There was an error: "+response.error);
                }

            }
        });
    
}

function openQuickComment(id){
    qcd = $("#qcd"+id);
    qcd.toggleClass("dp-none");
    if(qcd.hasClass("dp-none")){
	$("#qct"+id).html("Hizlica-bi-yorum-yaz");
    }else{
	$("#qct"+id).html("Salla");
    }
}

function toggleComment(id){
    icon = $("#tci"+id);
    comment_parent = $("#cpd"+id);
    comment_parent.toggleClass("dp-none");
    if(icon.hasClass("foundicon-minus")){
	//close comment panel
	icon.removeClass("foundicon-minus");
	icon.addClass("foundicon-plus");
    }else{
	//open comment panel
	icon.removeClass("foundicon-plus");
	icon.addClass("foundicon-minus");
    }
}

function login(){
    if($("#login-container").hasClass("dp-none")){
	$("#login-container").removeClass("dp-none");
	h = $(window).height();
	if($("#login-modal").height() < h){
	    $("#login-modal").css("top","50px");
	}
    }
    return false;
}

function loginWith(){
    name = $("#nickname").val();
    password = $("#password").val();
    $.ajax({
            url: 'login/',
		type: 'POST',
		data: {'username':name,'password':password},
                success: function(response) {
		response = JSON.parse(response);
		if(response.result == 0){
		    location.reload();
		}else{
		    showLoginError(response.error);
		}
            }
        });
}

function showLoginError(text){
    $("#login-error").html(text);
    $("#login-error").removeClass("dp-none");
}

function showRegisterError(text){
    $("#register-error").html(text);
    $("#register-error").removeClass("dp-none");
}

function register(){
    name = $("#rnickname").val();
    password = $("#rpassword").val();
    email = $("#remail").val();
    $.ajax({
            url: 'register/',
                type: 'POST',
                data: {'username':name,'password':password,'email':email},
                success: function(response) {
		response = JSON.parse(response);
		if(response.result == 0){
		    location.reload();
		}else{
		    showRegisterError(response.error);
		}
		
            }
        });
}