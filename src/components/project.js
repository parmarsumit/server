
require('../actions/index.js');
require('../actions/view.js');
require('../actions/inviteOwner.js');

require('../actions/createProject.js');
require('../actions/fundProject.js');
require('../actions/issueNewTokens.js');
require('../actions/addOwner.js');
require('../actions/revokeOwner.js');

require('../actions/rewardContributor.js');
require('../actions/redeemToken.js');

require('../actions/deployContract.js');

require('../actions/validateEthereumAddress.js');

function unlockAccount(callback){
  var keystore = $('#content-main').data('keystore');
  if (keystore){
    $('#extrapanel').modal('show');
    $('#password_modal').bind('keypress', function(e) {
       if( e.which === 13 )
           var password = $('#account_password').val();
           if (password){
             /// unlocking account keystore with passwd
             var account = web3.eth.accounts.decrypt(keystore, password);
             var wallet = web3.eth.accounts.wallet.create();
             wallet.add(account);
             $('#extrapanel').modal('hide');
             $('#account_password').val('');
             callback();
             account = null;
             wallet = null;
           } else {
             // do nothing ...
           }
    });
  } else {
    callback();
  }
}

function wrapControllerTransaction(form_selector, method, args, options, callback){

    if (window.tributeControllerContract){
      wrapContractTransaction(window.tributeControllerContract, form_selector, method, args, options, callback);
    } else {

      var userAccount = $('#content-main').data('account');
      var controllerAddress = $('#app').data('address');

      $.getJSON("/static/contracts/TributeController.json?"+Math.random(), function(json) {

          var code = json.bytecode;
          var abi = json.abi;

          var tributeControllerContract = new window.web3.eth.Contract(abi, controllerAddress);
          tributeControllerContract.options.from = userAccount;
          //myContract.options.from = web3.eth.accounts[0]; // default from address
          //myContract.options.gasPrice = '20000000000000'; // default gas price in wei
          //myContract.options.gas = 5000000; // provide as fallback always 5M gas
          window.tributeControllerContract = tributeControllerContract;

          wrapContractTransaction(tributeControllerContract, form_selector, method, args, options, callback);
        });
    }
}
window.wrapControllerTransaction = wrapControllerTransaction;

function wrapTokenTransaction(form_selector, method, args, options, callback){

  var userAccount = $('#content-main').data('account');
  var tokenAddress = $('#content-main').data('address');

  if (tokenAddress == userAccount){
    alert('Ouch ... same same ...');
  }

  if(window.tributeTokenContract){
    wrapContractTransaction(window.tributeTokenContract, form_selector, method, args, options, callback);
  } else {
    $.getJSON("/static/contracts/TributeToken.json?"+Math.random(), function(json) {
      var tributeTokenInterface = json;
      var code = tributeTokenInterface.bytecode;
      var abi = tributeTokenInterface.abi;

      var tributeTokenContract = new window.web3.eth.Contract(abi, tokenAddress);
      tributeTokenContract.options.from = userAccount;

      window.tributeTokenContract = tributeTokenContract;
      wrapContractTransaction(tributeTokenContract, form_selector, method, args, options, callback);
    });
  }
}
window.wrapTokenTransaction = wrapTokenTransaction;

