const canvas = document.getElementById("plot");
const ctx = canvas.getContext("2d");

const controls = {
  V0: document.getElementById("V0"),
  a: document.getElementById("a"),
  emax: document.getElementById("emax"),
};

const outputs = {
  V0: document.getElementById("V0Out"),
  a: document.getElementById("aOut"),
  emax: document.getElementById("emaxOut"),
};

function transmission(E, V0, a) {
  if (E <= 0) return 0;

  if (Math.abs(E - V0) < 1e-7) {
    return 1 / (1 + (V0 * a * a) / 2);
  }

  if (E < V0) {
    const kappa = Math.sqrt(2 * (V0 - E));
    const s = Math.sinh(kappa * a);
    const term = (V0 * V0 * s * s) / (4 * E * (V0 - E));
    return 1 / (1 + term);
  }

  const kPrime = Math.sqrt(2 * (E - V0));
  const s = Math.sin(kPrime * a);
  const term = (V0 * V0 * s * s) / (4 * E * (E - V0));
  return 1 / (1 + term);
}

function readControls() {
  const V0 = Number(controls.V0.value);
  const a = Number(controls.a.value);
  const emax = Number(controls.emax.value);
  outputs.V0.textContent = V0.toFixed(1);
  outputs.a.textContent = a.toFixed(2);
  outputs.emax.textContent = emax.toFixed(1);
  return { V0, a, emax };
}

function drawAxes(width, height, pad) {
  ctx.strokeStyle = "#475569";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad, pad);
  ctx.lineTo(pad, height - pad);
  ctx.lineTo(width - pad, height - pad);
  ctx.stroke();

  ctx.fillStyle = "#94a3b8";
  ctx.font = "14px system-ui, sans-serif";
  ctx.fillText("T(E)", pad - 34, pad + 6);
  ctx.fillText("E", width - pad, height - pad + 28);

  ctx.textAlign = "center";
  for (let i = 0; i <= 4; i += 1) {
    const y = pad + ((height - 2 * pad) * i) / 4;
    const value = 1 - i / 4;
    ctx.fillText(value.toFixed(1), pad - 22, y + 4);
    ctx.strokeStyle = "rgba(71, 85, 105, 0.35)";
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(width - pad, y);
    ctx.stroke();
  }
  ctx.textAlign = "left";
}

function draw() {
  const { V0, a, emax } = readControls();
  const width = canvas.width;
  const height = canvas.height;
  const pad = 54;

  ctx.clearRect(0, 0, width, height);
  drawAxes(width, height, pad);

  const xFor = (E) => pad + ((E / emax) * (width - 2 * pad));
  const yFor = (T) => height - pad - (T * (height - 2 * pad));

  ctx.strokeStyle = "#38bdf8";
  ctx.lineWidth = 3;
  ctx.beginPath();
  const steps = 900;
  for (let i = 0; i <= steps; i += 1) {
    const E = 0.02 + ((emax - 0.02) * i) / steps;
    const T = transmission(E, V0, a);
    const x = xFor(E);
    const y = yFor(T);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  ctx.strokeStyle = "#f59e0b";
  ctx.lineWidth = 2;
  ctx.setLineDash([7, 7]);
  ctx.beginPath();
  ctx.moveTo(xFor(V0), pad);
  ctx.lineTo(xFor(V0), height - pad);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = "#fbbf24";
  ctx.font = "14px system-ui, sans-serif";
  ctx.fillText("E = V0", xFor(V0) + 8, pad + 18);
}

Object.values(controls).forEach((control) => control.addEventListener("input", draw));
draw();
