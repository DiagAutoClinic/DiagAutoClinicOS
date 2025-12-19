// --- NEURAL NETWORK BACKGROUND ---
const canvas = document.getElementById('neural-bg');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
const mouse = { x: null, y: null };

window.addEventListener('mousemove', (event) => {
    mouse.x = event.x;
    mouse.y = event.y;
});

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initParticles();
});

class Particle {
    constructor(x, y, size, color, speedX, speedY) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.color = color;
        this.speedX = speedX;
        this.speedY = speedY;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = this.color;
        ctx.fill();
    }

    update() {
        if (this.x > canvas.width || this.x < 0) this.speedX = -this.speedX;
        if (this.y > canvas.height || this.y < 0) this.speedY = -this.speedY;
        this.x += this.speedX;
        this.y += this.speedY;
        this.draw();
    }
}

function initParticles() {
    particles = [];
    let numberOfParticles = (canvas.height * canvas.width) / 9000;
    for (let i = 0; i < numberOfParticles; i++) {
        let size = Math.random() * 1.5 + 0.5;
        let x = Math.random() * (innerWidth - size * 2) + size;
        let y = Math.random() * (innerHeight - size * 2) + size;
        let speedX = Math.random() * 0.4 - 0.2;
        let speedY = Math.random() * 0.4 - 0.2;
        let color = 'rgba(0, 229, 255, 0.7)';
        particles.push(new Particle(x, y, size, color, speedX, speedY));
    }
}

function connectParticles() {
    let opacityValue = 1;
    for (let a = 0; a < particles.length; a++) {
        for (let b = a; b < particles.length; b++) {
            let distance = ((particles[a].x - particles[b].x) * (particles[a].x - particles[b].x))
                         + ((particles[a].y - particles[b].y) * (particles[a].y - particles[b].y));
            if (distance < (canvas.width / 7) * (canvas.height / 7)) {
                opacityValue = 1 - (distance / 20000);
                ctx.strokeStyle = `rgba(0, 229, 255, ${opacityValue})`;
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(particles[a].x, particles[a].y);
                ctx.lineTo(particles[b].x, particles[b].y);
                ctx.stroke();
            }
        }
    }
}

function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    particles.forEach(p => p.update());
    connectParticles();
}

// --- LOADING SEQUENCE & TYPING EFFECT ---
document.addEventListener('DOMContentLoaded', () => {
    const loadingText = document.getElementById('loading-text');
    const loader = document.getElementById('loader');
    const heroDesc = document.getElementById('hero-desc');
    const textToType = "Open-source, modular, and secure diagnostic suite designed for the modern workshop.";

    const loadingSteps = [
        "INITIALIZING SYSTEM...",
        "LOADING DACOS KERNEL...",
        "CALIBRATING NEURAL NET...",
        "SYSTEM ONLINE"
    ];

    let currentStep = 0;
    const stepInterval = setInterval(() => {
        currentStep++;
        if (currentStep < loadingSteps.length) {
            loadingText.textContent = loadingSteps[currentStep];
        } else {
            clearInterval(stepInterval);
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
                startTypingEffect();
            }, 500);
        }
    }, 1000);

    function startTypingEffect() {
        heroDesc.style.width = '100%';
        heroDesc.textContent = textToType;
        // Reset animation to make it type
        heroDesc.style.animation = 'none';
        heroDesc.offsetHeight; /* trigger reflow */
        heroDesc.style.animation = null; 
    }

    initParticles();
    animate();
});
