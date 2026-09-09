# src/fyproject/test_tpm.py
import json
import hashlib
import subprocess
import os
import tempfile
import base64
from fyproject.main import agent

def get_ai_payload() -> dict:
    """Generates the deterministic AI output."""
    agent.reset()
    response = agent.run("What's the weather like in Lagos right now?")
    
    # Extract only semantic data (exclude floating-point hardware metrics)
    semantic_data = {
        "type": response.get("type"),
        "success": response.get("success"),
        "reasoning": response.get("reasoning"),
        "results": response.get("results")
    }
    return semantic_data

def hash_payload(data: dict) -> bytes:
    """Hashes the semantic payload using SHA-256."""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode('utf-8')).digest()

def tpm_sign_and_verify(hash_bytes: bytes) -> tuple[bytes, bytes, bool]:
    """Signs the hash with TPM 2.0 in an isolated temp directory and verifies it."""
    # MAGIC: This creates a temporary folder that is automatically deleted 
    # when the block ends. No files left in your project directory!
    with tempfile.TemporaryDirectory() as tmpdir:
        # Define paths INSIDE the temp folder
        primary_ctx = os.path.join(tmpdir, "primary.ctx")
        key_pub = os.path.join(tmpdir, "key.pub")
        key_priv = os.path.join(tmpdir, "key.priv")
        key_ctx = os.path.join(tmpdir, "key.ctx")
        data_hash = os.path.join(tmpdir, "data.hash")
        sig_file = os.path.join(tmpdir, "signature.sig")
        
        # 1. Write hash to temp file
        with open(data_hash, "wb") as f:
            f.write(hash_bytes)
            
        # 2. Create Primary Key (inside temp dir)
        subprocess.run(["tpm2_createprimary", "-C", "o", "-c", primary_ctx], check=True, capture_output=True)
        
        # 3. Create Signing Key (inside temp dir)
        subprocess.run(["tpm2_create", "-G", "rsa", "-u", key_pub, "-r", key_priv, "-C", primary_ctx], check=True, capture_output=True)
        
        # 4. Load Key (inside temp dir)
        subprocess.run(["tpm2_load", "-C", primary_ctx, "-u", key_pub, "-r", key_priv, "-c", key_ctx], check=True, capture_output=True)
        
        # 5. Sign the hash
        subprocess.run(["tpm2_sign", "-c", key_ctx, "-o", sig_file, data_hash], check=True, capture_output=True)
        
        # 6. Read the binary results back into Python memory
        with open(key_pub, "rb") as f:
            pub_key_bytes = f.read()
        with open(sig_file, "rb") as f:
            sig_bytes = f.read()
            
        # 7. Verify the signature
        verify_hash = os.path.join(tmpdir, "verify.hash")
        with open(verify_hash, "wb") as f:
            f.write(hash_bytes)
            
        result = subprocess.run(
            ["tpm2_verifysignature", "-c", key_ctx, "-g", "sha256", "-m", verify_hash, "-s", sig_file],
            capture_output=True
        )
        
        return pub_key_bytes, sig_bytes, result.returncode == 0

def main() -> None:
    print("1. Generating deterministic AI output...")
    payload = get_ai_payload()
    print(f"   Payload: {json.dumps(payload)}")
    
    print("\n2. Hashing semantic output (SHA-256)...")
    payload_hash = hash_payload(payload)
    print(f"   Hash (Hex): {payload_hash.hex()}")
    
    print("\n3. Sending hash to TPM 2.0 (Isolated Temp Environment)...")
    pub_key, signature, is_valid = tpm_sign_and_verify(payload_hash)
    
    print("\n" + "="*60)
    print("TPM ARTIFACTS (Base64 Encoded for Readability)")
    print("="*60)
    
    # Convert binary bytes to readable Base64 strings
    pub_key_b64 = base64.b64encode(pub_key).decode('utf-8')
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    
    print(f"\n🔑 PUBLIC KEY:\n{pub_key_b64}")
    print(f"\n✍️ SIGNATURE:\n{sig_b64}")
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    if is_valid:
        print("✅ SUCCESS: Cryptographically verified by hardware.")
        print("   (No files were generated in your current directory)")
    else:
        print("❌ FAILURE: Verification failed.")

# THIS IS THE TRIGGER. Without this, the script runs silently.
if __name__ == "__main__":
    main()