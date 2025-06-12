document.addEventListener("DOMContentLoaded", function () {

  //=====================================
  // Theme Onload Toast
  //=====================================
  window.addEventListener("load", () => {
    let myAlert = document.querySelectorAll('.toast')[0];
    if (myAlert) {
      let bsAlert = new bootstrap.Toast(myAlert);
      bsAlert.show();
    }
  })

  // -----------------------------------------------------------------------
  // Customers
  // -----------------------------------------------------------------------

  var options = {
    chart: {
      id: "customers",
      type: "area",
      height: 70,
      sparkline: {
        enabled: true,
      },
      group: "sparklines",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
    },
    series: [
      {
        name: "customers",
        color: "var(--bs-secondary)",
        data: [36, 45, 31, 47, 38, 43],
      },
    ],
    stroke: {
      curve: "smooth",
      width: 2,
    },
    fill: {
      type: "gradient",
      color: "var(--bs-secondary)",

      gradient: {
        shadeIntensity: 0,
        inverseColors: false,
        opacityFrom: 0.2,
        opacityTo: 0.1,
        stops: [100],
      },
    },

    markers: {
      size: 0,
    },
    tooltip: {
      theme: "dark",
      fixed: {
        enabled: true,
        position: "right",
      },
      x: {
        show: false,
      },
    },
  };
  new ApexCharts(document.querySelector("#customers"), options).render();

  // -----------------------------------------------------------------------
  // Projects
  // -----------------------------------------------------------------------
  // var chart_bounce_rate = {
  //   series: [
  //     {
  //       name: 'Temps passé', // Nom de la série affiché dans la légende et au survol
  //       data: [10, 5, 5, 7, 6, 5],
  //     },
  //   ],
  //   chart: {
  //     fontFamily: "inherit",
  //     height: 80,
  //     type: "bar",
  //     offsetX: -10,
  //     toolbar: {
  //       show: false,
  //     },
  //     sparkline: {
  //       enabled: true,
  //     },
  //   },
  //   colors: ["var(--bs-white)"],
  //   plotOptions: {
  //     bar: {
  //       horizontal: false,
  //       columnWidth: "55%",
  //       endingShape: "flat",
  //       borderRadius: 4,
  //     },
  //   },
  //   tooltip: {
  //     theme: "dark",
  //     followCursor: true,
  //   },
  //   xaxis: {
  //     categories: ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"], // Noms sous les barres
  //     labels: {
  //       style: {
  //         colors: "var(--bs-white)", // Pour s'assurer qu'on voit bien les labels si fond sombre
  //       },
  //     },
  //   },
  // };

  // var chart_line_basic = new ApexCharts(
  //   document.querySelector("#projects"),
  //   chart_bounce_rate
  // );
  // chart_line_basic.render();

  async function graphe2() {
    try {
      const response = await fetch("/etu/get_temps_utilisation_chart/");
      const data = await response.json();
  
      if (data.error) {
        console.error(data.error);
        return;
      }
  
      var chart_bounce_rate = {
        series: [
          {
            name: "Temps passé",
            data: data.data,  // Charger les données dynamiquement
          },
        ],
        chart: {
          fontFamily: "inherit",
          height: 80,
          type: "bar",
          toolbar: { show: false },
          sparkline: { enabled: true },
        },
        colors: ["var(--bs-white)"],
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: "55%",
            endingShape: "flat",
            borderRadius: 4,
          },
        },
        tooltip: {
          theme: "dark",
          followCursor: true,
          y: {
            formatter: function (value, { seriesIndex, dataPointIndex }) {
              let heures = Math.floor(value / 60);
              let minutes = value % 60;
              return heures > 0 ? `${heures}h ${minutes}min` : `${minutes}min`;
            },
          },
        },
        xaxis: {
          categories: data.categories,  // Charger les jours dynamiquement
          labels: {
            style: { colors: "var(--bs-white)" },
          },
        },
      };
  
      var chart_line_basic = new ApexCharts(
        document.querySelector("#projects"),
        chart_bounce_rate
      );
      chart_line_basic.render();


    } catch (error) {
      console.error("Erreur lors du chargement des données :", error);
    }
  }
  graphe2();

  // -----------------------------------------------------------------------
  // Revenue Forecast !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  // -----------------------------------------------------------------------

  // var chart = {
  //   series: [
  //     {
  //       name: "depasser",
  //       data: [5, 5, 5, 4, 7, 3, 0],
  //     },

  //     {
  //       name: "done",
  //       data: [15, 16, 16, 17, 19, 25, 25],
  //     },
  //     {
  //       name: "not done, a venir",
  //       data: [10, 9, 9, 9, 8, 8, 8],
  //     },
  //   ],
  //   chart: {
  //     toolbar: {
  //       show: false,
  //     },
  //     type: "area",
  //     fontFamily: "inherit",
  //     foreColor: "#adb0bb",
  //     height: 300,
  //     width: "100%",
  //     stacked: false,
  //     offsetX: -10,
  //   },
  //   colors: ["var(--bs-danger)", "var(--bs-secondary)", "var(--bs-primary)"],
  //   plotOptions: {},
  //   dataLabels: {
  //     enabled: false,
  //   },
  //   legend: {
  //     show: false,
  //   },
  //   stroke: {
  //     width: 2,
  //     curve: "monotoneCubic",
  //   },
  //   grid: {
  //     show: true,
  //     padding: {
  //       top: 0,
  //       bottom: 0,
  //     },
  //     borderColor: "rgba(0,0,0,0.05)",
  //     xaxis: {
  //       lines: {
  //         show: true,
  //       },
  //     },
  //     yaxis: {
  //       lines: {
  //         show: true,
  //       },
  //     },
  //   },
  //   fill: {
  //     type: "gradient",
  //     gradient: {
  //       shadeIntensity: 0,
  //       inverseColors: false,
  //       opacityFrom: 0.1,
  //       opacityTo: 0.01,
  //       stops: [0, 100],
  //     },
  //   },
  //   xaxis: {
  //     axisBorder: {
  //       show: false,
  //     },
  //     axisTicks: {
  //       show: false,
  //     },
  //     categories: ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
  //   },
  //   markers: {
  //     strokeColor: [
  //       "var(--bs-danger)",
  //       "var(--bs-secondary)",
  //       "var(--bs-primary)",
  //     ],
  //     strokeWidth: 2,
  //   },
  //   tooltip: {
  //     theme: "dark",
  //   },
  // };

  // var chart = new ApexCharts(
  //   document.querySelector("#revenue-forecast"),
  //   chart
  // );
  // chart.render();

  async function graphe1() {
    try {
      const response = await fetch("/etu/get_taches_stats_2/");
      const data = await response.json();
  
      if (data.error) {
        console.error(data.error);
        return;
      }
  
      var chart = {
        series: data.series, // Injecter les données reçues
        chart: {
          toolbar: { show: false },
          type: "area",
          fontFamily: "inherit",
          foreColor: "#adb0bb",
          height: 300,
          width: "100%",
          stacked: false,
          offsetX: -10,
        },
        colors: ["var(--bs-danger)", "var(--bs-secondary)", "var(--bs-primary)"],
        dataLabels: { enabled: false },
        stroke: { width: 2, curve: "monotoneCubic" },
        fill: {
          type: "gradient",
          gradient: {
            shadeIntensity: 0,
            inverseColors: false,
            opacityFrom: 0.1,
            opacityTo: 0.01,
            stops: [0, 100],
          },
        },
        xaxis: {
          categories: data.categories, // Injecter les dates formatées
          axisBorder: { show: false },
          axisTicks: { show: false },
        },
        markers: {
          strokeColor: ["var(--bs-danger)", "var(--bs-secondary)", "var(--bs-primary)"],
          strokeWidth: 2,
        },
        tooltip: { theme: "dark" },
      };
  
      var chart = new ApexCharts(
        document.querySelector("#revenue-forecast"),
        chart
      );
      chart.render();


    } catch (error) {
      console.error("Erreur lors du chargement des données :", error);
    }
  }
  graphe1();

  // =====================================
  // Your Preformance
  // =====================================

  var options = {
    series: [20, 20, 20, 20, 20],
    labels: ["245", "45", "14", "78", "95"],
    chart: {
      height: 205,
      fontFamily: "inherit",
      type: "donut",
    },
    plotOptions: {
      pie: {
        startAngle: -90,
        endAngle: 90,
        offsetY: 10,
        donut: {
          size: "90%",
        },
      },
    },
    grid: {
      padding: {
        bottom: -80,
      },
    },
    legend: {
      show: false,
    },
    dataLabels: {
      enabled: false,
      name: {
        show: false,
      },
    },
    stroke: {
      width: 2,
      colors: "var(--bs-card-bg)",
    },
    tooltip: {
      fillSeriesColor: false,
    },
    colors: [
      "var(--bs-danger)",
      "var(--bs-warning)",
      "var(--bs-warning-bg-subtle)",
      "var(--bs-secondary-bg-subtle)",
      "var(--bs-secondary)",
    ],
    responsive: [{
      breakpoint: 1400,
      options: {
        chart: {
          height: 170
        },
      },
    }],
  };

  var chart = new ApexCharts(
    document.querySelector("#your-preformance"),
    options
  );
  chart.render();

  // -----------------------------------------------------------------------
  // Customers Area !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  // -----------------------------------------------------------------------
  var chart_users = {
    series: [
      {
        name: "April 07 ",
        data: [0, 1, 0, 0, 1, 0, 0],
      },
      {
        name: "Last Week",
        data: [2, 3, 3, 3, 4, 4, 3],
      },
      {
        name: "April 07 ",
        data: [5, 5, 5, 5, 5, 5, 6],
      },
    ],
    chart: {
      fontFamily: "inherit",
      height: 100,
      type: "line",
      toolbar: {
        show: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    colors: ["var(--bs-danger)", "var(--bs-primary)", "var(--bs-success)"],
    grid: {
      show: false,
    },
    stroke: {
      curve: "smooth",
      colors: ["var(--bs-danger)", "var(--bs-primary)", "var(--bs-success)"],
      width: 2,
    },
    markers: {
      colors: ["var(--bs-danger)", "var(--bs-primary)", "var(--bs-success)"],
      strokeColors: "transparent",
    },
    tooltip: {
      theme: "dark",
      x: {
        show: false,
      },
      followCursor: true,
    },
  };
  var chart_line_basic = new ApexCharts(
    document.querySelector("#customers-area"),
    chart_users
  );
  chart_line_basic.render();

  // -----------------------------------------------------------------------
  // Sales Overview !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  // -----------------------------------------------------------------------
  var options = {
    series: [50, 80, 30],
    labels: ["36%", "10%", "36%"],
    chart: {
      type: "radialBar",
      height: 230,
      fontFamily: "inherit",
      foreColor: "#c6d1e9",
    },
    plotOptions: {
      radialBar: {
        inverseOrder: false,
        startAngle: 0,
        endAngle: 270,
        hollow: {
          margin: 1,
          size: "40%",
        },
        dataLabels: {
          show: false,
        },
      },
    },
    legend: {
      show: false,
    },
    stroke: { width: 1, lineCap: "round" },
    tooltip: {
      enabled: false,
      fillSeriesColor: false,
    },
    colors: ["var(--bs-primary)", "var(--bs-secondary)", "var(--bs-danger)"],
  };

  var chart = new ApexCharts(
    document.querySelector("#sales-overview"),
    options
  );
  chart.render();

  // -----------------------------------------------------------------------
  // Total settlements
  // -----------------------------------------------------------------------
  var settlements = {
    series: [
      {
        name: "settlements",
        data: [
          40, 40, 80, 80, 30, 30, 10, 10, 30, 30, 100, 100, 20, 20, 140, 140,
        ],
      },
    ],
    chart: {
      fontFamily: "inherit",
      type: "line",
      height: 300,
      toolbar: { show: !1 },
    },
    legend: { show: !1 },
    dataLabels: { enabled: !1 },
    stroke: {
      curve: "smooth",
      show: !0,
      width: 2,
      colors: ["var(--bs-primary)"],
    },
    xaxis: {
      categories: [
        "1W",
        "",
        "3W",
        "",
        "5W",
        "6W",
        "7W",
        "8W",
        "9W",
        "",
        "11W",
        "",
        "13W",
        "",
        "15W",
      ],
      axisBorder: { show: !1 },
      axisTicks: { show: !1 },
      tickAmount: 6,
      labels: {
        rotate: 0,
        rotateAlways: !0,
        style: { fontSize: "10px", colors: "#adb0bb", fontWeight: "600" },
      },
    },
    yaxis: {
      show: false,
      tickAmount: 3,
    },
    tooltip: {
      theme: "dark",
    },
    colors: ["var(--bs-primary)"],
    grid: {
      borderColor: "var(--bs-primary-bg-subtle)",
      strokeDashArray: 4,
      yaxis: { show: false },
    },
    markers: {
      strokeColor: ["var(--bs-primary)"],
      strokeWidth: 3,
    },
  };

  var chart_area_spline = new ApexCharts(
    document.querySelector("#settlements"),
    settlements
  );
  chart_area_spline.render();
});

