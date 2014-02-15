
var g_data;
var g_source;
var g_mutant;

function xx_highlightMutant(m_id) {
    if(g_data === undefined || g_source == undefined)
	return;

    var date = new Date(g_data.timestamp * 1000);

    $('#timestamp').text(date.toLocaleDateString() + ' ' + date.toLocaleTimeString());
    $('#md5').text(g_data.md5);
    $('#filename').text(g_data.filename);
    $("#report").text(g_data.name);

    var src = g_source;
    g_mutant = undefined;

    for(var i=0; i<g_data.mutants.length; i++) {
	var mutant = g_data.mutants[i];

	prefix = g_source.substring(0, mutant.start);
	postfix = g_source.substring(mutant.stop);
	original = g_source.substring(mutant.start, mutant.stop);

	if($('#current_mutant').css('display') == 'none') {
	    $('#current_mutant').append(
		$('<option>', {
		    value: mutant.id,
		    text: '#' + mutant.id + " ('" + original + "' ==> '" + mutant.value + "')"
		})
	    );
	}

	if(m_id == mutant.id) {
	    src = prefix + mutant.value + postfix;
	    g_mutant = new Object();

	    g_mutant.id = mutant.id;
	    g_mutant.original = original;
	    g_mutant.value = mutant.value;
	    g_mutant.line = mutant.line;
	    g_mutant.start = mutant.start;
	    g_mutant.stop = mutant.start + mutant.value.length;
	}
    }

    if(g_mutant == undefined)
	$("#current_mutant").val(0);
    else
	$("#current_mutant").val(g_mutant.id);

    $('#code').hide();
    $('#code').text(src);
 
    sh_highlightDocument();
 
    $("#current_mutant").show();
    $('#info').show();
    $('#code').show();

    $(".xx_mutation").each(function(i, obj) {
	if(i == 0) {
	    $('#popup').text(g_mutant.original);
	    obj.id = g_mutant.id;
	}

	$(this).mouseover(function() {
	    $('#popup').show();
	});

	$(this).mouseout(function() {
	    $('#popup').hide();
	});
    });

    if(g_mutant != undefined) { 
	var o = $("#" + m_id);

	$(document).bind('mousemove', function(e){
	    $('#popup').css({
		left:  e.pageX,
		top:   e.pageY
	    });
	});

	window.scrollTo(0, o.get(0).offsetTop - 30);
    }
}

function xx_load(base) {
    url = base + '.json?r=' + Math.random();

    $.getJSON(url, function(data) {
	g_data = data;
	xx_highlightMutant(window.location.hash.substring(1));
    });

    url = base + '.p?r=' + Math.random();

    $.get(url, function(data) {
	g_source = data;
	xx_highlightMutant(window.location.hash.substring(1));
    });

    $('#current_mutant').change(function() {
	window.location.hash = $('#current_mutant').val();
	xx_highlightMutant($('#current_mutant').val());
    });

    var top = $('#info').offset().top - parseFloat($('#info').css('marginTop').replace(/auto/, 0));
    var left = $(window).width() - $('#info').width() - 30;
 
    $('#info').css('left', left);
    $('#info').css('top', top);

    $(window).scroll(function (event) {

	if ($(this).scrollTop() >= top)
	    $('#info').addClass('fixed');
	else
	    $('#info').removeClass('fixed');
    });
}