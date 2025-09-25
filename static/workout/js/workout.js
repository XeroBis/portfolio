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
                        const translations = JSON.parse(document.getElementById('workout-translations').textContent);

                        // Determine which exercise types are present
                        var hasStrength = data.exercises.some(ex => ex.exercise_type === 'strength');
                        var hasCardio = data.exercises.some(ex => ex.exercise_type === 'cardio');

                        html += '<table><thead><tr>';
                        html += '<th>' + translations.exercise + '</th>';

                        if (hasStrength) {
                            html += '<th>' + translations.series + '</th>';
                            html += '<th>' + translations.reps + '</th>';
                            html += '<th>' + translations.weight_kg + '</th>';
                        }

                        if (hasCardio) {
                            html += '<th>' + translations.duration_min + '</th>';
                            html += '<th>' + translations.distance_m + '</th>';
                        }

                        html += '</tr></thead><tbody>';

                        data.exercises.forEach(function (exercise) {
                            html += '<tr>';
                            html += '<td>' + exercise.name + '</td>';

                            if (exercise.exercise_type === 'strength') {
                                if (hasStrength) {
                                    html += '<td>' + (exercise.data.nb_series || '-') + '</td>';
                                    html += '<td>' + (exercise.data.nb_repetition || '-') + '</td>';
                                    html += '<td>' + (exercise.data.weight || '-') + '</td>';
                                }
                                if (hasCardio) {
                                    html += '<td>-</td>';
                                    html += '<td>-</td>';
                                }
                            } else if (exercise.exercise_type === 'cardio') {
                                if (hasStrength) {
                                    html += '<td>-</td>';
                                    html += '<td>-</td>';
                                    html += '<td>-</td>';
                                }
                                if (hasCardio) {
                                    html += '<td>' + (exercise.data.duration_seconds ? Math.round(exercise.data.duration_seconds / 60) : '-') + '</td>';
                                    html += '<td>' + (exercise.data.distance_m || '-') + '</td>';
                                }
                            }
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
