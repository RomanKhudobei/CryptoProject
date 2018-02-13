$('#get-coin-button').click(function() {
	//var address = 'address goes here';
	$.ajax({
		type: 'GET',
		url: '/get_coin?state=' + $('#state').text().trim(' '),
		success: function(result) {
					switch (result.status) {

						case "OK":
							$('#qr-code').append('<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + result.coin + '">');
							$('#coin-string').text(result.coin);
							$('#copy-button-wrap').html(
								`<button class="btn btn-default btn-xs" id="copy-button" data-clipboard-target="#coin-string">
									Copy
								</button>`
							);
							var clipboard = new Clipboard('#copy-button');
							$('#copy-button').click(function() {
								$(this).text("Copied");
								$(this).removeClass("btn-default");
								$(this).addClass("btn-success");
							});
							$('#get-coin-button').text('Get Another Coin');
							break

						case "Error":
							$('#flash-message').html(
								`<div class="alert alert-info fade in" role="alert">
									<strong>%message%</strong>
									<button type="button" class="close" data-dismiss="alert" aria-label="Close">
										<span aria-hidden="true">&times;</span>
									</button>
								</div>`.replace('%message%', result.description)
							);
							break
					};
				}
	});
});
