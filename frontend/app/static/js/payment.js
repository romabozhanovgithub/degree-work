document.getElementById('form-amount').addEventListener('submit', async function(event) {
    event.preventDefault();
    // Load the publishable key from the server. The publishable key
    // is set in your .env file.
    const {publishableKey} = await fetch('http://localhost:5000/payment/publishable-key').then((r) => r.json());
    if (!publishableKey) {
      alert('Please set your Stripe publishable API key in the .env file');
    }
  
    const stripe = Stripe(publishableKey, {
      apiVersion: '2020-08-27',
    });
  
    // On page load, we create a PaymentIntent on the server so that we have its clientSecret to
    // initialize the instance of Elements below. The PaymentIntent settings configure which payment
    // method types to display in the PaymentElement.
    amount = document.getElementById('amount').value;
    currency = document.getElementById('currency').value;
    token = localStorage.getItem('accessToken');
    const {
      error: backendError,
      clientSecret
    } = await fetch(
        'http://localhost:5000/payment/deposit',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              amount: amount,
              currency: currency
            })
        }
    ).then(r => r.json());

    let amountForm = document.getElementById('form-amount');
    amountForm.style.display = "none";

    let paymentForm = document.getElementById('payment-form');
    paymentForm.style.display = "block";

    // Initialize Stripe Elements with the PaymentIntent's clientSecret,
    // then mount the payment element.
    const elements = stripe.elements({ clientSecret });
    const paymentElement = elements.create('payment');
    paymentElement.mount('#payment-element');
    // Create and mount the linkAuthentication Element to enable autofilling customer payment details
    const linkAuthenticationElement = elements.create("linkAuthentication");
    linkAuthenticationElement.mount("#link-authentication-element");
    // If the customer's email is known when the page is loaded, you can
    // pass the email to the linkAuthenticationElement on mount:
    //
    //   linkAuthenticationElement.mount("#link-authentication-element",  {
    //     defaultValues: {
    //       email: 'jenny.rosen@example.com',
    //     }
    //   })
    // If you need access to the email address entered:
    //
    //  linkAuthenticationElement.on('change', (event) => {
    //    const email = event.value.email;
    //    console.log({ email });
    //  })
  
    // When the form is submitted...
    const form = document.getElementById('payment-form');
    let submitted = false;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      // Disable double submission of the form
      if(submitted) { return; }
      submitted = true;
      form.querySelector('button').disabled = true;
  
      const nameInput = document.querySelector('#name');
  
      // Confirm the payment given the clientSecret
      // from the payment intent that was just created on
      // the server.
      const {error: stripeError} = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment/success`,
        }
      });
  
      if (stripeError) {
        // reenable the form.
        submitted = false;
        form.querySelector('button').disabled = false;
        return;
      }
    });
  });
