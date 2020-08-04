$(function () {
    let selected_icon = $(document).find('.highlight-selected-icon');
    let hidden_input = $('#hidden-icon-field');

    $(document).on('click', 'button.field-plugin-icon-select', () => {
        let font_class_name = $(this.activeElement).data('icon-class')
        let icon_name = $(this.activeElement).data('icon-name')

        console.log('click');

        // set hidden input value
        hidden_input.val(font_class_name);

        selected_icon.find('i').removeClass().addClass(font_class_name)
        selected_icon.find('.name').text(icon_name)
        selected_icon.show();
    });
});