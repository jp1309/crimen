// Global Data Store
let rawData = [];
let chartInstances = {};
let mapInstance = null;
let heatLayer = null;
let currentView = 'timeline'; // timeline, ranking, map
let geoRankMode = 'province'; // province, canton

// Configuration
const DATA_URL = 'homicidios_clean.csv';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});

async function initDashboard() {
    console.log("Initializing Dashboard v2...");
    try {
        Papa.parse(DATA_URL, {
            download: true,
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: function (results) {
                console.log("Data loaded:", results.data.length, "rows");
                rawData = results.data;
                populateFilters();
                updateDashboard();
            },
            error: function (err) {
                console.error("Error loading CSV:", err);
                alert("Error cargando datos. Revisa consola.");
            }
        });
    } catch (e) { console.error(e); }
}

function switchView(viewId) {
    currentView = viewId;

    // UI Updates
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    document.getElementById(`view-${viewId}`).classList.remove('hidden');

    document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active-tab'));
    document.getElementById(`btn-${viewId}`).classList.add('active-tab');

    // Context-Aware Filter Adjustments
    const yearSelect = document.getElementById('filter-year');
    if (yearSelect) {
        // Reset - show all options first
        Array.from(yearSelect.options).forEach(opt => opt.hidden = false);

        if (viewId === 'map') {
            const safeYears = ['2023', '2024', '2025'];

            // Force selection to a safe year if current is invalid (including 'all')
            if (!safeYears.includes(yearSelect.value)) {
                yearSelect.value = '2025';
            }

            // Hide unsafe years AND 'all' option
            Array.from(yearSelect.options).forEach(opt => {
                if (!safeYears.includes(opt.value)) {
                    opt.hidden = true;
                }
            });
        }
    }

    // Re-render
    setTimeout(updateDashboard, 50);
}

function toggleGeoRank(mode) {
    geoRankMode = mode;
    updateDashboard(); // Refreshes the ranking chart
}

// --------------------------------------------------------
// Filters Logic
// --------------------------------------------------------
function populateFilters() {
    const years = [...new Set(rawData.map(d => d.anio))].sort((a, b) => b - a);
    const provinces = [...new Set(rawData.map(d => d.provincia))].filter(Boolean).sort();
    // Cantons - initially load all
    const cantons = [...new Set(rawData.map(d => d.canton))].filter(Boolean).sort();

    fillSelect('filter-year', years);
    fillSelect('filter-province', provinces);
    fillSelect('filter-canton', cantons);

    // General listener for updates
    document.querySelectorAll('select').forEach(s => {
        s.addEventListener('change', (e) => {
            // If province changed, update cantons first
            if (e.target.id === 'filter-province') {
                updateCantonOptions();
            }
            updateDashboard();
        });
    });
}

function updateCantonOptions() {
    const provinceSelect = document.getElementById('filter-province');
    const cantonSelect = document.getElementById('filter-canton');

    const selectedProvs = Array.from(provinceSelect.selectedOptions).map(opt => opt.value);

    // Determine available cantons based on province selection(s)
    let availableCantons = [];
    if (selectedProvs.includes('all') || selectedProvs.length === 0) {
        availableCantons = [...new Set(rawData.map(d => d.canton))].filter(Boolean).sort();
    } else {
        availableCantons = [...new Set(rawData
            .filter(d => selectedProvs.includes(d.provincia))
            .map(d => d.canton)
        )].filter(Boolean).sort();
    }

    // Save current selections
    const currentCantons = Array.from(cantonSelect.selectedOptions).map(opt => opt.value);

    // Refill options
    fillSelect('filter-canton', availableCantons);

    // Restore selections that still exist in new list
    Array.from(cantonSelect.options).forEach(opt => {
        if (currentCantons.includes(opt.value) && availableCantons.includes(opt.value)) {
            opt.selected = true;
        } else if (opt.value === 'all' && currentCantons.includes('all')) {
            opt.selected = true;
        }
    });

    // If nothing is selected, select 'all'
    if (cantonSelect.selectedOptions.length === 0) {
        cantonSelect.options[0].selected = true; // Select 'all'
    }
}

