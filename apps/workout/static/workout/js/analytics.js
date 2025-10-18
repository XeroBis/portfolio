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
        let currentYear = parseInt(currentYearSpan.textContent);

        // Check if there's data for previous/next year and disable accordingly
        let hasPrevData = prevYearBtn.getAttribute('data-has-data') === 'true';
        let hasNextData = nextYearBtn.getAttribute('data-has-data') === 'true';

        function updateYearNavButtons(hasPrev, hasNext) {
            if (!hasPrev) {
                prevYearBtn.disabled = true;
                prevYearBtn.style.opacity = '0.3';
                prevYearBtn.style.cursor = 'not-allowed';
            } else {
                prevYearBtn.disabled = false;
                prevYearBtn.style.opacity = '1';
                prevYearBtn.style.cursor = 'pointer';
            }

            if (!hasNext) {
                nextYearBtn.disabled = true;
                nextYearBtn.style.opacity = '0.3';
                nextYearBtn.style.cursor = 'not-allowed';
            } else {
                nextYearBtn.disabled = false;
                nextYearBtn.style.opacity = '1';
                nextYearBtn.style.cursor = 'pointer';
            }
        }

        // Initial button state
        updateYearNavButtons(hasPrevData, hasNextData);

        // Function to update calendar via AJAX
        async function updateCalendar(year) {
            try {
                // Fetch calendar data from server
                const response = await fetch(`/workout/get_calendar_data/?year=${year}`);
                const data = await response.json();

                // Update year display
                currentYear = data.year;
                currentYearSpan.textContent = currentYear;

                // Update navigation buttons
                hasPrevData = data.has_prev_year_data;
                hasNextData = data.has_next_year_data;
                updateYearNavButtons(hasPrevData, hasNextData);

                // Update the calendar grid
                const calendarGrid = document.querySelector('.calendar-grid');
                calendarGrid.innerHTML = '';

                // Create months
                data.months.forEach(month => {
                    const monthDiv = document.createElement('div');
                    monthDiv.className = 'calendar-month' + (month.is_current ? ' current-month' : '');

                    // Month header
                    const monthHeader = document.createElement('h3');
                    monthHeader.textContent = month.name;
                    monthDiv.appendChild(monthHeader);

                    // Weekday headers
                    const weekdaysDiv = document.createElement('div');
                    weekdaysDiv.className = 'calendar-weekdays';
                    chartTranslations.weekdays.forEach(day => {
                        const dayDiv = document.createElement('div');
                        dayDiv.className = 'weekday';
                        dayDiv.textContent = day;
                        weekdaysDiv.appendChild(dayDiv);
                    });
                    monthDiv.appendChild(weekdaysDiv);

                    // Days container
                    const daysDiv = document.createElement('div');
                    daysDiv.className = 'calendar-days';

                    // Empty days before month starts
                    for (let i = 0; i < month.start_weekday; i++) {
                        const emptyDiv = document.createElement('div');
                        emptyDiv.className = 'calendar-day empty';
                        daysDiv.appendChild(emptyDiv);
                    }

                    // Month days
                    for (let day = 1; day <= month.num_days; day++) {
                        const dayDiv = document.createElement('div');
                        dayDiv.className = 'calendar-day';
                        dayDiv.textContent = day;

                        // Check if this day has a workout
                        const workout = month.workout_days[day];
                        if (workout) {
                            dayDiv.classList.add('has-workout');
                            dayDiv.setAttribute('data-workout-type', workout.type);
                            dayDiv.setAttribute('data-workout-id', workout.id);
                            dayDiv.setAttribute('title', workout.type);

                            // Add click handler
                            dayDiv.addEventListener('click', () => {
                                window.location.href = `/workout/edit_workout/${workout.id}/`;
                            });
                        }

                        daysDiv.appendChild(dayDiv);
                    }

                    monthDiv.appendChild(daysDiv);
                    calendarGrid.appendChild(monthDiv);
                });

                // Update URL without reloading
                const url = new URL(window.location.href);
                url.searchParams.set('year', year);
                window.history.pushState({}, '', url);

            } catch (error) {
                console.error('Error updating calendar:', error);
                alert('Error updating calendar data. Please try again.');
            }
        }

        prevYearBtn.addEventListener('click', () => {
            if (hasPrevData) {
                const newYear = currentYear - 1;
                updateCalendar(newYear);
            }
        });

        nextYearBtn.addEventListener('click', () => {
            if (hasNextData) {
                const newYear = currentYear + 1;
                updateCalendar(newYear);
            }
        });
    }

    // Calendar day click functionality - for initial page load
    function attachCalendarDayClickHandlers() {
        const calendarDays = document.querySelectorAll('.calendar-day.has-workout');
        calendarDays.forEach(day => {
            day.addEventListener('click', () => {
                const workoutId = day.getAttribute('data-workout-id');
                if (workoutId) {
                    window.location.href = `/workout/edit_workout/${workoutId}/`;
                }
            });
        });
    }
    attachCalendarDayClickHandlers();

    // Initialize charts on page load if dashboard is active
    if (document.getElementById('dashboard-section').classList.contains('active')) {
        initializeCharts();
    }

    // Date filter functionality
    const applyFilterBtn = document.getElementById('apply-filter');
    const resetFilterBtn = document.getElementById('reset-filter');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const quickSelectButtons = document.querySelectorAll('.quick-select-btn');

    // Function to format date as YYYY-MM-DD
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Function to calculate date range
    function getDateRange(range) {
        const today = new Date();
        const endDate = formatDate(today);
        let startDate;

        switch(range) {
            case '7days':
                const sevenDaysAgo = new Date(today);
                sevenDaysAgo.setDate(today.getDate() - 7);
                startDate = formatDate(sevenDaysAgo);
                break;
            case '1month':
                const oneMonthAgo = new Date(today);
                oneMonthAgo.setMonth(today.getMonth() - 1);
                startDate = formatDate(oneMonthAgo);
                break;
            case '3months':
                const threeMonthsAgo = new Date(today);
                threeMonthsAgo.setMonth(today.getMonth() - 3);
                startDate = formatDate(threeMonthsAgo);
                break;
            case '6months':
                const sixMonthsAgo = new Date(today);
                sixMonthsAgo.setMonth(today.getMonth() - 6);
                startDate = formatDate(sixMonthsAgo);
                break;
            case '1year':
                const oneYearAgo = new Date(today);
                oneYearAgo.setFullYear(today.getFullYear() - 1);
                startDate = formatDate(oneYearAgo);
                break;
            case 'ytd':
                const yearStart = new Date(today.getFullYear(), 0, 1);
                startDate = formatDate(yearStart);
                break;
            default:
                return null;
        }

        return { startDate, endDate };
    }

    // Function to update dashboard data via AJAX
    async function updateDashboard(startDate, endDate) {
        try {
            // Build URL with parameters
            const params = new URLSearchParams();
            if (startDate) params.set('start_date', startDate);
            if (endDate) params.set('end_date', endDate);

            // Fetch data from server
            const response = await fetch(`/workout/get_dashboard_data/?${params.toString()}`);
            const data = await response.json();

            // Update stats cards
            document.querySelector('.stat-card:nth-child(1) .stat-value').textContent = data.total_workouts;
            document.querySelector('.stat-card:nth-child(2) .stat-value').textContent = data.total_exercises;
            document.querySelector('.stat-card:nth-child(3) .stat-value').textContent = data.total_volume.toLocaleString() + ' kg';

            // Update global variables for charts
            window.weeklyWorkouts = data.weekly_workouts;
            window.workoutsByType = data.workouts_by_type;
            window.topExercises = data.top_exercises;

            // Destroy existing charts
            if (window.weeklyChart) window.weeklyChart.destroy();
            if (window.typeChart) window.typeChart.destroy();
            if (window.exercisesChart) window.exercisesChart.destroy();

            // Reinitialize charts with new data
            window.chartsInitialized = false;
            initializeCharts();

            // Update URL without reloading
            const url = new URL(window.location.href);
            if (startDate) {
                url.searchParams.set('start_date', startDate);
            } else {
                url.searchParams.delete('start_date');
            }
            if (endDate) {
                url.searchParams.set('end_date', endDate);
            } else {
                url.searchParams.delete('end_date');
            }
            window.history.pushState({}, '', url);

        } catch (error) {
            console.error('Error updating dashboard:', error);
            alert('Error updating dashboard data. Please try again.');
        }
    }

    // Quick select button handlers
    quickSelectButtons.forEach(button => {
        button.addEventListener('click', () => {
            const range = button.getAttribute('data-range');
            const dates = getDateRange(range);

            if (dates) {
                // Update input fields
                startDateInput.value = dates.startDate;
                endDateInput.value = dates.endDate;

                // Update dashboard via AJAX
                updateDashboard(dates.startDate, dates.endDate);
            }
        });
    });

    if (applyFilterBtn && startDateInput && endDateInput) {
        applyFilterBtn.addEventListener('click', () => {
            const startDate = startDateInput.value;
            const endDate = endDateInput.value;

            // Update dashboard via AJAX
            updateDashboard(startDate, endDate);
        });
    }

    if (resetFilterBtn && startDateInput && endDateInput) {
        resetFilterBtn.addEventListener('click', () => {
            // Clear the date inputs
            startDateInput.value = '';
            endDateInput.value = '';

            // Update dashboard via AJAX with no filters
            updateDashboard('', '');
        });
    }
});

