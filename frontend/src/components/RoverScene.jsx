import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, Stars } from '@react-three/drei';
import * as THREE from 'three';

/**
 * Procedural low-poly rover built from Three.js primitives.
 * Auto-rotates slowly and has animated wheels.
 */
function Rover() {
  const groupRef = useRef();
  const wheelsRef = useRef([]);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.003;
      // Gentle floating motion
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.05;
    }
    // Spin wheels
    wheelsRef.current.forEach((wheel) => {
      if (wheel) wheel.rotation.x += 0.02;
    });
  });

  const bodyMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#1a2744',
        metalness: 0.7,
        roughness: 0.3,
      }),
    []
  );

  const accentMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#3b82f6',
        metalness: 0.8,
        roughness: 0.2,
        emissive: '#1d4ed8',
        emissiveIntensity: 0.3,
      }),
    []
  );

  const wheelMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#0f172a',
        metalness: 0.6,
        roughness: 0.5,
      }),
    []
  );

  const antennaMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#64748b',
        metalness: 0.9,
        roughness: 0.1,
      }),
    []
  );

  const lensMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: '#22d3ee',
        metalness: 1.0,
        roughness: 0.0,
        emissive: '#06b6d4',
        emissiveIntensity: 0.8,
      }),
    []
  );

  const wheelPositions = [
    [-0.85, -0.45, 0.6],
    [0.85, -0.45, 0.6],
    [-0.85, -0.45, -0.6],
    [0.85, -0.45, -0.6],
    [-0.85, -0.45, 0],
    [0.85, -0.45, 0],
  ];

  return (
    <group ref={groupRef} position={[0, 0, 0]} scale={1.2}>
      {/* Main body */}
      <mesh material={bodyMaterial} position={[0, 0, 0]}>
        <boxGeometry args={[1.6, 0.35, 1.2]} />
      </mesh>

      {/* Top deck */}
      <mesh material={bodyMaterial} position={[0, 0.25, -0.1]}>
        <boxGeometry args={[1.2, 0.2, 0.8]} />
      </mesh>

      {/* Accent stripe */}
      <mesh material={accentMaterial} position={[0, 0.18, 0.01]}>
        <boxGeometry args={[1.62, 0.02, 1.22]} />
      </mesh>

      {/* Solar panel */}
      <mesh material={accentMaterial} position={[0, 0.37, -0.1]}>
        <boxGeometry args={[1.1, 0.02, 0.7]} />
      </mesh>

      {/* Camera head */}
      <mesh material={bodyMaterial} position={[0, 0.55, 0.2]}>
        <boxGeometry args={[0.3, 0.25, 0.25]} />
      </mesh>

      {/* Camera lens */}
      <mesh material={lensMaterial} position={[0, 0.55, 0.34]}>
        <cylinderGeometry args={[0.08, 0.08, 0.04, 16]} />
        <primitive object={new THREE.Euler(Math.PI / 2, 0, 0)} attach="rotation" />
      </mesh>

      {/* Neck */}
      <mesh material={antennaMaterial} position={[0, 0.42, 0.2]}>
        <cylinderGeometry args={[0.04, 0.04, 0.15, 8]} />
      </mesh>

      {/* Antenna */}
      <mesh material={antennaMaterial} position={[-0.4, 0.55, -0.2]}>
        <cylinderGeometry args={[0.015, 0.015, 0.4, 6]} />
      </mesh>

      {/* Antenna tip */}
      <mesh material={lensMaterial} position={[-0.4, 0.76, -0.2]}>
        <sphereGeometry args={[0.035, 12, 12]} />
      </mesh>

      {/* Wheels with suspension arms */}
      {wheelPositions.map((pos, idx) => (
        <group key={idx} position={pos}>
          {/* Suspension arm */}
          <mesh material={antennaMaterial} position={[pos[0] > 0 ? -0.2 : 0.2, 0.15, 0]}>
            <boxGeometry args={[0.4, 0.05, 0.05]} />
          </mesh>
          {/* Wheel */}
          <mesh
            ref={(el) => (wheelsRef.current[idx] = el)}
            material={wheelMaterial}
            rotation={[0, 0, Math.PI / 2]}
          >
            <cylinderGeometry args={[0.18, 0.18, 0.12, 16]} />
          </mesh>
          {/* Wheel hub */}
          <mesh material={accentMaterial} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.06, 0.06, 0.14, 8]} />
          </mesh>
        </group>
      ))}

      {/* Rear instruments */}
      <mesh material={bodyMaterial} position={[0.5, 0.3, -0.35]}>
        <boxGeometry args={[0.15, 0.15, 0.15]} />
      </mesh>
      <mesh material={bodyMaterial} position={[-0.5, 0.3, -0.35]}>
        <boxGeometry args={[0.15, 0.15, 0.15]} />
      </mesh>
    </group>
  );
}

/**
 * Grid floor with subtle glow effect
 */
function GridFloor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.75, 0]}>
      <planeGeometry args={[40, 40, 40, 40]} />
      <meshStandardMaterial
        color="#0a0f1e"
        wireframe={true}
        transparent
        opacity={0.15}
      />
    </mesh>
  );
}

/**
 * Floating data particles around the rover
 */
function DataParticles() {
  const particlesRef = useRef();
  const count = 60;

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 8;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 4 + 1;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.02;
      const posArr = particlesRef.current.geometry.attributes.position.array;
      for (let i = 0; i < count; i++) {
        posArr[i * 3 + 1] += Math.sin(state.clock.elapsedTime + i) * 0.001;
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        color="#3b82f6"
        size={0.04}
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
}

/**
 * RoverScene — Main 3D canvas component.
 * Renders the rover, stars, grid floor, and data particles.
 */
export default function RoverScene() {
  return (
    <Canvas
      camera={{ position: [3, 2, 4], fov: 45 }}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
      }}
      gl={{ antialias: true, alpha: true }}
      dpr={[1, 2]}
    >
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <directionalLight position={[5, 5, 5]} intensity={0.8} color="#e2e8f0" />
      <directionalLight position={[-3, 3, -3]} intensity={0.3} color="#3b82f6" />
      <pointLight position={[0, 2, 0]} intensity={0.5} color="#22d3ee" distance={8} />

      {/* Stars background */}
      <Stars
        radius={50}
        depth={50}
        count={2000}
        factor={3}
        saturation={0.1}
        fade
        speed={0.5}
      />

      {/* Rover */}
      <Float speed={0.8} rotationIntensity={0.05} floatIntensity={0.3}>
        <Rover />
      </Float>

      {/* Environment */}
      <GridFloor />
      <DataParticles />

      {/* Controls */}
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.3}
        maxPolarAngle={Math.PI / 2.2}
        minPolarAngle={Math.PI / 4}
      />
    </Canvas>
  );
}