function resetFilters() {
    // Reset Year & Month
    document.getElementById('filter-year').value = 'all';
    document.getElementById('filter-month').value = 'all';

    // Reset Multi-selects (Province, Canton, Age, Sex)
    const selects = ['filter-province', 'filter-canton', 'filter-age', 'filter-sex'];
    selects.forEach(id => {
        const sel = document.getElementById(id);
        if (sel) {
            Array.from(sel.options).forEach(opt => opt.selected = false);
            if (sel.options.length > 0) sel.options[0].selected = true; // Select 'Todos'
        }
    });

    // Reset Canton logic dependent on Province
    updateCantonOptions();

    // Trigger update
    updateDashboard();
}

function fillSelect(id, values) {
    const select = document.getElementById(id);
    if (!select) return;
    // Clear existing options except first
    while (select.options.length > 1) { select.remove(1); }

    values.forEach(v => {
        if (v) {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            select.appendChild(opt);
        }
    });
}

function getFilteredData() {
    const fYear = document.getElementById('filter-year').value;
    const fMonth = document.getElementById('filter-month').value;

    // Multi-select inputs
    const provinceSelect = document.getElementById('filter-province');
    const cantonSelect = document.getElementById('filter-canton');
    const ageSelect = document.getElementById('filter-age');
    const sexSelect = document.getElementById('filter-sex');

    const selectedProvs = Array.from(provinceSelect.selectedOptions).map(o => o.value);
    const selectedCants = Array.from(cantonSelect.selectedOptions).map(o => o.value);
    const selectedAges = Array.from(ageSelect.selectedOptions).map(o => o.value);
    const selectedSex = Array.from(sexSelect.selectedOptions).map(o => o.value);

    return rawData.filter(d => {
        // Year & Month (Single Select)
        if (fYear !== 'all' && d.anio != fYear) return false;
        if (fMonth !== 'all' && d.mes != fMonth) return false;

        // Province (Multi Select)
        if (!selectedProvs.includes('all') && !selectedProvs.includes(d.provincia)) return false;

        // Canton (Multi Select)
        if (!selectedCants.includes('all') && !selectedCants.includes(d.canton)) return false;

        // Age (Multi Select)
        const ageVal = d.rango_edad || 'DESCONOCIDO';
        if (!selectedAges.includes('all') && !selectedAges.includes(ageVal)) return false;

        // Sex (Multi Select)
        const sexVal = d.sexo || 'DESCONOCIDO';
        if (!selectedSex.includes('all') && !selectedSex.includes(sexVal)) return false;

        return true;
    });
}

// --------------------------------------------------------
// Main Update Loop
// --------------------------------------------------------
function updateDashboard() {
    const data = getFilteredData();
    console.log("Updating Dashboard. Data items:", data.length);

    // Update KPI (Mini Global)
    const kpiElement = document.getElementById('indicator-total');
    if (kpiElement) {
        animateValue('indicator-total', parseInt(kpiElement.textContent.replace(',', '') || 0), data.length, 500);
    }

    // Only render active view charts to save performance
    if (currentView === 'timeline') {
        try { renderTimeline(data); } catch (e) { console.error("Error rendering Timeline:", e); }
        try { renderWeaponStats(data); } catch (e) { console.error("Error rendering WeaponStats:", e); }
        try { renderHourDistribution(data); } catch (e) { console.error("Error rendering HourDistribution:", e); }
    }
    else if (currentView === 'ranking') {
        try { renderDemographics(data); } catch (e) { console.error("Error rendering Demographics:", e); }
        try { renderGeoRanking(data); } catch (e) { console.error("Error rendering GeoRanking:", e); }
    }
    else if (currentView === 'map') {
        try { renderMap(data); } catch (e) { console.error("Error rendering Map:", e); }
    }
}

