fyproject

raw output:
```bash
[sudha@nryn-laptop-dualboot:~/fyproject]$ uv run fyproject
User: What's the weather like in Lagos right now?

---raw output---
{
  "type": "respond",
  "success": true,
  "error": null,
  "error_code": null,
  "reason": null,
  "function_calls": [],
  "reasoning": "User asked a question, respond with the weather data.",
  "confidence": 0.7025,
  "prefill_tps": 930.5,
  "decode_tps": 412.7,
  "peak_ram_mb": 52.3,
  "results": [
    {
      "city": "Lagos",
      "temp_c": 27,
      "sky": "clear"
    }
  ]
}
```

determinism output:
```bash
sudha@nryn-laptop-dualboot:~/fyproject]$ uv run python -m fyproject.test_determinism
Run 1: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 2: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 3: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 4: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 5: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 6: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 7: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 8: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 9: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5
Run 10: 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5

SUCCESS: All logical AI parameters are 100% functionally deterministic.

```
tpm signing:
```bash
(fyproject)
[sudha@nryn-laptop-dualboot:~/fyproject]$ uv run python -m fyproject.test_tpm
1. Generating deterministic AI output...
   Payload: {"type": "respond", "success": true, "error": null, "error_code": null, "reason": null, "function_calls": [], "reasoning": "User asked a question, respond with the weather data.", "results": [{"city": "Lagos", "temp_c": 27, "sky": "clear"}]}

2. Hashing semantic output (SHA-256)...
   Hash (Hex): 87d83df583a9f6656f42bc3c137d3f487e68f09ca55e8e20bcd3694d40226af5

3. Sending hash to TPM 2.0 (Isolated Temp Environment)...

============================================================
TPM ARTIFACTS (Base64 Encoded for Readability)
============================================================

PUBLIC KEY:
ARYAAQALAAYAcgAAABAAEAgAAAAAAAEAvFiE7ovhzTPOfGCvG/sP4CJv9q0rgNlaetF2dDntiFdGUqVcNm3tEnGZTvu8hjwMUkcbHFTJg96phWWY3UIy7BDtMONcDmGZMBybAMp+YM7DYOv0jOt6KHBDmGpUb2XHIcfdql2ZLACcu3viocQVbfXjp35m/JXvTLLge/biO+C0yPQLdTh/COA+jf3Y6E7/UNfKfPkwD93LdMKBkAz2KvBuwKqxVLgjOE1n+6K9WpZ/SVfQKHJ+oHlXd3rWXJFuhc2yjjxy/c2WXBOo/RU4lMmrW53bfEhe9bcjzu77QGeFfKCBnD+7fv821oshH86DLLpNMZHdwi6yJ5kn1ARBIQ==

SIGNATURE:
ABQACwEABe2C2Y06hqaRR0ZescVjpxk7x2kT2l7GtwD0l7hpcqc3T/MEAEfpeQJlJzEAMMq1gD6GhptoOMqyLUtFa0i06rghsCUlBng5cjO+gHnbzQNImkYLabijY3AoDgvGkT77ZO5Q5VyHf+5L6L1Rd+3eMdqZhSCMNZVyBqVnqCA0VtoXjZGyI3bgA8NI386ijCpUyaj/qN8GUb7ABU3MK7Ig5/WpMwjIGRrwo4ioGXpjBdowfR0zOn7j7iS7YJ4HcaIRaAzBKH2TLqxoaunDPvxCWVvPBj8XJNxdojDsCn/pXdNwPVt8zXRqw/fmLnWgFn1M9CLUhqVTRGItgwzSY3GRnw==

============================================================
VERIFICATION
============================================================
SUCCESS: Cryptographically verified by hardware.
   (No files were generated in your current directory)
```