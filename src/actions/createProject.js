
$('#app').on('app.switched', function(event){

  if (event.action == 'createProject'){

    $('#app form').off('submit');

    $('#createProject_form').submit( function(event){
        event.preventDefault();

        var tokenName = $('#id_title').val();
        var tokenSymbol = $('#id_symbol').val();
        var tokenSupply = $('#id_amount').val().toString();

        var options = {}
        //if (ethAmount > 0){
        //  options.value = window.web3.utils.toWei(ethAmount, "ether");
        //}

        var createdTokenCallback = function(receipt){
          //
          $('#id_address').val(receipt.events.CreatedToken.returnValues.token);
          $('#id_tx').val(receipt.transactionHash);

          console.log(receipt.events.CreatedToken.returnValues.token);
          console.log(receipt.transactionHash);

          // send the final
          $('#app form').off('submit');
          $('#createProject_form').submit(window.submitAForm);
          $('#createProject_form').submit();
        }

        window.wrapControllerTransaction('#createProject_form',
                                          'createProject',
                                          [tokenName, tokenSymbol, tokenSupply],
                                          options,
                                          createdTokenCallback);

        return false;
    });
  }
});


$('#app').on('app.switched', function(event){
  // activate if action is createProject
  if ( event.action == 'ZcreateProject'){

    $('#app form').off('submit');
    $('#createProject_form').submit( function(event){

        event.preventDefault();

        // we need to check if user can do web3


        var notyf = new Noty({theme: 'relax',
          type: 'success',
          timeout: mtimeout,
          layout: 'topRight',
          text: 'Waiting for transaction ...',
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

        var tokenName = $('#id_title').val();
        var tokenSymbol = $('#id_symbol').val();
        var tokenSupply = $('#id_amount').val();

        var userAccount = $('#content-main').data('account');

        // move panel content to another box
        // waiting for the transaction to execute

        window.tributeControllerContract.methods.createProject(tokenName, tokenSymbol, tokenSupply)
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

          $('#id_address').val(receipt.events.CreatedToken.returnValues.token);
          $('#id_tx').val(receipt.transactionHash);

          console.log(receipt.events.CreatedToken.returnValues.token);
          console.log(receipt.transactionHash);

          // send the final
          $('#app form').off('submit');
          $('#createProject_form').submit(window.submitAForm);
          $('#createProject_form').submit();

        })
        .on('error', console.error);

        return false;
      });
    }

});
