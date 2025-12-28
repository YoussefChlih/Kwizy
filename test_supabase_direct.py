import os
import time
from dotenv import load_dotenv
load_dotenv()

from services.supabase_service import supabase_service

print("Testing Supabase connectivity...")
try:
    if not supabase_service.is_available:
        print("Supabase service not available (client init failed)")
    else:
        print("Supabase client initialized.")
        print("Attempting login with dummy credentials to check connectivity...")
        # detailed tracing
        start = time.time()
        try:
             # This should fail fast with "Invalid login" if connected, or hang if network issue
            result = supabase_service.login("test@test.com", "wrongpassword")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Exception during login: {e}")
        print(f"Time taken: {time.time() - start:.2f}s")

except Exception as e:
    print(f"Top level error: {e}")
