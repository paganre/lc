function toggleInlineTag(id){
    $("#tagwrap"+id).toggleClass("dp-none");
    if($("#tagwrap"+id).hasClass("dp-none")){
	$("#tagopen"+id).html("etiketle");
    }else{
	$("#tagopen"+id).html("salla");
	$("#tagalert"+id).addClass('dp-none');
    }
    return false;
}

function tag(id){
    val = $("#tagfield"+id).val().trim();
    $("#tagfield"+id).val('');
    if(val != ''){
	toggleInlineTag(id);
	$("#tagalert"+id).html('oluyo');
	$("#tagalert"+id).removeClass('dp-none');
	$("#tagopen"+id).addClass('dp-none');
	$.ajax({
		url: '/tag/',
		    type: 'POST',
		    data: {'tid':id,'tag':val},
		    success: function(response) {
		    response = JSON.parse(response);
		    if(response.result == 0){
			$("#tagalert"+id).html('oldu');
			setTimeout(function(){tagEnable(id);},2000);
		    }else{
			$("#tagalert"+id).html('olmadi: '+response.error);
			setTimeout(function(){tagEnable(id);},3000);
		    }
		}
	    });
    }
    return false;
}

function tagEnable(id){
    $("#tagopen"+id).removeClass("dp-none");
    $("#tagalert"+id).addClass("dp-none");
}

function removeNot(cid){
    $.ajax({
            url: '/remnot/',
                type: 'POST',
                data: {'cid':cid},
                success: function(response){}});
    $("#notitem"+cid).remove();
}

function checkNot(){
    $.ajax({
            url: '/notif/',
                type: 'GET',
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    dispNot(response.html);
                }else{
                    //alert(response.e);
                }

            }
        });
}

function dispNot(html){
    $("#right-bar").html(html);
}

function sendQuickComment(id){
    text = $("#qcf"+id).val();
    if(text.trim() == ""){
	return false;
    }
    $("#qcf"+id).val('');
    $("#qclabel"+id).removeClass("dp-none");
    $("#qclabel"+id).html("yollaniyo...");
    $.ajax({
            url: 'scribe/',
                type: 'POST',
                data: {'text':text,'tid':id},
                success: function(response) {
                response = JSON.parse(response);
                if(response.result == 0){
                    $("#qclabel"+id).html("yorumun eklendi");
		    getNewComment(response.id,id);
                }else{
                    $("#qclabel"+id).html("bi problem cikti: "+response.error);
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
                    $("#qclabel"+tid).html("bi problem cikti: "+response.error);
                }

            }
        });
    
}

function openQuickComment(id){
    qcd = $("#qcd"+id);
    qcd.toggleClass("dp-none");
    if(qcd.hasClass("dp-none")){
	$("#qct"+id).html("hizlica-bi-yorum-yaz");
    }else{
	$("#qct"+id).html("salla");
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
            url: '/login/',
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
            url: '/register/',
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