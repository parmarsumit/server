
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
  if ( $(e.currentTarget).data('action') && $(e.currentTarget).data('uid') ){
    var action = $(e.currentTarget).data('action');
    var uid = $(e.currentTarget).data('uid');

    var payload = {context:window.context, action:action, path:$(e.currentTarget).attr('href'), 'ext':'.html'}
    console.log('Sending ', payload);

    var app_event = new CustomEvent('ws-send', {'detail':payload});
    document.body.dispatchEvent(app_event);
  } else {
    loadUrl(url, target);
  }
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
    console.log(content.data('close'));

  //  $(target).modal('hide');
  //  return;
  }
  //console.log('Closing ?',);
  //console.log(content.data('close'))

  if (content.data('close')){
      console.log('Closing ...',);
      $(target).modal('hide');
      if (!redirect){
        window.popReload(window.location.href);
      }
  }

  //
  var signatureRequired = content.data('require-signature');
  var transactionRequired = content.data('require-transaction');

  var defaultAccount = content.data('account');
  if ( !defaultAccount && ( signatureRequired=='True' || transactionRequired=='True' )){
      window.popReload('/web3.html', '#sidepanel');
  } else {

    //
    $('#content-main').attr('id', 'content-prev');
    
    $(target).html( $(data).find('#content').html() );

    //
    $(target+' a').click(loadNext);

    if (target == '#content'){
      history.pushState( {}, $(data).has('title').text(), url);
      $('#sidepanel').modal('hide');
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

  (function(){
   var serviceLocation = "wss://"+document.location.hostname+":"+document.location.port+"/io.ws";
   var start = function(serviceLocation){
     var ws = new WebSocket(serviceLocation);
     var wsInterface = document.location.hash.slice(1);
     ws.onopen = function() {
        console.log('Connected ...');
        //notie.alert({ text: 'Connected !' });
        var notyf = new Noty({theme: 'relax',
                  type: 'success',
                  timeout: '5000',
                  layout: 'bottomLeft',
                  text: 'Okay, we are online'});
        //
        notyf.show();

        // ask the user to sign in
        if (window.web3) {
          //https://guillaumeduveau.com/fr/blockchain/ethereum/metamask-web3
          // Then replace the old injected version by the latest build of Web3.js version 1.0.0
          window.web3old = window.web3;
          window.web3 = new Web3(window.web3.currentProvider);
          console.log('Got web3 ...');
        } else {
          var infura_url = 'https://ropsten.infura.io/v3/85b874cf0fe74f98a1006219a5e03985';
          //var infura_url = 'http://localhost:7545';
          window.web3 = new Web3(new Web3.providers.HttpProvider(infura_url));
          console.log('Default infura web3 ...');
        }

        // listen for message handshake ?
        var web3 = new Web3();
        var account = web3.eth.accounts.create();

        // listen for calls
        document.body.addEventListener('ws-send', function(event){
          // sign and send
          console.log(event);
          var eventData = event.detail;
          eventData.interface = wsInterface;
          var request = JSON.stringify(event.detail);
          var signature = account.sign(request);
          //console.log(signature);
          ws.send(JSON.stringify(signature));
        });

     };
     ws.onmessage = function (evt) {
        //console.log(evt.data);
        var msg = JSON.parse(evt.data);
        //var app_event = new CustomEvent(msg['action'], {'detail':msg});
        //document.body.dispatchEvent(app_event);
        var mtype = 'success';
        var mtimeout = 15000;
        if (msg.todo){
          mtype = 'warning';
          mtimeout = 0;
        }
        var notyf = new Noty({theme: 'relax',
                  type: mtype,
                  timeout: mtimeout,
                  layout: 'bottomLeft',
                  text: msg.text,
                  callbacks: {
                    onTemplate: function() {
                        this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                        // Important: .noty_body class is required for setText API method.
                    },
                    onShow: function() {
                        $('.noty_body a').click(loadNext);
                    },
                  }
                  }).show();

        if (msg.path){
          //history.pushState( {}, msg.text, msg.path);
        }
        if (msg.ext == '.html'){
          parseResponse(msg.path, '#content', msg.data);
        }
        window.context = msg.context;

        //console.log(msg.text);

        // ws.send( JSON.stringify({action:'index', path:msg.context, 'ext':'/' }) );
     };
     ws.onclose = function(){
       console.log('Connection lost ...');

       var notyf = new Noty({theme: 'relax',
                 type: 'error',
                 timeout: '5000',
                 layout: 'bottomLeft',
                 text: 'Ooops .. looks like something went wrong'});
       notyf.show();

       //notie.alert({ text: 'Connection lost ...' });
       window.ws = null;
       setTimeout(function(){start(serviceLocation)}, 5000);
     }
   };

   var content = $('#content-main');
   var redirect = content.data('redirect');
   var action = content.data('action');
   var uid = content.data('uid');

   stwitch('#content', action, uid);
   start(serviceLocation);
  })();

  $('#sidepanel').on('hide.bs.modal', function(){
     //window.popReload();
  });

});
