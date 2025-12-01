const snowCanvas = document.getElementById('snow');
if (snowCanvas) {
  const ctx = snowCanvas.getContext('2d');

  const FLAKE_COUNT = 200;
  const flakes = [];
  let width, height;

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    snowCanvas.width = width;
    snowCanvas.height = height;
  }

  window.addEventListener('resize', resize);
  resize();

  function createFlakes() {
    flakes.length = 0;
    for (let i = 0; i < FLAKE_COUNT; i++) {
      flakes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: 1 + Math.random() * 3,
        vy: 0.5 + Math.random() * 1.5,
        vx: -0.5 + Math.random() * 1,
        alpha: 0.4 + Math.random() * 0.6
      });
    }
  }

  createFlakes();

  function drawVillage() {
    // ciel dégradé
    const sky = ctx.createLinearGradient(0, 0, 0, height);
    sky.addColorStop(0, '#020617');
    sky.addColorStop(1, '#0b1220');
    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, width, height);

    // neige au sol
    ctx.fillStyle = '#e5e7eb';
    ctx.beginPath();
    ctx.moveTo(0, height * 0.75);
    ctx.quadraticCurveTo(width * 0.5, height * 0.68, width, height * 0.75);
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fill();

    // quelques maisons stylisées
    const baseY = height * 0.7;
    const houseWidth = 80;
    const houseHeight = 60;

    function drawHouse(x) {
      // corps
      ctx.fillStyle = '#111827';
      ctx.fillRect(x, baseY - houseHeight, houseWidth, houseHeight);

      // toit
      ctx.fillStyle = '#1f2937';
      ctx.beginPath();
      ctx.moveTo(x - 10, baseY - houseHeight);
      ctx.lineTo(x + houseWidth / 2, baseY - houseHeight - 30);
      ctx.lineTo(x + houseWidth + 10, baseY - houseHeight);
      ctx.closePath();
      ctx.fill();

      // fenêtres
      ctx.fillStyle = '#facc15';
      for (let i = 0; i < 2; i++) {
        ctx.fillRect(
          x + 15 + i * 30,
          baseY - houseHeight + 20,
          12,
          16
        );
      }
    }

    drawHouse(width * 0.2);
    drawHouse(width * 0.45);
    drawHouse(width * 0.7);
  }

  function drawSnow() {
    ctx.save();
    ctx.shadowColor = '#e5f0ff';
    ctx.shadowBlur = 8;

    for (const flake of flakes) {
      ctx.beginPath();
      ctx.arc(flake.x, flake.y, flake.r, 0, Math.PI * 2);
      ctx.closePath();
      ctx.fillStyle = `rgba(241,245,249,${flake.alpha})`;
      ctx.fill();

      // mouvement
      flake.y += flake.vy;
      flake.x += flake.vx + Math.sin(flake.y * 0.01) * 0.3;

      // reset si flocon sort de l'écran
      if (flake.y > height + flake.r) {
        flake.y = -flake.r;
        flake.x = Math.random() * width;
      }
      if (flake.x < -flake.r) {
        flake.x = width + flake.r;
      }
      if (flake.x > width + flake.r) {
        flake.x = -flake.r;
      }
    }

    ctx.restore();
  }

  function animate() {
    drawVillage();
    drawSnow();
    requestAnimationFrame(animate);
  }

  animate();
}
