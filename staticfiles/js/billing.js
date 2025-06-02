$(document).ready(function() {
    var formsetPrefix = 'formset';
    var formsetCount = $('#id_' + formsetPrefix + '-TOTAL_FORMS').val();

    $('#add-formset').click(function() {
        var formsetCopy = $('#empty-formset').html().replace(/__prefix__/g, formsetCount);
        $('#formset-container').append(formsetCopy);
        formsetCount++;
        $('#id_' + formsetPrefix + '-TOTAL_FORMS').val(formsetCount);
    });

    $(document).on('click', '.delete-formset', function() {
        $(this).closest('.formset-item').remove();
    });
});
