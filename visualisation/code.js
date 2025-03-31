let svg = d3.select("svg"),
  width = +svg.node().getBoundingClientRect().width,
  height = +svg.node().getBoundingClientRect().height;

// svg objects
let link,
  node,
  nodeCirc,
  nodeLabel,
  nodeSubscript,
  edgeLabel,
  edgepaths,
  edgelabels;
// the data - an object with nodes and links
let graph;

// load the data

const getFileName = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const file = urlParams.get("graph");
  return file || "graph.json";
};

const fileName = getFileName();

d3.json(fileName, (error, _graph) => {
  if (error) throw error;

  graph = _graph;

  graph.links.forEach((d) => {
    const reverseEdge = graph.links.find(
      (e) => e.source === d.target && e.target === d.source,
    );

    if (reverseEdge) {
      d.bidirectional = true;
      reverseEdge.bidirectional = true;
    }
  });

  document.querySelector("#graph-name").innerText = fileName;

  document
    .querySelector("#frameSlider")
    .setAttribute("max", graph.frames.length - 1);
  d3.select("#frame-label").text(`Frame ${config.frame}: ${curFrame().label}`);

  initializeDisplay();
  initializeSimulation();
});

const SINK_COLOR = "#f3722c";
const SOURCE_COLOR = "#277da1";
const DEAD_COLOR = "#f94144";

const EDGE_COLOR = "#aaa";
const USED_EDGE_COLOR = "#43aa8b";
const SATURATED_EDGE_COLOR = DEAD_COLOR;
const AUG_EDGE_COLOR = SOURCE_COLOR;

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
  enableVertexHeights: true,
  contractSameGroupEdges: false,
  frame: 0,
  showWeightsAsEdgeLabels: false,
  enableSimulation: true,
};

const curFrame = () => graph.frames[+config.frame];

const onFramePick = (value) => {
  config.frame = value;
  d3.select("#frame-label").text(`Frame ${value}: ${curFrame().label}`);
  updateDisplay();
};

