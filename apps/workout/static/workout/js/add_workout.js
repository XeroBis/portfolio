function addExercice() {
    fetch('/workout/get_list_exercice/')
        .then(response => response.json())
        .then(data => {
            const exercisesContainer = document.getElementById('exercises');
            let exerciseCount = document.querySelectorAll('.exercise').length;

            const exerciseDiv = document.createElement('div');
            exerciseDiv.className = 'exercise';
            exerciseDiv.id = `exercise_row_${exerciseCount}`;

            exerciseDiv.innerHTML = `
                <div class="exercise-name-header">
                    <div class="exercise-search-container">
                        <input type="text" class="workout_input exercise-search-input"
                               id="exercise_${exerciseCount}_search"
                               placeholder="Search exercise..."
                               onkeyup="filterExercises(${exerciseCount})"
                               onfocus="showExerciseDropdown(${exerciseCount})"
                               onblur="hideExerciseDropdown(${exerciseCount})">
                        <input type="hidden" id="exercise_${exerciseCount}_name" name="exercise_${exerciseCount}_name" required>
                        <div class="exercise-dropdown" id="exercise_${exerciseCount}_dropdown" style="display: none;">
                            ${data.all_exercises.map(ex => `<div class="exercise-option" data-name="${ex.name}" data-type="${ex.exercise_type}" onclick="selectExercise(${exerciseCount}, '${ex.name}', '${ex.exercise_type}')">${ex.name}</div>`).join('')}
                        </div>
                    </div>
                    <button type="button" class="add_workout_btn_delete" onclick="deleteExercise(${exerciseCount})">❌</button>
                </div>
                <div id="exercise_${exerciseCount}_fields" class="exercise-fields"></div>
            `;

            exercisesContainer.appendChild(exerciseDiv);
            exerciseCount++;
        });
};

function deleteExercise(index) {
    const exerciseRow = document.getElementById(`exercise_row_${index}`);
    if (exerciseRow) {
        exerciseRow.remove();
    }
};

function filterExercises(exerciseIndex) {
    const searchInput = document.getElementById(`exercise_${exerciseIndex}_search`);
    const dropdown = document.getElementById(`exercise_${exerciseIndex}_dropdown`);
    const searchTerm = searchInput.value.toLowerCase();

    const options = dropdown.querySelectorAll('.exercise-option');
    options.forEach(option => {
        const exerciseName = option.getAttribute('data-name').toLowerCase();
        if (exerciseName.includes(searchTerm)) {
            option.style.display = 'block';
        } else {
            option.style.display = 'none';
        }
    });

    if (searchTerm.length > 0) {
        dropdown.style.display = 'block';
    }
}

function showExerciseDropdown(exerciseIndex) {
    const dropdown = document.getElementById(`exercise_${exerciseIndex}_dropdown`);
    dropdown.style.display = 'block';
}

function hideExerciseDropdown(exerciseIndex) {
    setTimeout(() => {
        const dropdown = document.getElementById(`exercise_${exerciseIndex}_dropdown`);
        dropdown.style.display = 'none';
    }, 200);
}

function selectExercise(exerciseIndex, exerciseName, exerciseType) {
    const searchInput = document.getElementById(`exercise_${exerciseIndex}_search`);
    const hiddenInput = document.getElementById(`exercise_${exerciseIndex}_name`);
    const dropdown = document.getElementById(`exercise_${exerciseIndex}_dropdown`);

    searchInput.value = exerciseName;
    hiddenInput.value = exerciseName;
    dropdown.style.display = 'none';

    updateExerciseFields(exerciseIndex, exerciseType);
}

function updateExerciseFields(exerciseIndex, exerciseType = null) {
    const hiddenInput = document.getElementById(`exercise_${exerciseIndex}_name`);
    const fieldsContainer = document.getElementById(`exercise_${exerciseIndex}_fields`);

    if (!exerciseType && hiddenInput.value) {
        const dropdown = document.getElementById(`exercise_${exerciseIndex}_dropdown`);
        const selectedOption = dropdown.querySelector(`[data-name="${hiddenInput.value}"]`);
        exerciseType = selectedOption ? selectedOption.getAttribute('data-type') : null;
    }

    let fieldsHTML = '';
    const translations = JSON.parse(document.getElementById('add-workout-translations').textContent);

    if (exerciseType === 'strength') {
        fieldsHTML = `
            <div class="series-container" id="exercise_${exerciseIndex}_series_container">
                <div class="series-header">
                    <h4>${translations.series}:</h4>
                    <button type="button" class="cliquable button_add_series" onclick="addSeries(${exerciseIndex}, 'strength')">+ ${translations.series}</button>
                </div>
                <div id="exercise_${exerciseIndex}_series_list"></div>
            </div>
        `;
        fieldsContainer.innerHTML = fieldsHTML;
        addSeries(exerciseIndex, 'strength');
    } else if (exerciseType === 'cardio') {
        fieldsHTML = `
            <div class="series-container" id="exercise_${exerciseIndex}_series_container">
                <div class="series-header">
                    <h4>Intervals:</h4>
                    <button type="button" class="cliquable button_add_series" onclick="addSeries(${exerciseIndex}, 'cardio')">+ Interval</button>
                </div>
                <div id="exercise_${exerciseIndex}_series_list"></div>
            </div>
        `;
        fieldsContainer.innerHTML = fieldsHTML;
        addSeries(exerciseIndex, 'cardio');
    }
}

