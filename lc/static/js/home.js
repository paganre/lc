function login(){
    if($("#login-container").hasClass("dp-none")){
	$("#login-container").removeClass("dp-none");
	h = $(window).height();
	if($("#login-modal").height() < h){
	    $("#login-modal").css("top", (h-$("#login-modal").height())/4);
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