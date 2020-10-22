$(function () {
    let form = $('form');
    let select = form.find('select#id_link_type');

    // map select values to fields
    let fieldMapping = {
        '': '',
        'cmspage': ['.field-cms_page', '.field-section'],
        'download': ['.field-download_file', '.field-file_as_page'],
        'exturl': ['.field-ext_url'],
        'email': ['.field-mail_to'],
    }

    // helper to get all fields from fieldMapping
    let allFields = () => {
        let _all = [];
        for (let key in fieldMapping) {
            _all = _all.concat(fieldMapping[key]);
        }
        return _all;
    }

    let toggleFields = (mappingKey) => {
        // Iterate fields and make visible fields with class names defined in mapping
        $.each(allFields(), (key, val) => {
            // Check if value exists for key in mapping
            if (fieldMapping.hasOwnProperty(mappingKey) && fieldMapping[mappingKey].indexOf(val) < 0) {
                $(val).fadeOut('fast');
            } else {
                $(val).fadeIn('fast');
            }
        });
    };

    // call initial state
    toggleFields(select.val());

    select.on('change',() => {
        toggleFields(this.activeElement.value)
    });
});