function addSeries(exerciseIndex, exerciseType) {
    const seriesList = document.getElementById(`exercise_${exerciseIndex}_series_list`);
    const seriesCount = seriesList.querySelectorAll('.series-item').length + 1;

    const translations = JSON.parse(document.getElementById('add-workout-translations').textContent);

    let seriesHTML = '';
    if (exerciseType === 'strength') {
        seriesHTML = `
            <div class="series-item" id="exercise_${exerciseIndex}_series_${seriesCount}">
                <div class="series-number">${translations.series} ${seriesCount}</div>
                <div class="series-fields">
                    <div class="input-group">
                        <label class="input-label">${translations.reps}</label>
                        <input type="number" class="workout_input" name="exercise_${exerciseIndex}_series_${seriesCount}_reps" value="8" required>
                    </div>
                    <div class="input-group">
                        <label class="input-label">${translations.weight_kg}</label>
                        <input type="number" class="workout_input" name="exercise_${exerciseIndex}_series_${seriesCount}_weight" value="0">
                    </div>
                    <button type="button" class="add_workout_btn_delete" onclick="deleteSeries(${exerciseIndex}, ${seriesCount})">❌</button>
                </div>
            </div>
        `;
    } else if (exerciseType === 'cardio') {
        seriesHTML = `
            <div class="series-item" id="exercise_${exerciseIndex}_series_${seriesCount}">
                <div class="series-number">Interval ${seriesCount}</div>
                <div class="series-fields">
                    <div class="input-group">
                        <label class="input-label">${translations.duration_sec}</label>
                        <input type="number" class="workout_input" name="exercise_${exerciseIndex}_series_${seriesCount}_duration_seconds" value="1200">
                    </div>
                    <div class="input-group">
                        <label class="input-label">${translations.distance_m}</label>
                        <input type="number" class="workout_input" name="exercise_${exerciseIndex}_series_${seriesCount}_distance_m">
                    </div>
                    <button type="button" class="add_workout_btn_delete" onclick="deleteSeries(${exerciseIndex}, ${seriesCount})">❌</button>
                </div>
            </div>
        `;
    }

    seriesList.insertAdjacentHTML('beforeend', seriesHTML);
}

function deleteSeries(exerciseIndex, seriesNumber) {
    const seriesItem = document.getElementById(`exercise_${exerciseIndex}_series_${seriesNumber}`);
    if (seriesItem) {
        seriesItem.remove();
    }
}

function changeWorkoutType() {
    const selectedType = document.getElementById('add_workout_type_workout').value;
    if (selectedType) {
        fetch(`/workout/get_last_workout/?type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                if (data.date) {
                    document.getElementById('add_workout_date').value = data.date;
                }

                const exercisesContainer = document.getElementById('exercises');
                exercisesContainer.innerHTML = '';

                if (data.exercises && data.exercises.length > 0) {
                    data.exercises.forEach((exercise, index) => {
                        const exerciseDiv = document.createElement('div');
                        exerciseDiv.className = 'exercise';
                        exerciseDiv.id = `exercise_row_${index}`;

                        exerciseDiv.innerHTML = `
                            <div class="exercise-name-header">
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
                                        ${data.all_exercises.map(ex => `<div class="exercise-option" data-name="${ex.name}" data-type="${ex.exercise_type}" onclick="selectExercise(${index}, '${ex.name}', '${ex.exercise_type}')">${ex.name}</div>`).join('')}
                                    </div>
                                </div>
                                <button type="button" class="add_workout_btn_delete" onclick="deleteExercise(${index})">❌</button>
                            </div>
                            <div id="exercise_${index}_fields" class="exercise-fields"></div>
                        `;

                        exercisesContainer.appendChild(exerciseDiv);

                        // Now populate the fields with series data
                        const fieldsContainer = exerciseDiv.querySelector(`#exercise_${index}_fields`);
                        const translations = JSON.parse(document.getElementById('add-workout-translations').textContent);

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
            });
    }
};

function loadWorkoutTypes() {
    fetch('/workout/get_workout_types/')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('add_workout_type_workout');

            // Clear existing options except the first one (placeholder)
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }

            // Add workout types from database
            data.workout_types.forEach(workoutType => {
                const option = document.createElement('option');
                option.value = workoutType.value;
                option.textContent = workoutType.display;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading workout types:', error);
        });
}

// Load workout types when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadWorkoutTypes();
});