// Chart.js Configuration
function initializeCharts() {
    if (window.chartsInitialized) return;
    window.chartsInitialized = true;

    // Use global variables (will be updated via AJAX)
    const weeklyData = window.weeklyWorkouts || weeklyWorkouts;
    const typeData = window.workoutsByType || workoutsByType;
    const exerciseData = window.topExercises || topExercises;

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
    const weeklyLabels = weeklyData.map(w => w.start);
    const weeklyCounts = weeklyData.map(w => w.count);

    const weeklyCtx = document.getElementById('weeklyTrendChart');
    if (weeklyCtx) {
        window.weeklyChart = new Chart(weeklyCtx, {
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
    const typeLabels = typeData.map(w => w.type_workout__name_workout || 'No Type');
    const typeCounts = typeData.map(w => w.count);

    const typeCtx = document.getElementById('workoutTypeChart');
    if (typeCtx) {
        window.typeChart = new Chart(typeCtx, {
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
    const exerciseLabels = exerciseData.map(e => e.name__name);
    const exerciseCounts = exerciseData.map(e => e.count);

    const exercisesCtx = document.getElementById('topExercisesChart');
    if (exercisesCtx) {
        // Determine font size based on screen width
        const isMobile = window.innerWidth <= 480;
        const isTablet = window.innerWidth <= 768;
        const labelFontSize = isMobile ? 9 : isTablet ? 10 : 11;

        window.exercisesChart = new Chart(exercisesCtx, {
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
