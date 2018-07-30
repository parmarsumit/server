
$('#app').on('app.switched', function(event){

  if (event.action == 'createEthereumAddress'){

    $('#app form').off('submit');

    var createdAccountAddress = '';
    var createdAccountKeystore = '';

    $('#createEthereumAddress_form').submit( function(event){

        event.preventDefault();
        $('#id_address').val(createdAccountAddress);
        $('#id_keystore').val(createdAccountKeystore);

    });

  }

});
