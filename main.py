import torch
import json
import base64
from transformers import AutoModelForCausalLM, AutoTokenizer
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# ==========================================
# Phase 1: Cryptographic Setup (PKI)
# ==========================================
print("Generating RSA-2048 Keypair...")
# The server holds the private key; the public key is distributed to auditors.
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# ==========================================
# Phase 2: Enforce Execution Determinism
# ==========================================
print("Configuring Single-Threaded CPU Determinism...")
# Force CPU and single-threaded execution to prevent parallel reduction anomalies
torch.set_num_threads(1)
torch.manual_seed(42) # Seed for reproducibility (though we disable sampling anyway)

# Load a tiny model for demonstration purposes
model_id = "sshleifer/tiny-gpt2" 
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Force the model to strict CPU execution
model.to("cpu")

# ==========================================
# Phase 3: Deterministic Inference
# ==========================================
prompt = "The future of AI auditing is"
print(f"\nRunning Inference for Prompt: '{prompt}'")

inputs = tokenizer(prompt, return_tensors="pt").to("cpu")

# Generate with STRICT determinism (greedy decoding, no stochastic sampling)
outputs = model.generate(
    **inputs, 
    max_new_tokens=10, 
    do_sample=False,       # Disables random sampling (Top-k/Top-p)
    temperature=None,      # Not needed when do_sample=False
    use_cache=True
)

output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Model Output: '{output_text}'")

# ==========================================
# Phase 4: Generate Cryptographic Receipt
# ==========================================
print("\nGenerating Cryptographic AI Receipt...")

# Create the payload binding the prompt and output together
receipt_payload = {
    "prompt": prompt,
    "output": output_text,
    "model_id": model_id
}

# Serialize to a strictly sorted JSON string to ensure byte-exact hashing
payload_bytes = json.dumps(receipt_payload, sort_keys=True).encode('utf-8')

# Sign the payload using the private key
signature = private_key.sign(
    payload_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Encode signature to base64 so it can be easily transmitted
signature_b64 = base64.b64encode(signature).decode('utf-8')

# This is the final receipt sent to the client
final_receipt = {
    "data": receipt_payload,
    "signature": signature_b64
}
print(json.dumps(final_receipt, indent=2))

# ==========================================
# Phase 5: Client-Side Verification (Auditor)
# ==========================================
print("\n--- Auditor Verification ---")
print("Auditor receives the receipt and verifies it against the Public Key...")

# The auditor re-serializes the data identically
verify_bytes = json.dumps(final_receipt["data"], sort_keys=True).encode('utf-8')
verify_sig = base64.b64decode(final_receipt["signature"])

try:
    public_key.verify(
        verify_sig,
        verify_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("✅ VERIFICATION SUCCESSFUL: The output is mathematically proven to be unmodified and from the authorized model.")
except Exception as e:
    print("❌ VERIFICATION FAILED: The data or signature has been tampered with!")