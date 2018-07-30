
$('#app').on('app.switched', function(event){

  if (event.action == 'fundProject'){


    $('#app form').off('submit');
    $('#fundProject_form').submit( function(event){
        event.preventDefault();

        var ethAmount = $('#id_amount').val();
        var options = {}
        if (ethAmount > 0){
          options.value = window.web3.utils.toWei(ethAmount, "ether");
        }
        window.wrapTokenTransaction('#fundProject_form', 'fundProject', [], options);
        return false;
    });
    require('../components/web3.js')();

  }

});
