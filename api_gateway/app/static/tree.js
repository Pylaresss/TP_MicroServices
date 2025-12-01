const canvas = document.getElementById('tree');
if (canvas) {
  const ctx = canvas.getContext('2d');

  function resize() {
    const size = Math.min(window.innerWidth, window.innerHeight) * 0.7;
    canvas.width = size;
    canvas.height = size;
  }
  resize();
  window.addEventListener('resize', resize);

  const lights = [];
  const maxLayers = 18;
  const baseRadius = 0.45;
  let mouse = { x: null, y: null };
  let angle = 0;

    function generateTree() {
    lights.length = 0;
    for (let layer = 0; layer < maxLayers; layer++) {
        const t = layer / (maxLayers - 1); // 0 = sommet, 1 = bas

        // rayon PETIT en haut, GRAND en bas
        const radius = baseRadius * t;  // <--- ICI le changement

        // position verticale : de haut (-0.8) vers bas (+0.7)
        const y = -0.8 + t * 1.5;

        const pointsInLayer = 16 + layer * 2;
        for (let i = 0; i < pointsInLayer; i++) {
        const theta = (i / pointsInLayer) * Math.PI * 2;
        const x = radius * Math.cos(theta);
        const z = radius * Math.sin(theta);

        lights.push({
            x, y, z,
            baseBrightness: 0.2 + Math.random() * 0.4,
            colorHue: 40 + Math.random() * 40
        });
        }
    }
    }


  generateTree();

  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = ((e.clientY - rect.top) / rect.height) * 2 - 1;
  });

  canvas.addEventListener('mouseleave', () => {
    mouse.x = null;
    mouse.y = null;
  });

  function draw() {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const grad = ctx.createRadialGradient(
      w / 2, h / 2, 0,
      w / 2, h / 2, w / 2
    );
    grad.addColorStop(0, '#0f172a');
    grad.addColorStop(1, '#020617');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    angle += 0.01;

    const cx = w / 2;
    const cy = h / 2 + h * 0.05;

    lights.forEach(light => {
      const cosA = Math.cos(angle);
      const sinA = Math.sin(angle);
      const rx = light.x * cosA - light.z * sinA;
      const rz = light.x * sinA + light.z * cosA;

      const depth = 1.5 + rz;
      const projX = rx / depth;
      const projY = light.y / depth;

      const screenX = cx + projX * (w * 0.4);
      const screenY = cy + projY * (h * 0.4);



      let brightness = light.baseBrightness;
      if (mouse.x !== null && mouse.y !== null) {
        const dx = projX - mouse.x * 0.7;
        const dy = projY - mouse.y * 0.7;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const influence = Math.max(0, 1 - dist * 3);
        brightness += influence * 0.8;
      }

      const radius = 3 + brightness * 4;

      ctx.beginPath();
      ctx.arc(screenX, screenY, radius, 0, Math.PI * 2);
      ctx.closePath();
      ctx.fillStyle = `hsla(${light.colorHue}, 100%, ${40 + brightness * 40}%, 0.9)`;
      ctx.shadowColor = ctx.fillStyle;
      ctx.shadowBlur = 8 + brightness * 12;
      ctx.fill();
    });

    ctx.shadowBlur = 0;
    requestAnimationFrame(draw);
  }

  requestAnimationFrame(draw);
}
