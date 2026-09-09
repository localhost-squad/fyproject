# src/fyproject/test_determinism.py
import json
import hashlib
from fyproject.main import agent

def test_determinism() -> None:
    prompt = "What's the weather like in Lagos right now?"
    hashes = []
    
    for i in range(5):
        agent.reset() # Clear state
        response = agent.run(prompt)
        
        # EXTRACT EVERY SINGLE LOGICAL/AI PARAMETER POSSIBLE
        # We explicitly exclude floating-point metrics (tps, ram, confidence) 
        # because SIMD math causes micro-fluctuations in decimals (e.g., 0.7011 vs 0.7025)
        semantic_response = {
            "type": response.get("type"),
            "success": response.get("success"),
            "error": response.get("error"),
            "error_code": response.get("error_code"),
            "reason": response.get("reason"),
            "function_calls": response.get("function_calls"),
            "reasoning": response.get("reasoning"),
            "results": response.get("results")
        }
        
        # Convert to a deterministic JSON string (sort_keys ensures consistent ordering)
        json_str = json.dumps(semantic_response, sort_keys=True)
        
        # Calculate the SHA-256 hash of the output
        hash_val = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        hashes.append(hash_val)
        print(f"Run {i+1}: {hash_val}")
        
    # Check if all hashes are identical
    if len(set(hashes)) == 1:
        print("\n✅ SUCCESS: All logical AI parameters are 100% functionally deterministic.")
    else:
        print("\n❌ FAILURE: Logical output varied between runs.")
        print("Differing output:", semantic_response)

if __name__ == "__main__":
    test_determinism()