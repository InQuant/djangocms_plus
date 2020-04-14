$(function () {
    let form = $('form#textlinkpluginmodel_form');
    let select = form.find('select#id_link_type');

    // map select values to fields
    let fieldMapping = {
        'cmspage': ['.field-cms_page', '.field-section'],
        'download': ['.field-download_file'],
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
        $.each(allFields(), (key, val) => {
            if (fieldMapping[mappingKey].indexOf(val) < 0) {
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
