$(function () {
    let form = $('#plusplugin_form');
    let selected_icon = form.find('.highlight-selected-icon');
    let hidden_input = $('#hidden-icon-field');

    form.on('click', 'button.field-plugin-icon-select', () => {
        let font_class_name = $(this.activeElement).data('icon-class')
        let icon_name = $(this.activeElement).data('icon-name')

        // set hidden input value
        hidden_input.val(font_class_name);

        selected_icon.find('i').removeClass().addClass(font_class_name)
        selected_icon.find('.name').text(icon_name)
        selected_icon.show();
    });
});