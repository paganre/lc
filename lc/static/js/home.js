function login(){
    if($("#login-container").hasClass("dp-none")){
	$("#login-container").removeClass("dp-none");
	h = $(window).height();
	if($("#login-modal").height() < h){
	    $("#login-modal").css("top", (h-$("#login-modal").height())/4);
	}
    }
}