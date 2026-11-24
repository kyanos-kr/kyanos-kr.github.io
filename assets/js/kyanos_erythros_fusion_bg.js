/* ==========================================================================
   KYANOS × ERYTHROS — 3D Fusion Ambient Background (Dynamic Pulse Reactive)
   - Kyanos Mode : 청색 3중 공전 고리 중심의 정제된 평온 (루비 코어 은은한 심박)
   - Erythros Mode: 에리트로스 루비 태양 코어가 강렬하게 맥박치며 깨어나는 활력 상태
   ========================================================================== */
(function () {
    function initFusionBackground() {
        if (typeof THREE === 'undefined') return;

        var isErythros = document.documentElement.getAttribute('data-theme') === 'erythros';
        var targetMix = isErythros ? 1.0 : 0.0;
        var currentMix = targetMix;

        const canvas = document.createElement('canvas');
        canvas.id = 'kyanos-fusion-bg';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '0';
        canvas.style.pointerEvents = 'none';
        canvas.style.opacity = isErythros ? '0.58' : '0.38';
        canvas.style.transition = 'opacity 0.6s ease';
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
            emissiveIntensity: isErythros ? 2.0 : 0.72,
            roughness: 0.15,
            metalness: 0.3,
            flatShading: true
        });
        const rubyCore = new THREE.Mesh(rubyGeo, rubyMat);
        scene.add(rubyCore);

        // 키아노스 3중 공전 고리 (Kyanos <-> Erythros 색상 보간)
        const rings = [];
        const ringConfigs = [
            { radius: 4.5, tube: 0.03, colorK: 0x00f2fe, colorE: 0xff2a55, rotX: 1.15, rotY: 0.3, speed: 0.0025 },
            { radius: 6.0, tube: 0.022, colorK: 0x38bdf8, colorE: 0xfbbf24, rotX: -0.85, rotY: 0.7, speed: -0.0018 },
            { radius: 7.6, tube: 0.018, colorK: 0x818cf8, colorE: 0xf43f5e, rotX: 0.45, rotY: -1.1, speed: 0.0012 }
        ];

        ringConfigs.forEach(function (cfg) {
            const geo = new THREE.TorusGeometry(cfg.radius, cfg.tube, 12, 96);
            const mat = new THREE.MeshBasicMaterial({
                color: isErythros ? cfg.colorE : cfg.colorK,
                transparent: true,
                opacity: 0.65
            });
            const ring = new THREE.Mesh(geo, mat);
            ring.rotation.x = cfg.rotX;
            ring.rotation.y = cfg.rotY;
            ring.userData.speed = cfg.speed;
            ring.userData.colorK = new THREE.Color(cfg.colorK);
            ring.userData.colorE = new THREE.Color(cfg.colorE);
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

        const rubyLight = new THREE.PointLight(0xff2a55, isErythros ? 5.2 : 2.6, 38);
        scene.add(rubyLight);

        const kyanosLight = new THREE.DirectionalLight(0x38bdf8, isErythros ? 0.55 : 1.35);
        kyanosLight.position.set(10, 10, 10);
        scene.add(kyanosLight);

        // Dynamic Pulse Mode 실시간 연동
        window.addEventListener('kyanos:themechange', function (e) {
            isErythros = e.detail && e.detail.mode === 'erythros';
            targetMix = isErythros ? 1.0 : 0.0;
            canvas.style.opacity = isErythros ? '0.58' : '0.38';
        });

        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);
            const t = clock.getElapsedTime();

            // 부드러운 상태 보간 (lerp)
            currentMix += (targetMix - currentMix) * 0.05;

            const pulseFreq = 1.5 + currentMix * 1.1;
            const pulseAmp = 0.03 + currentMix * 0.045;
            const baseScale = 0.96 + currentMix * 0.14;
            const pulse = baseScale + Math.sin(t * pulseFreq) * pulseAmp;

            rubyCore.scale.set(pulse, pulse, pulse);
            rubyCore.rotation.y += 0.0022 + currentMix * 0.0024;
            rubyCore.rotation.x += 0.0009 + currentMix * 0.0012;
            rubyMat.emissiveIntensity = 0.72 + currentMix * 1.35;

            rubyLight.intensity = 2.6 + currentMix * 2.8;
            kyanosLight.intensity = 1.35 - currentMix * 0.8;

            const speedBoost = 1 + currentMix * 0.55;
            rings.forEach(function (r) {
                r.rotation.z += r.userData.speed * speedBoost;
                r.material.color.copy(r.userData.colorK).lerp(r.userData.colorE, currentMix);
            });

            particles.rotation.y += 0.00055 + currentMix * 0.00045;
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