// --------------------------------------------------------
// Charts: Timeline View
// --------------------------------------------------------
function renderTimeline(data) {
    const ctx = document.getElementById('chart-timeline').getContext('2d');

    const provinceSelect = document.getElementById('filter-province');
    const cantonSelect = document.getElementById('filter-canton');
    const ageSelect = document.getElementById('filter-age');
    const sexSelect = document.getElementById('filter-sex');

    const selectedProvs = Array.from(provinceSelect.selectedOptions).map(opt => opt.value);
    const selectedCants = Array.from(cantonSelect.selectedOptions).map(opt => opt.value);
    const selectedAges = Array.from(ageSelect.selectedOptions).map(opt => opt.value);
    const selectedSex = Array.from(sexSelect.selectedOptions).map(opt => opt.value);

    const isSingleYear = document.getElementById('filter-year').value !== 'all';

    const comparingProvinces = selectedProvs.length > 1 || (selectedProvs.length === 1 && !selectedProvs.includes('all'));
    const comparingCantons = selectedCants.length > 1 || (selectedCants.length === 1 && !selectedCants.includes('all'));
    const comparingAges = selectedAges.length > 1 || (selectedAges.length === 1 && !selectedAges.includes('all'));
    const comparingSex = selectedSex.length > 1 || (selectedSex.length === 1 && !selectedSex.includes('all'));

    const colors = [
        '#22d3ee', '#f97316', '#a855f7', '#22c55e', '#ef4444', '#eab308',
        '#ec4899', '#06b6d4', '#8b5cf6', '#14b8a6', '#f59e0b', '#10b981'
    ];

    let datasets = [];
    let labels = [];
    const minYear = 2014;
    const maxYear = new Date().getFullYear();

    if (isSingleYear) {
        for (let i = 1; i <= 12; i++) {
            labels.push(getMonthName(i));
        }
    } else {
        for (let y = minYear; y <= maxYear; y++) {
            labels.push(y.toString());
        }
    }

    function createDataset(label, subsetData, colorIdx) {
        const counts = {};
        subsetData.forEach(d => {
            let key = isSingleYear ? d.mes : d.anio;
            counts[key] = (counts[key] || 0) + 1;
        });

        let values = [];
        if (isSingleYear) {
            for (let i = 1; i <= 12; i++) {
                values.push(counts[i] || 0);
            }
        } else {
            for (let y = minYear; y <= maxYear; y++) {
                values.push(counts[y] || 0);
            }
        }

        return {
            label: label,
            data: values,
            borderColor: colors[colorIdx % colors.length],
            backgroundColor: colors[colorIdx % colors.length] + '20',
            tension: 0.3,
            fill: false,
            spanGaps: false,
            borderWidth: 2
        };
    }

    if (comparingProvinces && !comparingCantons) {
        const targets = selectedProvs.filter(p => p !== 'all');
        targets.forEach((target, idx) => {
            const subset = data.filter(d => d.provincia === target);
            datasets.push(createDataset(titleCase(target), subset, idx));
        });
    }
    else if (comparingCantons) {
        const targets = selectedCants.filter(c => c !== 'all');
        targets.forEach((target, idx) => {
            const subset = data.filter(d => d.canton === target);
            datasets.push(createDataset(titleCase(target), subset, idx));
        });
    }
    else if (comparingAges) {
        const targets = selectedAges.filter(a => a !== 'all');
        targets.forEach((target, idx) => {
            const subset = data.filter(d => (d.rango_edad || 'DESCONOCIDO') === target);
            datasets.push(createDataset(target, subset, idx));
        });
    }
    else if (comparingSex) {
        const targets = selectedSex.filter(s => s !== 'all');
        targets.forEach((target, idx) => {
            const subset = data.filter(d => (d.sexo || 'DESCONOCIDO') === target);
            datasets.push(createDataset(target, subset, idx));
        });
    }
    else {
        const counts = {};
        data.forEach(d => {
            let key = isSingleYear ? d.mes : d.anio;
            counts[key] = (counts[key] || 0) + 1;
        });

        let values = [];
        if (isSingleYear) {
            for (let i = 1; i <= 12; i++) {
                values.push(counts[i] || 0);
            }
        } else {
            for (let y = minYear; y <= maxYear; y++) {
                values.push(counts[y] || 0);
            }
        }

        datasets.push({
            label: 'Total Homicidios',
            data: values,
            borderColor: '#22d3ee',
            backgroundColor: 'rgba(34, 211, 238, 0.1)',
            tension: 0.3,
            fill: true,
            spanGaps: false,
            borderWidth: 2
        });
    }

    destroyChart('timeline');

    const chartOptions = getChartOptions('Evolución');
    if (datasets.length > 1) {
        chartOptions.plugins.legend = {
            display: true,
            position: 'top',
            labels: {
                color: 'white',
                usePointStyle: true,
                padding: 15
            }
        };
    }

    chartInstances.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: chartOptions
    });
}

