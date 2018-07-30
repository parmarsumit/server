
$('#app').on('app.switched', function(event){

  if (event.action == 'inviteOwner' || event.action == 'inviteVisitor'){
    //
    var ref_form = event.action+'_form';

    if ( $('#id_target').val() )
    {
      var email = $('#id_target').val();
      if ( validateEmail(email) && $('#id_target_field').hasClass('error') ){
          //$('#inviteOwner_form').css({height:'0px'});
          $('#'+ref_form).find('fieldset').attr('disabled', true);
          createProfile(ref_form);
      }
    }
  }
});

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function createProfile(ref_form){

  // get form parameters
  var email_key = document.getElementById(ref_form).elements['target'].value;
  var data = {};
  data.email = email_key;

  var name = email_key.substring(0, email_key.lastIndexOf("@"));
  data.title = name;

  data.csrfmiddlewaretoken = document.getElementById(ref_form).elements['csrfmiddlewaretoken'].value;

  console.log(data);

  //
  var action_url = '/'+$('#content-main').data('actor')+'/createProfile/';

  // send it
  $.ajax({
      url: action_url,
      data: data,
      method: 'POST',
      type: 'POST', // For jQuery < 1.9
      statusCode: {
        402: function(response){
          alert('Error creating profile');
        },
        403: function(response){
          alert('Error creating profile');
        },
        401: function(response){
          alert('Error creating profile');
        },
        404: function(response){
          alert('Error creating profile');
          //parseCreated(response.responseText);
        },
        415: function(response){
          console.log(response);
        },
      },
      success: function(data){
          $('#'+ref_form).find('fieldset').attr('disabled', false);
          $('#'+ref_form).submit();
      },

    beforeSend:function(){
      //$('#'+from_form).find('fieldset').attr('disabled', true);
    }
  });
}