function wrapContractTransaction(contract, form_selector, method, args, options, callback){

  $('#app form').off('submit');

  var userAccount = $('#content-main').data('account');
  var tokenAddress = $('#content-main').data('address');

  var notyfReceipt = new Noty();
  var receipt;

  var notyfTransaction = new Noty(
    {theme: 'relax',
    type: 'warning',
    timeout: 0,
    layout: 'bottomRight',
    text: 'Preparing transaction ...',
    callbacks: {
      onTemplate: function() {
          this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
          // Important: .noty_body class is required for setText API method.
      },
      onShow: function() {},
    }
  }).show();

  // hide the form panel
  //$(form_selector).closest('.modal-dialog').hide();
  //$(form_selector).closest('.modal-dialog').css({'z-index':0});
  //$(form_selector).closest('.modal-dialog').modal('hide');
  function freeSpace(){

    notyfTransaction.close();
    $('#loader-overlay').modal('hide');

  }

  var sendTrans = function(){

    contract.methods[method].apply(this, args)
    .send(options)
    .on('transactionHash', function(hash){
        console.log(hash);
        //notyf.close();
        notyfReceipt = new Noty({theme: 'relax',
          type: 'warning',
          timeout: 0,
          closeWith: [],
          layout: 'bottomRight',
          text: 'Transaction processing.<br /><a class="text-primary" href="https://ropsten.etherscan.io/tx/'+hash+'" target="_etherscan" >'+hash+'</a><br/>Waiting for validation.',
          callbacks: {
            onTemplate: function() {
                this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                // Important: .noty_body class is required for setText API method.
            },
            onShow: function() {},
          }
        }).show();



    })
    .on('confirmation', function(confirmationNumber, receipt){
        console.log('confirmationNumber '+confirmationNumber);
        if (confirmationNumber == 0){

          console.log(receipt);

          var notyfTransaction = new Noty({
            theme: 'relax',
            type: 'success',
            timeout: 3500,
            layout: 'bottomRight',
            text: 'Transaction confirmed !',
            callbacks: {
              onTemplate: function() {
                  this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                  // Important: .noty_body class is required for setText API method.
              },
              onShow: function() {},
            }
          }).show();

          notyfReceipt.close();
          //notyfReceipt.closeWith = ['click'];
          //notyfReceipt.timeout = 5500;
          //notyfReceipt.type = 'success';

          if (callback){

            callback(receipt);

            freeSpace();

          } else {
            var hash = receipt.transactionHash;
            $('#id_tx').val(hash);
            console.log(hash);

            // send the final
            $('#app form').off('submit');

            $(form_selector).closest('.modal-dialog').hide();

            $('#sidepanel').modal('hide');
            $('#modalpanel').modal('hide');

            //$(form_selector).submit(window.submitAForm);
            //$(form_selector).submit();

            console.log('Sending form ...');
            var dataString = $(form_selector).serialize();

            $.ajax({
                type: "POST",
                url: $(form_selector).attr('action'),
                data: dataString,
                success: function(msg) {
                  console.log('Ok sent ...');
                  freeSpace();
                  //$('#loader-overlay').modal('hide');
                  //notyfTransaction.close();
                },
                error: function(msg) {
                  console.log('Error pushing form');
                }
            });
          }
        }
    })
    .on('receipt', function(receipt){
      console.log('Receipt for transaction '+receipt.transactionHash );
    })
    .on('error', function(err){

        console.log('ERROR');

        console.error

        notyfTransaction.close();
        var notyfError = new Noty({theme: 'relax',
          type: 'error',
          timeout: 0,
          layout: 'bottomRight',
          text: err.message,
          callbacks: {
            onTemplate: function() {
                this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                // Important: .noty_body class is required for setText API method.
            },
            onShow: function() {},
          }
        }).show();

        // hide the form panel
        $('#sidepanel').modal('hide');
        $('#loader-overlay').modal('hide');

    });

  };


  //
  function checkAndSend(){

    //
    var zIndex = 1040 + (10 * $('.modal:visible').length);
    $('#loader-overlay').css('z-index', zIndex);
    $('#loader-overlay').modal('show');

    // user balance has to have enought ether for the gas
    web3.eth.getBalance(userAccount).then(function(balance){

      var currentBalance = balance;
      // Number.parseFloat(web3.utils.fromWei(balance)).toPrecision(4);

      console.log('Balance:', currentBalance, balance);

      if (currentBalance < 1){
        ///
        var notyfBalanceError = new Noty(
          {theme: 'relax',
          type: 'error',
          timeout: 5000,
          layout: 'bottomRight',
          text: 'You don\' have enought ETH to for the gas.',
          callbacks: {
            onTemplate: function() {
                this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                // Important: .noty_body class is required for setText API method.
            },
            onShow: function() {},
          }
        }).show();

        console.log('No balance for gas');
        freeSpace();

      } else {

        contract.methods[method].apply(this, args).estimateGas({options})
        .then(function(gasAmount){

            options.gas = Math.round(gasAmount*2);

            console.log(options);

            if (currentBalance > options.gas){
              sendTrans();
            } else {
              ///
              var notyfNoBalance = new Noty(
                {theme: 'relax',
                type: 'error',
                timeout: 0,
                layout: 'bottomRight',
                text: 'You don\' have enought ETH to for the gas.',
                callbacks: {
                  onTemplate: function() {
                      this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                      // Important: .noty_body class is required for setText API method.
                  },
                  onShow: function() {},
                }
              }).show();

              freeSpace();
              ///
              //$('#sidepanel').modal('hide');
              console.log('No enougth eth for transaction');

            }
            //sendTrans();
        })
        .catch(function(error){
          console.log(error);
          console.log('Cannot estimate gas');
          var notyfError = new Noty(
            {theme: 'relax',
            type: 'error',
            timeout: 0,
            layout: 'bottomRight',
            text: 'Cannot estimate gas cost.',
            callbacks: {
              onTemplate: function() {
                  this.barDom.innerHTML = '<div class="noty_body">' + this.options.text + '<div>';
                  // Important: .noty_body class is required for setText API method.
              },
              onShow: function() {},
            }
          }).show();

          console.error();
          freeSpace();

        });

      }


    });

  }


  if ( $('#content-main').data('keystore') ){
    unlockAccount(function(account){
      checkAndSend();
    });
  } else {
    checkAndSend();
  }

}
