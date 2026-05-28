import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  Environment,
  Float,
  MeshDistortMaterial,
  OrbitControls,
  Sparkles,
} from "@react-three/drei";

import { BrainCircuit, Cpu, Radio, ScanLine } from "lucide-react";

function AnimatedOrb() {
  const orbRef = useRef();
  const ringRef = useRef();
  const innerRingRef = useRef();

  useFrame((state) => {
    const time = state.clock.elapsedTime;

    if (orbRef.current) {
      orbRef.current.rotation.x = time * 0.45;
      orbRef.current.rotation.y = time * 0.65;
      orbRef.current.position.y = Math.sin(time * 1.5) * 0.08;
    }

    if (ringRef.current) {
      ringRef.current.rotation.z = time * 0.8;
      ringRef.current.rotation.x = Math.sin(time * 0.6) * 0.35;
    }

    if (innerRingRef.current) {
      innerRingRef.current.rotation.z = -time * 1.15;
      innerRingRef.current.rotation.y = Math.cos(time * 0.7) * 0.35;
    }
  });

  return (
    <group>
      <Float speed={2.2} rotationIntensity={0.45} floatIntensity={0.5}>
        <mesh ref={orbRef}>
          <sphereGeometry args={[1.15, 96, 96]} />
          <MeshDistortMaterial
            color="#60a5fa"
            emissive="#1d4ed8"
            emissiveIntensity={0.55}
            roughness={0.28}
            metalness={0.62}
            distort={0.35}
            speed={2}
            clearcoat={1}
            clearcoatRoughness={0.18}
          />
        </mesh>

        <mesh ref={ringRef} rotation={[Math.PI / 2.5, 0, 0]}>
          <torusGeometry args={[1.72, 0.025, 12, 160]} />
          <meshStandardMaterial
            color="#93c5fd"
            emissive="#3b82f6"
            emissiveIntensity={1.1}
            transparent
            opacity={0.78}
          />
        </mesh>

        <mesh ref={innerRingRef} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.38, 0.018, 12, 140]} />
          <meshStandardMaterial
            color="#22d3ee"
            emissive="#06b6d4"
            emissiveIntensity={1.1}
            transparent
            opacity={0.72}
          />
        </mesh>

        <mesh position={[0, 0, 0]}>
          <icosahedronGeometry args={[0.62, 1]} />
          <meshStandardMaterial
            color="#dbeafe"
            emissive="#60a5fa"
            emissiveIntensity={0.7}
            roughness={0.18}
            metalness={0.8}
            transparent
            opacity={0.92}
          />
        </mesh>
      </Float>

      <Sparkles
        count={70}
        scale={[5.5, 3.2, 3.2]}
        size={3.5}
        speed={0.55}
        color="#93c5fd"
        opacity={0.55}
      />
    </group>
  );
}

const INITIAL_POINTS = (() => {
  const temp = [];
  for (let i = 0; i < 130; i++) {
    temp.push([
      (Math.random() - 0.5) * 8,
      (Math.random() - 0.5) * 5,
      (Math.random() - 0.5) * 4,
    ]);
  }
  return temp;
})();

function ParticleGrid() {
  const points = INITIAL_POINTS;

  return (
    <group>
      {points.map((position, index) => (
        <mesh key={index} position={position}>
          <sphereGeometry args={[0.012, 8, 8]} />
          <meshBasicMaterial
            color={index % 2 === 0 ? "#60a5fa" : "#22d3ee"}
            transparent
            opacity={0.45}
          />
        </mesh>
      ))}
    </group>
  );
}

function AssistantScene() {
  return (
    <Canvas camera={{ position: [0, 0, 5.8], fov: 42 }}>
      <ambientLight intensity={1.2} />
      <directionalLight position={[4, 5, 6]} intensity={2.2} />
      <pointLight position={[-3, -2, 4]} intensity={2} color="#3b82f6" />
      <pointLight position={[3, 2, 3]} intensity={1.5} color="#22d3ee" />

      <ParticleGrid />
      <AnimatedOrb />

      <Environment preset="city" />
      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.75}
      />
    </Canvas>
  );
}

function StatusItem({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/15 bg-white/10 px-3 py-2 backdrop-blur-xl">
      <div className="grid h-8 w-8 place-items-center rounded-full bg-white/10 text-cyan-200">
        <Icon className="h-4 w-4" />
      </div>

      <div>
        <p className="text-[10px] font-bold uppercase tracking-wide text-white/45">
          {label}
        </p>
        <p className="text-xs font-black text-white">{value}</p>
      </div>
    </div>
  );
}

export default function AiAssistantAnimation() {
  return (
    <section className="panel relative h-full min-h-[360px] overflow-hidden rounded-[30px] p-5">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_35%,rgba(59,130,246,0.28),transparent_35%),radial-gradient(circle_at_80%_90%,rgba(34,211,238,0.22),transparent_38%)]" />

      <div className="relative z-10 flex h-full flex-col">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-full bg-white/15 text-cyan-200 shadow-lg">
              <BrainCircuit className="h-5 w-5" />
            </div>

            <div>
              <h2 className="text-base font-black tracking-[-0.04em] text-white">
                AI Assistant Core
              </h2>
              <p className="text-[11px] font-medium text-white/45">
                Processing YOLO, LiDAR and rover telemetry
              </p>
            </div>
          </div>

          <div className="rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-[10px] font-black text-emerald-200">
            ACTIVE
          </div>
        </div>

        <div className="relative min-h-0 flex-1 overflow-hidden rounded-[26px] border border-white/15 bg-black/30">
          <AssistantScene />

          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-black/55 to-transparent" />

          <div className="absolute bottom-5 left-5 right-5 text-center">
            <h3 className="text-xl font-black tracking-[-0.05em] text-white">
              SAMP ROBO AI is analyzing the environment
            </h3>
            <p className="mx-auto mt-2 max-w-[560px] text-xs leading-relaxed text-white/50">
              Real-time object detection, LiDAR scanning and telemetry fusion
              are being monitored for autonomous movement decisions.
            </p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-3">
          <StatusItem icon={ScanLine} label="LiDAR" value="Scanning" />
          <StatusItem icon={Radio} label="YOLO Feed" value="Active" />
          <StatusItem icon={Cpu} label="AI Core" value="Stable" />
        </div>
      </div>
    </section>
  );
}