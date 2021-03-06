

$('#app').on('app.switched', function(event){

  if (event.action == 'signOwnership'){

    $('#app form').off('submit');

    $('#id_address').val( $('#target_actor').data('address') );

    $('#signOwnership_form').submit( function(event){
        event.preventDefault();

        var ownerAddress = $('#id_address').val();
        var options = {};
        window.wrapTokenTransaction('#signOwnership_form', 'addOwner', [ownerAddress], options);
        return false;
    });
  }

});
