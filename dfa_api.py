from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import json

app = Flask(__name__)

CORS(app)

def read_dfa_from_json(dfa_data):
    """
    Read DFA data from the JSON received.
    """
    # Check for required fields and ensure final is a list
    if 'final' not in dfa_data:
        raise ValueError("'final' key is missing in the input data")

    states = dfa_data['states']
    num_states = len(states)
    start_state = dfa_data['start']
    final_states = set(dfa_data['final']) if isinstance(dfa_data['final'], list) else set()
    alphabet = set(dfa_data['alphabet'])
    transitions = dfa_data['transitions']
    
    return {
        "states": set(states),
        "start": start_state,
        "final": final_states,
        "alphabet": alphabet,
        "transitions": transitions,
    }


def remove_unreachable_states(dfa):
    reachable = set()
    queue = {dfa["start"]}  # Using a set for better performance

    while queue:
        current = queue.pop()  # Pop from the set for efficiency
        reachable.add(current)
        queue.update(
            state for state in dfa["transitions"].get(current, {}).values()
            if state not in reachable
        )

    new_transitions = {
        state: {sym: dest for sym, dest in dfa["transitions"].get(state, {}).items() if dest in reachable}
        for state in reachable
    }

    return {
        "states": reachable,
        "alphabet": dfa["alphabet"],
        "transitions": new_transitions,
        "start": dfa["start"],
        "final": dfa["final"] & reachable,
    }

def remove_dead_states(dfa):
    productive = set(dfa["final"])  # Start with final states
    reverse_transitions = {state: set() for state in dfa["states"]}

    # Build reverse transition map
    for state, transitions in dfa["transitions"].items():
        for symbol, dest in transitions.items():
            reverse_transitions[dest].add(state)

    # Work backward from productive states
    queue = list(productive)
    while queue:
        state = queue.pop()
        for prev in reverse_transitions[state]:
            if prev not in productive:
                productive.add(prev)
                queue.append(prev)

    new_transitions = {
        state: {sym: dest for sym, dest in dfa["transitions"].get(state, {}).items() if dest in productive}
        for state in productive
    }

    return {
        "states": productive,
        "alphabet": dfa["alphabet"],
        "transitions": new_transitions,
        "start": dfa["start"] if dfa["start"] in productive else None,
        "final": dfa["final"] & productive,
    }

def hopcroft_minimization(dfa):
    # Clean the DFA.
    dfa_clean = remove_unreachable_states(dfa)
    dfa_clean = remove_dead_states(dfa_clean)
    
    states = dfa_clean["states"]
    alphabet = dfa_clean["alphabet"]
    transitions = {}
    for state in states:
        for sym, dest in dfa_clean["transitions"].get(state, {}).items():
            transitions[(state, sym)] = dest
    start = dfa_clean["start"]
    accepting = set(dfa_clean["final"])
    
    F = accepting
    non_F = states - F
    P = []
    if F:
        P.append(F)
    if non_F:
        P.append(non_F)
    
    W = []
    if F:
        W.append(F)
    if non_F:
        W.append(non_F)
    
    while W:
        A = W.pop()
        for c in alphabet:
            X = {s for s in states if (s, c) in transitions and transitions[(s, c)] in A}
            for Y in P.copy():
                intersection = Y & X
                difference = Y - X
                if intersection and difference:
                    P.remove(Y)
                    P.append(intersection)
                    P.append(difference)
                    if Y in W:
                        W.remove(Y)
                        W.append(intersection)
                        W.append(difference)
                    else:
                        if len(intersection) <= len(difference):
                            W.append(intersection)
                        else:
                            W.append(difference)
    
    new_states = {frozenset(block) for block in P}
    state_map = {}
    for block in new_states:
        for s in block:
            state_map[s] = block
    new_start = state_map[start]
    new_final = {block for block in new_states if block & accepting}
    new_transitions = {}
    for block in new_states:
        representative = next(iter(block))
        for c in alphabet:
            if (representative, c) in transitions:
                target = transitions[(representative, c)]
                new_transitions[(block, c)] = state_map[target]
    
    # Convert to string representation (concatenating state names)
    def block_name(block):
        return "".join(sorted(block, key=lambda x: int(x) if x.isdigit() else x))
    
    dfa_min = {}
    for (block, sym), target in new_transitions.items():
        block_str = block_name(block)
        target_str = block_name(target)
        if block_str not in dfa_min:
            dfa_min[block_str] = {}
        dfa_min[block_str][sym] = target_str
    
    return {
        "states": [block_name(b) for b in new_states],  # Convert set to list
        "alphabet": list(alphabet),  # Convert set to list
        "transitions": dfa_min,
        "start": block_name(new_start),
        "final": [block_name(b) for b in new_final],  # Convert set to list
    }


@app.route('/minimize', methods=['POST'])
def minimize_dfa():
    try:
        # Get DFA data from the request
        dfa_data = request.get_json()
        
        # Process the DFA (minimization steps)
        dfa = read_dfa_from_json(dfa_data)
        dfa_minimized = hopcroft_minimization(dfa)
        
        # Return the minimized DFA as a JSON response
        return jsonify(dfa_minimized)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
