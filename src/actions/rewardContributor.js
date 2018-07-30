

$('#app').on('app.switched', function(event){
  if (event.action == 'signReward'){
    //
    
  }
});


$('#app').on('app.switched', function(event){

  if (event.action == 'index'){

    // check if there is a approve button
    // we will load form in the background
    // and trigger web3 transaction

  } else if (event.action == 'Zapprove'){
    $('#app form').off('submit');

    $('#approve_form').submit( function(event){

        event.preventDefault();

        var userAccount = $('#content-main').data('account');
        var tokenAddress = $('#content-main').data('address');

        var cAddress = $('#contributor').data('address');
        var cValue = $('#contribution').data('value');

        $.getJSON("/static/contracts/TributeToken.json?"+Math.random(), function(json) {

          var tributeTokenInterface = json;

          var code = tributeTokenInterface.bytecode;
          var abi = tributeTokenInterface.abi;

          tributeTokenContract = new window.web3.eth.Contract(abi, tokenAddress);
          tributeTokenContract.options.from = userAccount;

          tributeTokenContract.methods.rewardContributor(cAddress, cValue)
          .send({value:window.web3.utils.toWei(ethAmount, "ether")})
          .on('transactionHash', function(hash){
              console.log(hash);
              //$('#id_tx').val(hash);
          })
          .on('confirmation', function(confirmationNumber, receipt){
              //console.log('confirmationNumber');
              //console.log(confirmationNumber);
          })
          .on('receipt', function(receipt){

            $('#id_tx').val(receipt.transactionHash);

            // send the final
            $('#app form').off('submit');
            $('#fundProject_form').submit(window.submitAForm);
            $('#fundProject_form').submit();
          })
          .on('error', console.error);
        });
        return false;
      });
    }

});
