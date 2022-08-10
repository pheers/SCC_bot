$("li").click((e) => {
    console.log($(e.target))
    if($(e.target).data("link")){
        $(".content#selected").css("left", "-100%").css("opacity", "0").attr("id", null)
        $('li.selected').removeClass("selected")
        setTimeout(()=>{
            $(".content#selected").css("display", "none").css("left", "100%")
            $(e.target).addClass("selected")
            $(`.content*[data-link="${$(e.target).data("link")}"]`).css("display", "block").css("left", "15%").css("opacity", "1").attr("id", "selected")
            location.hash = $(e.target).data("link")
        },200)
    }
})