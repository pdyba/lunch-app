$().ready(function(){
    $('.meal_menu_link').on('click', function(event){
        event.preventDefault();
        var current = event.currentTarget,
            desc = $('#description');
        desc.val(desc.val() + current.dataset.desc + '\n');
        $('#company').val(current.dataset.comp);
        var $cost = $('#cost');
        $cost.val(parseFloat($cost.val() || 0) + parseFloat(current.dataset.cost))
    });

    $('#reset').on('click', function(event) {
        $('#description').html('');
    });

    $('#softrandom').on('click', function(event) {
        $.getJSON("/random_meal/0", function(data){
        $('#description').val(data["description"]);
        $('#company').val(data["company"]);
        $('#cost').val(data["cost"])
        });

    });
});

