const form = $('#search-graph-form');

const checkName = function checkName(event) {
  event.preventDefault();
  $('.error').empty();

  const url = form.attr('action');
  // const formData = $('#search-for').val();
  const formData = form.serialize();

  console.log(formData)

  $.get(url, formData, (response) => {
    console.log('success!');
    console.log(response);

    

  }).fail(() => {
    const html = '<p class="error">Not a valid name.</p>';
    $('.error').append(html);
  });
  // $.ajax({
  //   url: form.attr('action'),
  //   data: form.serialize(),
  //   dataType: 'json',
  //   success(data) {
  //     console.log(data.status);
  //   },
  //
  // });
};

$(document).ready(() => {
  // $(document).foundation();

  form.on('click', 'button', checkName);
});
