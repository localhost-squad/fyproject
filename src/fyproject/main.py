# src/fyproject/main.py
import needle
import json

@needle.tool
def get_weather(city: str) -> dict:
    """Get the current weather for a city.
    
    Args:
        city: The name of the city to get weather for.
    """
    return {"city": city, "temp_c": 27, "sky": "clear"}

# Initialize agent (C engine defaults to temperature=0.0 for deterministic greedy decoding)
agent = needle.Needle(tools=[get_weather])

def main() -> None:
    # Clear the KV cache to ensure a pristine, deterministic starting state
    agent.reset()
    
    prompt = "What's the weather like in Lagos right now?"
    print(f"User: {prompt}\n")
    
    response = agent.run(prompt)
    
    if response.get("success") and response.get("results"):
        result = response["results"][0]
        confidence = response.get("confidence", 0.0)
        
        print("---raw output---")
        print(json.dumps(response, indent=2))
    else:
        print("--- Raw Response ---")
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()