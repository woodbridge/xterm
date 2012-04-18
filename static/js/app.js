Stripe.setPublishableKey("pk_AWIYRuPDl3RHuAVg1lOca0s0tqiK7")

$(document).ready(function() {
  function addInputNames() {
    $(".card-number").attr("name", "card-number")
    $(".card-cvc").attr("name", "card-cvc")
    $(".card-expiry-year").attr("name", "card-expiry-year")
  }

  function removeInputNames() {
    $(".card-number").removeAttr("name")
    $(".card-cvc").removeAttr("name")
    $(".card-expiry-year").removeAttr("name")
  }

  function submit(form) {
      $('.submit-button').attr('disabled', 'disabled');

      Stripe.createToken({
        number: $('.card-number').val(),
        cvc: $('.card-cvc').val(),
        exp_month: $('.card-expiry-month').val(),
        exp_year: $('.card-expiry-year').val()
      }, function(status, response) {
        if(response.error) {
          $(form['button']).removeAttr('disabled')
          $('.payment-errors').html(response.error.message);
          addInputNames()
        } else {
          var token = response['id'];
          var input = $("<input name='stripeToken' value='" + token + "' style='display:none;' />");
          form.appendChild(input[0])
          form.submit()
        }
      });
      return false;
  }

  $.validator.addMethod('cardNumber', Stripe.validateCardNumber, "Please enter a valid credit card number.")
  $.validator.addMethod('cardCVC', Stripe.validateCVC, "Please enter a valid security code.")
  $.validator.addMethod('cardExpiry', function() {
    return Stripe.validateExpiry($('.card-expiry-month').val(),
                                $('.card-expiry-year').val())
  }, "Please enter a valid expiration.");

  $('#payments').validate({
    submitHandler: submit,
    rules: {
      'email': {
        required: true,
        email: true
      },

      'amount': {
        required: true,
        digits: true
      },

      'name': {
        required: true
      },

      'card-cvc': {
        cardCVC: true,
        required: true
      },

      'card-number': {
        cardNumber: true,
        required: true
      },

      'card-expiry-year': 'cardExpiry'
    }
  })

  addInputNames()
});