function navbar(e) {
    if($(e.target).data("link")){
        $(".content#selected").css("left", "100%").css("opacity", "0")
        $('li.selected').removeClass("selected").click(navbar)
        setTimeout(()=>{
            $(".content#selected").css("left", "-100%").attr("id", null)
            $(e.target).addClass("selected").off('click');
            $(`.content*[data-link="${$(e.target).data("link")}"]`).css("left", "15%").css("opacity", "1").attr("id", "selected")
        },200)
    }
}

$("li").not(".selected").click(navbar)

$('.direction-input').click((e)=> {
    $($($(e.target).closest('.direction-input')).children('input')[0]).css("display", "block");
    $($($(e.target).closest('.direction-input')).children('input')[0]).focus()
})

$('.direction-input>input').keydown((e) => {
    if(e.keyCode === 13 && [...$(e.target).val()].length>1) {
        createDirection(e.target)
    }
});

$('.direction-input>input').blur((e) => {
    $(e.target).val(null).css('display', 'none')
});

$(".delete-direction").click((e) => deleteDirection($(e.target)))

$(".delete-team").click((e) => deleteTeam($(e.target)))

$("#create-team>button").click((e) => createTeam($($(e.target).closest("form"))))

$(".team-form.update>button").click((e) => updateTeam($($(e.target).closest("form"))))

$(".add-date").click((e)=> {
    $($(e.target).next()).append(`<div class="data-div"><input class="Data" name="Date"><img class="icon" src="static/img/cancel.png" alt="create"></div>`)
    $(".data-div>img").click((e) => {
        $(e.target).closest(".data-div").remove()
    })
})

$('input[name="Picture"]').change(function(){
    readURL(this)
})

$(".delete-date").click((e) => {
    $(e.target).closest(".data-div").remove()
})

function readURL(input) {
 if (input.files && input.files[0]) {
  var reader = new FileReader();
    
  reader.onloadend = function(e) {
   $('#prevImage').css("display", "block").attr('src', e.target.result);
  }
    
  reader.readAsDataURL(input.files[0]);
 }
}

function createTeam(team_form){
    let formData = new FormData($(team_form)[0])
    $(".spinner").css("display", "block")
    fetch("/teams",
        {
            headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').attr('value')
            },
            method: "POST",
            body: formData
        })
        .then((response) => response.json())
        .then((data) => {
            $(".spinner").css("display", "none")
            console.log(data)})
            // $('.direction-input').after(
            //     $('<div>', {
            //         class: "direction",
            //         text: data.Name
            //     }).prepend($(`<img data-direction-id="${data.id}" class="icon delete-direction" src="/static/img/cancel.png" alt="??????????????">`).click((e) => deleteDirection($(e.target)))))
            //     $(team).val(null).css('display', 'none') 
            // })
        .catch(function(res){
            console.log(res)
            $(".spinner").css("display", "none")
        }) 
}

function updateTeam(team_form){
    let formData = new FormData($(team_form)[0])
    $(".spinner").css("display", "block")
    fetch("/team/update",
        {
            headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').attr('value')
            },
            method: "POST",
            body: formData
        })
        .then((response) => response.json())
        .then((data) => {
            $(".spinner").css("display", "none")
            console.log(data)})
            // $('.direction-input').after(
            //     $('<div>', {
            //         class: "direction",
            //         text: data.Name
            //     }).prepend($(`<img data-direction-id="${data.id}" class="icon delete-direction" src="/static/img/cancel.png" alt="??????????????">`).click((e) => deleteDirection($(e.target)))))
            //     $(team).val(null).css('display', 'none') 
            // })
        .catch(function(res){
            console.log(res)
            //$(".spinner").css("display", "none")
        }) 
}

function createDirection(team){
    $(".spinner").css("display", "block")
    fetch("/directions",
        {
            headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').attr('value')
            },
            method: "POST",
            body: JSON.stringify({name: $(team).val()})
        })
        .then((response) => response.json())
        .then((data) => {
            console.log(data)
            $('.direction-input').after(
                $('<div>', {
                    class: "direction",
                    text: data.Name
                }).prepend($(`<img data-direction-id="${data.id}" class="icon delete delete-direction" src="/static/img/cancel.png" alt="??????????????">`).click((e) => deleteDirection($(e.target)))))
                $(team).val(null).css('display', 'none') 
                $(".spinner").css("display", "none")
            }
            
            )
        .catch(function(res){ 
            $(team).val(null).css('display', 'none')
            $(".spinner").css("display", "none") 
    })
}

function deleteTeam(team){
    $(".spinner").css("display", "block")
    fetch('/teams?id=' + team.data('team-id'), {
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').attr('value')
            },
        method: 'DELETE',
    })
    .then(() => {
        $(".spinner").css("display", "none")
        $(team.closest(".team")).remove()
        
    })
}


function deleteDirection(direction){
    console.log(direction)
    $(".spinner").css("display", "block")
    fetch('/directions?id=' + direction.data('direction-id'), {
        headers: {
            'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').attr('value')
            },
        method: 'DELETE',
    })
    .then(() => {
        $(".spinner").css("display", "none")
        $(direction.closest('.direction')).css("opacity", "0")
        $(direction.closest('.direction')).css("width", "0")
        $(direction.closest('.direction')).css("margin", "0")
        setTimeout(() => {$(direction.closest(".direction")).remove()}, 300)
        
    })
}

function getData() {
    fetch('/applications', {
        headers : {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
         }
      }).then((response) => response.json())
      .then((data) => {
            console.log(data.applications)
            let html = `<div class="annotation">
            <div class="col-1">??????</div>
            <div class="col-2">?????????? ????????????????</div>
            <div class="col-3">????????????????????</div>
            <div class="col-4">??????????????????</div>
            <div class="col-5">????????</div>
        </div>`
            data.applications.forEach(element => {
                html += `<div data-id="${element.id}" class="application">
                <div class="col-1">${element.Name}</div>
                <div class="col-2">${element.Phone}</div>
                <div class="col-3">${element.Direction__Name}</div>
                <div class="col-4">${element.Team__Name}</div>
                <div class="col-5">${element.Date__Date}</div></div>`
            })
            
            $('.content > .applications').html(html);
            $('#delete-application')
    })
}

setInterval(() => {
    getData();
}, 5000);