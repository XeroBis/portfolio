// Load existing workout data when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // First load workout types
    loadWorkoutTypes();

    // Wait a bit for workout types to load, then populate the form
    setTimeout(function() {
        populateWorkoutData();
    }, 500);
});

function populateWorkoutData() {
    // Get data from JSON scripts
    const workout = JSON.parse(document.getElementById('workout-data').textContent);
    const exercises = JSON.parse(document.getElementById('exercises-data').textContent);
    const all_exercises = JSON.parse(document.getElementById('all-exercises-data').textContent);

    if (!workout) {
        console.error('No workout data found');
        return;
    }

    // Set workout type
    const typeSelect = document.getElementById('add_workout_type_workout');
    if (typeSelect && workout.type_workout) {
        typeSelect.value = workout.type_workout;
    }

    // Populate exercises
    const exercisesContainer = document.getElementById('exercises');
    if (!exercisesContainer) {
        console.error('Exercises container not found');
        return;
    }

    exercisesContainer.innerHTML = '';

    if (exercises && exercises.length > 0) {
        const translations = JSON.parse(document.getElementById('add-workout-translations').textContent);

        exercises.forEach((exercise, index) => {
            const exerciseDiv = document.createElement('div');
            exerciseDiv.className = 'exercise';
            exerciseDiv.id = `exercise_row_${index}`;

            exerciseDiv.innerHTML = `
                <div class="exercise-name-header">
                    <div class="exercise-position-number">${index + 1}.</div>
                    <div class="exercise-search-container">
                        <input type="text" class="workout_input exercise-search-input"
                               id="exercise_${index}_search"
                               value="${exercise.name}"
                               placeholder="Search exercise..."
                               onkeyup="filterExercises(${index})"
                               onfocus="showExerciseDropdown(${index})"
                               onblur="hideExerciseDropdown(${index})">
                        <input type="hidden" id="exercise_${index}_name" name="exercise_${index}_name" value="${exercise.name}" required>
                        <div class="exercise-dropdown" id="exercise_${index}_dropdown" style="display: none;">
                            ${all_exercises.map(ex => `<div class="exercise-option" data-name="${ex.name}" data-type="${ex.exercise_type}" onclick="selectExercise(${index}, '${ex.name}', '${ex.exercise_type}')">${ex.name}</div>`).join('')}
                        </div>
                    </div>
                    <button type="button" class="add_workout_btn_delete" onclick="deleteExercise(${index})">❌</button>
                </div>
                <div id="exercise_${index}_fields" class="exercise-fields"></div>
            `;

            exercisesContainer.appendChild(exerciseDiv);

            // Populate the fields with series data
            const fieldsContainer = exerciseDiv.querySelector(`#exercise_${index}_fields`);

            if (exercise.exercise_type === 'strength') {
                fieldsContainer.innerHTML = `
                    <div class="series-container" id="exercise_${index}_series_container">
                        <div class="series-header">
                            <h4>${translations.series}:</h4>
                            <button type="button" class="cliquable button_add_series" onclick="addSeries(${index}, 'strength')">+ ${translations.series}</button>
                        </div>
                        <div id="exercise_${index}_series_list"></div>
                    </div>
                `;

                const seriesList = exerciseDiv.querySelector(`#exercise_${index}_series_list`);
                exercise.series.forEach((series) => {
                    const seriesHTML = `
                        <div class="series-item" id="exercise_${index}_series_${series.series_number}">
                            <div class="series-number">${translations.series} ${series.series_number}</div>
                            <div class="series-fields">
                                <div class="input-group">
                                    <label class="input-label">${translations.reps}</label>
                                    <input type="number" class="workout_input" name="exercise_${index}_series_${series.series_number}_reps" value="${series.reps}" required>
                                </div>
                                <div class="input-group">
                                    <label class="input-label">${translations.weight_kg}</label>
                                    <input type="number" class="workout_input" name="exercise_${index}_series_${series.series_number}_weight" value="${series.weight}">
                                </div>
                                <button type="button" class="add_workout_btn_delete" onclick="deleteSeries(${index}, ${series.series_number})">❌</button>
                            </div>
                        </div>
                    `;
                    seriesList.insertAdjacentHTML('beforeend', seriesHTML);
                });
            } else if (exercise.exercise_type === 'cardio') {
                fieldsContainer.innerHTML = `
                    <div class="series-container" id="exercise_${index}_series_container">
                        <div class="series-header">
                            <h4>Intervals:</h4>
                            <button type="button" class="cliquable button_add_series" onclick="addSeries(${index}, 'cardio')">+ Interval</button>
                        </div>
                        <div id="exercise_${index}_series_list"></div>
                    </div>
                `;

                const seriesList = exerciseDiv.querySelector(`#exercise_${index}_series_list`);
                exercise.series.forEach((series) => {
                    const seriesHTML = `
                        <div class="series-item" id="exercise_${index}_series_${series.series_number}">
                            <div class="series-number">Interval ${series.series_number}</div>
                            <div class="series-fields">
                                <div class="input-group">
                                    <label class="input-label">${translations.duration_sec}</label>
                                    <input type="number" class="workout_input" name="exercise_${index}_series_${series.series_number}_duration_seconds" value="${series.duration_seconds || ''}">
                                </div>
                                <div class="input-group">
                                    <label class="input-label">${translations.distance_m}</label>
                                    <input type="number" class="workout_input" name="exercise_${index}_series_${series.series_number}_distance_m" value="${series.distance_m || ''}">
                                </div>
                                <button type="button" class="add_workout_btn_delete" onclick="deleteSeries(${index}, ${series.series_number})">❌</button>
                            </div>
                        </div>
                    `;
                    seriesList.insertAdjacentHTML('beforeend', seriesHTML);
                });
            }
        });
    }
}
