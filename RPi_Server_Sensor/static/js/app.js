$(document).ready(function () {

  // Marker Points for simple Track IDs
  var trace1 = {
    x: [0], y: [0], z: [0],
    mode: 'markers',
    marker: {
      color: 'rgba(255, 0, 0, 0.75)',
      size: 5,
      line: {
        color: 'rgba(217, 217, 217, 0.14)',
        width: 0.3
      },
      opacity: 0.8
    },
    type: 'scatter3d'
  };

  // Zones of Interest 
  var zone1 = {
    x: [-2, 0, -2, 0, -2, 0, -2, 0],
    y: [0, 0, 3, 3, 0, 0, 3, 3],
    z: [3, 3, 3, 3, 0, 0, 0, 0],
    colorscale: 'YlGnBu',
    value: [1,1,1,1,1,1,1,1],
    isomin: 0,
    isomax: 5,
    opacity: 0.5,
    visible: false,
    showscale: false,
    type: 'volume'
  };

  var zone2 = {
    x: [-2, 0, -2, 0, -2, 0, -2, 0],
    y: [3, 3, 6, 6, 3, 3, 6, 6],
    z: [3, 3, 3, 3, 0, 0, 0, 0],
    colorscale: 'YlGnBu',
    value: [2,2,2,2,2,2,2,2],
    isomin: 0,
    isomax: 5,
    opacity: 0.5,
    visible: false,
    showscale: false,
    type: 'volume'
  };

  var zone3 = {
    x: [2, 0, 2, 0, 2, 0, 2, 0],
    y: [0, 0, 3, 3, 0, 0, 3, 3],
    z: [3, 3, 3, 3, 0, 0, 0, 0],
    colorscale: 'YlGnBu',
    value: [3, 3, 3, 3, 3, 3, 3, 3],
    isomin: 0,
    isomax: 5,
    opacity: 0.5,
    visible: false,
    showscale: false,
    type: 'volume'
  };

  var zone4 = {
    x: [2, 0, 2, 0, 2, 0, 2, 0],
    y: [3, 3, 6, 6, 3, 3, 6, 6],
    z: [3, 3, 3, 3, 0, 0, 0, 0],
    colorscale: 'YlGnBu',
    value: [4,4,4,4,4,4,4,4],
    isomin: 0,
    isomax: 5,
    opacity: 0.5,
    visible: false,
    showscale: false,
    type: 'volume'
  };

  // Data Marker for Track Ids with velocity direction
  var cone_data = {
    type: "cone",
    x: [0], y: [0], z: [0],
    u: [0], v: [0], w: [0],
    sizemode: "absolute",
    sizeref: 0.5,
    showscale: false,
  };

  var data = [trace1, zone1, zone2, zone3, zone4, cone_data];

  // Plotly layout
  var layout = {
    scene: {
      aspectmode: 'cube',
      xaxis: {
        color: 'white',
        tickcolor: 'white',
        gridwidth: 3,
        nticks: 10,
        range: [-2, 2],
      },
      yaxis: {
        color: 'white',
        tickcolor: 'white',
        gridwidth: 3,
        nticks: 10,
        range: [0, 7],
      },
      zaxis: {
        color: 'white',
        tickcolor: 'white',
        gridwidth: 3,
        nticks: 10,
        range: [0, 3],
      },
      camera: {
        center: {x: 0, y: 0, z: 0}, 
        eye: {x: 1.5, y: 1.5, z: 1.5}, 
        up: {x: 0, y: 0, z: 1}
      },
    },
    width: 700,
    height: 700,
    margin: {
      l: 1,
      r: 1,
      b: 1,
      t: 1,
      pad: 0
    },
    paper_bgcolor: 'rgba(0, 0, 0, 0)',
  };

  // Create new Plot in 'myChart' DIV
  Plotly.newPlot('myChart', data, layout);

  //connect to the socket server.
  //   var socket = io.connect("http://" + document.domain + ":" + location.port);
  var socket = io.connect();

  // Callback for Run Switch, tells server to Start/Stop mmWave Sensor
  $('#runswitch').on('click', function () {
    var buttonstate = document.getElementById("runswitch").checked;
    socket.emit("runmessage", { 'status': buttonstate });
  });

  // Sets run statuses equal between all clients
  socket.on("runstatus", function (msg) {
    document.getElementById("runswitch").checked = msg.status;
  });


  // Change to Side View
  $('#xview').on('click', function () {
    var update = {
      'scene.camera.eye.x': 2,
      'scene.camera.eye.y': 0,
      'scene.camera.eye.z': 0.1,
      'scene.camera.up.x': 0,
      'scene.camera.up.y': 0,
      'scene.camera.up.z': 1,
    };

    Plotly.relayout('myChart', update);
  });

  // Change to Front View
  $('#yview').on('click', function () {
    var update = {
      'scene.camera.eye.x': 0,
      'scene.camera.eye.y': -2,
      'scene.camera.eye.z': 0.1,
    };

    Plotly.relayout('myChart', update);
  });

  // Change to Top View
  $('#zview').on('click', function () {
    var update = {
      'scene.camera.eye.x': 0,
      'scene.camera.eye.y': 0,
      'scene.camera.eye.z': 2,
      'scene.camera.up.x': 0,
      'scene.camera.up.y': 1,
      'scene.camera.up.z': 0,
    };

    Plotly.relayout('myChart', update);
  });

  // Reset View
  $('#resetview').on('click', function () {
    var update = {
      'scene.camera.eye.x': 1.5,
      'scene.camera.eye.y': 1.5,
      'scene.camera.eye.z': 1.5,
      'scene.camera.up.x': 0,
      'scene.camera.up.y': 0,
      'scene.camera.up.z': 1,
    };

    Plotly.relayout('myChart', update);
  });

  var i = 0;
  // Toggle between Cone and Dot
  $('#setmarker').on('click', function () {
    if (i == 0) {
      i = 1;
      var data_update = { x: [0], y: [0], z: [0] };
      Plotly.update('myChart', data_update, layout, 0);
    }
    else {
      i = 0;
      var data_update = { x: [0], y: [0], z: [0], u: [0], v: [0], w: [0] };
      Plotly.update('myChart', data_update, layout, 5);
    }
  });

  //receive details from server
  socket.on("updateSensorData", function (msg) {
    console.log(
      "Received Sensor Data"
      + "\n   ID :: " + msg.ID
      + "\nX Pos :: " + msg.x_data
      + "\nY Pos :: " + msg.y_data
      + "\nZ Pos :: " + msg.z_data
      + "\nX Vel :: " + msg.x_vel
      + "\nY Vel :: " + msg.y_vel
      + "\nZ Vel :: " + msg.z_vel
      + "\n On Z :: " + msg.on_zones
      + "\nOff Z :: " + msg.off_zones
    );

    document.getElementById("xpos").innerText = msg.x_data;
    document.getElementById("ypos").innerText = msg.y_data;
    document.getElementById("zpos").innerText = msg.z_data;
    document.getElementById("xvel").innerText = msg.x_vel;
    document.getElementById("yvel").innerText = msg.y_vel;
    document.getElementById("zvel").innerText = msg.z_vel;
    document.getElementById("ids").innerText = msg.ID;
    document.getElementById("onzones").innerText = msg.on_zones;
    document.getElementById("offzones").innerText = msg.off_zones;
    
    // In restyle, arrays are assumed to be used in conjunction with the trace indices provided. 
    // Therefore, to apply an array as a value, you need to wrap it in an additional array.
    // https://plotly.com/javascript/plotlyjs-function-reference/#plotlyupdate

    switch (i) {
      case 0:
        var data_update = { x: [msg.x_data], y: [msg.y_data], z: [msg.z_data] };
        Plotly.update('myChart', data_update, layout, 0);
        break;
      case 1:
        var data_update = { x: [msg.x_data], y: [msg.y_data], z: [msg.z_data], u: [msg.x_vel], v: [msg.y_vel], w: [msg.z_vel] };
        Plotly.update('myChart', data_update, layout, 5);
    }

    Plotly.update('myChart', { visible: true }, layout, msg.on_zones);
    Plotly.update('myChart', { visible: false }, layout, msg.off_zones);
  });

  socket.on('users', function (users) {
    userCount = document.getElementById('user_counter');
    userCount.innerHTML = users.user_count;
  })

  socket.on("updateTime", function (msg) {
    document.getElementById('time').innerText = msg.up_time;
  })
});
