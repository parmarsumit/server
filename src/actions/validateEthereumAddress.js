
$('#app').on('app.switched', function(event){

  if (event.action == 'validateEthereumAddress'){
    //
    var userAccount = $('#content-main').data('account');
    if (userAccount){
      console.log('Actual account ', userAccount);
    } else {
      // call metamask
      window.web3.eth.getAccounts().then(function(accounts){
        defaultAccount = accounts[0];
        $('#id_address').val(defaultAccount);
      });
    }
  }



});
