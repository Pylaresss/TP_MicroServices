const snowCanvas = document.getElementById("snowflakes");
if (snowCanvas) {
    const ctx = snowCanvas.getContext("2d");

    let flakes = [];
    const FLAKE_COUNT = 200;

    function resize() {
        snowCanvas.width = window.innerWidth;
        snowCanvas.height = window.innerHeight;
    }

    window.addEventListener("resize", resize);
    resize();

    function createFlakes() {
        flakes = [];
        for (let i = 0; i < FLAKE_COUNT; i++) {
            flakes.push({
                x: Math.random() * snowCanvas.width,
                y: Math.random() * snowCanvas.height,
                r: Math.random() * 3 + 1,
                dx: Math.random() * 0.5 - 0.25,
                dy: Math.random() * 1 + 0.5,
                opacity: Math.random() * 0.7 + 0.3
            });
        }
    }

    createFlakes();

    function animate() {
        ctx.clearRect(0, 0, snowCanvas.width, snowCanvas.height);

        ctx.fillStyle = "white";
        ctx.shadowColor = "white";

        flakes.forEach(flake => {
            ctx.globalAlpha = flake.opacity;
            ctx.beginPath();
            ctx.arc(flake.x, flake.y, flake.r, 0, Math.PI * 2);
            ctx.fill();

            flake.x += flake.dx;
            flake.y += flake.dy;

            if (flake.y > snowCanvas.height) {
                flake.y = -flake.r;
                flake.x = Math.random() * snowCanvas.width;
            }
        });

        requestAnimationFrame(animate);
    }

    animate();
}
