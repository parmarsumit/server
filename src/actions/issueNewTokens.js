
$('#app').on('app.switched', function(event){

  if (event.action == 'issueNewTokens'){

    $('#app form').off('submit');
    $('#issueNewTokens_form').submit( function(event){
        event.preventDefault();

        var tokenAmount = $('#id_amount').val();
        var options = {}
        window.wrapTokenTransaction('#issueNewTokens_form', 'issueTokens', [tokenAmount], options);
        return false;
    });
    require('../components/web3.js')();
  }

});
