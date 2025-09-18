let isLoading = false;
let hasMoreContent = document.getElementById('load-more') ? true : false;
let currentPage = document.getElementById('load-more') ? parseInt(document.getElementById('load-more').getAttribute('data-next-page')) : null;

function loadMore() {
    if (isLoading || !hasMoreContent) return;
    
    isLoading = true;
    $('#loading-indicator').show();
    $('#load-more').hide();
    
    var url = "/workout/?page=" + currentPage;

    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function (response) {
            if (response.workout_data.length > 0) {
                var html = '';
                response.workout_data.forEach(function (data) {
                    html += '<div>';
                    html += '<h2 class="workout_date_type">' + data.workout.date + ' - ' + data.workout.type_workout;
                    
                    if (data.workout.duration > 0) {
                        var hours = Math.floor(data.workout.duration / 60);
                        var minutes = data.workout.duration % 60;
                        var timeStr = hours > 0 ? hours + 'h ' + (minutes > 0 ? minutes + 'min' : '') : minutes + 'min';
                        html += ' - ' + timeStr.trim();
                    }
                    html += '</h2>';

                    if (data.exercises && data.exercises.length > 0) {
                        var lang = document.body.getAttribute('data-lang');
                        html += '<table><thead><tr>';
                        if (lang === "fr") {
                            html += '<th>Exercice</th>';
                            if (data.workout.type_workout !== "CrossFit") html += '<th>Séries</th>';
                            html += '<th>Répétitions</th><th>Poids (kg)</th>';
                        } else {
                            html += '<th>Exercise</th>';
                            if (data.workout.type_workout !== "CrossFit") html += '<th>Series</th>';
                            html += '<th>Repetitions</th><th>Weight (kg)</th>';
                        }
                        html += '</tr></thead><tbody>';
                        data.exercises.forEach(function (exercise) {
                            html += '<tr>';
                            html += '<td>' + exercise.name + '</td>';
                            if (data.workout.type_workout !== "CrossFit") html += '<td>' + exercise.nb_series + '</td>';
                            html += '<td>' + exercise.nb_repetition + '</td>';
                            html += '<td>' + exercise.weight + '</td>';
                            html += '</tr>';
                        });
                        html += '</tbody></table>';
                    }
                    html += '</div>';
                });
                $('#workout-list').append(html);
            }

            if (response.has_next) {
                currentPage = response.next_page_number;
                $('#load-more').show();
            } else {
                hasMoreContent = false;
                $('#load-more').remove();
            }
            
            $('#loading-indicator').hide();
            isLoading = false;
        },
        error: function() {
            $('#loading-indicator').hide();
            $('#load-more').show();
            isLoading = false;
        }
    });
}

$(document).ready(function() {
    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 200) {
            loadMore();
        }
    });
    
    $('#load-more').click(function() {
        loadMore();
    });
});