function renderWeaponStats(data) {
    const ctx = document.getElementById('chart-weapon').getContext('2d');

    // Aggregation by 'arma'
    const counts = {};
    data.forEach(d => {
        const val = d.arma || "DESCONOCIDO";
        counts[val] = (counts[val] || 0) + 1;
    });

    // Sort descending and take top 8
    const sorted = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);

    destroyChart('weapon');

    const horizontalOptions = getChartOptions('Tipo de Arma', true);
    horizontalOptions.plugins.datalabels = {
        color: 'white',
        anchor: 'end',
        align: 'end',
        font: { weight: 'bold', size: 10 },
        formatter: (value) => value.toLocaleString(),
        display: function (context) { return context.dataset.data[context.dataIndex] > 0; }
    };
    horizontalOptions.layout = { padding: { right: 40 } };

    chartInstances.weapon = new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels],
        data: {
            labels: sorted.map(x => titleCase(x[0])),
            datasets: [{
                label: 'Eventos',
                data: sorted.map(x => x[1]),
                backgroundColor: '#f97316',
                borderRadius: 4,
                barThickness: 20
            }]
        },
        options: horizontalOptions
    });
}

function renderHourDistribution(data) {
    const ctx = document.getElementById('chart-hour').getContext('2d');

    const timeRanges = ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24'];
    const daysOrder = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    function normalizeDay(d) {
        if (!d) return null;
        const s = d.toString().toLowerCase().trim();
        const map = {
            'lunes': 'Lunes', 'monday': 'Lunes', 'mon': 'Lunes',
            'martes': 'Martes', 'tuesday': 'Martes', 'tue': 'Martes',
            'miércoles': 'Miércoles', 'miercoles': 'Miércoles', 'wednesday': 'Miércoles', 'wed': 'Miércoles',
            'jueves': 'Jueves', 'thursday': 'Jueves', 'thu': 'Jueves',
            'viernes': 'Viernes', 'friday': 'Viernes', 'fri': 'Viernes',
            'sábado': 'Sábado', 'sabado': 'Sábado', 'saturday': 'Sábado', 'sat': 'Sábado',
            'domingo': 'Domingo', 'sunday': 'Domingo', 'sun': 'Domingo'
        };
        return map[s] || null;
    }

    function getRangeIndex(h) {
        if (h >= 0 && h < 4) return 0;
        if (h >= 4 && h < 8) return 1;
        if (h >= 8 && h < 12) return 2;
        if (h >= 12 && h < 16) return 3;
        if (h >= 16 && h < 20) return 4;
        if (h >= 20 && h < 24) return 5;
        return -1;
    }

    let grid = Array(7).fill().map(() => Array(6).fill(0));

    data.forEach(d => {
        if (d.hora_infraccion !== undefined && d.dia_semana) {
            let h = -1;
            if (typeof d.hora_infraccion === 'number') h = Math.floor(d.hora_infraccion);
            else if (typeof d.hora_infraccion === 'string') {
                const parts = d.hora_infraccion.split(':');
                h = parseInt(parts[0]);
            }

            const dayName = normalizeDay(d.dia_semana);
            const dayIdx = daysOrder.indexOf(dayName);
            const rangeIdx = getRangeIndex(h);

            if (dayIdx >= 0 && rangeIdx >= 0) {
                grid[dayIdx][rangeIdx]++;
            }
        }
    });

    let matrixData = [];
    let maxCount = 0;

    grid.forEach((row, dayIdx) => {
        row.forEach((count, rangeIdx) => {
            matrixData.push({
                x: rangeIdx,
                y: dayIdx,
                v: count
            });
            if (count > maxCount) maxCount = count;
        });
    });

    destroyChart('hourDist');

    chartInstances.hourDist = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Densidad',
                data: matrixData.map(d => ({
                    x: d.x,
                    y: d.y,
                    r: d.v === 0 ? 3 : Math.max(5, Math.min(30, (d.v / maxCount) * 25))
                })),
                backgroundColor: matrixData.map(d =>
                    d.v === 0
                        ? 'rgba(100, 100, 100, 0.2)'
                        : interpolateColor(d.v, maxCount)
                ),
                borderColor: 'rgba(255,255,255,0.3)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    min: -0.5,
                    max: 5.5,
                    title: { display: true, text: 'Franja Horaria', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: {
                        color: '#94a3b8',
                        autoSkip: false,
                        callback: function (val) {
                            const index = Math.round(val);
                            return timeRanges[index] || '';
                        }
                    },
                    afterBuildTicks: function (axis) {
                        axis.ticks = [0, 1, 2, 3, 4, 5].map(value => ({ value }));
                    }
                },
                y: {
                    type: 'linear',
                    min: -0.5,
                    max: 6.5,
                    title: { display: true, text: 'Día de la Semana', color: '#94a3b8' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: {
                        color: '#94a3b8',
                        autoSkip: false,
                        callback: function (val) {
                            const index = Math.round(val);
                            return daysOrder[index] || '';
                        }
                    },
                    afterBuildTicks: function (axis) {
                        axis.ticks = [0, 1, 2, 3, 4, 5, 6].map(value => ({ value }));
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const d = matrixData[ctx.dataIndex];
                            return `${daysOrder[d.y]} (${timeRanges[d.x]}): ${d.v} homicidios`;
                        }
                    }
                }
            }
        }
    });
}

