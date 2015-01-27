$().ready(function(){
    $('.meal_menu_link').on('click', function(event){
        event.preventDefault();

        var current = event.currentTarget;
        $('#description').append(current.dataset.desc).append('\n');
        $('#company').val(current.dataset.comp);
        var $cost = $('#cost');
        $cost.val(parseFloat($cost.val() || 0) + parseFloat(current.dataset.cost))
    });
    $('#reset').on('click', function(event) {
        $('#description').html('');
    });
});
