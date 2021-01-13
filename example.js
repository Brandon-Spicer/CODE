"use strict";

// From https://webgl2fundamentals.org/webgl/lessons/webgl-fundamentals.html.

// Take positions in pixels, convert to clipspace.
var pixelsToClipspaceShaderSource = `#version 300 es

// an attribute is an input (in) to a vertex shader.
// It will receive data from a buffer
in vec2 a_position;

// Used to pass in the resolution of the canvas
uniform vec2 u_resolution;

// all shaders have a main function
void main() {

  // convert the position from pixels to 0.0 to 1.0
  vec2 zeroToOne = a_position / u_resolution;

  // convert from 0->1 to -1->1
  vec2 clipSpace = zeroToOne * 2.0 - 1.0;

  gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
}
`;

// Output constant color.
var constantColorFragmentShader = `#version 300 es

precision highp float;

uniform vec4 u_color;

// we need to declare an output for the fragment shader
out vec4 outColor;

void main() {
  outColor = u_color;
}
`;

async function main() {
  // Get A WebGL context
  var canvas = document.querySelector("#c");
  var gl = canvas.getContext("webgl2");
  if (!gl) {
    return;
  }

  // Use our boilerplate utils to compile the shaders and link into a program
  var program = webglUtils.createProgramFromSources(gl,
      [pixelsToClipspaceShaderSource, constantColorFragmentShader]);

  // Look up the "locations" --------
  // look up where the vertex data needs to go.
  var positionAttributeLocation = gl.getAttribLocation(program, "a_position");

  // look up uniform locations
  var resolutionUniformLocation = gl.getUniformLocation(program, "u_resolution");
  var colorLocation = gl.getUniformLocation(program, "u_color");

  // Set up state for the position buffer. ------
  // Create a buffer
  var positionBuffer = gl.createBuffer();

  // Create a vertex array object (attribute state)
  var vao = gl.createVertexArray();

  // and make it the one we're currently working with
  gl.bindVertexArray(vao);

  // Turn on the attribute
  gl.enableVertexAttribArray(positionAttributeLocation);

  // Bind it to ARRAY_BUFFER (think of it as ARRAY_BUFFER = positionBuffer)
  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);

  // Tell the attribute how to get data out of positionBuffer (ARRAY_BUFFER)
  var size = 2;          // 2 components per iteration (e.g., 2d points)
  var type = gl.FLOAT;   // the data is 32bit floats
  var normalize = false; // don't normalize the data
  var stride = 0;        // 0 = move forward size * sizeof(type) each iteration to get the next position
  var offset = 0;        // start at the beginning of the buffer
  gl.vertexAttribPointer(
      positionAttributeLocation, size, type, normalize, stride, offset);

  // Set up the canvas. -------
  webglUtils.resizeCanvasToDisplaySize(gl.canvas);

  // Tell WebGL how to convert from clip space to pixels
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

  // Clear the canvas 
  gl.clearColor(0, 0, 0, 0);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  // Tell it to use our program (pair of shaders)
  gl.useProgram(program);

  // Is this redundant??
  // Bind the attribute/buffer set we want.
  gl.bindVertexArray(vao);

  // Pass in the canvas resolution so we can convert from
  // pixels to clipspace in the shader
  gl.uniform2f(resolutionUniformLocation, gl.canvas.width, gl.canvas.height);

  var x = 100;
  var y = 100;
  var dx = 1;
  var dy = 1;
  const radius = 50;
  const num_triangles = 100;
  const num_spheres = 10;
  var spheres = []
  for (var j = 0; j < num_spheres; j++) {
    spheres.push(new Sphere(gl, 
      Math.random() * gl.canvas.width,
                            Math.random() * gl.canvas.height,
                            dx, 
                            dy,
                            radius));
  }

  while (true) {
      // Clear buffer
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    // Draw a sphere
    spheres.forEach(function(s) {
      setSphere(gl, s.x, s.y, s.radius, num_triangles);
      gl.uniform4f(colorLocation, 0, 0, 0, 1);

      s.update()

      var primitiveType = gl.TRIANGLES;
      var offset = 0;
      var count = 3 * num_triangles;
      gl.drawArrays(primitiveType, offset, count);
    });

    // Sleep for 5 milliseconds
    await new Promise(r => setTimeout(r, 5));
  }



  // for (var j = 0; j < 50; j++) {
  //   // Sleep for 5 milliseconds
  //   await new Promise(r => setTimeout(r, 5));
  //   gl.clearColor(0, 0, 0, 0);
  //   gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  //   // draw 50 random rectangles in random colors
  //   for (var ii = 0; ii < 1000; ++ii) {
  //     // Put a rectangle in the position buffer
  //     setRectangle(
  //         gl, randomInt(300), randomInt(300), randomInt(300), randomInt(300));

  //     // Set a random color.
  //     gl.uniform4f(colorLocation, Math.random(), Math.random(), Math.random(), 1);

  //     // Draw the rectangle.
  //     var primitiveType = gl.TRIANGLES;
  //     var offset = 0;
  //     var count = 6;
  //     gl.drawArrays(primitiveType, offset, count);
  //   }

  // }

}

// class Simulation {
//   constructor(spheres) {
//     this.spheres = spheres
//   }

//   clumps() {
//     this.spheres.sort((a, b) => a.x - b.x)

//   }

//   static clumpBy(list, comparator) {

//   }

//   static x_comparator(s, t) {
//     if s.x - t.x < 
//   }
// }

class Sphere {
  constructor(gl, x, y, dx, dy, radius) {
    this.gl = gl
    this.x = x;
    this.y = y;
    this.dx = dx;
    this.dy = dy;
    this.radius = radius;
  }

  update() {
    this.x += this.dx
    this.y += this.dy

    if (this.x - this.radius < 0 || this.x + this.radius > this.gl.canvas.width) {
      this.dx = -this.dx;
    }

    if (this.y - this.radius< 0 || this.y + this.radius > this.gl.canvas.height) {
      this.dy = -this.dy;
    }
  }
}

// Returns a random integer from 0 to range - 1.
function randomInt(range) {
  return Math.floor(Math.random() * range);
}

// Fill the buffer with the values that define a rectangle.
function setRectangle(gl, x, y, width, height) {
  var x1 = x;
  var x2 = x + width;
  var y1 = y;
  var y2 = y + height;
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
    // Triangle 1
     x1, y1,
     x2, y1,
     x1, y2,
     // Triangle 2
     x1, y2,
     x2, y1,
     x2, y2,
  ]), gl.STATIC_DRAW);
}

function setSphere(gl, x, y, radius, num_triangles) {
  if (num_triangles < 2) {
    throw new Error("Too few triangles.")
  }
  
  var delta_angle = 2 * Math.PI / num_triangles
  var valuesList = [];
  for (var i = 0; i < num_triangles; i++) {
    // the origin
    valuesList.push(x + radius * 0);
    valuesList.push(y + radius * 0);
    // point 1 on the circle
    valuesList.push(x + radius * Math.cos(i * delta_angle))
    valuesList.push(y + radius * Math.sin(i * delta_angle))
    // point 2 on the circle
    valuesList.push(x + radius * Math.cos((i + 1) * delta_angle))
    valuesList.push(y + radius * Math.sin((i + 1) * delta_angle))
  }
  // console.log(valuesList)
  var values = new Float32Array(valuesList);

  gl.bufferData(gl.ARRAY_BUFFER, values, gl.STATIC_DRAW);
}


main();