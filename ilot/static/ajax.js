
var loadNext;

function addParameterToURL(url, param){
    //_url = location.href;
    _url = url;
    _url += (_url.split('?')[1] ? '&':'?') + param;
    return _url;
}

function loadNext(e){
  var url = $(e.currentTarget).attr('href');
  var target = "#content";
  if (!url || url == ''){
    return true;
  } else if (url.split('#').length > 1 ){
    return true;
  } else if ( $(e.currentTarget).attr('target') ){
    return true;
  }
  else if ( $(e.currentTarget).hasClass('subpanel') ) {
    target = '#sidepanel';
  }
  else if ( $(e.currentTarget).hasClass('modalpanel') ) {
    target = '#modalpanel';
  }
  else if ( $(e.currentTarget).hasClass('btn-primary') ) {
  //  target = '#modalpanel';
  }
  loadUrl(url, target);
  return false;
}

window.popReload = function(url, target){
  //window.location.replace(url);
  //return;
  if (url){
    if (!target){
      loadUrl(url, "#content");
    } else {
      loadUrl(url, target);
    }
  } else {
    loadUrl(window.location.href, "#content");
  }


};

function extractHostname(url) {
    var hostname;
    //find & remove protocol (http, ftp, etc.) and get hostname

    if (url.indexOf("://") > -1) {
        hostname = url.split('/')[2];
    }
    else {
        hostname = url.split('/')[0];
    }

    //find & remove port number
    hostname = hostname.split(':')[0];
    //find & remove "?"
    hostname = hostname.split('?')[0];

    return hostname;
}


function loadUrl(url, target){

  // check if url is on same domain
  var urlDomain =  extractHostname(url);
  if (urlDomain && document.domain != urlDomain){
    window.open(url, urlDomain);
    return false;
  }

  //$('.modal').modal('hide');
  $('.popover').remove();
  //$('.modal').modal('hide');
  $('.tooltip').remove();

  $.ajax({
      url: url,
      method: 'GET',
      type: 'GET', // For jQuery < 1.9
      statusCode: {
        402: function(response){
          parseResponse(url, target, response.responseText);
        },
        403: function(response){
          parseResponse(url, target, response.responseText);
        },
        401: function(response){
          parseResponse(url, target, response.responseText);
        },
        404: function(response){
          parseResponse(url, target, response.responseText);
        },
        500: function(response){
          parseResponse(url, target, response.responseText);
        },
      },
      success: function(data){
          parseResponse(url, target, data);
      }
  });

};

function parseResponse(url, target, data){

  var content = $(data).find('#content-main');
  var redirect = content.data('redirect');

  var action = content.data('action');
  var uid = content.data('uid');

  if (redirect){
    window.popReload(redirect, '#content');
    console.log('Redirecting ...', redirect);
    console.log(content.data('close'))

  //  $(target).modal('hide');
  //  return;
  }
  //console.log('Closing ?',);
  //console.log(content.data('close'))

  if ( content.data('close')){
      console.log('Closing ...',);
      $(target).modal('hide');
      //if (!redirect){
      //  window.popReload(window.location.href);
      //}
  }

  //
  $(target).html( $(data).find('#content').html() );

  $(target+' a').click(loadNext);

  if (target == '#content'){
    history.pushState( {}, $(data).has('title').text(), url);
  } else {
    document.title = $(data).find('title').text();
  }

  stwitch(target, action, uid);

  if (target == '#modalpanel'){
    $(target).modal('show');
  } else if (target == '#sidepanel') {
    $(target).modal('show');
  } else {
    //$('.modal-backdrop').remove();
  }
  if (target == '#content'){
  //  app.init();
  }
}

window.parseResponse = parseResponse;

$('body a').click(loadNext);

function bind_dates(){

  $('time.moment-from-now').each( function( index ){
    try {
        var datetime = moment( $(this).attr('datetime') );
        $(this).text( datetime.fromNow(false) );
    } catch( err ) {
        console.log(err);
    }
  });

}

function stwitch(target, action, uid) {
    bind_dates();
    $('.message .close')
      .on('click', function() {
        $(this)
          .closest('.message')
          .transition('fade')
        ;
      });

    // handle form submits to panel
    $('#app form').bind('keypress', function(e) {
       if( e.which === 13 )
           return false;
    });
    $('#app form').submit(submitAForm);

    console.log(uid+'/'+action);
    $('#app').trigger({type:'app.switched',
                       action:action,
                       uid:uid});
}

function submitAForm(event){

  event.preventDefault();

  // get form parameters
  var data = new FormData( $(event.currentTarget).closest("form")[0] );

  //
  var target = '#'+$(event.currentTarget).closest('.pane').attr('id');
  var action_url = $(event.currentTarget).attr('action');

  // send it
  $.ajax({
      url: action_url,
      data: data,
      cache: false,
      contentType: false,
      processData: false,
      method: 'POST',
      type: 'POST', // For jQuery < 1.9
      statusCode: {
        402: function(response){
          parseResponse(action_url, target, response.responseText);
        },
        403: function(response){
          parseResponse(action_url, target, response.responseText);
        },
        401: function(response){
          parseResponse(action_url, target, response.responseText);
        },
        404: function(response){
          parseResponse(action_url, target, response.responseText);
        },
      },
      success: function(data){
          parseResponse(action_url, target, data);
      },
    beforeSend:function(){
      $(event.currentTarget).find('fieldset').attr('disabled', true);
    }
  });
  // disable form interactions
  // prevent panel close
  return false;
}

window.submitAForm = submitAForm;
// finally init
$(document).ready(function(){

  Noty.setMaxVisible(10);
  //Noty.setTheme('relax');
  //Noty.setTimeout(4500);
  var content = $('#content-main');
  var redirect = content.data('redirect');
  if (redirect){
    window.popReload(redirect, '#content');
    return;
  }

  window.onpopstate = function(event) {
    //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
    window.popReload(document.location);
  };

  $('#sidepanel').on('hide.bs.modal', function(){
     //window.popReload();
  });

  var content = $('#content-main');
  var redirect = content.data('redirect');
  var action = content.data('action');
  var uid = content.data('uid');
  stwitch('#content', action, uid);

});
