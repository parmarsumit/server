

$('#app').on('app.switched', function(event){

  if (event.action == 'signReward'){

    $('#app form').off('submit');

    $('#signReward_form').submit( function(event){
        event.preventDefault();

        var contributorAddress = $('#contribution-data').data('address');
        var contributionAmount = $('#contribution-data').data('amount');
        
        var options = {};

        window.wrapTokenTransaction('#signReward_form', 'rewardContribution', [contributorAddress, contributionAmount], options);

        return false;
    });
  }

});
