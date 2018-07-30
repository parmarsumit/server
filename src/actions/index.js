

$('#app').on('app.switched', function(event){

  if (event.action == 'index' || event.action == 'view'){

    if ($('#welcome_updateProfile').length ){
      // provide the update profile form
      var actor = $('#content-main').data('actor');
      var profileUpdateUrl = '/'+actor+'/updateProfile/';
      console.log(profileUpdateUrl);
      var data = {
        redirect:window.location.href,
        embed:true,
      }
      // send it
      $.ajax({
          url: profileUpdateUrl,
          data:data,
          method: 'GET',
          type: 'GET', // For jQuery < 1.9
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
              window.parseResponse(profileUpdateUrl, '#updateProfile_form', data);
          },

        beforeSend:function(){
        }
      });

    }

  }
});
