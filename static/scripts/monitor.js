$(document).ready(function() {
	document.session = $('#session').val();
	
	setTimeout(requestInventory, 100);
});

function requestInventory() {
	var host = 'ws://10.10.20.134/status?session=' + document.session;
	
	var websocket = new WebSocket(host);
	
	websocket.onopen = function (evt) { };
	websocket.onmessage = function(evt) { 
		$('#switch').attr("src", $.parseJSON(evt.data)['swData']);
		$('#temphum').html($.parseJSON(evt.data)['tempData']);
	};
	websocket.onerror = function (evt) { };
}
