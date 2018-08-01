
$('#app').on('app.switched', function(event){

  if (event.action == 'validateEthereumAddress'){
    //
    var userAccount = $('#content-main').data('account');

    $('#app form').off('submit');

    /// check if user is connected to a provider
    if (userAccount){
      console.log('Actual account ', userAccount);
    } else {
      // call metamask
      window.web3.eth.getAccounts().then(function(accounts){
        defaultAccount = accounts[0];
        $('#id_address').val(defaultAccount);
      });
    }

    /**
    $('#validateEthereumAddress_form').submit( function(event){
        /// ask for signature before the user can register it's address
        var address = $('#id_address').val();
        var message = 'By signing this message, i prove that i\'m the owner of the account and associate it with my Tribute id '+$('#content-main').data('actor');
        var signature = web3.eth.sign(message, address, function(signHash){
          // okay we got the signature
          console.log(signHash);
          $('#id_tx').val(signHash);
        });
        return false;
    });
    **/

  }

});
