const svg = d3.select("svg"),
  width = +svg.node().getBoundingClientRect().width,
  height = +svg.node().getBoundingClientRect().height;

// svg objects
let link, node;
// the data - an object with nodes and links
let graph;

// load the data
d3.json("miserables.json", (error, _graph) => {
  if (error) throw error;

  graph = _graph;

  initializeDisplay();
  initializeSimulation();
});

//////////// FORCE SIMULATION ////////////

// force simulator
let simulation = d3.forceSimulation();

// set up the simulation and event to update locations after each tick
function initializeSimulation() {
  simulation.nodes(graph.nodes);
  initializeForces();
  simulation.on("tick", ticked);
}

// values for all forces
forceProperties = {
  center: {
    x: 0.5,
    y: 0.5,
  },
  charge: {
    enabled: true,
    strength: -30,
    distanceMin: 1,
    distanceMax: 2000,
  },
  collide: {
    enabled: true,
    strength: 0.7,
    iterations: 1,
    radius: 5,
  },
  forceX: {
    enabled: false,
    strength: 0.1,
    x: 0.5,
  },
  forceY: {
    enabled: false,
    strength: 0.1,
    y: 0.5,
  },
  link: {
    enabled: true,
    distance: 30,
    iterations: 1,
  },
};

// add forces to the simulation
function initializeForces() {
  // add forces and associate each with a name
  simulation
    .force("link", d3.forceLink())
    .force("charge", d3.forceManyBody())
    .force("collide", d3.forceCollide())
    .force("center", d3.forceCenter())
    .force("forceX", d3.forceX())
    .force("forceY", d3.forceY());

  // apply properties to each of the forces
  updateForces();
}

// apply new force properties
function updateForces() {
  // get each force by name and update the properties
  simulation
    .force("center")
    .x(width * forceProperties.center.x)
    .y(height * forceProperties.center.y);

  simulation
    .force("charge")
    .strength(forceProperties.charge.strength * forceProperties.charge.enabled)
    .distanceMin(forceProperties.charge.distanceMin)
    .distanceMax(forceProperties.charge.distanceMax);

  simulation
    .force("collide")
    .strength(
      forceProperties.collide.strength * forceProperties.collide.enabled,
    )
    .radius(forceProperties.collide.radius)
    .iterations(forceProperties.collide.iterations);

  simulation
    .force("forceX")
    .strength(forceProperties.forceX.strength * forceProperties.forceX.enabled)
    .x(width * forceProperties.forceX.x);

  simulation
    .force("forceY")
    .strength(forceProperties.forceY.strength * forceProperties.forceY.enabled)
    .y(height * forceProperties.forceY.y);

  simulation
    .force("link")
    .id((d) => d.id)
    .distance(forceProperties.link.distance)
    .iterations(forceProperties.link.iterations)
    .links(forceProperties.link.enabled ? graph.links : []);

  // updates ignored until this is run
  // restarts the simulation (important if simulation has already slowed down)
  simulation.alpha(1).restart();
}

//////////// DISPLAY ////////////

// generate the svg objects and force simulation
function initializeDisplay() {
  svg
    .append("svg:defs")
    .append("svg:marker")
    .attr("id", "arrowhead")
    .attr("refX", 3)
    .attr("refY", 3)
    .attr("markerWidth", 50)
    .attr("markerHeight", 50)
    .attr("orient", "auto")
    .append("path")
    .style("fill", "black")
    .attr("d", "M 0 0 6 3 0 6 1.5 3");

  // set the data and properties of link lines
  link = svg
    .append("g")
    .attr("class", "links")
    .attr("marker-end", "url(#arrowhead)")
    .selectAll("line")
    .data(graph.links)
    .enter()
    .append("line");

  // set the data and properties of node circles
  node = svg
    .append("g")
    .attr("class", "nodes")
    .selectAll("circle")
    .data(graph.nodes)
    .enter()
    .append("circle")
    .call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended),
    );

  // node tooltip
  node.append("title").text((d) => d.id);
  // visualize the graph
  updateDisplay();
}

const STROKE_WIDTH = 2;

// update the display based on the forces (but not positions)
function updateDisplay() {
  node
    .attr("r", forceProperties.collide.radius)
    .attr("stroke", "black")
    .attr("stroke-width", STROKE_WIDTH)
    .attr("fill", "white");

  link
    .attr("stroke-width", forceProperties.link.enabled ? 1 : 0.5)
    .attr("opacity", forceProperties.link.enabled ? 1 : 0);
}

// Some useful vector math functions
const length = ({ x, y }) => Math.sqrt(x * x + y * y);
const sum = ({ x: x1, y: y1 }, { x: x2, y: y2 }) => ({
  x: x1 + x2,
  y: y1 + y2,
});
const diff = ({ x: x1, y: y1 }, { x: x2, y: y2 }) => ({
  x: x1 - x2,
  y: y1 - y2,
});
const prod = ({ x, y }, scalar) => ({ x: x * scalar, y: y * scalar });
const div = ({ x, y }, scalar) => ({ x: x / scalar, y: y / scalar });
const unit = (vector) => div(vector, length(vector));
const scale = (vector, scalar) => prod(unit(vector), scalar);

const free = ([coord1, coord2]) => diff(coord2, coord1);

// update the display positions after each simulation tick
function ticked() {
  // Some vector math to have the tip on the edge of the vertex circle instead of
  // at the center of it. For the sake of arrow heads.
  const targetBorder = (d) => {
    const nodeRadius = +forceProperties.collide.radius + STROKE_WIDTH + 1;
    return diff(d.target, scale(free([d.source, d.target]), nodeRadius));
  };

  link
    .attr("x1", ({ source }) => source.x)
    .attr("y1", ({ source }) => source.y)
    .attr("x2", (d) => targetBorder(d).x)
    .attr("y2", (d) => targetBorder(d).y);

  node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

  d3.select("#alpha_value").style("flex-basis", simulation.alpha() * 100 + "%");
}

//////////// UI EVENTS ////////////

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0.0001);
  d.fx = null;
  d.fy = null;
}

// update size-related forces
d3.select(window).on("resize", () => {
  width = +svg.node().getBoundingClientRect().width;
  height = +svg.node().getBoundingClientRect().height;
  updateForces();
});

// convenience function to update everything (run after UI input)
function updateAll() {
  updateForces();
  updateDisplay();
}
