def estimate_calls(pairs, models, methods, repetitions, orderings=2):
    return pairs * models * methods * repetitions * orderings

if __name__ == "__main__":
    print("Smoke test (3 pairs, 1 model, 3 methods, 1 rep, 2 orderings):", estimate_calls(3, 1, 3, 1, 2), "API calls")
    print("Full run max (15 pairs, 2 models, 3 methods, 3 reps, 2 orderings):", estimate_calls(15, 2, 3, 3, 2), "API calls")

