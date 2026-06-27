# IBM-Racing
🏎️ IBM AI Racing League: Project Corkscrew

Team: PŚK RACING TEAM

University: Kielce University Of Technology

Fastest Lap Time: 1:22:15 ⏱️

Welcome to our official repository for the IBM AI Racing League. This project represents our journey from a standard reactive driving bot to a highly optimized, evolutionary machine learning pipeline capable of pushing a 600kg Open Wheel race car to its absolute limits on the Corkscrew circuit.

🧠 AI Architecture

Our project is divided into two distinct engineering phases: the physical execution layer and the evolutionary learning layer.

1. The Reactive Base Model

Before applying machine learning, we built a robust foundation for car control:

Custom Traction Control System (TCS): Calculates real-time wheel slip differential between the front and rear axles to dynamically modulate throttle, preventing spin-outs on the RWD layout.

Proportional-Derivative (PD) Steering: Smoothly targets the apex while minimizing oscillations.

Trail Braking Logic: Dynamically reduces braking force based on steering intent, allowing the car to maintain cornering rotation without locking the tires.

2. The Metaheuristic Genetic Optimizer

Instead of relying on human intuition to tune physics variables, we built a Genetic Algorithm (GA) in Python to train our driver.

We parameterized 8 critical vectors (e.g., deceleration limits, slip tolerance, safety margins, apex width) into a Genome.

We initialized a population of 100 virtual drivers and automated the TORCS simulator to run 200 generations (20,000 headless races).

The Fitness Function rewarded absolute lap speed while applying severe penalties for track collisions.

Through tournament selection and mutation, the algorithm discovered extreme late-braking exploits and grip limits that a human could never manually calculate, achieving our final 1:22:15 lap time.

⚠️ CRITICAL: Hardware Overfitting & FPS Calibration

IMPORTANT NOTE FOR JUDGES AND TESTERS:
To reproduce our 1:22:15 lap time, the simulator environment must be locked to 75 FPS.

During the evolution process, we encountered a classic reinforcement learning phenomenon known as Hardware Overfitting (or Frame Rate Dependent Physics).

Our champion genome was evolved on a machine rendering TORCS at exactly 75 frames per second.

Consequently, the AI's steering control loop frequencies and braking latencies became mathematically entangled with this specific Delta T (tick rate).

Running this bot on an unlocked framerate (e.g., 300-400 FPS on a modern laptop) will cause the PD controller to overcorrect (executing commands 5x faster than intended), resulting in severe aerodynamic instability and track departure.

How to replicate our environment:
Please force a frame rate limit of 75 FPS for wtorcs.exe via your GPU driver settings (e.g., NVIDIA Control Panel -> Max Frame Rate) or enable V-Sync on a 75Hz display before executing the script.

📂 Repository Structure (AI Core Only)

Please Note: This repository contains only our proprietary AI driver logic and the evolutionary training framework. It does not include the standard IBM TORCS UDP client boilerplate.

racing_bot.py - The core AI driving logic. This script contains our TCS, PD controller, and genome parser. (To be plugged into the standard IBM client's driving loop).

genetic_optimizer.py - The AI Trainer. A headless script that automates the TORCS executable, spawns populations, evaluates fitness, and handles crossover/mutation math.

champion_genome.json - The final, evolved set of physics parameters that achieved the 1:22:15 lap time.

🚀 How to Run

1. Watch the Champion Race

To witness the 1:22:15 lap:

Integrate racing_bot.py into your standard TORCS client loop.

Ensure your TORCS environment is locked to 75 FPS.

Verify that champion_genome.json is located in the working directory (rename to genome.json if required by the script).

Start the TORCS server (wtorcs.exe) and run the client.

2. Run the Genetic Optimizer

To train a new model from scratch:

Ensure the paths inside genetic_optimizer.py match your local TORCS installation.

Execute the trainer:

python genetic_optimizer.py


The script will automatically launch TORCS, evaluate generations, and output a new optimized genome JSON file.

🛠️ IBM Ecosystem Integration

This project was built with the invaluable support of the IBM ecosystem.

All team members completed the mandatory IBM SkillsBuild credentials.

We actively utilized IBM Granite models during our development cycle to optimize our Python automation wrappers, refine our genetic crossover mathematical logic, and troubleshoot complex telemetry data parsing.

Designed for the IBM AI Racing League.