// values for all forces
forceProperties = {
  center: {
    x: 0.5,
    y: 0.5,
  },
  charge: {
    enabled: true,
    strength: -180,
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
  const r = +forceProperties.collide.radius;
  return d.source || d.sink ? r * 1.5 : r;
};

const nodeColor = (d) => {
  return d.source
    ? SOURCE_COLOR
    : d.sink
      ? SINK_COLOR
      : d.group
        ? colors[d.group]
        : "white";
};

const mkMarker = (id, color) => {
  svg
    .append("svg:defs")
    .append("svg:marker")
    .attr("id", id)
    .attr("refX", 3)
    .attr("refY", 3)
    .attr("markerWidth", 50)
    .attr("markerHeight", 50)
    .attr("orient", "auto")
    .append("path")
    .style("fill", color)
    .attr("d", "M 0 0 6 3 0 6");
};

const mkRevMarker = (id, color) => {
  svg
    .append("svg:defs")
    .append("svg:marker")
    .attr("id", id)
    .attr("refX", 3)
    .attr("refY", 3)
    .attr("markerWidth", 50)
    .attr("markerHeight", 50)
    .attr("orient", "auto-start-reverse")
    .append("path")
    .style("stroke", color)
    .style("fill", "white")
    .attr("d", "M 0 0 6 3 0 6 1.5 3 0 0");
};

// generate the svg objects and force simulation
function initializeDisplay() {
  const setLegendColor = (id, color = null, border = null) => {
    if (color) d3.select(id).style("background-color", color);
    if (border) d3.select(id).style("border", `2px ${border}`);
  };

  setLegendColor("#legend-source", SOURCE_COLOR);
  setLegendColor("#legend-sink", SINK_COLOR);
  setLegendColor("#legend-dead", null, `solid ${DEAD_COLOR}`);
  setLegendColor("#legend-edge", EDGE_COLOR);
  setLegendColor("#legend-used-edge", USED_EDGE_COLOR);
  setLegendColor("#legend-saturated-edge", SATURATED_EDGE_COLOR);
  setLegendColor("#legend-aug-edge", AUG_EDGE_COLOR);
  setLegendColor("#legend-inadmissible-edge", null, `dashed black`);
  setLegendColor("#legend-reverse", null, `solid black`);

  const mkMarkers = (id, color) => {
    mkMarker(id, color);
    mkRevMarker(`${id}-rev`, color);
  };

  mkMarkers("arrowhead", EDGE_COLOR);
  mkMarkers("arrowhead-aug", AUG_EDGE_COLOR);
  mkMarkers("arrowhead-saturated", SATURATED_EDGE_COLOR);
  mkMarkers("arrowhead-used", USED_EDGE_COLOR);

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
    .attr("font-size", 8)
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
    .attr("fill", nodeColor);

  node.append("title").text((d) => d.id);

  nodeLabel = node
    .append("text")
    .text((d) => d.id)
    .attr("font-size", 8)
    .attr("text-anchor", "middle")
    .attr("dy", 3);

  nodeSubscript = node
    .append("text")
    .attr("font-size", 5)
    .attr("text-anchor", "middle");

  // visualize the graph
  updateDisplay();
}

const STROKE_WIDTH = 2;

const isAdmissible = (d) => curFrame().edges[d.id].admissible;
const isRevAdmissible = (d) => curFrame().edges[d.id].reverseAdmissible;

// update the display based on the forces (but not positions)
function updateDisplay() {
  const f = curFrame();

  const borderColor = (d) => (f.vertices[d.id].alive ? "black" : DEAD_COLOR);
  const nodeOpacity = (d) => (f.vertices[d.id].alive ? 1 : 0.2);

  nodeCirc.attr("r", nodeRadius).attr("stroke", borderColor);

  node.attr("opacity", nodeOpacity);

  nodeLabel
    .attr("display", config.enableVertexLabels ? "initial" : "none")
    .text((d) => d.id);

  nodeSubscript
    .attr("display", config.enableVertexHeights ? "initial" : "none")
    .text((d) => f.vertices[d.id].height)
    .attr("dy", (d) => nodeRadius(d) + 6);

  const edgeColor = (d) => {
    if (f.augmentingPath.some((id) => Math.abs(id) === d.id))
      return AUG_EDGE_COLOR;
    if (f.edges[d.id].remainingCapacity === 0) return SATURATED_EDGE_COLOR;
    if (f.edges[d.id].flow > 0) return USED_EDGE_COLOR;
    return EDGE_COLOR;
  };

  const edgeMarker = (d) => {
    if (!isAdmissible(d) && isRevAdmissible(d)) return "none";

    let color = "";
    if (f.augmentingPath.includes(d.id)) color = "-aug";
    else if (f.edges[d.id].remainingCapacity === 0) color = "-saturated";
    else if (f.edges[d.id].flow > 0) color = "-used";
    return `url(#arrowhead${color})`;
  };

  const edgeMarkerStart = (d) => {
    if (!isRevAdmissible(d)) return "none";

    let color = "";
    if (f.augmentingPath.includes(d.id)) color = "-aug";
    else if (f.edges[d.id].remainingCapacity === 0) color = "-saturated";
    else if (f.edges[d.id].flow > 0) color = "-used";
    return `url(#arrowhead${color}-rev)`;
  };

  const edgeWidth = (d) => (f.augmentingPath.includes(d.id) ? 1.5 : 1);

  link
    .attr("stroke-width", edgeWidth)
    .attr("stroke", edgeColor)
    .attr("marker-start", edgeMarkerStart)
    .attr("marker-end", edgeMarker)
    .attr("opacity", forceProperties.link.enabled ? 1 : 0)
    .attr("stroke-dasharray", (d) =>
      isAdmissible(d) || isRevAdmissible(d) ? "0,0" : "4",
    )
    .attr("text-anchor", "middle");

  edgelabels
    .attr("display", config.enableEdgeLabels ? "initial" : "none")
    .text((d) => {
      if (config.showWeightsAsEdgeLabels) {
        return `w=${d.weight}`;
      }
      return `${f.edges[d.id].flow}/${d.capacity}`;
    });

  ticked();
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

const rotate = ({ x, y }, angle) => ({
  x: x * Math.cos(angle) - y * Math.sin(angle),
  y: x * Math.sin(angle) + y * Math.cos(angle),
});

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
  const calcEdgeEndpoints = (d) => {
    const makeDelta = (p, add = 0) => {
      const r = nodeRadius(p) + STROKE_WIDTH + add;
      return scale(free([d.source, d.target]), r);
    };

    let edgySource = makeDelta(d.source, isRevAdmissible(d) ? 1 : -1);
    let edgyTarget = makeDelta(
      d.target,
      !isAdmissible(d) && isRevAdmissible(d) ? -1 : 1,
    );
    if (d.bidirectional) {
      edgySource = rotate(edgySource, -Math.PI / 2 / 5);
      edgyTarget = rotate(edgyTarget, Math.PI / 2 / 5);
    }

    const start = sum(d.source, edgySource);
    const end = diff(d.target, edgyTarget);

    return {
      start,
      end,
    };
  };

  link
    .attr("x1", (d) => calcEdgeEndpoints(d).start.x)
    .attr("y1", (d) => calcEdgeEndpoints(d).start.y)
    .attr("x2", (d) => calcEdgeEndpoints(d).end.x)
    .attr("y2", (d) => calcEdgeEndpoints(d).end.y);

  node.attr("transform", (d) => `translate(${d.x}, ${d.y})`);

  d3.select("#alpha_value").style("flex-basis", simulation.alpha() * 100 + "%");

  edgepaths.attr(
    "d",
    (d) =>
      `M ${calcEdgeEndpoints(d).start.x} ${calcEdgeEndpoints(d).start.y} L ${calcEdgeEndpoints(d).end.x} ${calcEdgeEndpoints(d).end.y}`,
  );
}

const findSvgBoundingBox = () => {
  const coords = [...document.querySelectorAll("g.nodes")].map((c) =>
    c
      .getAttribute("transform")
      .replace("translate(", "")
      .replace(")", "")
      .split(", ")
      .map((d) => Number.parseFloat(d)),
  );

  const r = +forceProperties.collide.radius * 1.5 + STROKE_WIDTH;

  return {
    minX: Math.floor(Math.min(...coords.map((c) => c[0])) - r),
    minY: Math.floor(Math.min(...coords.map((c) => c[1])) - r),
    maxX: Math.ceil(Math.max(...coords.map((c) => c[0])) + r),
    maxY: Math.ceil(Math.max(...coords.map((c) => c[1])) + r),
  };
};

const exportSvg = () => {
  const { minX, minY, maxX, maxY } = findSvgBoundingBox();
  let width = maxX - minX;
  let height = maxY - minY;

  let viewBox = `viewBox="${minX} ${minY} ${width} ${height}"`;

  let s = `<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg" ${viewBox} xmlns:xlink="http://www.w3.org/1999/xlink">`;
  s += document.querySelector("svg").innerHTML;
  s += "</svg>";

  console.log(s);
};

const fitViewBox = () => {
  exportSvg();

  const { minX, minY, maxX, maxY } = findSvgBoundingBox();
  const width = maxX - minX;
  const height = maxY - minY;

  const pct = 0.1;
  const x = minX - width * pct;
  const y = minY - height * pct;
  const w = width * (1 + 2 * pct);
  const h = height * (1 + 2 * pct);

  svg.attr("viewBox", `${x} ${y} ${w} ${h}`);
};

//////////// UI EVENTS ////////////

function dragstarted(d) {
  if (!config.enableSimulation) return;

  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  if (config.enableSimulation) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  } else {
    d.x = d3.event.x;
    d.y = d3.event.y;
    ticked();
  }
}

