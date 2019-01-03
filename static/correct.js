var inputNum = 2
var count = 1
console.log('correct version')

function doFirst() {
    var addBtn = document.getElementById('addBtn')
    var keywordsInput = document.querySelectorAll('.keywords')
    var courses = document.getElementsByClassName('courses')
    var input1 = document.getElementById('course-1')
    var input2 = document.getElementById('course-2')
    var input3 = document.getElementById('course-3')
    var input4 = document.getElementById('course-4')
    var input5 = document.getElementById('course-5')
    var citeBtn = document.getElementById('citeBtn')
    var numCitations = document.getElementById('numCitations')
    var surely = document.getElementById('surely')
    var form_div = document.getElementById('form_div')
    var step2 = document.getElementById('step2')
    var bottom = document.getElementById('bottom')
    var title_button = document.getElementById('title_button')
    var firstPage = document.getElementById('firstPage')
    var form1 = document.getElementById('form1')

    input1.addEventListener("keydown", function (e) {
        if (e.keyCode === 13) {  //checks whether the pressed key is "Enter"
            addInput(e);
        }
    });

    input2.addEventListener("keydown", function (e) {
        if (e.keyCode === 13) {  //checks whether the pressed key is "Enter"
            addInput(e);
        }
    });
    input3.addEventListener("keydown", function (e) {
        if (e.keyCode === 13) {  //checks whether the pressed key is "Enter"
            addInput(e);
        }
    });
    input4.addEventListener("keydown", function (e) {
        if (e.keyCode === 13) {  //checks whether the pressed key is "Enter"
            addInput(e);
        }
    });
    addBtn.addEventListener('click', addInput, false)
}

function change() {
    firstPage.style.display = 'none'
    form_div.style.display = 'block'
    console.log('title_page')
}

function submitCourseForm() {
    if (document.getElementById('course-1').value != ''
        && document.getElementById('course-1').value != '') {
        document.getElementById('circularG').style.display = 'block';
        document.getElementById('empty-course-notice').style.display = 'none';
        document.getElementById('form_div').style.display = 'none';
        document.getElementById('form1').submit();
    }
    else {
        document.getElementById('empty-course-notice').style.display = 'block';
    }
}

function addInput(e) {
    inputNum += 1
    console.log(inputNum)
    if (inputNum == 2) {
        input2.style.display = 'block'
        window.setTimeout(function () {
            console.log('SET TIMEOUT')
            input2.focus()
            input2.select();
        }, 0)

    }
    if (inputNum == 3) {
        input3.style.display = 'block'
        input3.focus();
        input3.select();
    }
    if (inputNum == 4) {
        input4.style.display = 'block'
        addBtn.style.display = 'none'
        input4.focus();
        input4.select();
    }
    if (inputNum == 5) {
        input5.style.display = 'block'
        addBtn.style.display = 'none'
        input5.focus();
        input5.select();
    }
}

function next1() {
    console.log(123)
    addBtn.style.display = 'none'
    nextBtn.style.display = 'none'
    step2.style.display = 'block'
    bottom.style.display = 'block'

}

function clickedCite() {
    console.log('clicked site')
}

function renderAssessmentItems(assessments) {
    let html = '';

    movies.forEach(function (movie) {
        html += `
          <div class="single-movie">
          <img class="movie-image" src="${movie.Image}">
          <div class="movie-details">
            <h1>${movie.Name}</h1>
            <h4>Description:&nbsp</h4> <p>${movie.Description}</p>
            <h4>Director:&nbsp</h4> <p>${movie.Director}</p>
            <h4>Release Date:&nbsp</h4> <p>${movie.ReleaseDate}</p>
            <h4>Runtime:&nbsp</h4> <p>${movie.RunningTime}</p>
            <h4>Rating:&nbsp</h4> <p>${movie.StarRating}/5</p>
          </div>
      </div>
      `
    })
    document.getElementById('movies').innerHTML = html
}

function changeTab(evt, tab) {
    // Declare all variables
    var i, tabcontent, tablinks;
    console.log('changing tab')

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tab).style.display = "block";
    evt.currentTarget.className += " active";
}


window.addEventListener("load", doFirst, false)
