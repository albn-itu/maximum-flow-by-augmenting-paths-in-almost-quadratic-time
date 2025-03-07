let svg = d3.select("svg"),
  width = +svg.node().getBoundingClientRect().width,
  height = +svg.node().getBoundingClientRect().height;

// svg objects
let link, node, nodeCirc, nodeLabel, edgeLabel, edgepaths, edgelabels;
// the data - an object with nodes and links
let graph;

// load the data
d3.json("expander.json", (error, _graph) => {
  if (error) throw error;

  graph = _graph;

  initializeDisplay();
  initializeSimulation();
});

const SINK_COLOR = "red";
const SOURCE_COLOR = "#00ffff";
const EDGE_COLOR = "#aaa";

//////////// FORCE SIMULATION ////////////

// force simulator
let simulation = d3.forceSimulation();

// set up the simulation and event to update locations after each tick
function initializeSimulation() {
  simulation.nodes(graph.nodes);
  initializeForces();
  simulation.on("tick", ticked);
}

const config = {
  enableEdgeLabels: false,
  enableVertexLabels: true,
  contractSameGroupEdges: false,
};

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
    radius: 8,
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
    .distance((d) => {
      const dist = forceProperties.link.distance;
      if (config.contractSameGroupEdges) {
        const isCluster = d.source.group && d.source.group === d.target.group;
        return isCluster ? dist * 0.4 : dist;
      }
      return dist;
    })
    .iterations(forceProperties.link.iterations)
    .links(forceProperties.link.enabled ? graph.links : []);

  // updates ignored until this is run
  // restarts the simulation (important if simulation has already slowed down)
  simulation.alpha(1).restart();
}

//////////// DISPLAY ////////////
const nodeRadius = (d) => {
  const r = forceProperties.collide.radius;
  return d.source || d.sink ? r * 1.5 : r;
};

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
    .style("fill", EDGE_COLOR)
    .attr("d", "M 0 0 6 3 0 6 1.5 3");

  // set the data and properties of link lines
  link = svg
    .selectAll(".links")
    .data(graph.links)
    .enter()
    .append("line")
    .attr("class", "links")
    .attr("marker-end", "url(#arrowhead)");

  edgepaths = svg
    .selectAll(".edgepath") //make path go along with the link provide position for link labels
    .data(graph.links)
    .enter()
    .append("path")
    .attr("class", "edgepath")
    .attr("fill-opacity", 0)
    .attr("stroke-opacity", 0)
    .attr("id", function (d, i) {
      return "edgepath" + i;
    })
    .style("pointer-events", "none");

  edgelabels = svg
    .selectAll(".edgelabel")
    .data(graph.links)
    .enter()
    .append("text")
    .style("pointer-events", "none")
    .attr("class", "edgelabel")
    .attr("id", function (d, i) {
      return "edgelabel" + i;
    })
    .attr("font-size", 10)
    .attr("fill", EDGE_COLOR)
    .append("textPath") //To render text along the shape of a <path>, enclose the text in a <textPath> element that has an href attribute with a reference to the <path> element.
    .attr("xlink:href", (d, i) => "#edgepath" + i)
    .style("text-anchor", "middle")
    .style("pointer-events", "none")
    .attr("startOffset", "50%");

  // set the data and properties of node circles
  node = svg
    .selectAll(".nodes")
    .data(graph.nodes)
    .enter()
    .append("g")
    .attr("class", "nodes")
    .call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended),
    );

  nodeCirc = node
    .append("circle")
    .attr("r", nodeRadius)
    .attr("stroke", "black")
    .attr("stroke-width", STROKE_WIDTH)
    .attr("fill", "white");

  node.append("title").text((d) => d.id);

  nodeLabel = node
    .append("text")
    .text((d) => d.id)
    .attr("font-size", 8)
    .attr("text-anchor", "middle")
    .attr("dy", 3);

  // visualize the graph
  updateDisplay();
}

const STROKE_WIDTH = 2;

// update the display based on the forces (but not positions)
function updateDisplay() {
  nodeCirc.attr("r", nodeRadius);

  const nodeColor = (d) => {
    return d.source
      ? SOURCE_COLOR
      : d.sink
        ? SINK_COLOR
        : d.group
          ? colors[d.group]
          : "white";
  };

  nodeCirc
    .attr("stroke", (d) => {
      return d.source ? SOURCE_COLOR : d.sink ? SINK_COLOR : "black";
    })
    .attr("fill", nodeColor);

  nodeLabel.attr("display", config.enableVertexLabels ? "initial" : "none");

  link
    .attr("stroke-width", forceProperties.link.enabled ? 1 : 0.5)
    .attr("stroke", EDGE_COLOR)
    .attr("opacity", forceProperties.link.enabled ? 1 : 0)
    .attr("text-anchor", "middle");

  edgelabels
    .attr("display", config.enableEdgeLabels ? "initial" : "none")
    .text((d) => d.value);
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

const colors = [
  "#FF6633",
  "#FFB399",
  "#FF33FF",
  "#FFFF99",
  "#00B3E6",
  "#E6B333",
  "#3366E6",
  "#999966",
  "#809980",
  "#E6FF80",
  "#1AFF33",
  "#999933",
  "#FF3380",
  "#CCCC00",
  "#66E64D",
  "#4D80CC",
  "#FF4D4D",
  "#99E6E6",
  "#6666FF",
];

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

  node.attr("transform", (d) => `translate(${d.x}, ${d.y})`);

  d3.select("#alpha_value").style("flex-basis", simulation.alpha() * 100 + "%");

  edgepaths.attr(
    "d",
    (d) =>
      "M " +
      d.source.x +
      " " +
      d.source.y +
      " L " +
      d.target.x +
      " " +
      d.target.y,
  );
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
