const form = $('#search-graph-form');

const hideOverlay = function hideOverlay(event) {
  const overlay = $(event.currentTarget).find('.overlay');
  overlay.hide();
};
const showOverlay = function showOverlay(event) {
  const overlay = $(event.currentTarget).find('.overlay');
  overlay.show();
};

const searchGraph = function searchGraph(findActorId) {
  const searchUrl = '/submit';
  const data = {
    searchFor: findActorId,
  };

  $.get(searchUrl, data, (response) => {
    const path = response.path
    const endPath = response.path_end
    const lenPath = path.length;

    $('.score').append(`Bacon Score: ${lenPath}`);

    let actorHtml;
    let movieHtml;
    let endHtml;

    const anonImage = 'static/scores/images/profile.jpg';
    const anonAlt = 'no photo available';

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
        imageSrc = anonImage;
        imageAlt = anonAlt;
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

        movieHtml += `
          <li class="grid-x small-3 cell align-center">
            <div class="image-container poster">
              <a href="http://www.imdb.com/title/${movieId}" target="_blank">
                <img src="${movieUrl}" alt="poster for ${movieName}" class="images posters"/>
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
      imageSrc = anonImage;
      imageAlt = anonAlt;
    }

    endHtml = `
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

const resetDisplay = function resetDisplay() {
  $('.score').empty();
  $('ul.actors').empty();
  $('.error').empty();
};

const checkName = function checkName(event) {
  event.preventDefault();
  resetDisplay();

  const url = form.attr('action');
  const formData = form.serialize();

  $.get(url, formData, (response) => {
    searchGraph(response.actor_id);
  }).fail(() => {
    const html = '<p class="error">Not a valid name.</p>';
    $('.error').append(html);
  });
};

const fileUrl = 'https://s3-us-west-2.amazonaws.com/moviegraph-static/data/actors.json';

const getActorList = function getActorList() {
  console.log('running')
  $.get(fileUrl, (response) => {
    console.log(response);

    const actors = response.actors;
    const numActors = actors.length;
    const dataList = $('actor-list');

    for (let i = 0; i < numActors; i += 1) {
      const opt = `<option data-id="${actors[i].actor_id}" value="${actors[i].actor_name}">`;
      dataList.append(opt);
    }
  });
};

const getActors = function getActors(event) {
  const text = $(event.currentTarget).val();
  const dataList = $('#actor-list');

  // clear current data list
  dataList.empty();

  // exit if input is blank or short len
  if (text === '' || text.length < 3) return;

  $.get('/actors', { name: text }, (response) => {
    const actors = response.actors;

    for (let i = 0, len = actors.length; i < len; i += 1) {
      const opt = `
        <option data-id="${actors[i].actor_id}" value="${actors[i].actor_name}"></option>
      `;

      dataList.append(opt);
    }
  });
};

$(document).ready(() => {
  // $(document).foundation();

  // form.on('click', 'button', checkName);

  $('.path').on('mouseenter', '.image-container', hideOverlay);
  $('.path').on('mouseleave', '.image-container', showOverlay);

  $('#search-for').on('input', getActors);
});
