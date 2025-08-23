function loadMore() {

    var nextPage = document.getElementById('load-more').getAttribute('data-next-page');
    var lang = document.body.getAttribute('data-lang');
    var name_workout = (lang === "en") ? "workout" : "sports";
    var url = "/" + lang + "/" + name_workout + "/?page=" + nextPage;

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
                    
                    /* On affiche la durée si elle est supérieur à 0 */
                    if (data.workout.duration > 0) {
                        var hours = Math.floor(data.workout.duration / 60);
                        var minutes = data.workout.duration % 60;
                        var timeStr = hours > 0 ? hours + 'h ' + (minutes > 0 ? minutes + 'min' : '') : minutes + 'min';
                        html += ' - ' + timeStr.trim();
                    }
                    html += '</h2>';

                    /* on affiche les exo seulement si il y en as plus qu'un */
                    if (data.exercises && data.exercises.length > 0) {
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
                $('#load-more').attr('data-next-page', response.next_page_number);
            } else {
                $('#load-more').remove();
            }
        }
    });
}
