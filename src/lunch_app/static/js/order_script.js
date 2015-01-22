$().ready(function(){
    $('.meal_menu_link').on('click', function(event){
        event.preventDefault();

        var current = event.currentTarget;

        var desc = document.getElementById('description');
        var cost = document.getElementById('cost');
        var comp = document.getElementById('company');

        desc.value = current.dataset.desc;
        cost.value = current.dataset.cost;
        comp.value = current.dataset.comp;

    })
});
