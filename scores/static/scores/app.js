const form = $('#search-graph-form');
let complete = false; // used to track whether datalist is complete or not

const hideOverlay = function hideOverlay(event) {
  const overlay = $(event.currentTarget).find('.overlay');
  overlay.hide();
};

const showOverlay = function showOverlay(event) {
  const overlay = $(event.currentTarget).find('.overlay');
  overlay.show();
};

// validate actor names are in graph
const isValid = function isValid() {
  let valid = true;
  const startFrom = $('#start-from').val();
  const searchFor = $('#search-for').val();

  if (!startFrom || startFrom.trim() === '') {
    valid = false;
    $('p.start-from').text('Can\'t be blank');
    $('#start-from').addClass('error');
  }
  if (!searchFor || searchFor.trim() === '') {
    valid = false;
    $('p.search-for').text('Can\'t be blank');
    $('#search-for').addClass('error');
  }
  if (startFrom.toLowerCase() === searchFor.toLowerCase()) {
    valid = false;
    $('p.both').text('Names must be different');
    $('#start-from').addClass('error');
  }

  return valid;
};

const eraseErrors = function eraseErrors() {
  $('p.error').empty();
  $('#start-from, #search-for').removeClass('error');
};

const erasePath = function erasePath() {
  $('.score').empty();
  $('ul.actors').empty();
};

const init = () => {
  $('body').removeClass('init grid-x align-middle');
  $('body').addClass('grid-y');
  $('header').show();
  $('.loader').show();
  $('footer').addClass('grid-x');
  $('footer').show();

  // form styling
  form.removeClass('small-10 large-8');
  form.addClass('small-12');
  $('.input-wrapper').addClass('large-5');
  $('.button-wrapper').addClass('large-2');
};

const searchGraph = function searchGraph(data) {
  // event.preventDefault();
  // resetDisplay();

  // const url = form.attr('action');
  // const formData = form.serialize();
  if ($('body').hasClass('init')) init();

  erasePath();

  $.get('/search', data, (response) => {
    const path = response.path
    const endPath = response.path_end
    const lenPath = path.length;

    $('.score').append(`Bacon Score: ${lenPath}`);

    let actorHtml;
    let movieHtml;
    // let endHtml;

    const imageDir = 'https://s3-us-west-2.amazonaws.com/moviegraph-static/static/scores/images/';
    const noPhotoSrc = `${imageDir}profile.jpg`;
    const noPhotoAlt = 'no photo available';
    const noPosterSrc = `${imageDir}no_image_avail.png`;
    const noPosterAlt = 'no image available';

    let imageSrc;
    let imageAlt;

    for (let i = 0; i < lenPath; i += 1) {
      const [actorId, actorName, actorUrl] = path[i].actor;
      const movies = path[i].movies;
      const numMovies = movies.length;

      if (actorUrl) {
        imageSrc = actorUrl;
        imageAlt = `photo of ${actorName}`;
      } else {
        imageSrc = noPhotoSrc;
        imageAlt = noPhotoAlt;
      }

      actorHtml = `
      <li class="grid-x small-12 cell align-center">
        <div class="image-container photo">
          <a href="http://www.imdb.com/name/${actorId}" target="_blank">
            <img src="${imageSrc}" alt="${imageAlt}" class="images profile-photos"/>
            <div class="overlay grid-x align-middle">
              <span class="overlay-text small-12 cell"><p>${actorName}</p></span>
            </div>
          </a>
        </div>
      </li>
      <p class="connector">was in</p>
      <ul class="movies grid-x small-12 cell align-center">
      `;

      movieHtml = '';
      for (let j = 0; j < numMovies; j += 1) {
        const [movieId, movieName, movieYear, movieUrl] = movies[j];

        if (movieUrl) {
          imageSrc = movieUrl;
          imageAlt = `poster for ${movieName}`;
        } else {
          imageSrc = noPosterSrc;
          imageAlt = noPosterAlt;
        }

        movieHtml += `
          <li class="grid-x small-3 cell align-center">
            <div class="image-container poster">
              <a href="http://www.imdb.com/title/${movieId}" target="_blank">
                <img src="${imageSrc}" alt="${imageAlt}" class="images posters"/>
                <div class="overlay grid-x align-middle">
                  <span class="overlay-text small-12 cell"><p>${movieName}, ${movieYear}</p></span>
                </div>
              </a>
            </div>
          </li>
        `;
      }
      movieHtml += '</ul><p class="connector">with</p>';
      $('ul.actors').append(actorHtml + movieHtml);
    }

    const [endId, endName, endUrl] = endPath;

    if (endUrl) {
      imageSrc = endUrl;
      imageAlt = `photo of ${endName}`;
    } else {
      imageSrc = noPhotoSrc;
      imageAlt = noPhotoAlt;
    }

    const endHtml = `
      <li class="grid-x small-12 cell align-center">
        <div class="image-container photo">
          <a href="http://www.imdb.com/name/${endId}" target="_blank">
            <img src="${imageSrc}" alt="${imageAlt}" class="images profile-photos"/>
            <div class="overlay grid-x align-middle">
              <span class="overlay-text small-12 cell"><p>${endName}</p></span>
            </div>
          </a>
        </div>
      </li>
    `;

    // const html = actorHtml + movieHtml + endHtml;
    $('ul.actors').append(endHtml);
  });
};

const getPath = function getPath(event) {
  event.preventDefault();
  eraseErrors();

  if (!isValid()) return;

  const formData = form.serialize();

  $.get('/validate', formData, (response) => {
    searchGraph(response);
  }).fail((response) => {
    const errors = response.responseJSON.errors;

    Object.keys(errors).forEach((field) => {
      const error = errors[field];
      form.find(`p.${field}`).text(error);
      $(`#${field}`).addClass('error');
    });
  });
};

const getActors = function getActors(event) {
  const text = $(event.currentTarget).val();
  // const dataList = $('#actor-list');
  const dataList = $(event.currentTarget).next();

  // exit if input is blank or short len
  if (text === '' || text.length < 4) {
    dataList.empty();
    return;
  }

  $.get('/actors', { name: text }, (response) => {
    // exit if complete filtered list has been returned
    // and if datalist already populated
    if (response.complete && complete) return;

    dataList.empty();

    const actors = response.actors;

    for (let i = 0, len = actors.length; i < len; i += 1) {
      const opt = `
        <option data-id="${actors[i].actor_id}" value="${actors[i].actor_name}"></option>
      `;

      dataList.append(opt);
    }
    if (response.complete) {
      complete = true;
    } else {
      complete = false;
    }
  });
};

const config = {
  attributes: false,
  childList: true,
  characterData: false,
};

const targetNode = document.querySelector('ul');

const callback = function callback(mutationsList) {
  for (let i = 0, len = mutationsList.length; i < len; i += 1) {
    const mutation = mutationsList[i];
    if (mutation.addedNodes.length > 0) {
      $('.loader').hide();
    } else {
      $('.loader').show();
    }
  }
};

const observer = new MutationObserver(callback);


$(document).ready(() => {
  form.on('click', 'button', getPath);
  $('#search-for').focus();

  // toggle loader when waiting for path to load
  observer.observe(targetNode, config);

  $('.path').on('mouseenter', '.image-container', hideOverlay);
  $('.path').on('mouseleave', '.image-container', showOverlay);

  $('#search-for').on('input', getActors);
  $('#start-from').on('input', getActors);
});
