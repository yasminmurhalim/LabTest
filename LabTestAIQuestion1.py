#Lab Test AI Question 1

import numpy as np
import pandas as pd
import streamlit as st

POPULATIONSIZE = 300
CHROMOSOMELENGTH = 80
GENERATIONS = 50
FITNESSONES = 40       
MAXFITNESS = 80         

PC = 0.9          
PM = 0.01         
ELITE_COUNT = 2
TOUR_SIZE = 3
RANDOM_SEED = 42

rng = np.random.default_rng(RANDOM_SEED)


def evaluate(chromosome):
    """
    Target exactly 40 ones. 
    Formula: Max Fitness - |Current Ones - Target Ones|
    If valid (40 ones), score is 80. If all 0s or all 1s, score drops.
    """
    current_ones = chromosome.sum()
    # Calculate distance from target (40)
    distance = abs(current_ones - TARGET_ONES)
    # Higher fitness is better, max is 80
    return MAXFITNESS- distance

def create_population():
    return rng.integers(0, 2, (POPULATIONSIZE,GENERATIONS))

def select_parent(population, scores):
    candidates = rng.choice(len(population), TOUR_SIZE, replace=False)
    best_idx = candidates[np.argmax(scores[candidates])]
    return population[best_idx]

def recombine(parent_a, parent_b):
    if rng.random() < PC:
        cut = rng.integers(1, GENERATIONS)
        child1 = np.hstack((parent_a[:cut], parent_b[cut:]))
        child2 = np.hstack((parent_b[:cut], parent_a[cut:]))
        return child1, child2
    return parent_a.copy(), parent_b.copy()

def flip_bits(individual):
    mutation_mask = rng.random(GENERATIONS) < PM
    individual[mutation_mask] ^= 1
    return individual

def genetic_algorithm():
    population = create_population()
    log = []

    for gen in range(1, GENERATIONS + 1):
        fitness_scores = np.array([evaluate(ind) for ind in population])

        log.append({
            "Generation": gen,
            "Best Fitness": fitness_scores.max(),
            "Average Fitness": fitness_scores.mean()
        })

        # Preserve elites
        elite_indices = np.argsort(fitness_scores)[-ELITE_COUNT:]
        elites = population[elite_indices]

        offspring = []

        while len(offspring) < POPULATIONSIZE - ELITE_COUNT:
            p1 = select_parent(population, fitness_scores)
            p2 = select_parent(population, fitness_scores)

            c1, c2 = recombine(p1, p2)
            offspring.append(flip_bits(c1))

            if len(offspring) < POPULATIONSIZE - ELITE_COUNT:
                offspring.append(flip_bits(c2))

        population = np.vstack((offspring, elites))

    final_scores = np.array([evaluate(ind) for ind in population])
    best_idx = np.argmax(final_scores)

    return pd.DataFrame(log), population[best_idx], final_scores[best_idx]

# streamlit ui
st.set_page_config(page_title="Lab Test AI 1(b)", layout="centered")

st.markdown("""
    <style>
        .title {
            color: #4CAF50;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">GA Bit Pattern Generator (Target: 40 Ones)</p>', unsafe_allow_html=True)

st.caption("Solves Q1(b): Generate a bit pattern with 80 bits where fitness peaks at 40 ones.")

# Use a different section layout for controls
with st.expander("Adjust GA Settings", expanded=True):
    # Defaults set to Exam Requirements 
    col1, col2 = st.columns(2)
    with col1:
        POP_SIZE = st.number_input("Population Size", value=300)
        GENE_LENGTH = st.number_input("Chromosome Length", value=80)
        N_GENERATIONS = st.number_input("Generations", value=50)
    with col2:
        PC = st.slider("Crossover Probability", 0.0, 1.0, PC)
        PM = st.slider("Mutation Probability", 0.0, 1.0, PM)
        TARGET_ONES = st.number_input("Target Ones", value=40)

# Button to run the algorithm
if st.button("Run Genetic Algorithm"):
    history_df, best_individual, best_score = genetic_algorithm()

    st.subheader("Fitness Progress")
    st.line_chart(history_df.set_index("Generation"))

    st.subheader("Best Solution Found")
    
    # Calculate actual ones in the result for verification
    actual_ones = best_individual.sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Best Fitness (Max 80)", best_score)
    col2.metric("Bit Count (Target 40)", actual_ones)

    st.text("Binary Pattern:")
    st.code("".join(map(str, best_individual)))

    if actual_ones == TARGET_ONES:
        st.success(f"Success! The algorithm found a pattern with exactly {TARGET_ONES} ones.")
    else:
        st.warning(f"Result has {actual_ones} ones. Try increasing generations or population.")