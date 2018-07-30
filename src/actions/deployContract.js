
$('#app').on('app.switched', function(event){
if (event.action == 'deployContract'){

  $('#app form').off('submit');

  console.log('Unbound ...');

  $('#deployContract_form').submit( function(event){

      event.preventDefault();

      var contractCompiled = JSON.parse( $('#id_contract').val() );
      var contractCode = contractCompiled.bytecode;
      var abi = contractCompiled.abi;

      window.tributeControllerContract.deploy({
        data: contractCode,
        arguments: []
      })
      .send()
      .on('transactionHash', function(hash){
          console.log(hash);
          //$('#id_tx').val(hash);
      })
      .on('confirmation', function(confirmationNumber, receipt){
          //console.log('confirmationNumber');
          //console.log(confirmationNumber);
      })
      .on('receipt', function(receipt){

        console.log('receipt')
        console.log(receipt);
        $('#id_address').val(receipt.contractAddress);
        $('#id_tx').val(receipt.transactionHash);
        $('#id_network').val($('#app').data('network'));
        // send the final
        $('#app form').off('submit');
        $('#deployContract_form').submit(window.submitAForm);
        $('#deployContract_form').submit();
      })
      .on('error', console.error);

      return false;
  });


}
});
