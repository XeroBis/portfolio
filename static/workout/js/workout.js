let isLoading = false;
let hasMoreContent = document.getElementById('load-more') ? true : false;
let currentPage = document.getElementById('load-more') ? parseInt(document.getElementById('load-more').getAttribute('data-next-page')) : null;

// Cache for SVG content
let frontSvgContent = null;
let backSvgContent = null;

function muscleNameToSvgId(muscleName) {
    let svgId = muscleName.toLowerCase().trim();

    if (svgId === 'lower back') {
        return 'lowerback';
    } else if (svgId === 'traps middle') {
        return 'traps-middle';
    } else if (svgId === 'rear shoulder') {
        return 'rear-shoulder';
    } else if (svgId === 'front shoulders') {
        return 'front-shoulders';
    } else if (svgId === 'hamstring') {
        return 'hamstrings';
    }

    return svgId;
}

async function loadSvgContent() {
    if (!frontSvgContent) {
        const frontResponse = await fetch('/static/images/front.svg');
        frontSvgContent = await frontResponse.text();
    }
    if (!backSvgContent) {
        const backResponse = await fetch('/static/images/back.svg');
        backSvgContent = await backResponse.text();
    }
}


function createMuscleModal() {
    // Create backdrop for mobile
    if (isMobileDevice()) {
        let backdrop = document.getElementById('muscle-modal-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'muscle-modal-backdrop';
            backdrop.className = 'muscle-modal-backdrop';
            backdrop.addEventListener('click', hideMuscleModal);
            document.body.appendChild(backdrop);
        }
    }

    const modal = document.createElement('div');
    modal.id = 'muscle-modal';
    modal.className = 'muscle-modal';
    modal.innerHTML = '<div class="muscle-modal-content"></div>';
    document.body.appendChild(modal);
    return modal;
}


async function showMuscleModal(exerciseRow, muscleGroups) {
    const modal = document.getElementById('muscle-modal') || createMuscleModal();
    const modalContent = modal.querySelector('.muscle-modal-content');

    if (!muscleGroups || muscleGroups.trim() === '') {
        modalContent.innerHTML = '<p>No muscle groups specified</p>';
    } else {
        await loadSvgContent();

        const muscleList = muscleGroups.split(',').map(m => m.trim()).filter(m => m);

        const svgIdsToHighlight = new Set();
        muscleList.forEach(muscle => {
            const svgId = muscleNameToSvgId(muscle);
            svgIdsToHighlight.add(svgId);
        });

        modalContent.innerHTML = `
            <div class="muscle-modal-layout">
                <div class="muscle-list-section">
                    <h3>Muscle Groups</h3>
                    <ul>${muscleList.map(muscle => '<li>' + muscle + '</li>').join('')}</ul>
                </div>
                <div class="muscle-svg-section">
                    <div class="svg-container">
                        <h4>Front</h4>
                        <div class="body-svg">${frontSvgContent}</div>
                    </div>
                    <div class="svg-container">
                        <h4>Back</h4>
                        <div class="body-svg">${backSvgContent}</div>
                    </div>
                </div>
            </div>
        `;

        // Highlight muscles in both SVGs
        svgIdsToHighlight.forEach(id => {
            const allElements = modalContent.querySelectorAll(`.body-svg svg #${id}`);

            allElements.forEach(element => {
                // Apply color to all paths within the group
                const paths = element.querySelectorAll('path');
                paths.forEach(path => {
                    path.style.fill = '#ff6b6b';
                    path.style.opacity = '0.9';
                });
            });
        });
    }

    // Position the modal near the cursor
    modal.style.display = 'block';

    // Show backdrop on mobile
    const backdrop = document.getElementById('muscle-modal-backdrop');
    if (backdrop) {
        backdrop.style.display = 'block';
    }

    // Position the modal relative to the row (only on desktop)
    if (!isMobileDevice()) {
        const rect = exerciseRow.getBoundingClientRect();
        const modalWidth = 700; // max-width from CSS
        const spaceOnRight = window.innerWidth - rect.right;

        // Check if there's enough space on the right
        if (spaceOnRight > modalWidth + 40) {
            // Position to the right (original behavior)
            modal.style.top = (rect.top + window.scrollY - 10) + 'px';
            modal.style.left = (rect.right + 20) + 'px';
            modal.style.transform = 'none';
        } else {
            // Position above/below the exercise (centered horizontally)
            const rowCenter = rect.left + (rect.width / 2);
            modal.style.left = rowCenter + 'px';
            modal.style.transform = 'translateX(-50%)';

            // Wait for modal to render to get accurate height
            requestAnimationFrame(() => {
                const modalHeight = modal.offsetHeight;
                const spaceAbove = rect.top;
                const spaceBelow = window.innerHeight - rect.bottom;

                // Position above if there's more space above and enough room
                if (spaceAbove > spaceBelow && spaceAbove > modalHeight + 20) {
                    modal.style.top = (rect.top + window.scrollY - modalHeight - 10) + 'px';
                } else {
                    // Position below
                    modal.style.top = (rect.bottom + window.scrollY + 10) + 'px';
                }
            });
        }
    }
}

