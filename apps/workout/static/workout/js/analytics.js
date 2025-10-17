// Analytics Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const sections = document.querySelectorAll('.analytics-section');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');

            // Remove active class from all buttons and sections
            tabButtons.forEach(btn => btn.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));

            // Add active class to clicked button and corresponding section
            button.classList.add('active');
            document.getElementById(`${targetTab}-section`).classList.add('active');

            // Initialize charts when dashboard tab is activated
            if (targetTab === 'dashboard' && !window.chartsInitialized) {
                initializeCharts();
            }
        });
    });

    // Year navigation functionality
    const prevYearBtn = document.getElementById('prev-year');
    const nextYearBtn = document.getElementById('next-year');
    const currentYearSpan = document.getElementById('current-year');

    if (prevYearBtn && nextYearBtn && currentYearSpan) {
        const currentYear = parseInt(currentYearSpan.textContent);

        // Check if there's data for previous/next year and disable accordingly
        const hasPrevData = prevYearBtn.getAttribute('data-has-data') === 'true';
        const hasNextData = nextYearBtn.getAttribute('data-has-data') === 'true';

        if (!hasPrevData) {
            prevYearBtn.disabled = true;
            prevYearBtn.style.opacity = '0.3';
            prevYearBtn.style.cursor = 'not-allowed';
        }

        if (!hasNextData) {
            nextYearBtn.disabled = true;
            nextYearBtn.style.opacity = '0.3';
            nextYearBtn.style.cursor = 'not-allowed';
        }

        prevYearBtn.addEventListener('click', () => {
            if (hasPrevData) {
                const newYear = currentYear - 1;
                window.location.href = `?year=${newYear}`;
            }
        });

        nextYearBtn.addEventListener('click', () => {
            if (hasNextData) {
                const newYear = currentYear + 1;
                window.location.href = `?year=${newYear}`;
            }
        });
    }

    // Calendar day click functionality
    const calendarDays = document.querySelectorAll('.calendar-day.has-workout');
    calendarDays.forEach(day => {
        day.addEventListener('click', () => {
            const workoutId = day.getAttribute('data-workout-id');
            if (workoutId) {
                window.location.href = `/workout/edit_workout/${workoutId}/`;
            }
        });
    });

    // Initialize charts on page load if dashboard is active
    if (document.getElementById('dashboard-section').classList.contains('active')) {
        initializeCharts();
    }
});

// Chart.js Configuration
function initializeCharts() {
    if (window.chartsInitialized) return;
    window.chartsInitialized = true;

    // Common chart options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: true,
                position: 'top',
            }
        }
    };

    // Weekly Trend Chart
    const weeklyLabels = weeklyWorkouts.map(w => w.start);
    const weeklyCounts = weeklyWorkouts.map(w => w.count);

    const weeklyCtx = document.getElementById('weeklyTrendChart');
    if (weeklyCtx) {
        new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels: weeklyLabels,
                datasets: [{
                    label: chartTranslations.workoutsPerWeek,
                    data: weeklyCounts,
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }]
            },
            options: {
                ...commonOptions,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    // Workout Type Chart
    const typeLabels = workoutsByType.map(w => w.type_workout__name_workout || 'No Type');
    const typeCounts = workoutsByType.map(w => w.count);

    const typeCtx = document.getElementById('workoutTypeChart');
    if (typeCtx) {
        new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: typeLabels,
                datasets: [{
                    data: typeCounts,
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(245, 87, 108, 0.8)',
                        'rgba(254, 158, 73, 0.8)',
                        'rgba(72, 201, 176, 0.8)',
                    ],
                    borderWidth: 2,
                    borderColor: '#fff',
                }]
            },
            options: {
                ...commonOptions,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }

    // Top Exercises Chart
    const exerciseLabels = topExercises.map(e => e.name__name);
    const exerciseCounts = topExercises.map(e => e.count);

    const exercisesCtx = document.getElementById('topExercisesChart');
    if (exercisesCtx) {
        // Determine font size based on screen width
        const isMobile = window.innerWidth <= 480;
        const isTablet = window.innerWidth <= 768;
        const labelFontSize = isMobile ? 9 : isTablet ? 10 : 11;

        new Chart(exercisesCtx, {
            type: 'bar',
            data: {
                labels: exerciseLabels,
                datasets: [{
                    label: chartTranslations.timesPerformed,
                    data: exerciseCounts,
                    backgroundColor: 'rgba(118, 75, 162, 0.8)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2,
                }]
            },
            options: {
                ...commonOptions,
                indexAxis: 'y',
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 10,
                        top: 10,
                        bottom: 10
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            font: {
                                size: labelFontSize
                            }
                        }
                    },
                    y: {
                        ticks: {
                            autoSkip: false,
                            font: {
                                size: labelFontSize
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Export function for external use
window.initializeCharts = initializeCharts;
