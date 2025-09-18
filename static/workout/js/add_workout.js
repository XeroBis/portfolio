function addExercice() {
    fetch('/workout/get_list_exercice/')
        .then(response => response.json())
        .then(data => {
            const exercisesContainer = document.getElementById('exercises');

            let exerciseCount = document.querySelectorAll('.exercise').length;

            let ex_name = "Exercice"
            let nb_series = "Séries"
            let nb_rep = "Répétitions"
            let weight = "Poids (kg)"

            if (document.getElementById("my_projects").innerHTML === "Home") {
                ex_name = "Exercise";
                nb_series = "Series";
                nb_rep = "Repetitions";
                weight = "Weight (kg)";
            }

            const exerciseDiv = document.createElement('div');
            exerciseDiv.className = 'exercise';
            exerciseDiv.id = `exercise_row_${exerciseCount}`;

            let exerciseOptions = data.all_exercises.map(ex =>
                `<option value="${ex}">${ex}</option>`
            ).join('');

            exerciseDiv.innerHTML = `
                <select class="workout_input" id="exercise_${exerciseCount}_name" name="exercise_${exerciseCount}_name" required>
                            ${exerciseOptions}
                        </select>
                <input type="number" class="workout_input" id="exercise_${exerciseCount}_nb_series" name="exercise_${exerciseCount}_nb_series" placeholder="${nb_series}" required>
                <input type="number" class="workout_input" id="exercise_${exerciseCount}_nb_repetition" name="exercise_${exerciseCount}_nb_repetition" placeholder="${nb_rep}" required>
                <input type="number" class="workout_input" id="exercise_${exerciseCount}_weight" name="exercise_${exerciseCount}_weight" placeholder="${weight}" required>
                <button type="button" class="add_workout_btn_delete" onclick="deleteExercise(${exerciseCount})">❌</button>
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

function changeWorkoutType() {
    const selectedType = document.getElementById('add_workout_type_workout').value;
    if (selectedType) {
        fetch(`/workout/get_last_workout/?type=${selectedType}`)
            .then(response => response.json())
            .then(data => {
                if (data.date) {
                    document.getElementById('add_workout_date').value = data.date;
                }

                document.getElementById('btn_add_exercise').style.display = "block";
                const exercisesContainer = document.getElementById('exercises');
                const acc = document.getElementById("my_projects").innerHTML;
                var ex_name = "Exercice"
                var nb_series = "Séries"
                var nb_rep = "Répétitions"
                var weight = "Poids (kg)"
                if (acc == "Home") {
                    ex_name = "Exercise"
                    nb_series = "Series"
                    nb_rep = "Repetitions"
                    weight = "Weight (kg)"
                }

                exercisesContainer.innerHTML = '';

                if (data.exercises && data.exercises.length > 0) {
                    const headerRow = document.createElement('div');
                    headerRow.className = 'exercise-header';
                    headerRow.innerHTML = `
                    <span>${ex_name}</span>
                    <span>${nb_series}</span>
                    <span>${nb_rep}</span>
                    <span>${weight}</span>
                `;
                    exercisesContainer.appendChild(headerRow);

                    data.exercises.forEach((exercise, index) => {
                        const exerciseDiv = document.createElement('div');
                        exerciseDiv.className = 'exercise';
                        exerciseDiv.id = `exercise_row_${index}`;

                        let exerciseOptions = data.all_exercises.map(ex =>
                            `<option value="${ex}" ${exercise.name === ex ? 'selected' : ''}>${ex}</option>`
                        ).join('');

                        exerciseDiv.innerHTML = `
                        <select class="workout_input" id="exercise_${index}_name" name="exercise_${index}_name" required>
                            ${exerciseOptions}
                        </select>
                        <input type="number" class="workout_input" id="exercise_${index}_nb_series" name="exercise_${index}_nb_series" value="${exercise.nb_series}" required>
                        <input type="number"  class="workout_input" id="exercise_${index}_nb_repetition" name="exercise_${index}_nb_repetition" value="${exercise.nb_repetition}" required>
                        <input type="number" class="workout_input" id="exercise_${index}_weight" name="exercise_${index}_weight" value="${exercise.weight}" required>
                        <button type="button" class="add_workout_btn_delete" onclick="deleteExercise(${index})">❌</button>
                    `;

                        exercisesContainer.appendChild(exerciseDiv);
                    });
                }
            });
    }
};
