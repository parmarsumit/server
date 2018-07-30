


$('#app').on('app.switched', function(event){

  if (event.action == 'view'){
    //
    //
    $.getJSON("/static/contracts/TributeToken.json?"+Math.random(), function(json) {

      var userAccount = $('#content-main').data('account');
      var tributeTokenAddress = $('#content-main').data('address');

      var tributeTokenContract = new window.web3.eth.Contract(json.abi, tributeTokenAddress);
      tributeTokenContract.options.from = userAccount;
      tributeTokenContract.methods.totalSupply()
      .call()
      .then(function(result){
          console.log(result)
      });

    });
  }
});