function dragended(d) {
  if (config.enableSimulation) {
    if (!d3.event.active) simulation.alphaTarget(0.0001);
    d.fx = null;
    d.fy = null;
  } else {
    // Snap to grid
    const nearestMultiple = (n, m) => Math.round(n / m) * m;
    d.x = nearestMultiple(d.x, 20);
    d.y = nearestMultiple(d.y, 20);
    ticked();
  }
}

// update size-related forces
d3.select(window).on("resize", () => {
  width = +svg.node().getBoundingClientRect().width;
  height = +svg.node().getBoundingClientRect().height;
});

d3.select(window).on("keypress", () => {
  const key = d3.event.key;

  if (key === "l") {
    const newVal = Math.min(config.frame + 1, graph.frames.length - 1);
    d3.select("#frameSlider").property("value", newVal);
    onFramePick(newVal);
  }

  if (key === "h") {
    const newVal = Math.max(config.frame - 1, 0);
    d3.select("#frameSlider").property("value", newVal);
    onFramePick(newVal);
  }

  if (key === "e") {
    document.querySelector("#edge-labels-checkbox").click();
  }

  if (key === "v") {
    document.querySelector("#vertex-labels-checkbox").click();
  }

  if (key === "k") {
    document.querySelector("#vertex-heights-checkbox").click();
  }

  if (key === "w") {
    config.showWeightsAsEdgeLabels = !config.showWeightsAsEdgeLabels;
    updateDisplay();
  }

  if (key === "r") {
    fitViewBox();
  }
});

// convenience function to update everything (run after UI input)
function updateAll() {
  updateForces();
  updateDisplay();
}
