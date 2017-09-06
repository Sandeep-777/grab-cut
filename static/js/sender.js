$(function() {
	//initialize canvas, one for image and another for drawing paths
	var canvas = document.getElementById('myCanvas');
	var canvas2 = document.getElementById('myCanvas2');
	var canvas3 = document.getElementById('myCanvas3');
	
	var canvaswidth = canvas.width;
	var canvasheight = canvas.height;
	var imagewidth = canvas.width;
	var imageheight = canvas.height;
	
	var ctx = canvas.getContext('2d');
	var ctx2 = canvas2.getContext('2d');
	var ctx3 = canvas3.getContext('2d');
	
	//some global constants
	var max_val = Number.MAX_VALUE;
	
	//for loading images
	var loader = document.getElementById("uploadimage");
	var orig_img_data = null;
	var output_mask_img = null;
	
	//for drawing in canvas
	var clickX = new Array();
	var clickY = new Array();
	var clickDrag = new Array();
	var clicks = new Array();
	var paint = 0;
	
	var drawRect = false;
	var drawingRect = false;
	var rectX = 0;
	var rectY = 0;
	var rectW = 0;
	var rectH = 0;
	
	var drawBG = false;
	var drawFG = false;
	var strokeColor = 'rgba(255,255,255,1)';
	
	//reader function
	function readImage(file) {
		var reader = new FileReader();
		reader.addEventListener("load", function() {
			var image = new Image();
			var f = document.getElementById("uploadimage").files[0];
			var url = window.URL || window.webkitURL;
			var src = url.createObjectURL(f);

			useBlob = false && window.URL;
			image.addEventListener("load", function() {
				if (useBlob) {
					window.URL.revokeObjectURL(image.src);
				}
			});
			image.src = useBlob ? window.URL.createObjectURL(file) : reader.result;
			image.src = src;
			image.onload = function() {
				//expand canvas sizes according to image
				canvas.width = image.width;
				canvas.height = image.height;
				canvas2.width = image.width;
				canvas2.height = image.height;
				canvas3.width = image.width;
				canvas3.height = image.height;
				canvaswidth = canvas.width;
				canvasheight = canvas.height;
				
				//clear and draw images
				ctx.clearRect(0, 0, canvas.width, canvas.height);
				ctx2.clearRect(0, 0, canvas.width, canvas.height);
				ctx3.clearRect(0, 0, canvas.width, canvas.height);
				ctx.drawImage(image, 0, 0);
				//store pixel information
				orig_img_data = ctx.getImageData(0, 0, canvas.width, canvas.height);
				//creating cost function of the image for each pixels
				upload(canvas, 'canvasImage','/upload');
				// document.getElementsByTagName('form')[0].submit();
			};
		});
		//varibles to store the user input
		init_canvases();
		reader.readAsDataURL(file);
	}
	function init_canvases(){
		clickX = new Array();
		clickY = new Array();
		clickDrag = new Array();
		clicks = new Array();
		paint = 0;
		
		drawRect = false;
		drawingRect = false;
		rectX = 0;
		rectY = 0;
		rectW = 0;
		rectH = 0;
	}
	function upload(canvas, name, url) {
		var dataURL = canvas.toDataURL('image/png', 0.5);
		var blob = dataURItoBlob(dataURL);
		var fd = new FormData(document.forms[0]);
		fd.append(name, blob);
		// console.log(fd);
		$.ajax({
			type : "POST",
			url : url,
			data: fd,
			// data : new FormData($('#img-form')[0]),
			processData : false,
			contentType : false,
			success : function(data) {
				console.log(data);
			},
			error : function(data) {
				console.log(data);
			}
		}); 
	}
	//mouse functions
	function getMousePos(canvas, evt) {
		var rect = canvas2.getBoundingClientRect();
		return {
			x : evt.clientX - rect.left,
			y : evt.clientY - rect.top
		};
	}
	
	
	//event listeners
	loader.addEventListener("change", function() {
		var files = this.files;
		var errors = "";
		if (!files) {
			errors += "File upload not supported by your browser.";
		}
		if (files && files[0]) {
			for (var i = 0; i < files.length; i++) {
				var file = files[i];
				if ((/\.(png|jpeg|jpg)$/i).test(file.name)) {
					readImage(file);
				} else {
					errors += file.name + " Unsupported Image extension\n";
				}
			}
		}
		if (errors) {
			alert(errors);
		}
	});
	//for drawing outline in canvas
	$('#myCanvas3').mousedown(function(e) {
		var mousePos = getMousePos(canvas2, e);
		if(drawRect){
			rectX = parseInt(mousePos.x);
			rectY = parseInt(mousePos.y);
			drawingRect = true;
		} else if(drawBG||drawFG){
			addClick(mousePos.x, mousePos.y);
			clicks = remove_redundant(clicks);
			paint++;
			redraw(e);
		}
	});
	
	$('#myCanvas3').mousemove(function(e) {
		var mousePos = getMousePos(canvas2, e);
		if(drawRect){
			if (!drawingRect) {
				return;
			}
			rectW = parseInt(mousePos.x) - rectX;
			rectH = parseInt(mousePos.y) - rectY;
			ctx3.clearRect(0, 0, canvas.width, canvas.height);
			ctx3.restore();
			ctx3.strokeRect(rectX, rectY, rectW, rectH);
			// console.log('x '+rectX+' y '+rectY+' w '+rectW+' h '+rectH );
		}else if(drawBG||drawFG){
			if (paint) {
				paint++;
				addClick(mousePos.x, mousePos.y, true);
				clicks = remove_redundant(clicks);
				redraw(e);
			}
		}
	});
	
	$('#myCanvas3').mouseup(function(e) {
		e.preventDefault();
		e.stopPropagation();
		if(drawRect){
			drawingRect = false;
		}else if(drawBG||drawFG){
			paint = 0;
		}
	});
	
	$('#myCanvas3').mouseleave(function(e) {
		e.preventDefault();
		e.stopPropagation();
		if(drawRect){
			drawingRect = false;
		}else if(drawBG||drawFG){
			paint = 0;
		}
	});
	
	//storing click information from user
	function addClick(x, y, dragging) {
		clickX.push(x);
		clickY.push(y);
		clicks.push(parseInt((y)*imagewidth+(x)));
		clickDrag.push(dragging);
	}
	
	//removing duplicate elements, pixels clicked by user
	function remove_redundant(arr) {
		if (arr.length === 0) return arr;
			arr = arr.sort(function (a, b) { return a*1 - b*1; });
			var ret = [arr[0]];
			for (var i = 1; i < arr.length; i++) { // start loop at 1 as element 0 can never be a duplicate
				if (arr[i-1] !== arr[i]) {
					ret.push(arr[i]);
			}
		}
		return ret;
	}
	/* used to paint on canvas, canvas is not cleared but its state is saved everytime function is called */
	function redraw(e) {
		var mousePos = getMousePos(canvas, e);
		ctx2.beginPath();
		ctx2.strokeStyle = strokeColor;
		ctx2.lineJoin = "round";
		ctx2.lineWidth = 20;
		if (paint > 1) {
			// 2*clickX[n-1] - clickX[n-2] is used to draw line of correct length while dragging
			ctx2.moveTo(2 * clickX[clickX.length - 1] - clickX[clickX.length - 2], 2 * clickY[clickY.length - 1] - clickY[clickY.length - 2]);
		} else {
			//used to draw dot
			ctx2.moveTo(clickX[clickX.length - 1] - 1, clickY[clickY.length - 1] - 1);
		}
		// line drawn to current mouse position
		ctx2.lineTo(mousePos.x, mousePos.y);
		ctx2.closePath();
		ctx2.stroke();
		ctx2.save();
	}
	
	
	$('#rect-btn').click(function() {
		ctx3.strokeStyle = "rgba(0, 0, 255, 1)";
		ctx3.lineJoin = "miter";
		ctx3.lineWidth = 5;
		drawBG = false;
		drawFG = false;
		if(!drawRect){
			drawRect = true;
			$('.current_select').removeClass('selected-rect');
			$(this).addClass('current_select');
			$(this).addClass('selected-rect');
		}else{
			drawRect = false;
			$(this).removeClass('current_select');
			$(this).removeClass('selected-rect');
		}
	});
	
	function dataURItoBlob(dataURI) {
		// convert base64/URLEncoded data component to raw binary data held in a string
		var byteString;
		if (dataURI.split(',')[0].indexOf('base64') >= 0)
			byteString = atob(dataURI.split(',')[1]);
		else
			byteString = unescape(dataURI.split(',')[1]);
		// separate out the mime component
		var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
		// write the bytes of the string to a typed array
		var ia = new Uint8Array(byteString.length);
		for (var i = 0; i < byteString.length; i++) {
			ia[i] = byteString.charCodeAt(i);
		}
		return new Blob([ia], {
			type : mimeString
		});
	}

	$('#draw-fg').click(function(){
		drawingRect = false;
		drawBG = false;
		if(!drawFG){
			drawFG = true;
			strokeColor = 'rgba(0,255,0,1)';
			$('.current_select').removeClass('selected-rect');
			$(this).addClass('current_select');
			$(this).addClass('selected-rect');
		}else{
			drawFG = false;
			$(this).removeClass('current_select');
			$(this).removeClass('selected-rect');
		}
	});
	$('#draw-bg').click(function(){
		drawingRect = false;
		drawFG = false;
		if(!drawBG){
			drawBG = true;
			strokeColor = 'rgba(255,0,0,1)';
			$('.current_select').removeClass('selected-rect');
			$(this).addClass('current_select');
			$(this).addClass('selected-rect');
		}else{
			drawBG = false;
			$(this).removeClass('current_select');
			$(this).removeClass('selected-rect');
		}
	});
	$('#segment-btn').click(function() {
		var dataURL = canvas2.toDataURL('image/png', 0.5);
		var blob = dataURItoBlob(dataURL);
		var fd = new FormData(document.forms[0]);
		fd.append("canvasImage", blob);
		// console.log(fd);
		$.ajax({
			type : "POST",
			url : '/uploadmask',
			data: fd,
			// data : new FormData($('#img-form')[0]),
			processData : false,
			contentType : false,
			success : function(data) {
				console.log(data);
			},
			error : function(data) {
				console.log(data);
			}
		}); 
		
		var ndata = {x_0: rectX, y_0:rectY, width: rectW, height:rectH};
		$.ajax({
			type : "POST",
			url : '/uploadrect',
			data: JSON.stringify(ndata),
			dataType: 'json',
			contentType : 'application/json',
			success : function(data) {
				console.log(data);
			},
			error : function(data) {
				console.log(data);
			}
		});
		// $.get( "/segment", function( data ) {
			// // alert(typeof(data));
			// console.log(data);
			// // ctx.clearRect(0, 0, canvas.width, canvas.height);
			// // ctx.drawImage(data, 0, 0);
			// $('body').append('<img src="data:image/png;base64,' + data + '" />');
		// });
		var img = $("<img />").attr('src', '/segment').on('load', function() {
			if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
				alert('broken image!');
			} else {
				$("#something").append(img);
			}
		}); 
		$("#image-container").append(img);
	});
});
