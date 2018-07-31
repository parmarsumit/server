
$('#app').on('app.switched', function(event){

  if (event.action == 'createEthereumAccount'){

    $('#app form').off('submit');

    console.log('Hello !')

    $('#createEthereumAccount_form').submit( function(event){


        var password = $('#account_password').val();
        var confirm = $('#account_confirm').val();

        if (password && password==confirm){

          var createdAccountAddress = '';
          var createdAccountKeystore = '';

          var account = web3.eth.accounts.create();
          createdAccountAddress = account.address;

          createdAccountKeystore = account.encrypt(password);

          $('#id_address').val(createdAccountAddress);
          $('#id_keystore').val( JSON.stringify(createdAccountKeystore) );

          ///
          var signatureData = {
            akey: $('#content').data('actor')
          }
          var signature = account.sign(JSON.stringify(signatureData));
          $('#id_tx').val(signature);

          console.log('Submitting ...');
          window.submitAform(event);
          return false;

        } else {

          alert('Paswwords does not match');

        }
        return false;
    });

  }

});