function renderDemographics(data) {
    const ctx = document.getElementById('chart-pyramid').getContext('2d');

    // Define Age Bins
    const bins = [
        { label: '0-4', min: 0, max: 4 },
        { label: '5-9', min: 5, max: 9 },
        { label: '10-14', min: 10, max: 14 },
        { label: '15-19', min: 15, max: 19 },
        { label: '20-24', min: 20, max: 24 },
        { label: '25-29', min: 25, max: 29 },
        { label: '30-34', min: 30, max: 34 },
        { label: '35-39', min: 35, max: 39 },
        { label: '40-44', min: 40, max: 44 },
        { label: '45-49', min: 45, max: 49 },
        { label: '50-54', min: 50, max: 54 },
        { label: '55-59', min: 55, max: 59 },
        { label: '60-64', min: 60, max: 64 },
        { label: '65-69', min: 65, max: 69 },
        { label: '70-74', min: 70, max: 74 },
        { label: '75-79', min: 75, max: 79 },
        { label: '80+', min: 80, max: 200 }
    ];

    const males = new Array(bins.length).fill(0);
    const females = new Array(bins.length).fill(0);

    data.forEach(d => {
        let age = -1;
        // Parse Age
        if (d.edad !== undefined && d.edad !== null && d.edad !== '') {
            if (d.medida_edad && (d.medida_edad.toLowerCase().includes('mes') || d.medida_edad.toLowerCase().includes('dias'))) {
                age = 0;
            } else {
                age = parseInt(d.edad);
            }
        }

        if (age === -1 || isNaN(age)) return;

        // Find bin
        const binIndex = bins.findIndex(b => age >= b.min && age <= b.max);
        if (binIndex === -1) return;

        const sex = (d.sexo || '').toUpperCase();
        if (sex === 'HOMBRE') {
            males[binIndex]++;
        } else if (sex === 'MUJER') {
            females[binIndex]++;
        }
    });

    destroyChart('pyramid');

    chartInstances.pyramid = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: bins.map(b => b.label).reverse(), // Reverse for older ages at top
            datasets: [
                {
                    label: 'Mujeres',
                    data: females.map(v => -v).reverse(), // Negative values for left side
                    backgroundColor: '#ec4899',
                    borderRadius: { topLeft: 4, bottomLeft: 4 },
                    barPercentage: 0.9,
                    categoryPercentage: 0.9
                },
                {
                    label: 'Hombres',
                    data: males.reverse(), // Positive values for right side
                    backgroundColor: '#06b6d4',
                    borderRadius: { topRight: 4, bottomRight: 4 },
                    barPercentage: 0.9,
                    categoryPercentage: 0.9
                }
            ]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        color: '#94a3b8',
                        callback: function (value) {
                            return Math.abs(value).toLocaleString();
                        }
                    },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                y: {
                    stacked: true,
                    ticks: { color: '#94a3b8' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    labels: { color: 'white', usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${Math.abs(context.raw).toLocaleString()}`;
                        }
                    }
                },
                datalabels: {
                    display: false // Disable data labels
                }
            }
        }
    });

    // Force resize to ensure proper display
    setTimeout(() => {
        if (chartInstances.pyramid) {
            chartInstances.pyramid.resize();
        }
    }, 50);
}

function renderGeoRanking(data) {
    const ctx = document.getElementById('chart-ranking-geo').getContext('2d');
    const field = geoRankMode === 'province' ? 'provincia' : 'canton';

    const counts = getCounts(data, field);
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 15);

    // Region Mapping
    const regionMap = {
        // COSTA
        'ESMERALDAS': 'COSTA', 'SANTO DOMINGO DE LOS TSACHILAS': 'COSTA', 'SANTO DOMINGO': 'COSTA', 'STO DGO DE LOS TSACHILAS': 'COSTA',
        'MANABI': 'COSTA', 'LOS RIOS': 'COSTA', 'GUAYAS': 'COSTA', 'SANTA ELENA': 'COSTA', 'EL ORO': 'COSTA',
        // SIERRA
        'CARCHI': 'SIERRA', 'IMBABURA': 'SIERRA', 'PICHINCHA': 'SIERRA', 'COTOPAXI': 'SIERRA',
        'TUNGURAHUA': 'SIERRA', 'BOLIVAR': 'SIERRA', 'CHIMBORAZO': 'SIERRA', 'CANAR': 'SIERRA',
        'AZUAY': 'SIERRA', 'LOJA': 'SIERRA',
        // AMAZONIA
        'SUCUMBIOS': 'AMAZONIA', 'ORELLANA': 'AMAZONIA', 'NAPO': 'AMAZONIA', 'PASTAZA': 'AMAZONIA',
        'MORONA SANTIAGO': 'AMAZONIA', 'ZAMORA CHINCHIPE': 'AMAZONIA',
        // INSULAR
        'GALAPAGOS': 'INSULAR'
    };

    const regionColors = {
        'COSTA': '#facc15',    // Yellow-500
        'SIERRA': '#a855f7',   // Purple-500
        'AMAZONIA': '#22c55e', // Green-500
        'INSULAR': '#3b82f6',  // Blue-500
        'UNKNOWN': '#94a3b8'   // Gray
    };

    // Helper to find region
    function getRegionColor(name) {
        let province = name;

        // Handle explicit Cantons that failed logic previously
        if (geoRankMode === 'canton') {
            const n = name.trim().toUpperCase();
            if (n === 'SANTO DOMINGO' || n === 'LA CONCORDIA') return regionColors['COSTA'];

            // Try to find province in data
            const found = rawData.find(d => d.canton && d.canton.trim() === name.trim());
            if (found) province = found.provincia;
        }

        const region = regionMap[province ? province.trim() : ''] || 'UNKNOWN';
        return regionColors[region];
    }

    destroyChart('geoRank');

    // Chart Options with DataLabels
    const options = getChartOptions('Ranking', true);
    options.plugins.legend = {
        display: true,
        align: 'start', // Align legend to left
        labels: {
            generateLabels: (chart) => {
                return [
                    { text: 'Costa', fillStyle: regionColors['COSTA'], strokeStyle: regionColors['COSTA'], fontColor: '#ffffff' },
                    { text: 'Sierra', fillStyle: regionColors['SIERRA'], strokeStyle: regionColors['SIERRA'], fontColor: '#ffffff' },
                    { text: 'Amazonía', fillStyle: regionColors['AMAZONIA'], strokeStyle: regionColors['AMAZONIA'], fontColor: '#ffffff' },
                    { text: 'Insular', fillStyle: regionColors['INSULAR'], strokeStyle: regionColors['INSULAR'], fontColor: '#ffffff' }
                ];
            },
            color: '#ffffff', // Force white text global
            usePointStyle: true,
            padding: 20,
            font: { size: 12, weight: 'bold' }
        }
    };

    // Configure DataLabels plugin specifically for this chart
    options.plugins.datalabels = {
        color: 'white',
        anchor: 'end',
        align: 'end',
        font: { weight: 'bold', size: 10 },
        formatter: (value) => value.toLocaleString(),
        display: function (context) {
            return context.dataset.data[context.dataIndex] > 0; // Only show if > 0
        }
    };
    // Add extra padding on right for labels
    options.layout = { padding: { right: 50 } };

    chartInstances.geoRank = new Chart(ctx, {
        type: 'bar',
        plugins: [ChartDataLabels], // Activate plugin
        data: {
            labels: sorted.map(x => titleCase(x[0])),
            datasets: [{
                label: 'Casos',
                data: sorted.map(x => x[1]),
                backgroundColor: sorted.map(x => getRegionColor(x[0])),
                borderRadius: 4,
                barThickness: 15
            }]
        },
        options: options
    });

    // Force resize to ensure proper display
    setTimeout(() => {
        if (chartInstances.geoRank) {
            chartInstances.geoRank.resize();
        }
    }, 50);
}

// --------------------------------------------------------
// Map View
// --------------------------------------------------------
function renderMap(data) {
    if (!mapInstance) {
        mapInstance = L.map('map', { zoomControl: false }).setView([-1.8312, -78.1834], 6);
        // Voyager style shows roads, highways, and labels
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19,
            minZoom: 5
        }).addTo(mapInstance);
        L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);
    }

    // Hybrid: Heatmap + Individual Markers
    const points = data
        .filter(d => d.coordenada_y && d.coordenada_x && !isNaN(d.coordenada_y));

    // Remove old layers if exist
    if (heatLayer) mapInstance.removeLayer(heatLayer);
    if (window.markersLayer) mapInstance.removeLayer(window.markersLayer);

    if (points.length > 0) {
        // 1. HEATMAP LAYER (for concentration/density)
        const heatPoints = points.map(d => [d.coordenada_y, d.coordenada_x, 0.6]);
        heatLayer = L.heatLayer(heatPoints, {
            radius: 15,
            blur: 20,
            maxZoom: 10,
            gradient: { 0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red' }
        }).addTo(mapInstance);

        // 2. INDIVIDUAL MARKERS LAYER (for precise points)
        window.markersLayer = L.layerGroup();

        points.forEach(d => {
            // Format popup content
            const fecha = d.fecha_infraccion ? new Date(d.fecha_infraccion).toLocaleDateString('es-EC', {
                year: 'numeric', month: 'long', day: 'numeric'
            }) : 'Desconocida';
            const edad = d.edad ? `${Math.round(d.edad)} años` : 'Desconocida';
            const arma = d.arma || 'Desconocida';
            const sexo = d.sexo === 'HOMBRE' ? '👨 Hombre' : d.sexo === 'MUJER' ? '👩 Mujer' : 'Desconocido';


            const popupContent = `
                <div style="font-family: sans-serif; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #dc2626; font-size: 14px; border-bottom: 2px solid #dc2626; padding-bottom: 5px;">
                        🔴 Caso de Homicidio
                    </h4>
                    <div style="font-size: 12px; line-height: 1.6;">
                        <p style="margin: 5px 0;"><strong>📅 Fecha:</strong> ${fecha}</p>
                        <p style="margin: 5px 0;"><strong>🎂 Edad:</strong> ${edad}</p>
                        <p style="margin: 5px 0;"><strong>🔫 Arma:</strong> ${arma}</p>
                        <p style="margin: 5px 0;"><strong>👤 Sexo:</strong> ${sexo}</p>
                    </div>
                </div>
            `;

            L.circleMarker([d.coordenada_y, d.coordenada_x], {
                radius: 3,
                fillColor: '#dc2626', // Red
                color: '#991b1b', // Dark red border
                weight: 1,
                opacity: 0.9,
                fillOpacity: 0.7
            })
                .bindPopup(popupContent, {
                    maxWidth: 300,
                    className: 'custom-popup'
                })
                .addTo(window.markersLayer);
        });

        window.markersLayer.addTo(mapInstance);

        // Auto fit bounds if filtered
        if (data.length < 5000 && data.length > 0) {
            const lats = points.map(p => p.coordenada_y);
            const lngs = points.map(p => p.coordenada_x);
            mapInstance.fitBounds([
                [Math.min(...lats), Math.min(...lngs)],
                [Math.max(...lats), Math.max(...lngs)]
            ]);
        }
    }
}



// --------------------------------------------------------
// Utilities & Helpers
// --------------------------------------------------------
function getCounts(data, field) {
    const c = {};
    data.forEach(d => {
        const val = d[field] || "DESCONOCIDO";
        c[val] = (c[val] || 0) + 1;
    });
    return c;
}

function getChartOptions(title, horizontal = false) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: horizontal ? 'y' : 'x',
        plugins: { legend: { display: false } },
        scales: {
            x: {
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: {
                    color: '#94a3b8',
                    precision: horizontal ? 0 : undefined
                }
            },
            y: {
                grid: { color: 'rgba(255,255,255,0.05)' },
                ticks: {
                    color: '#94a3b8',
                    precision: horizontal ? undefined : 0
                }
            }
        }
    };
}

function interpolateColor(value, max) {
    if (!max || max === 0) return 'rgba(100, 100, 100, 0.2)';
    const r = Math.min(255, Math.floor(255 * (value / max)));
    const b = 255 - r;
    return `rgba(${r}, 0, ${b}, 0.7)`;
}

function destroyChart(key) {
    if (chartInstances[key]) {
        chartInstances[key].destroy();
        chartInstances[key] = null;
    }
}

function getMonthName(m) {
    const months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
    return months[m - 1] || m;
}

function titleCase(str) {
    if (!str) return "";
    return str.toString().toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) window.requestAnimationFrame(step);
    };
    window.requestAnimationFrame(step);
}
