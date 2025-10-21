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
        fieldsHTML += `
            <div class="input-group">
                <label class="input-label">${translations.series}</label>
                <input type="number" class="workout_input" id="exercise_${exerciseIndex}_nb_series" name="exercise_${exerciseIndex}_nb_series" required>
            </div>
            <div class="input-group">
                <label class="input-label">${translations.reps}</label>
                <input type="number" class="workout_input" id="exercise_${exerciseIndex}_nb_repetition" name="exercise_${exerciseIndex}_nb_repetition" required>
            </div>
            <div class="input-group">
                <label class="input-label">${translations.weight_kg}</label>
                <input type="number" class="workout_input" id="exercise_${exerciseIndex}_weight" name="exercise_${exerciseIndex}_weight">
            </div>
        `;
    } else if (exerciseType === 'cardio') {
        fieldsHTML += `
            <div class="input-group">
                <label class="input-label">${translations.duration_sec}</label>
                <input type="number" class="workout_input" id="exercise_${exerciseIndex}_duration_seconds" name="exercise_${exerciseIndex}_duration_seconds" required>
            </div>
            <div class="input-group">
                <label class="input-label">${translations.distance_m}</label>
                <input type="number" class="workout_input" id="exercise_${exerciseIndex}_distance_m" name="exercise_${exerciseIndex}_distance_m">
            </div>
        `;
    }

    fieldsContainer.innerHTML = fieldsHTML;
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

                        let fieldsHTML = '';
                        const translations = JSON.parse(document.getElementById('add-workout-translations').textContent);

                        for (let field in exercise) {
                            if (['name', 'exercise_type', 'type'].includes(field)) continue;
                            const value = exercise[field] || 0;

                            let labelText = field;
                            if (field === 'nb_series') {
                                labelText = translations.series;
                            } else if (field === 'nb_repetition') {
                                labelText = translations.reps;
                            } else if (field === 'weight') {
                                labelText = translations.weight_kg;
                            } else if (field === 'duration_seconds') {
                                labelText = translations.duration_sec;
                            } else if (field === 'distance_m') {
                                labelText = translations.distance_m;
                            }

                            fieldsHTML += `
                                <div class="input-group">
                                    <label class="input-label">${labelText}</label>
                                    <input type="number" class="workout_input"
                                        id="exercise_${index}_${field}"
                                        name="exercise_${index}_${field}"
                                        value="${value}">
                                </div>`;
                        }

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
                            <div id="exercise_${index}_fields" class="exercise-fields">${fieldsHTML}</div>
                        `;

                        exercisesContainer.appendChild(exerciseDiv);
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
