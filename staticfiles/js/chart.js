// // static/js/charts.js
// let lineChart, barChart, pieChart;
// const MAX_POINTS = 20;  // how many points visible on line chart

// function initCharts() {
//   // initial labels (0..MAX_POINTS-1)
//   const labels = Array.from({length: MAX_POINTS}, (_, i) => (i+1).toString());
//   const initial = Array(MAX_POINTS).fill(0);

//   // LINE CHART (smooth)
//   lineChart = new Chart(document.getElementById('lineChart'), {
//     type: 'line',
//     data: {
//       labels: labels,
//       datasets: [{
//         label: 'Sales (live)',
//         data: initial.slice(),
//         tension: 0.35,
//         borderWidth: 2,
//         pointRadius: 2,
//         fill: false
//       }]
//     },
//     options: {
//       animation: { duration: 600 },
//       scales: { y: { beginAtZero: true } }
//     }
//   });

//   // BAR CHART
//   barChart = new Chart(document.getElementById('barChart'), {
//     type: 'bar',
//     data: {
//       labels: ['Mon','Tue','Wed','Thu','Fri'],
//       datasets: [{ label: 'Visitors', data: [0,0,0,0,0] }]
//     },
//     options: { animation: { duration: 500 } }
//   });

//   // PIE CHART
//   pieChart = new Chart(document.getElementById('pieChart'), {
//     type: 'pie',
//     data: {
//       labels: ['Completed','Pending','Failed'],
//       datasets: [{ data: [0,0,0] }]
//     },
//     options: { animation: { duration: 500 } }
//   });
// }

// // fetch latest and update charts smoothly
// async function fetchAndUpdate() {
//   try {
//     const res = await fetch('/api/live');
//     if (!res.ok) throw new Error('Network response not OK');

//     const payload = await res.json();

//     // 1) LINE chart: push single point and pop oldest
//     const newPoint = payload.sales_point;
//     lineChart.data.labels.push(new Date().toLocaleTimeString());
//     lineChart.data.labels.shift();

//     lineChart.data.datasets[0].data.push(newPoint);
//     lineChart.data.datasets[0].data.shift();

//     lineChart.update();

//     // 2) BAR chart: replace dataset with returned visitors array
//     barChart.data.datasets[0].data = payload.visitors;
//     barChart.update();

//     // 3) PIE chart:
//     pieChart.data.datasets[0].data = payload.orders;
//     pieChart.update();

//     // 4) Stat cards:
//     document.getElementById('salesValue').innerText = payload.sales_point;
//     document.getElementById('earningsValue').innerText = '$' + payload.earnings;
//     document.getElementById('visitorsValue').innerText = payload.visitors.reduce((a,b)=>a+b,0);
//     document.getElementById('ordersValue').innerText = payload.orders[0];

//   } catch (err) {
//     console.error('Update failed', err);
//   }
// }

// // initialize
// initCharts();
// // fetch once immediately
// fetchAndUpdate();
// // then update every second
// setInterval(fetchAndUpdate, 1000);



