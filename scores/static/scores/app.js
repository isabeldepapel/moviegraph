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
    console.log(response.actor_id);
  }).fail(() => {
    const html = '<p class="error">Not a valid name.</p>';
    $('.error').append(html);
  });
};

const hideOverlay = function hideOverlay(event) {
  const overlay = $(event.currentTarget).find('.overlay');
  overlay.hide();
};
const showOverlay = function showOverlay(event) {
  const overlay = $(event.currentTarget).find('.overlay');
  overlay.show();
};

$(document).ready(() => {
  // $(document).foundation();

  form.on('click', 'button', checkName);
  
  $('.path').on('mouseenter', '.image-container', hideOverlay);
  $('.path').on('mouseleave', '.image-container', showOverlay);

});
