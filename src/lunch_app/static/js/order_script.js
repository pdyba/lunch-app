$().ready(function(){
    $('.meal_menu_link').on('click', function(event){
        event.preventDefault();

        var current = event.currentTarget;

        $('#description').val(current.dataset.desc);
        $('#cost').val(current.dataset.cost);
        $('#company').val(current.dataset.comp);

    })
});