// Hide muscle modal
function hideMuscleModal() {
    const modal = document.getElementById('muscle-modal');
    if (modal) {
        modal.style.display = 'none';
    }

    // Hide backdrop on mobile
    const backdrop = document.getElementById('muscle-modal-backdrop');
    if (backdrop) {
        backdrop.style.display = 'none';
    }
}

// Check if device is mobile
function isMobileDevice() {
    return window.matchMedia('(max-width: 768px)').matches ||
           /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Attach event listeners to exercise rows
function attachHoverListeners() {
    const isMobile = isMobileDevice();

    document.querySelectorAll('.exercise-row').forEach(row => {
        // Remove all existing listeners
        row.removeEventListener('mouseenter', handleMouseEnter);
        row.removeEventListener('mouseleave', handleMouseLeave);
        row.removeEventListener('click', handleClick);

        if (isMobile) {
            // On mobile: use click
            row.addEventListener('click', handleClick);
        } else {
            // On desktop: use hover
            row.addEventListener('mouseenter', handleMouseEnter);
            row.addEventListener('mouseleave', handleMouseLeave);
        }
    });
}

function handleMouseEnter() {
    const muscleGroups = this.getAttribute('data-muscle-groups');
    showMuscleModal(this, muscleGroups);
}

function handleMouseLeave() {
    hideMuscleModal();
}

function handleClick(e) {
    e.preventDefault();
    e.stopPropagation();

    const muscleGroups = this.getAttribute('data-muscle-groups');
    const modal = document.getElementById('muscle-modal');

    // If modal is already visible for this row, hide it
    if (modal && modal.style.display === 'block' && modal.dataset.currentRow === this.dataset.rowId) {
        hideMuscleModal();
    } else {
        // Show modal for this row
        if (!this.dataset.rowId) {
            this.dataset.rowId = 'row-' + Math.random().toString(36).slice(2, 11);
        }
        showMuscleModal(this, muscleGroups);
        if (modal) {
            modal.dataset.currentRow = this.dataset.rowId;
        }
    }
}

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
                // Get translations once for all workouts
                const translations = JSON.parse(document.getElementById('workout-translations').textContent);

                var html = '';
                response.workout_data.forEach(function (data) {
                    html += '<div>';
                    html += '<div style="display: flex; justify-content: space-between; align-items: center;">';
                    html += '<h2 class="workout_date_type">' + data.workout.date + ' - ' + data.workout.type_workout;

                    if (data.workout.duration > 0) {
                        var hours = Math.floor(data.workout.duration / 60);
                        var minutes = data.workout.duration % 60;
                        var timeStr = hours > 0 ? hours + 'h ' + (minutes > 0 ? minutes + 'min' : '') : minutes + 'min';
                        html += ' - ' + timeStr.trim();
                    }
                    html += '</h2>';
                    html += '<a href="/workout/edit_workout/' + data.workout.id + '/">';
                    html += '<button class="cliquable button_workout">' + (translations.edit || 'Edit') + '</button>';
                    html += '</a>';
                    html += '</div>';

                    if (data.exercises && data.exercises.length > 0) {

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
                            var muscleGroups = exercise.muscle_groups ? exercise.muscle_groups.join(', ') : '';
                            html += '<tr class="exercise-row" data-muscle-groups="' + muscleGroups + '">';
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

                // Attach hover listeners to newly added exercises
                attachHoverListeners();
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
    // Pre-load SVG content for faster display
    loadSvgContent();

    // Initialize hover listeners for existing exercises
    attachHoverListeners();

    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 200) {
            loadMore();
        }
    });

    $('#load-more').click(function() {
        loadMore();
    });
});
