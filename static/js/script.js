$(document).ready(function() {
    $('#prediction-form').on('submit', function(e) {
        e.preventDefault();

        // Show loading, hide results and error
        $('#loading').removeClass('d-none');
        $('#results').addClass('d-none');
        $('#error').addClass('d-none');

        // Get form data
        const formData = {
            symbol: $('#symbol').val(),
            days: $('#days').val()
        };

        // Make AJAX request
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: formData,
            success: function(response) {
                $('#loading').addClass('d-none');
                displayResults(response);
            },
            error: function(xhr) {
                $('#loading').addClass('d-none');
                let errorMessage = 'An error occurred';

                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.error || errorMessage;
                } catch (e) {
                    errorMessage = 'Server error: ' + xhr.statusText;
                }

                $('#error').removeClass('d-none').text(errorMessage);
            }
        });
    });

    function displayResults(data) {
        // Update title and current price
        $('#result-title').text(`Predictions for ${data.symbol}`);
        $('#current-price').text(`$${data.current_price.toLocaleString()}`);

        // Clear previous predictions
        $('#predictions-table').empty();

        // Add predictions to table
        data.predictions.forEach(prediction => {
            const change = prediction.price - data.current_price;
            const changePercent = (change / data.current_price * 100).toFixed(2);
            const changeClass = change >= 0 ? 'positive-change' : 'negative-change';
            const changeSign = change >= 0 ? '+' : '';

            $('#predictions-table').append(`
                <tr>
                    <td>${prediction.day}</td>
                    <td>${prediction.date}</td>
                    <td>$${prediction.price.toLocaleString()}</td>
                    <td class="${changeClass}">${changeSign}${changePercent}%</td>
                </tr>
            `);
        });

        // Show results
        $('#results').removeClass('d-none');
    }
});