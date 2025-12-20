window.addEventListener('load', () => {
    if ('speechSynthesis' in window) {
        const welcome = new SpeechSynthesisUtterance('Welcome to DACOS, the future of automotive diagnostics.');
        speechSynthesis.speak(welcome);
    }
});

// Three.js 3D Scene
const canvas = document.getElementById('hero-canvas');
if (canvas) {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Create geometries
    const geometry1 = new THREE.TorusGeometry(10, 3, 16, 100);
    const material1 = new THREE.MeshBasicMaterial({ color: 0x00d4ff, wireframe: true });
    const torus = new THREE.Mesh(geometry1, material1);
    scene.add(torus);

    const geometry2 = new THREE.OctahedronGeometry(5);
    const material2 = new THREE.MeshBasicMaterial({ color: 0xff006e, wireframe: true });
    const octahedron = new THREE.Mesh(geometry2, material2);
    octahedron.position.set(15, 0, 0);
    scene.add(octahedron);

    const geometry3 = new THREE.IcosahedronGeometry(4);
    const material3 = new THREE.MeshBasicMaterial({ color: 0x8338ec, wireframe: true });
    const icosahedron = new THREE.Mesh(geometry3, material3);
    icosahedron.position.set(-15, 0, 0);
    scene.add(icosahedron);

    // Particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 1000;
    const posArray = new Float32Array(particlesCount * 3);
    for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 100;
    }
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particlesMaterial = new THREE.PointsMaterial({ size: 0.005, color: 0x00d4ff });
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particlesMesh);

    camera.position.z = 30;

    const animate = () => {
        requestAnimationFrame(animate);
        torus.rotation.x += 0.01;
        torus.rotation.y += 0.01;
        octahedron.rotation.x += 0.02;
        octahedron.rotation.y += 0.02;
        icosahedron.rotation.x += 0.015;
        icosahedron.rotation.y += 0.015;
        particlesMesh.rotation.y += 0.001;
        renderer.render(scene, camera);
    };
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add fade-in animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
        }
    });
}, observerOptions);

// Observe sections
document.querySelectorAll('section').forEach(section => {
    observer.observe(section);
});

// Add CSS for fade-in
const style = document.createElement('style');
style.textContent = `
    section {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
    section.fade-in {
        opacity: 1;
        transform: translateY(0);
    }
`;
document.head.appendChild(style);

// Initialize particles.js for hero background
particlesJS('hero', {
    particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: '#00d4ff' },
        shape: { type: 'circle' },
        opacity: { value: 0.5, random: true },
        size: { value: 3, random: true },
        line_linked: { enable: true, distance: 150, color: '#00d4ff', opacity: 0.4, width: 1 },
        move: { enable: true, speed: 2, direction: 'none', random: true, straight: false, out_mode: 'out' }
    },
    interactivity: {
        detect_on: 'canvas',
        events: { onhover: { enable: true, mode: 'repulse' }, onclick: { enable: true, mode: 'push' } },
        modes: { repulse: { distance: 100, duration: 0.4 }, push: { particles_nb: 4 } }
    },
    retina_detect: true
});

// Typing effect for hero text
const heroText = document.querySelector('.display-4');
if (heroText) {
    const text = heroText.textContent;
    heroText.textContent = '';
    let i = 0;
    const typeWriter = () => {
        if (i < text.length) {
            heroText.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, 100);
        }
    };
    setTimeout(typeWriter, 1000);
}

// Add confetti effect to "Explore Products" button
const exploreBtn = document.querySelector('.btn-primary');
if (exploreBtn) {
    exploreBtn.addEventListener('click', () => {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });
    });
}

// Live Demo Terminal
const demoModal = document.getElementById('demoModal');
const terminalOutput = document.getElementById('terminal-output');
const cursor = document.getElementById('cursor');

demoModal.addEventListener('shown.bs.modal', () => {
    terminalOutput.innerHTML = '';
    const messages = [
        'DACOS AutoDiag v5.0 Initialized...',
        'Connecting to VCI...',
        'VCI Connected: GODIAG GD101',
        'Scanning vehicle ECU...',
        'Vehicle: 2018 BMW 3 Series (F30)',
        'Engine: N55B30A',
        'Reading DTCs...',
        'DTC Found: P0300 - Random/Multiple Cylinder Misfire Detected',
        'DTC Found: P0171 - System Too Lean (Bank 1)',
        'Live Data: RPM: 850, Coolant Temp: 92°C, Fuel Pressure: 3.5 bar',
        'Diagnostic Complete. Recommendations: Check spark plugs, fuel injectors.',
        'Session ended.'
    ];

    let messageIndex = 0;
    let charIndex = 0;

    const typeMessage = () => {
        if (messageIndex < messages.length) {
            const message = messages[messageIndex];
            if (charIndex < message.length) {
                terminalOutput.innerHTML += message.charAt(charIndex);
                charIndex++;
                setTimeout(typeMessage, 50);
            } else {
                terminalOutput.innerHTML += '<br>';
                // Speak the message
                if ('speechSynthesis' in window) {
                    const utterance = new SpeechSynthesisUtterance(message);
                    utterance.rate = 1.2;
                    utterance.pitch = 1;
                    speechSynthesis.speak(utterance);
                }
                charIndex = 0;
                messageIndex++;
                setTimeout(typeMessage, 1000);
            }
        } else {
            cursor.style.display = 'none';
        }
    };

    setTimeout(typeMessage, 500);
});

demoModal.addEventListener('hidden.bs.modal', () => {
    cursor.style.display = 'inline';
});

// Add flip effect to product cards (simplified)
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = 'scale(1.05) rotateY(5deg)';
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'scale(1) rotateY(0deg)';
    });
});