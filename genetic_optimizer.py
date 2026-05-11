import random
import json
import os
import time
import subprocess


POPULATION_SIZE = 100     
GENERATIONS = 200         
MUTATION_RATE = 0.20     
MUTATION_IMPACT = 0.15   

BASE_GENOME = {
    "dec_base": 18.094226829212957,
    "dec_factor": 0.08617347616476877,
    "safety_margin_base": 3.372169755153338,
    "safety_margin_factor": 0.047120039165800834,
    "steer_apex_width": 1.4187496994536632,
    "accel_slip_base": 1.029694098013211,
    "accel_slip_fast": 4.391155211438576,
    "trail_braking": 0.16796919204678695
}

TORCS_EXE_PATH = r"D:\torcs\wtorcs.exe"
BOT_SCRIPT_NAME = "torcs_client.py"

def create_random_genome(base):
    new_genome = {}
    for key, value in base.items():
        change = random.uniform(-MUTATION_IMPACT, MUTATION_IMPACT)
        new_genome[key] = value * (1.0 + change)
    return new_genome

def mutate(genome):
    for key in genome:
        if random.random() < MUTATION_RATE:
            change = random.uniform(-MUTATION_IMPACT, MUTATION_IMPACT)
            genome[key] = genome[key] * (1.0 + change)
    return genome

def crossover(parent1, parent2):
    child = {}
    for key in parent1:
        child[key] = parent1[key] if random.random() < 0.5 else parent2[key]
    return child

def evaluate_fitness(genome, bot_id, gen_id):
    print(f"\n  [Pokolenie {gen_id} | Bot {bot_id}/{POPULATION_SIZE}] Testowanie...")
    
    with open("genome.json", "w") as f:
        json.dump(genome, f, indent=4)
        
    if os.path.exists("result.txt"):
        os.remove("result.txt")
        
    print("    -> Uruchamiam TORCS w tle (Fast-Forward Mode)...")
    torcs_process = subprocess.Popen([TORCS_EXE_PATH, "-r", r"D:\torcs\config\raceman\quickrace.xml"], cwd=r"D:\torcs", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(4) 
    
    try:
        print(f"    -> Agent AI podłączony. Trwa wyścig...")
        subprocess.run(["python", BOT_SCRIPT_NAME], timeout=120, stdout=subprocess.DEVNULL) 
    except subprocess.TimeoutExpired:
        print("    -> PRZEKROCZONO CZAS. Bot utknął.")
    finally:
        subprocess.run(["taskkill", "/F", "/IM", "wtorcs.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5) 

    if os.path.exists("result.txt"):
        try:
            with open("result.txt", "r") as f:
                time_result = float(f.read().strip())
                if time_result >= 9999.0:
                    print("    [!] Wynik: WYPADEK (Odrzucono)")
                else:
                    print(f"    [+] Wynik: {time_result:.3f}s")
                return time_result
        except ValueError:
            return 9999.0
    else:
        return 9999.0

def main():
    print("======================================================")
    print(" INICJALIZACJA: IBM AI Racing League - Ewolucja Bota")
    print(" Tryb Cichy - TORCS działa w tle dla maksymalnej prędkości")
    print("======================================================\n")
    
    subprocess.run(["taskkill", "/F", "/IM", "wtorcs.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    population = [create_random_genome(BASE_GENOME) for _ in range(POPULATION_SIZE)]
    
    best_all_time_score = float('inf')
    best_all_time_genome = None

    for gen in range(1, GENERATIONS + 1):
        print(f"\n================ POKOLENIE {gen}/{GENERATIONS} ================")
        
        scored_population = []
        for i, genome in enumerate(population):
            score = evaluate_fitness(genome, i + 1, gen)
            scored_population.append((score, genome))
            
        scored_population.sort(key=lambda x: x[0])
        best_gen_score, best_gen_genome = scored_population[0]
        
        if best_gen_score < best_all_time_score and best_gen_score < 9999.0:
            best_all_time_score = best_gen_score
            best_all_time_genome = best_gen_genome
            print(f"\n>>> NOWY REKORD ABSOLUTNY: {best_all_time_score:.3f}s! <<<")
            with open("champion_genome.json", "w") as f:
                json.dump(best_all_time_genome, f, indent=4)
        else:
            print(f"\n>>> Najlepszy czas w tej generacji: {best_gen_score:.3f}s (Rekord: {best_all_time_score:.3f}s)")

        elite_count = max(2, int(POPULATION_SIZE * 0.2))
        next_generation = [g for score, g in scored_population[:elite_count]]

        while len(next_generation) < POPULATION_SIZE:
            top_half = scored_population[:int(POPULATION_SIZE/2)]
            parents = random.choices(top_half, k=2)
            child = mutate(crossover(parents[0][1], parents[1][1]))
            next_generation.append(child)
            
        population = next_generation

    print("\n================ EWOLUCJA ZAKOŃCZONA ================")
    print(f" Rekordzista wykręcił czas: {best_all_time_score:.3f}s")
    print(" Genom zapisany w 'champion_genome.json'.")

if __name__ == "__main__":
    main()