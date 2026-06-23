$(document).ready(function() {
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);

    $('.table').each(function() {
        if ($(this).find('tbody tr').length > 10) {
            $(this).DataTable ? $(this).DataTable({pageLength: 10}) : null;
        }
    });

    $('[data-toggle="tooltip"]').tooltip();

    $('.search-input').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $(this).closest('.table-responsive').find('table tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $('.select-all').on('change', function() {
        $('.select-item').prop('checked', this.checked);
    });
});

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatCurrency(amount) {
    return '$' + parseFloat(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
