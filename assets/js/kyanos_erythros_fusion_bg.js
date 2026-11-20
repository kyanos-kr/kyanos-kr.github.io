/* ==========================================================================
   KYANOS × ERYTHROS — 3D Fusion Ambient Background
   메인 화면의 시야 선명도를 해치지 않도록 은은한 투명도(0.42)와 느린 공전 속도로 구동
   ========================================================================== */
(function () {
    function initFusionBackground() {
        if (typeof THREE === 'undefined') return;

        const canvas = document.createElement('canvas');
        canvas.id = 'kyanos-fusion-bg';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '0';
        canvas.style.pointerEvents = 'none';
        canvas.style.opacity = '0.42';
        document.body.insertBefore(canvas, document.body.firstChild);

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2.5, 18);

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

        // 중앙 에리트로스 루비 태양 코어
        const rubyGeo = new THREE.IcosahedronGeometry(2.0, 1);
        const rubyMat = new THREE.MeshPhysicalMaterial({
            color: 0xff1e4d,
            emissive: 0x990024,
            emissiveIntensity: 1.2,
            roughness: 0.15,
            metalness: 0.3,
            flatShading: true
        });
        const rubyCore = new THREE.Mesh(rubyGeo, rubyMat);
        scene.add(rubyCore);

        // 키아노스 3중 공전 고리
        const rings = [];
        const ringConfigs = [
            { radius: 4.5, tube: 0.03, color: 0x00f2fe, rotX: 1.15, rotY: 0.3, speed: 0.0025 },
            { radius: 6.0, tube: 0.022, color: 0x38bdf8, rotX: -0.85, rotY: 0.7, speed: -0.0018 },
            { radius: 7.6, tube: 0.018, color: 0x818cf8, rotX: 0.45, rotY: -1.1, speed: 0.0012 }
        ];

        ringConfigs.forEach(function (cfg) {
            const geo = new THREE.TorusGeometry(cfg.radius, cfg.tube, 12, 96);
            const mat = new THREE.MeshBasicMaterial({ color: cfg.color, transparent: true, opacity: 0.65 });
            const ring = new THREE.Mesh(geo, mat);
            ring.rotation.x = cfg.rotX;
            ring.rotation.y = cfg.rotY;
            ring.userData.speed = cfg.speed;
            scene.add(ring);
            rings.push(ring);
        });

        // 융해 입자 (최적화된 1,200개)
        const particleCount = 1200;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const colorKyanos = new THREE.Color(0x00f2fe);
        const colorErythros = new THREE.Color(0xff2a55);

        for (let i = 0; i < particleCount; i++) {
            const r = 3.2 + Math.random() * 14.0;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);

            positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta) * 0.65;
            positions[i * 3 + 2] = r * Math.cos(phi);

            const t = Math.min(1, Math.max(0, (r - 3.2) / 10.0));
            const mixed = colorErythros.clone().lerp(colorKyanos, t);
            colors[i * 3] = mixed.r;
            colors[i * 3 + 1] = mixed.g;
            colors[i * 3 + 2] = mixed.b;
        }

        const particleGeo = new THREE.BufferGeometry();
        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const particleMat = new THREE.PointsMaterial({
            size: 0.08,
            vertexColors: true,
            transparent: true,
            opacity: 0.8,
            blending: THREE.AdditiveBlending
        });
        const particles = new THREE.Points(particleGeo, particleMat);
        scene.add(particles);

        const rubyLight = new THREE.PointLight(0xff2a55, 3.8, 35);
        scene.add(rubyLight);

        const kyanosLight = new THREE.DirectionalLight(0x38bdf8, 1.2);
        kyanosLight.position.set(10, 10, 10);
        scene.add(kyanosLight);

        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const t = clock.getElapsedTime();
            const pulse = 1 + Math.sin(t * 1.6) * 0.035;
            rubyCore.scale.set(pulse, pulse, pulse);
            rubyCore.rotation.y += 0.0025;
            rubyCore.rotation.x += 0.001;

            rings.forEach(function (r) {
                r.rotation.z += r.userData.speed;
            });

            particles.rotation.y += 0.0006;
            renderer.render(scene, camera);
        }

        window.addEventListener('resize', function () {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFusionBackground);
    } else {
        initFusionBackground();
    }
})();
